"""Formal, structured execution of one Agent against one Case snapshot."""

from __future__ import annotations

import json
import os
import secrets
import shutil
import stat
import subprocess
import tempfile
import time
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from backend.build_gateway import (
    BuildGateway,
    GatewayContext,
    UnixBuildGatewayServer,
    Validator,
)
from backend.canonical_patch import (
    CanonicalPatchError,
    generate_canonical_patch,
    write_canonical_patch,
)
from backend.evaluation_models import TERMINAL_CASE_RUN_STATUSES


AGENT_RESULT_STATUSES = frozenset({"completed", "no_fix"})
VALIDATOR_STATUSES = frozenset(
    {
        "succeeded",
        "failed",
        "unresolvable",
        "timeout",
        "invalid_patch",
        "infrastructure_error",
    }
)


class CaseRunnerError(ValueError):
    pass


@dataclass(frozen=True)
class AgentExecution:
    status: str
    exit_code: int | None
    duration_seconds: int
    timed_out: bool = False
    message: str = ""


@dataclass(frozen=True)
class CaseRunResult:
    schema_version: str
    case_run_id: str
    case_ordinal: int
    status: str
    agent_status: str
    validator_status: str | None
    message: str
    duration_seconds: int
    agent_duration_seconds: int
    build_duration_seconds: int
    build_attempts: int
    repair_size_bytes: int
    modified_files: int
    timed_out: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class AgentExecutor(Protocol):
    def run(
        self,
        *,
        agent_dir: Path,
        workspace: Path,
        log_path: Path,
        gateway_socket: Path,
        gateway_token: str,
    ) -> AgentExecution: ...


class ValidatorExecutor(Protocol):
    def validate(
        self, case_dir: Path, patch_path: Path, output_dir: Path
    ) -> dict[str, object]: ...


@dataclass(frozen=True)
class DockerAgentConfig:
    image: str
    entrypoint: tuple[str, ...]
    timeout_seconds: int
    cpus: str = "1"
    memory: str = "2g"
    pids_limit: int = 256
    build_feedback_timeout_seconds: int = 900
    workspace_bytes: int = 512 * 1024 * 1024
    docker_command: str = "docker"


