"""Independent, durable Full Evaluation Worker process."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shlex
import socket
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from backend.evaluation_models import EvaluationConflict
from backend.evaluation_runner import (
    CaseRunResult,
    CommandValidatorExecutor,
    DockerAgentConfig,
    DockerAgentExecutor,
    FormalCaseRunner,
)
from backend.evaluation_scheduler import EvaluationScheduler
from backend.evaluation_store import EvaluationStore
from backend.security import (
    SAFE_VALIDATOR_ISOLATION_MODES,
    validate_isolation_attestation,
)
from backend.submissions import (
    ArchiveLimits,
    make_agent_read_only,
    safe_extract_zip,
)

LOGGER = logging.getLogger("buildbench.evaluation_worker")


class WorkerConfigurationError(ValueError):
    pass


class CaseExecutor(Protocol):
    def prepare(self, evaluation: dict[str, object]) -> None: ...

    def run(
        self,
        *,
        claim: dict[str, object],
        evaluation: dict[str, object],
        attempt_root: Path,
    ) -> CaseRunResult | dict[str, object]: ...


@dataclass(frozen=True)
class WorkerConfig:
    database_path: Path
    submission_root: Path
    case_set_root: Path
    output_root: Path
    starter_kit_root: Path
    validator_command: tuple[str, ...]
    cleanup_image: str
    concurrency: int = 1
    lease_seconds: int = 120
    heartbeat_seconds: int = 30
    poll_seconds: float = 2.0
    agent_timeout_seconds: int = 900
    build_timeout_seconds: int = 1800
    build_attempt_limit: int = 3
    infrastructure_retry_limit: int = 2
    retry_backoff_seconds: int = 5
    allow_unsafe_validator: bool = False
    validator_isolation: str = "unsafe_privileged"
    isolation_attestation: Path | None = None
    agent_workspace_bytes: int = 512 * 1024 * 1024

    def validate(self) -> None:
        if self.concurrency <= 0:
            raise WorkerConfigurationError("Worker concurrency must be positive.")
        if self.lease_seconds <= 0:
            raise WorkerConfigurationError("Worker lease must be positive.")
        if not 0 < self.heartbeat_seconds < self.lease_seconds:
            raise WorkerConfigurationError(
                "Heartbeat interval must be shorter than the lease."
            )
        if self.poll_seconds <= 0:
            raise WorkerConfigurationError("Worker poll interval must be positive.")
        if self.agent_timeout_seconds <= 0 or self.build_timeout_seconds <= 0:
            raise WorkerConfigurationError("Worker timeouts must be positive.")
        if self.build_attempt_limit < 0:
            raise WorkerConfigurationError(
                "Build attempt limit must not be negative."
            )
        if self.infrastructure_retry_limit < 0:
            raise WorkerConfigurationError(
                "Infrastructure retry limit must not be negative."
            )
        if not self.validator_command:
            raise WorkerConfigurationError("Validator command is required.")
        if self.agent_workspace_bytes <= 0:
            raise WorkerConfigurationError(
                "Agent workspace quota must be positive."
            )
        if (
            not self.allow_unsafe_validator
            and self.validator_isolation not in SAFE_VALIDATOR_ISOLATION_MODES
        ):
            raise WorkerConfigurationError(
                "Untrusted evaluation requires a dedicated disposable "
                "Validator VM/Worker isolation mode."
            )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def _result_payload(result: CaseRunResult | dict[str, object]) -> dict[str, object]:
    return result.to_dict() if isinstance(result, CaseRunResult) else dict(result)


def _has_initial_failure_log(case_dir: Path) -> bool:
    return any(
        candidate.is_file() and not candidate.is_symlink()
        for candidate in (
            case_dir / "logs" / "original-target-failed.log",
            case_dir / "logs" / "initial-build.log",
            case_dir / "input" / "log_failed.txt",
            case_dir / "log_failed.txt",
        )
    )


class FormalEvaluationExecutor:
    """Resolve frozen resources and invoke the FE-3 formal Case runner."""

    def __init__(self, config: WorkerConfig, store: EvaluationStore):
        self.config = config
        self.store = store
        self._bb_build = (
            Path(__file__).resolve().parent / "runner_assets" / "bb-build"
        ).resolve(strict=True)

    def _submission_directory(self, evaluation: dict[str, object]) -> Path:
        submission_id = str(evaluation["submission_id"])
        return self.config.submission_root / "submissions" / submission_id

    def _case_directory(self, claim: dict[str, object]) -> Path:
        case_snapshot_id = str(claim["case_snapshot_id"])
        candidate = (self.config.case_set_root / case_snapshot_id).resolve()
        root = self.config.case_set_root.resolve()
        try:
            candidate.relative_to(root)
        except ValueError as error:
            raise WorkerConfigurationError(
                "Case snapshot path escaped the configured Case Store."
            ) from error
        return candidate

    def prepare(self, evaluation: dict[str, object]) -> None:
        submission = self._submission_directory(evaluation)
        archive = submission / "agent-submission.zip"
        if not archive.is_file():
            raise WorkerConfigurationError(
                "Immutable Agent archive is unavailable."
            )
        if _sha256(archive) != str(evaluation["submission_sha256"]):
            raise WorkerConfigurationError(
                "Immutable Agent archive failed integrity verification."
            )
        if not self.config.allow_unsafe_validator:
            isolation_error = validate_isolation_attestation(
                isolation_mode=self.config.validator_isolation,
                attestation_path=self.config.isolation_attestation,
                validator_image_digest=str(
                    evaluation["validator_image_digest"]
                ),
                protocol_config_hash=str(
                    evaluation["protocol_config_hash"]
                ),
            )
            if isolation_error:
                raise WorkerConfigurationError(isolation_error)
        if not self.config.starter_kit_root.is_dir():
            raise WorkerConfigurationError("Starter Kit is unavailable.")
        for case_run in self.store.list_case_runs(
            str(evaluation["evaluation_id"])
        ):
            case_dir = self._case_directory(case_run)
            if not case_dir.is_dir():
                raise WorkerConfigurationError(
                    "A frozen Case snapshot is unavailable."
                )
            if not _has_initial_failure_log(case_dir):
                raise WorkerConfigurationError(
                    "A frozen Case snapshot has no initial target-build log."
                )

    def _entrypoint(self, agent_dir: Path) -> tuple[str, ...]:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "runner.check_agent",
                "--agent",
                str(agent_dir),
                "--entrypoint",
            ],
            cwd=self.config.starter_kit_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
        if completed.returncode != 0:
            raise WorkerConfigurationError(
                "Qualified Agent could not be revalidated before execution."
            )
        entrypoint = tuple(
            line.strip()
            for line in completed.stdout.splitlines()
            if line.strip()
        )
        if not entrypoint:
            raise WorkerConfigurationError("Agent entrypoint is empty.")
        return entrypoint

    def run(
        self,
        *,
        claim: dict[str, object],
        evaluation: dict[str, object],
        attempt_root: Path,
    ) -> CaseRunResult:
        submission = self._submission_directory(evaluation)
        archive = submission / "agent-submission.zip"
        if _sha256(archive) != str(evaluation["submission_sha256"]):
            raise WorkerConfigurationError(
                "Immutable Agent archive changed after evaluation creation."
            )
        agent_dir = attempt_root / "agent"
        run_output = attempt_root / "result"
        safe_extract_zip(archive, agent_dir, ArchiveLimits())
        make_agent_read_only(agent_dir)
        entrypoint = self._entrypoint(agent_dir)
        runtime_image = str(evaluation["runtime_image_digest"])
        validator_image = str(evaluation["validator_image_digest"])
        agent = DockerAgentExecutor(
            DockerAgentConfig(
                image=runtime_image,
                entrypoint=entrypoint,
                timeout_seconds=self.config.agent_timeout_seconds,
                build_feedback_timeout_seconds=max(
                    min(
                        self.config.build_timeout_seconds,
                        self.config.agent_timeout_seconds - 30,
                    ),
                    1,
                ),
                workspace_bytes=self.config.agent_workspace_bytes,
            ),
            self._bb_build,
        )
        validator = CommandValidatorExecutor(
            self.config.validator_command,
            timeout_seconds=self.config.build_timeout_seconds,
            environment={
                "BUILD_CASE_RUNTIME_IMAGE": validator_image,
                "BUILD_CASE_CLEANUP_IMAGE": self.config.cleanup_image,
            },
        )
        runner = FormalCaseRunner(
            agent,
            validator,
            build_attempt_limit=self.config.build_attempt_limit,
        )
        return runner.run(
            case_run_id=str(claim["case_run_id"]),
            case_ordinal=int(claim["case_ordinal"]),
            case_dir=self._case_directory(claim),
            agent_dir=agent_dir,
            output_dir=run_output,
        )


class EvaluationWorker:
    """Claim and execute one CaseRun at a time using a renewable lease."""

    def __init__(
        self,
        *,
        store: EvaluationStore,
        scheduler: EvaluationScheduler,
        executor: CaseExecutor,
        config: WorkerConfig,
        worker_id: str,
    ):
        self.store = store
        self.scheduler = scheduler
        self.executor = executor
        self.config = config
        self.worker_id = worker_id

    def _attempt_root(self, claim: dict[str, object]) -> Path:
        return (
            self.config.output_root
            / str(claim["evaluation_id"])
            / "cases"
            / f"{int(claim['case_ordinal']):04d}"
            / f"attempt-{int(claim['attempt_count']):03d}"
        )

    def run_once(self) -> bool:
        self.scheduler.maintain()
        claim = self.store.claim_case_run(
            worker_id=self.worker_id,
            lease_seconds=self.config.lease_seconds,
        )
        if claim is None:
            self.scheduler.finalize_ready()
            return False
        evaluation = self.store.get(str(claim["evaluation_id"]))
        attempt_root = self._attempt_root(claim)
        try:
            attempt_root.mkdir(parents=True, exist_ok=False)
        except OSError as error:
            self.store.complete_claim(
                case_run_id=str(claim["case_run_id"]),
                worker_id=self.worker_id,
                result={
                    "status": "infrastructure_error",
                    "agent_status": "not_started",
                    "validator_status": None,
                    "message": (
                        "Worker could not create an isolated attempt directory: "
                        f"{type(error).__name__}"
                    ),
                    "duration_seconds": 0,
                    "agent_duration_seconds": 0,
                    "build_duration_seconds": 0,
                    "build_attempts": 0,
                    "repair_size_bytes": 0,
                    "modified_files": 0,
                },
                result_internal_path=str(attempt_root.resolve()),
                infrastructure_retry_limit=(
                    self.config.infrastructure_retry_limit
                ),
                retry_backoff_seconds=self.config.retry_backoff_seconds,
            )
            self.scheduler.finalize_ready()
            return True
        stop_heartbeat = threading.Event()

        def renew() -> None:
            while not stop_heartbeat.wait(self.config.heartbeat_seconds):
                try:
                    renewed = self.store.heartbeat_case_run(
                        case_run_id=str(claim["case_run_id"]),
                        worker_id=self.worker_id,
                        lease_seconds=self.config.lease_seconds,
                    )
                except Exception:
                    LOGGER.exception("CaseRun heartbeat failed")
                    return
                if not renewed:
                    return

        heartbeat = threading.Thread(
            target=renew,
            name=f"{self.worker_id}-heartbeat",
            daemon=True,
        )
        heartbeat.start()
        try:
            result = _result_payload(
                self.executor.run(
                    claim=claim,
                    evaluation=evaluation,
                    attempt_root=attempt_root,
                )
            )
        except Exception as error:
            result = {
                "status": "infrastructure_error",
                "agent_status": "not_started",
                "validator_status": None,
                "message": f"Worker execution failed: {type(error).__name__}",
                "duration_seconds": 0,
                "agent_duration_seconds": 0,
                "build_duration_seconds": 0,
                "build_attempts": 0,
                "repair_size_bytes": 0,
                "modified_files": 0,
            }
            (attempt_root / "worker-error.json").write_text(
                json.dumps(
                    {
                        "error_type": type(error).__name__,
                        "message": str(error)[:1000],
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
        finally:
            stop_heartbeat.set()
            heartbeat.join(timeout=max(self.config.heartbeat_seconds, 1) + 1)

        try:
            self.store.complete_claim(
                case_run_id=str(claim["case_run_id"]),
                worker_id=self.worker_id,
                result=result,
                result_internal_path=str(attempt_root.resolve()),
                infrastructure_retry_limit=(
                    self.config.infrastructure_retry_limit
                ),
                retry_backoff_seconds=self.config.retry_backoff_seconds,
            )
        except EvaluationConflict:
            # A lease may expire during a host-level stall and be reclaimed by
            # another Worker. Keep this attempt as orphan evidence, but never
            # overwrite the new owner's result.
            (attempt_root / "lease-lost.json").write_text(
                json.dumps(
                    {
                        "case_run_id": claim["case_run_id"],
                        "worker_id": self.worker_id,
                        "message": (
                            "Result was not committed because the lease was "
                            "reclaimed."
                        ),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
        self.scheduler.finalize_ready()
        return True


class EvaluationWorkerPool:
    def __init__(
        self,
        *,
        store: EvaluationStore,
        executor: CaseExecutor,
        config: WorkerConfig,
        instance_id: str | None = None,
    ):
        config.validate()
        self.store = store
        self.executor = executor
        self.config = config
        base = instance_id or (
            f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        )
        self.scheduler = EvaluationScheduler(store, executor.prepare)
        self.workers = [
            EvaluationWorker(
                store=store,
                scheduler=self.scheduler,
                executor=executor,
                config=config,
                worker_id=f"{base}-{index + 1}",
            )
            for index in range(config.concurrency)
        ]

    def run_until_idle(self, idle_cycles: int = 2) -> int:
        processed = 0
        processed_lock = threading.Lock()

        def until_idle_loop(worker: EvaluationWorker) -> None:
            nonlocal processed
            idle = 0
            while idle < max(idle_cycles, 1):
                completed = worker.run_once()
                if completed:
                    with processed_lock:
                        processed += 1
                    idle = 0
                    continue
                self.scheduler.maintain()
                active = self.store.list_by_status(
                    "queued",
                    "preparing",
                    "evaluating",
                    "finalizing",
                )
                idle = 0 if active else idle + 1
                time.sleep(self.config.poll_seconds)

        with ThreadPoolExecutor(
            max_workers=len(self.workers),
            thread_name_prefix="bb-evaluation",
        ) as pool:
            futures = [
                pool.submit(until_idle_loop, worker)
                for worker in self.workers
            ]
            for future in futures:
                future.result()
        self.scheduler.maintain()
        return processed

    def run_forever(self) -> None:
        with ThreadPoolExecutor(
            max_workers=len(self.workers),
            thread_name_prefix="bb-evaluation",
        ) as pool:
            futures = []
            for worker in self.workers:
                futures.append(pool.submit(self._worker_loop, worker))
            for future in futures:
                future.result()

    def _worker_loop(self, worker: EvaluationWorker) -> None:
        while True:
            try:
                if not worker.run_once():
                    time.sleep(self.config.poll_seconds)
            except Exception:
                LOGGER.exception("Evaluation Worker iteration failed")
                time.sleep(self.config.poll_seconds)


def _default_path(environment: str, fallback: Path) -> Path:
    return Path(os.environ.get(environment, fallback)).expanduser()


def main() -> int:
    website_root = Path(__file__).resolve().parents[1]
    competition_root = website_root.parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database",
        type=Path,
        default=_default_path(
            "BB_EVALUATION_DB",
            website_root / "runtime-data" / "evaluations.sqlite3",
        ),
    )
    parser.add_argument(
        "--submission-root",
        type=Path,
        default=_default_path(
            "BB_WEB_DATA_ROOT",
            website_root / "runtime-data",
        ),
    )
    parser.add_argument(
        "--case-set-root",
        type=Path,
        default=_default_path(
            "BB_CASE_SET_ROOT",
            competition_root / "shared" / "case-store",
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=_default_path(
            "BB_EVALUATION_OUTPUT_ROOT",
            competition_root / "workspaces" / "full-evaluations",
        ),
    )
    parser.add_argument(
        "--starter-kit",
        type=Path,
        default=_default_path(
            "BB_STARTER_KIT_ROOT",
            competition_root / "buildbench-starter-kit",
        ),
    )
    parser.add_argument(
        "--validator-command",
        default=os.environ.get(
            "BB_VALIDATOR_COMMAND",
            str(competition_root / "docker-validator" / "bin" / "build-case-docker"),
        ),
    )
    parser.add_argument(
        "--cleanup-image",
        default=os.environ.get("BB_CLEANUP_IMAGE", "ubuntu:24.04"),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.environ.get("BB_EVALUATION_WORKERS", "2")),
    )
    parser.add_argument(
        "--lease-seconds",
        type=int,
        default=int(os.environ.get("BB_CASE_LEASE_SECONDS", "120")),
    )
    parser.add_argument(
        "--heartbeat-seconds",
        type=int,
        default=int(os.environ.get("BB_CASE_HEARTBEAT_SECONDS", "30")),
    )
    parser.add_argument(
        "--poll-seconds",
        type=float,
        default=float(os.environ.get("BB_WORKER_POLL_SECONDS", "2")),
    )
    parser.add_argument(
        "--agent-timeout",
        type=int,
        default=int(os.environ.get("BB_CASE_TIMEOUT_SECONDS", "900")),
    )
    parser.add_argument(
        "--build-timeout",
        type=int,
        default=int(os.environ.get("BB_BUILD_TIMEOUT_SECONDS", "1800")),
    )
    parser.add_argument(
        "--build-attempt-limit",
        type=int,
        default=int(os.environ.get("BB_BUILD_ATTEMPT_LIMIT", "3")),
    )
    parser.add_argument(
        "--infra-retry-limit",
        type=int,
        default=int(os.environ.get("BB_INFRA_RETRY_LIMIT", "2")),
    )
    parser.add_argument(
        "--retry-backoff-seconds",
        type=int,
        default=int(os.environ.get("BB_INFRA_RETRY_BACKOFF_SECONDS", "5")),
    )
    parser.add_argument(
        "--trusted-development",
        action="store_true",
        default=os.environ.get("BB_ALLOW_UNSAFE_VALIDATOR", "0") == "1",
        help=(
            "Allow organizer-controlled pilots with the current unsafe "
            "Validator. This is not a production security approval."
        ),
    )
    parser.add_argument(
        "--validator-isolation",
        default=os.environ.get(
            "BB_VALIDATOR_ISOLATION", "unsafe_privileged"
        ),
    )
    parser.add_argument(
        "--isolation-attestation",
        type=Path,
        default=(
            Path(os.environ["BB_VALIDATOR_ISOLATION_ATTESTATION"])
            if os.environ.get("BB_VALIDATOR_ISOLATION_ATTESTATION")
            else None
        ),
    )
    parser.add_argument(
        "--agent-workspace-bytes",
        type=int,
        default=int(
            os.environ.get("BB_AGENT_WORKSPACE_BYTES", str(512 * 1024 * 1024))
        ),
    )
    parser.add_argument(
        "--until-idle",
        action="store_true",
        help="Process available jobs, then exit after two idle polls.",
    )
    args = parser.parse_args()

    config = WorkerConfig(
        database_path=args.database.resolve(),
        submission_root=args.submission_root.resolve(),
        case_set_root=args.case_set_root.resolve(),
        output_root=args.output_root.resolve(),
        starter_kit_root=args.starter_kit.resolve(),
        validator_command=tuple(shlex.split(args.validator_command)),
        cleanup_image=args.cleanup_image,
        concurrency=args.concurrency,
        lease_seconds=args.lease_seconds,
        heartbeat_seconds=args.heartbeat_seconds,
        poll_seconds=args.poll_seconds,
        agent_timeout_seconds=args.agent_timeout,
        build_timeout_seconds=args.build_timeout,
        build_attempt_limit=args.build_attempt_limit,
        infrastructure_retry_limit=args.infra_retry_limit,
        retry_backoff_seconds=args.retry_backoff_seconds,
        allow_unsafe_validator=args.trusted_development,
        validator_isolation=args.validator_isolation,
        isolation_attestation=(
            args.isolation_attestation.resolve()
            if args.isolation_attestation
            else None
        ),
        agent_workspace_bytes=args.agent_workspace_bytes,
    )
    config.validate()
    config.output_root.mkdir(parents=True, exist_ok=True)
    store = EvaluationStore(config.database_path)
    executor = FormalEvaluationExecutor(config, store)
    logging.basicConfig(
        level=os.environ.get("BB_WORKER_LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    pool = EvaluationWorkerPool(
        store=store,
        executor=executor,
        config=config,
    )
    print(
        json.dumps(
            {
                "database": str(config.database_path),
                "case_set_root": str(config.case_set_root),
                "output_root": str(config.output_root),
                "concurrency": config.concurrency,
                "trusted_development": config.allow_unsafe_validator,
            },
            indent=2,
            sort_keys=True,
        ),
        flush=True,
    )
    if args.until_idle:
        processed = pool.run_until_idle()
        print(f"Processed attempts: {processed}", flush=True)
        return 0
    pool.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
