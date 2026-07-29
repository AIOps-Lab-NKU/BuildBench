"""Production isolation contracts for one-shot Full Evaluation workers."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import shutil
import stat
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
JOB_ID_PATTERN = re.compile(r"^JOB-[A-Za-z0-9][A-Za-z0-9._-]{7,95}$")
JOB_SCHEMA_VERSION = "0.1"
RECEIPT_SCHEMA_VERSION = "0.1"
ALLOWED_OUTPUT_FILES = frozenset(
    {
        "case-run-result.json",
        "worker-receipt.json",
        "agent.log",
        "build.log",
        "repair.diff",
        "validator-console.log",
        "worker-console.log",
    }
)
ALLOWED_OUTPUT_DIRECTORIES = frozenset({"artifacts"})


class IsolationError(ValueError):
    """A fail-closed production isolation or evidence error."""


def canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def sha256_tree(root: Path) -> str:
    """Hash a physical tree without following symlinks."""

    if not root.is_dir() or root.is_symlink():
        raise IsolationError("Case snapshot must be a physical directory.")
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise IsolationError("Case snapshot contains a symbolic link.")
        if stat.S_ISDIR(mode):
            digest.update(b"D\0" + relative.encode("utf-8") + b"\0")
            continue
        if not stat.S_ISREG(mode):
            raise IsolationError("Case snapshot contains a special file.")
        digest.update(b"F\0" + relative.encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(sha256_file(path).removeprefix("sha256:")))
    return "sha256:" + digest.hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_utc(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise IsolationError(f"{label} is not a valid timestamp.") from None
    if parsed.tzinfo is None:
        raise IsolationError(f"{label} must include a timezone.")
    return parsed.astimezone(timezone.utc)


def _require_sha256(value: str, label: str) -> str:
    if not SHA256_PATTERN.fullmatch(value):
        raise IsolationError(f"{label} must be a sha256 digest.")
    return value


@dataclass(frozen=True)
class IsolatedJobEnvelope:
    schema_version: str
    job_id: str
    evaluation_id: str
    case_run_id: str
    case_ordinal: int
    created_at: str
    expires_at: str
    submission_sha256: str
    case_snapshot_sha256: str
    runtime_image_digest: str
    validator_image_digest: str
    protocol_config_hash: str
    guest_image_sha256: str
    nonce: str
    agent_timeout_seconds: int
    build_timeout_seconds: int
    build_attempt_limit: int
    workspace_bytes: int

    def validate(self, *, now: datetime | None = None) -> None:
        if self.schema_version != JOB_SCHEMA_VERSION:
            raise IsolationError("Unsupported isolated job schema.")
        if not JOB_ID_PATTERN.fullmatch(self.job_id):
            raise IsolationError("Invalid isolated job ID.")
        for label, value in (
            ("evaluation_id", self.evaluation_id),
            ("case_run_id", self.case_run_id),
            ("nonce", self.nonce),
        ):
            if not value or len(value) > 160:
                raise IsolationError(f"{label} is invalid.")
        if self.case_ordinal <= 0:
            raise IsolationError("case_ordinal must be positive.")
        if (
            self.agent_timeout_seconds <= 0
            or self.build_timeout_seconds <= 0
            or self.build_attempt_limit < 0
            or self.workspace_bytes <= 0
        ):
            raise IsolationError("Isolated job resource policy is invalid.")
        for label, value in (
            ("submission_sha256", self.submission_sha256),
            ("case_snapshot_sha256", self.case_snapshot_sha256),
            ("runtime_image_digest", self.runtime_image_digest),
            ("validator_image_digest", self.validator_image_digest),
            ("protocol_config_hash", self.protocol_config_hash),
            ("guest_image_sha256", self.guest_image_sha256),
        ):
            _require_sha256(value, label)
        created = _parse_utc(self.created_at, "created_at")
        expires = _parse_utc(self.expires_at, "expires_at")
        current = now or _utc_now()
        if expires <= current:
            raise IsolationError("Isolated job envelope has expired.")
        if expires <= created or expires - created > timedelta(hours=24):
            raise IsolationError("Isolated job validity window is invalid.")

    def write(self, path: Path) -> None:
        self.validate()
        path.write_bytes(canonical_json(asdict(self)) + b"\n")

    @classmethod
    def read(cls, path: Path, *, now: datetime | None = None) -> "IsolatedJobEnvelope":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            envelope = cls(**payload)
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
            raise IsolationError("Isolated job envelope is invalid.") from None
        envelope.validate(now=now)
        return envelope


@dataclass(frozen=True)
class IsolationReceipt:
    schema_version: str
    job_id: str
    worker_id: str
    worker_boot_id: str
    started_at: str
    finished_at: str
    input_envelope_sha256: str
    result_sha256: str
    guest_image_sha256: str
    validator_image_digest: str
    protocol_config_hash: str
    docker_socket_exposed_to_agent: bool
    host_docker_socket_mounted_in_worker: bool
    host_case_store_mounted_in_worker: bool
    worker_reused_between_cases: bool
    network_mode: str
    nonce: str
    document_sha256: str

    def validate(
        self,
        envelope: IsolatedJobEnvelope,
        *,
        envelope_path: Path,
        result_path: Path,
    ) -> None:
        if self.schema_version != RECEIPT_SCHEMA_VERSION:
            raise IsolationError("Unsupported worker receipt schema.")
        expected = {
            "job_id": envelope.job_id,
            "input_envelope_sha256": sha256_file(envelope_path),
            "result_sha256": sha256_file(result_path),
            "guest_image_sha256": envelope.guest_image_sha256,
            "validator_image_digest": envelope.validator_image_digest,
            "protocol_config_hash": envelope.protocol_config_hash,
            "docker_socket_exposed_to_agent": False,
            "host_docker_socket_mounted_in_worker": False,
            "host_case_store_mounted_in_worker": False,
            "worker_reused_between_cases": False,
            "network_mode": "none",
            "nonce": envelope.nonce,
        }
        for key, value in expected.items():
            if getattr(self, key) != value:
                raise IsolationError(f"Worker receipt does not match {key}.")
        if not self.worker_id or not self.worker_boot_id:
            raise IsolationError("Worker identity evidence is incomplete.")
        started = _parse_utc(self.started_at, "started_at")
        finished = _parse_utc(self.finished_at, "finished_at")
        if finished < started:
            raise IsolationError("Worker receipt time range is invalid.")
        unsigned = asdict(self)
        unsigned.pop("document_sha256")
        actual = "sha256:" + hashlib.sha256(canonical_json(unsigned)).hexdigest()
        if not hmac.compare_digest(self.document_sha256, actual):
            raise IsolationError("Worker receipt digest is invalid.")

    @classmethod
    def read(
        cls,
        path: Path,
        envelope: IsolatedJobEnvelope,
        *,
        envelope_path: Path,
        result_path: Path,
    ) -> "IsolationReceipt":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            receipt = cls(**payload)
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError):
            raise IsolationError("Worker receipt is invalid.") from None
        receipt.validate(
            envelope,
            envelope_path=envelope_path,
            result_path=result_path,
        )
        return receipt


@dataclass(frozen=True)
class QemuIsolationConfig:
    launcher_image: str
    guest_image: Path
    guest_image_sha256: str
    cpus: int = 4
    memory_mb: int = 8192
    timeout_seconds: int = 7200
    docker_command: str = "docker"
    kvm_device: Path = Path("/dev/kvm")

    def validate(self) -> None:
        _require_sha256(self.launcher_image.split("@")[-1], "launcher image digest")
        _require_sha256(self.guest_image_sha256, "guest image digest")
        if sha256_file(self.guest_image) != self.guest_image_sha256:
            raise IsolationError("Guest appliance digest does not match.")
        if self.cpus <= 0 or self.memory_mb < 1024 or self.timeout_seconds <= 0:
            raise IsolationError("QEMU resource limits are invalid.")


class QemuIsolationProvider:
    """Stage and launch one disposable KVM worker without the host Docker socket."""

    def __init__(self, config: QemuIsolationConfig):
        config.validate()
        self.config = config

    def preflight(self) -> None:
        try:
            mode = self.config.kvm_device.stat().st_mode
        except OSError:
            raise IsolationError("KVM device is unavailable.") from None
        if not stat.S_ISCHR(mode):
            raise IsolationError("KVM device is invalid.")
        completed = subprocess.run(
            [
                self.config.docker_command,
                "image",
                "inspect",
                self.config.launcher_image,
            ],
            capture_output=True,
            text=True,
            check=False,
            shell=False,
            timeout=30,
        )
        if completed.returncode != 0:
            raise IsolationError("Pinned QEMU launcher image is unavailable.")

    def command(self, job_root: Path) -> tuple[str, ...]:
        job_root = job_root.resolve(strict=True)
        input_root = (job_root / "input").resolve(strict=True)
        output_root = (job_root / "output").resolve(strict=True)
        run_root = (job_root / "run").resolve(strict=True)
        return (
            self.config.docker_command,
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--device",
            f"{self.config.kvm_device}:/dev/kvm:rwm",
            "--tmpfs",
            "/tmp:rw,nosuid,nodev,size=256m",
            "-v",
            f"{self.config.guest_image.resolve()}:/appliance/base.qcow2:ro",
            "-v",
            f"{input_root}:/job/input:ro",
            "-v",
            f"{output_root}:/job/output:rw",
            "-v",
            f"{run_root}:/job/run:rw",
            self.config.launcher_image,
            "--cpus",
            str(self.config.cpus),
            "--memory-mb",
            str(self.config.memory_mb),
        )

    def run(self, job_root: Path) -> IsolationReceipt:
        self.preflight()
        envelope_path = job_root / "input" / "job.json"
        envelope = IsolatedJobEnvelope.read(envelope_path)
        output_root = job_root / "output"
        if any(output_root.iterdir()):
            raise IsolationError("Isolated job output must be empty.")
        started = time.monotonic()
        try:
            completed = subprocess.run(
                self.command(job_root),
                capture_output=True,
                text=True,
                check=False,
                shell=False,
                timeout=self.config.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            raise IsolationError("Disposable worker exceeded its timeout.") from None
        (job_root / "launcher.log").write_text(
            (completed.stdout or "") + (completed.stderr or ""),
            encoding="utf-8",
        )
        if completed.returncode != 0:
            raise IsolationError(
                "Disposable worker failed before producing trusted evidence."
            )
        result_path = output_root / "case-run-result.json"
        receipt_path = output_root / "worker-receipt.json"
        if not result_path.is_file() or not receipt_path.is_file():
            raise IsolationError("Disposable worker output is incomplete.")
        validate_output_tree(output_root)
        receipt = IsolationReceipt.read(
            receipt_path,
            envelope,
            envelope_path=envelope_path,
            result_path=result_path,
        )
        (job_root / "host-lifecycle.json").write_bytes(
            canonical_json(
                {
                    "schema_version": "0.1",
                    "job_id": envelope.job_id,
                    "launcher_exit_code": completed.returncode,
                    "duration_seconds": max(int(time.monotonic() - started), 0),
                    "overlay_destroyed": not any(
                        (job_root / "run").glob("*.qcow2")
                    ),
                }
            )
            + b"\n"
        )
        if any((job_root / "run").glob("*.qcow2")):
            raise IsolationError("Disposable worker overlay was not destroyed.")
        return receipt


def validate_output_tree(output_root: Path) -> None:
    for entry in output_root.iterdir():
        mode = entry.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise IsolationError("Worker output contains a symbolic link.")
        if stat.S_ISDIR(mode):
            if entry.name not in ALLOWED_OUTPUT_DIRECTORIES:
                raise IsolationError("Worker output contains an unexpected directory.")
            for artifact in entry.rglob("*"):
                artifact_mode = artifact.lstat().st_mode
                if stat.S_ISLNK(artifact_mode) or not stat.S_ISREG(artifact_mode):
                    raise IsolationError("Worker artifact output is invalid.")
                if artifact.stat().st_size > 1024 * 1024 * 1024:
                    raise IsolationError("Worker artifact exceeds the platform limit.")
            continue
        if not stat.S_ISREG(mode) or entry.name not in ALLOWED_OUTPUT_FILES:
            raise IsolationError("Worker output contains an unexpected file.")
        if entry.stat().st_size > 64 * 1024 * 1024:
            raise IsolationError("Worker output file exceeds the platform limit.")


def stage_isolated_job(
    *,
    job_root: Path,
    envelope: IsolatedJobEnvelope,
    submission_archive: Path,
    case_snapshot: Path,
) -> Path:
    envelope.validate()
    if sha256_file(submission_archive) != envelope.submission_sha256:
        raise IsolationError("Submission archive digest does not match.")
    if sha256_tree(case_snapshot) != envelope.case_snapshot_sha256:
        raise IsolationError("Case snapshot digest does not match.")
    if job_root.exists():
        raise IsolationError("Isolated job directory already exists.")
    input_root = job_root / "input"
    output_root = job_root / "output"
    run_root = job_root / "run"
    input_root.mkdir(parents=True)
    output_root.mkdir()
    run_root.mkdir()
    shutil.copy2(submission_archive, input_root / "agent-submission.zip")
    shutil.copytree(case_snapshot, input_root / "case")
    envelope.write(input_root / "job.json")
    for path in sorted(input_root.rglob("*"), reverse=True):
        path.chmod(0o555 if path.is_dir() else 0o444)
    input_root.chmod(0o555)
    output_root.chmod(0o777)
    # The launcher container may use a remapped/root-squashed identity on
    # shared storage. This directory contains only its disposable overlay.
    run_root.chmod(0o777)
    return job_root