class DockerAgentExecutor:
    """Run one managed Agent without exposing Docker or organizer paths."""

    def __init__(self, config: DockerAgentConfig, bb_build_client: Path):
        image_id = (
            config.image.startswith("sha256:")
            and len(config.image) == len("sha256:") + 64
        )
        repo_digest = "@sha256:" in config.image
        if not config.image or not (image_id or repo_digest):
            raise ValueError("Agent image must be pinned by digest")
        if not config.entrypoint:
            raise ValueError("Agent entrypoint is required")
        if config.timeout_seconds <= 0:
            raise ValueError("Agent timeout must be positive")
        if config.build_feedback_timeout_seconds <= 0:
            raise ValueError("Build feedback timeout must be positive")
        if config.workspace_bytes <= 0:
            raise ValueError("Agent workspace quota must be positive")
        self.config = config
        self.bb_build_client = bb_build_client.resolve(strict=True)

    def command(
        self,
        *,
        agent_dir: Path,
        workspace: Path,
        gateway_socket: Path,
        gateway_token: str,
        container_name: str,
    ) -> list[str]:
        del gateway_token
        socket_dir = gateway_socket.parent
        return [
            self.config.docker_command,
            "run",
            "--rm",
            "--name",
            container_name,
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--cpus",
            self.config.cpus,
            "--memory",
            self.config.memory,
            "--pids-limit",
            str(self.config.pids_limit),
            "--ulimit",
            "nofile=1024:1024",
            "--user",
            (
                f"{getattr(os, 'getuid', lambda: 1000)()}:"
                f"{getattr(os, 'getgid', lambda: 1000)()}"
            ),
            "-e",
            "HOME=/tmp",
            "-e",
            "PYTHONDONTWRITEBYTECODE=1",
            "-e",
            "PYTHONPATH=/agent",
            "-e",
            "PATH=/opt/buildbench/bin:/usr/local/bin:/usr/bin:/bin",
            "-e",
            "BB_WORKSPACE=/workspace",
            "-e",
            "BB_BUILD_GATEWAY_SOCKET=/run/buildbench/gateway.sock",
            "-e",
            "BB_BUILD_GATEWAY_TOKEN_FILE=/run/buildbench/capability-token",
            "-e",
            (
                "BB_BUILD_GATEWAY_TIMEOUT_SECONDS="
                f"{self.config.build_feedback_timeout_seconds}"
            ),
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=64m",
            "--tmpfs",
            "/opt/buildbench/bin:rw,exec,nosuid,nodev,size=1m",
            "-v",
            f"{agent_dir.resolve()}:/agent:ro",
            "-v",
            f"{workspace / 'input'}:/workspace/input:ro",
            "-v",
            f"{workspace / 'work'}:/workspace/work",
            "-v",
            f"{workspace / 'output'}:/workspace/output",
            "-v",
            f"{socket_dir.resolve()}:/run/buildbench:ro",
            "-v",
            f"{self.bb_build_client}:/opt/buildbench/assets/bb-build:ro",
            "-w",
            "/agent",
            self.config.image,
            "sh",
            "-eu",
            "-c",
            (
                "cp /opt/buildbench/assets/bb-build "
                "/opt/buildbench/bin/bb-build; "
                "chmod 0555 /opt/buildbench/bin/bb-build; "
                'exec "$@"'
            ),
            "sh",
            *self.config.entrypoint,
        ]

    def run(
        self,
        *,
        agent_dir: Path,
        workspace: Path,
        log_path: Path,
        gateway_socket: Path,
        gateway_token: str,
    ) -> AgentExecution:
        started = time.monotonic()
        container_name = "bb-agent-" + secrets.token_hex(8)
        command = self.command(
            agent_dir=agent_dir,
            workspace=workspace,
            gateway_socket=gateway_socket,
            gateway_token=gateway_token,
            container_name=container_name,
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        termination: str | None = None
        return_code: int | None = None
        try:
            with log_path.open("wb") as log:
                process = subprocess.Popen(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    shell=False,
                )
                while process.poll() is None:
                    elapsed = time.monotonic() - started
                    if elapsed >= self.config.timeout_seconds:
                        termination = "timeout"
                        break
                    if _tree_bytes(workspace / "work") + _tree_bytes(
                        workspace / "output"
                    ) > self.config.workspace_bytes:
                        termination = "workspace_limit"
                        break
                    time.sleep(0.25)
                if termination is None:
                    return_code = process.wait(timeout=5)
                else:
                    self._force_remove_container(container_name)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            termination = "timeout"
            self._force_remove_container(container_name)
        except OSError:
            return AgentExecution(
                status="agent_error",
                exit_code=None,
                duration_seconds=int(time.monotonic() - started),
                message="Agent runtime could not be started.",
            )
        if termination == "timeout":
            return AgentExecution(
                status="timeout",
                exit_code=None,
                duration_seconds=int(time.monotonic() - started),
                timed_out=True,
                message="Agent exceeded its Case wall-time limit.",
            )
        if termination == "workspace_limit":
            return AgentExecution(
                status="agent_error",
                exit_code=None,
                duration_seconds=int(time.monotonic() - started),
                message="Agent exceeded its Case workspace quota.",
            )
        status = "completed" if return_code == 0 else "agent_error"
        return AgentExecution(
            status=status,
            exit_code=return_code,
            duration_seconds=int(time.monotonic() - started),
            message=(
                "Agent completed."
                if return_code == 0
                else f"Agent exited with code {return_code}."
            ),
        )

    def _force_remove_container(self, container_name: str) -> None:
        """Best-effort, bounded cleanup even when the Docker daemon stalls."""

        try:
            subprocess.run(
                [self.config.docker_command, "rm", "-f", container_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                shell=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            # The container may not exist yet, or the daemon may be unhealthy.
            # Worker state handling must not be blocked by cleanup diagnostics.
            return


class CommandValidatorExecutor:
    """Invoke the versioned Docker Validator CLI as a separate component."""

    def __init__(
        self,
        command: tuple[str, ...],
        *,
        timeout_seconds: int,
        environment: dict[str, str] | None = None,
    ):
        if not command:
            raise ValueError("Validator command is required")
        if timeout_seconds <= 0:
            raise ValueError("Validator timeout must be positive")
        self.command = command
        self.timeout_seconds = timeout_seconds
        self.environment = dict(environment or {})

    def validate(
        self, case_dir: Path, patch_path: Path, output_dir: Path
    ) -> dict[str, object]:
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        console = output_dir.parent / f"{output_dir.name}.console.log"
        command = [
            *self.command,
            "--input",
            str(case_dir.resolve()),
            "--patch",
            str(patch_path.resolve()),
            "--output",
            str(output_dir.resolve()),
        ]
        environment = os.environ.copy()
        environment.update(self.environment)
        try:
            with console.open("wb") as log:
                completed = subprocess.run(
                    command,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                    shell=False,
                    timeout=self.timeout_seconds,
                    env=environment,
                )
        except subprocess.TimeoutExpired:
            return {
                "status": "infrastructure_error",
                "message": "Validator process exceeded its platform timeout.",
                "duration_seconds": self.timeout_seconds,
            }
        except OSError:
            return {
                "status": "infrastructure_error",
                "message": "Validator process could not be started.",
                "duration_seconds": 0,
            }

        result_path = output_dir / "build-result.json"
        try:
            payload = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return {
                "status": "infrastructure_error",
                "message": (
                    "Validator did not produce a valid build-result.json "
                    f"(exit {completed.returncode})."
                ),
                "duration_seconds": 0,
            }
        status = str(payload.get("status") or "")
        if status not in VALIDATOR_STATUSES:
            return {
                "status": "infrastructure_error",
                "message": "Validator returned an unsupported status.",
                "duration_seconds": int(payload.get("duration_seconds") or 0),
            }
        return payload


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        )
    temporary.replace(path)


def _tree_bytes(root: Path) -> int:
    """Measure regular files without following Agent-created symlinks."""

    total = 0
    if not root.exists():
        return 0
    for directory, directories, files in os.walk(root, followlinks=False):
        directories[:] = [
            name
            for name in directories
            if not (Path(directory) / name).is_symlink()
        ]
        for name in files:
            path = Path(directory) / name
            try:
                if not path.is_symlink():
                    total += path.stat().st_size
            except OSError:
                continue
    return total


def _copy_case(source: Path, destination: Path) -> None:
    if not source.is_dir() or source.is_symlink():
        raise CaseRunnerError("Case snapshot must be a physical directory")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise CaseRunnerError("Case snapshot contains a symbolic link")
    shutil.copytree(source, destination)


def _initial_log(case_dir: Path) -> Path:
    candidates = (
        case_dir / "logs" / "original-target-failed.log",
        case_dir / "logs" / "initial-build.log",
        case_dir / "input" / "log_failed.txt",
        case_dir / "log_failed.txt",
    )
    for candidate in candidates:
        if candidate.is_file() and not candidate.is_symlink():
            return candidate
    raise CaseRunnerError("Case snapshot has no initial target-build log")


def _agent_result(output_dir: Path) -> tuple[str, str]:
    path = output_dir / "agent-result.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "agent_error", "Agent did not produce a valid agent-result.json."
    if not isinstance(payload, dict):
        return "agent_error", "Agent result must be a JSON object."
    status = str(payload.get("status") or "")
    if status not in AGENT_RESULT_STATUSES:
        return "agent_error", "Agent result contains an unsupported status."
    message = str(payload.get("message") or "")
    return status, message[:500]


class FormalCaseRunner:
    """Run one Case without converting ordinary repair failures into job loss."""

    def __init__(
        self,
        agent_executor: AgentExecutor,
        validator_executor: ValidatorExecutor,
        *,
        build_attempt_limit: int,
        gateway_server_factory: Callable[
            [BuildGateway, Path], AbstractContextManager[object]
        ] = UnixBuildGatewayServer,
    ):
        if build_attempt_limit < 0:
            raise ValueError("build_attempt_limit must not be negative")
        self.agent_executor = agent_executor
        self.validator_executor = validator_executor
        self.build_attempt_limit = build_attempt_limit
        self.gateway_server_factory = gateway_server_factory

    def _finish(
        self,
        output_dir: Path,
        *,
        case_run_id: str,
        case_ordinal: int,
        status: str,
        agent_status: str,
        validator_status: str | None,
        message: str,
        started: float,
        agent_duration: int,
        build_duration: int,
        build_attempts: int,
        repair_size: int = 0,
        modified_files: int = 0,
        timed_out: bool = False,
    ) -> CaseRunResult:
        if status not in TERMINAL_CASE_RUN_STATUSES:
            raise AssertionError(f"invalid terminal CaseRun status: {status}")
        result = CaseRunResult(
            schema_version="0.1",
            case_run_id=case_run_id,
            case_ordinal=case_ordinal,
            status=status,
            agent_status=agent_status,
            validator_status=validator_status,
            message=message[:600],
            duration_seconds=max(int(time.monotonic() - started), 0),
            agent_duration_seconds=max(agent_duration, 0),
            build_duration_seconds=max(build_duration, 0),
            build_attempts=max(build_attempts, 0),
            repair_size_bytes=max(repair_size, 0),
            modified_files=max(modified_files, 0),
            timed_out=timed_out,
        )
        _write_json(output_dir / "case-run-result.json", result.to_dict())
        return result

    def run(
        self,
        *,
        case_run_id: str,
        case_ordinal: int,
        case_dir: Path,
        agent_dir: Path,
        output_dir: Path,
    ) -> CaseRunResult:
        started = time.monotonic()
        if case_ordinal <= 0:
            raise CaseRunnerError("case_ordinal must be positive")
        if output_dir.exists() and any(output_dir.iterdir()):
            raise CaseRunnerError("CaseRun output directory must be empty")
        output_dir.mkdir(parents=True, exist_ok=True)

        internal = output_dir / ".internal"
        original = internal / "case-original"
        workspace = internal / "workspace"
        worktree = workspace / "work" / "repo"
        agent_output = workspace / "output"
        gateway_root = internal / "gateway"
        final_root = internal / "final-validation"

        try:
            _copy_case(case_dir.resolve(strict=True), original)
            _copy_case(original, worktree)
            (workspace / "input").mkdir(parents=True)
            agent_output.mkdir(parents=True)
            gateway_root.mkdir(parents=True)
            initial = _initial_log(original)
            shutil.copyfile(initial, workspace / "input" / "initial-build.log")
            _write_json(
                workspace / "input" / "task.json",
                {
                    "schema_version": "0.1",
                    "case_ordinal": case_ordinal,
                    "worktree": "/workspace/work/repo",
                    "initial_build_log": (
                        "/workspace/input/initial-build.log"
                    ),
                    "build_feedback": {
                        "command": "bb-build",
                        "attempt_limit": self.build_attempt_limit,
                    },
                },
            )
        except (OSError, ValueError, CaseRunnerError) as error:
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="infrastructure_error",
                agent_status="not_started",
                validator_status=None,
                message=f"CaseRun preparation failed: {error}",
                started=started,
                agent_duration=0,
                build_duration=0,
                build_attempts=0,
            )

        def validate(
            fixed_case: Path, fixed_patch: Path, fixed_output: Path
        ) -> dict[str, object]:
            return self.validator_executor.validate(
                fixed_case, fixed_patch, fixed_output
            )

        gateway = BuildGateway(
            GatewayContext(
                original_case=original,
                worktree=worktree,
                output_root=gateway_root / "attempts",
                attempt_limit=self.build_attempt_limit,
            ),
            validate,
        )
        agent_log = output_dir / "agent.log"
        try:
            socket_root = os.environ.get(
                "BB_GATEWAY_SOCKET_ROOT",
                tempfile.gettempdir(),
            )
            with tempfile.TemporaryDirectory(
                prefix="bb-gw-",
                dir=socket_root,
            ) as runtime_name:
                runtime_dir = Path(runtime_name)
                runtime_dir.chmod(stat.S_IRWXU)
                socket_path = runtime_dir / "gateway.sock"
                token_path = runtime_dir / "capability-token"
                token_path.write_text(
                    gateway.capability_token + "\n",
                    encoding="utf-8",
                )
                token_path.chmod(stat.S_IRUSR)
                with self.gateway_server_factory(gateway, socket_path):
                    agent = self.agent_executor.run(
                        agent_dir=agent_dir,
                        workspace=workspace,
                        log_path=agent_log,
                        gateway_socket=socket_path,
                        gateway_token=gateway.capability_token,
                    )
        except (OSError, RuntimeError) as error:
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="infrastructure_error",
                agent_status="not_started",
                validator_status=None,
                message=str(error),
                started=started,
                agent_duration=0,
                build_duration=0,
                build_attempts=gateway.attempts,
            )

        if agent.timed_out or agent.status == "timeout":
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="timeout",
                agent_status="timeout",
                validator_status=None,
                message=agent.message or "Agent timed out.",
                started=started,
                agent_duration=agent.duration_seconds,
                build_duration=0,
                build_attempts=gateway.attempts,
                timed_out=True,
            )
        if agent.status != "completed" or agent.exit_code not in (0, None):
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="agent_error",
                agent_status="agent_error",
                validator_status=None,
                message=agent.message or "Agent failed.",
                started=started,
                agent_duration=agent.duration_seconds,
                build_duration=0,
                build_attempts=gateway.attempts,
            )

        declared_status, declared_message = _agent_result(agent_output)
        if declared_status == "agent_error":
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="agent_error",
                agent_status="invalid_output",
                validator_status=None,
                message=declared_message,
                started=started,
                agent_duration=agent.duration_seconds,
                build_duration=0,
                build_attempts=gateway.attempts,
            )
        if declared_status == "no_fix":
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="no_fix",
                agent_status="no_fix",
                validator_status=None,
                message=declared_message or "Agent proposed no repair.",
                started=started,
                agent_duration=agent.duration_seconds,
                build_duration=0,
                build_attempts=gateway.attempts,
            )

        patch_path = output_dir / "repair.diff"
        try:
            patch = generate_canonical_patch(original, worktree)
            write_canonical_patch(patch_path, patch)
        except CanonicalPatchError as error:
            status = (
                "no_fix"
                if "no allowed textual change" in str(error)
                else "invalid_patch"
            )
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status=status,
                agent_status="completed",
                validator_status=None,
                message=str(error),
                started=started,
                agent_duration=agent.duration_seconds,
                build_duration=0,
                build_attempts=gateway.attempts,
            )
        except (OSError, UnicodeError) as error:
            return self._finish(
                output_dir,
                case_run_id=case_run_id,
                case_ordinal=case_ordinal,
                status="infrastructure_error",
                agent_status="completed",
                validator_status=None,
                message=f"Canonical patch could not be persisted: {error}",
                started=started,
                agent_duration=agent.duration_seconds,
                build_duration=0,
                build_attempts=gateway.attempts,
            )

        final = self.validator_executor.validate(
            original, patch_path, final_root
        )
        validator_status = str(
            final.get("status") or "infrastructure_error"
        )
        if validator_status not in VALIDATOR_STATUSES:
            validator_status = "infrastructure_error"
        build_duration = int(final.get("duration_seconds") or 0)
        for name in ("build-result.json", "build.log"):
            source = final_root / name
            if source.is_file():
                shutil.copyfile(source, output_dir / name)
        artifacts = final_root / "artifacts"
        if artifacts.is_dir():
            shutil.copytree(artifacts, output_dir / "artifacts")

        return self._finish(
            output_dir,
            case_run_id=case_run_id,
            case_ordinal=case_ordinal,
            status=validator_status,
            agent_status="completed",
            validator_status=validator_status,
            message=str(final.get("message") or "Validation completed."),
            started=started,
            agent_duration=agent.duration_seconds,
            build_duration=build_duration,
            build_attempts=gateway.attempts,
            repair_size=patch.size_bytes,
            modified_files=len(patch.changed_paths),
            timed_out=bool(final.get("timed_out")),
        )
