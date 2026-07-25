from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable


ACTIVE_STATES = {"checking", "smoke_queued", "smoke_running"}
SMOKE_RETRY_STATES = {"qualified", "smoke_failed", "infrastructure_error"}
SUBMISSION_ID = re.compile(r"^[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}$")
MAX_PUBLIC_LOG_BYTES = 5 * 1024 * 1024


class SubmissionError(ValueError):
    pass


class SubmissionNotFound(SubmissionError):
    pass


class SubmissionConflict(SubmissionError):
    pass


@dataclass(frozen=True)
class ArchiveLimits:
    upload_bytes: int = 20 * 1024 * 1024
    file_count: int = 1_000
    entry_bytes: int = 20 * 1024 * 1024
    expanded_bytes: int = 100 * 1024 * 1024


@dataclass(frozen=True)
class SmokeOutcome:
    status: str
    message: str
    summary: dict[str, object] | None = None
    run_dir: str | None = None


Checker = Callable[[Path, Path], dict[str, object]]
SmokeRunner = Callable[[dict[str, object], Path, Path], SmokeOutcome]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_submission_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def atomic_json(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def read_json(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SubmissionError(f"expected JSON object: {path}")
    return data


def tail_text(path: Path, limit: int = 8_000) -> str:
    if not path.is_file():
        return ""
    content = path.read_text(encoding="utf-8", errors="replace")
    return content[-limit:]


def sanitize_smoke_summary(
    summary: dict[str, object] | None,
) -> dict[str, object] | None:
    if summary is None:
        return None
    sanitized: dict[str, object] = {}
    for key in (
        "schema_version",
        "status",
        "case_count",
        "succeeded",
        "failed",
    ):
        if key in summary:
            sanitized[key] = summary[key]
    cases: list[dict[str, object]] = []
    for raw_case in list(summary.get("cases") or []):
        if not isinstance(raw_case, dict):
            continue
        cases.append(
            {
                key: raw_case.get(key)
                for key in (
                    "case_id",
                    "status",
                    "initial_status",
                    "agent_status",
                )
                if key in raw_case
            }
        )
    sanitized["cases"] = cases
    return sanitized


def _safe_member_name(raw_name: str) -> PurePosixPath:
    if not raw_name or "\x00" in raw_name or "\\" in raw_name:
        raise SubmissionError(f"unsafe ZIP entry name: {raw_name!r}")
    path = PurePosixPath(raw_name)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise SubmissionError(f"unsafe ZIP entry path: {raw_name}")
    if path.parts[0].endswith(":"):
        raise SubmissionError(f"unsafe ZIP drive path: {raw_name}")
    return path


def safe_extract_zip(
    archive_path: Path,
    destination: Path,
    limits: ArchiveLimits,
) -> None:
    if archive_path.stat().st_size > limits.upload_bytes:
        raise SubmissionError("Agent ZIP exceeds the development upload limit")
    destination.mkdir(parents=True, exist_ok=False)
    destination_root = destination.resolve()

    try:
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            if not entries:
                raise SubmissionError("Agent ZIP is empty")
            if len(entries) > limits.file_count:
                raise SubmissionError("Agent ZIP contains too many entries")

            expanded = 0
            seen: set[str] = set()
            for info in entries:
                path = _safe_member_name(info.filename)
                normalized = path.as_posix().casefold()
                if normalized in seen:
                    raise SubmissionError(f"duplicate ZIP entry: {info.filename}")
                seen.add(normalized)
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    raise SubmissionError(f"symbolic links are not allowed: {info.filename}")
                if info.flag_bits & 0x1:
                    raise SubmissionError("encrypted ZIP entries are not allowed")
                if info.file_size > limits.entry_bytes:
                    raise SubmissionError(f"ZIP entry is too large: {info.filename}")
                expanded += info.file_size
                if expanded > limits.expanded_bytes:
                    raise SubmissionError("Agent ZIP expands beyond the safety limit")

                target = destination.joinpath(*path.parts)
                target_resolved = target.resolve()
                if os.path.commonpath((destination_root, target_resolved)) != str(
                    destination_root
                ):
                    raise SubmissionError(f"ZIP entry escapes destination: {info.filename}")

                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)
    except zipfile.BadZipFile as error:
        raise SubmissionError("uploaded file is not a valid ZIP archive") from error


def make_agent_read_only(agent_dir: Path) -> None:
    for path in sorted(agent_dir.rglob("*"), reverse=True):
        if path.is_file():
            path.chmod(0o444)
        elif path.is_dir():
            path.chmod(0o555)
    agent_dir.chmod(0o555)


class SubmissionStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.submissions_root = self.root / "submissions"
        self.submissions_root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def submission_dir(self, submission_id: str) -> Path:
        if not SUBMISSION_ID.fullmatch(submission_id):
            raise SubmissionNotFound("submission not found")
        return self.submissions_root / submission_id

    def metadata_path(self, submission_id: str) -> Path:
        return self.submission_dir(submission_id) / "submission.json"

    def create(self, record: dict[str, object]) -> None:
        submission_id = str(record["id"])
        with self._lock:
            directory = self.submission_dir(submission_id)
            directory.mkdir(parents=False, exist_ok=False)
            atomic_json(directory / "submission.json", record)

    def get(self, submission_id: str) -> dict[str, object]:
        with self._lock:
            path = self.metadata_path(submission_id)
            if not path.is_file():
                raise SubmissionNotFound("submission not found")
            return read_json(path)

    def update(
        self,
        submission_id: str,
        changes: dict[str, object],
    ) -> dict[str, object]:
        with self._lock:
            record = self.get(submission_id)
            record.update(changes)
            record["updated_at"] = utc_now()
            atomic_json(self.metadata_path(submission_id), record)
            return record

    def list(self) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        with self._lock:
            for path in self.submissions_root.glob("*/submission.json"):
                try:
                    records.append(read_json(path))
                except (OSError, UnicodeError, json.JSONDecodeError, SubmissionError):
                    continue
        return sorted(records, key=lambda item: str(item.get("created_at", "")), reverse=True)

    def recover_interrupted(self) -> None:
        for record in self.list():
            if record.get("status") not in ACTIVE_STATES:
                continue
            self.update(
                str(record["id"]),
                {
                    "status": "infrastructure_error",
                    "message": "Backend restarted before this operation completed.",
                    "smoke": {
                        **dict(record.get("smoke") or {}),
                        "status": "infrastructure_error",
                        "finished_at": utc_now(),
                    },
                },
            )


class SubmissionService:
    def __init__(
        self,
        store: SubmissionStore,
        starter_kit: Path,
        checker: Checker | None = None,
        limits: ArchiveLimits | None = None,
    ):
        self.store = store
        self.starter_kit = starter_kit.resolve()
        self.checker = checker or self._default_checker
        self.limits = limits or ArchiveLimits()

    def _default_checker(self, agent_dir: Path, log_path: Path) -> dict[str, object]:
        command = [
            sys.executable,
            "-m",
            "runner.check_agent",
            "--agent",
            str(agent_dir),
            "--json",
            "--report",
            str(log_path.with_name("check-result.json")),
        ]
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            command,
            cwd=self.starter_kit,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )
        log_path.write_text(result.stdout, encoding="utf-8")
        if result.returncode != 0:
            raise SubmissionError(
                tail_text(log_path, 4_000) or "Agent static check failed"
            )
        report_path = log_path.with_name("check-result.json")
        if not report_path.is_file():
            raise RuntimeError("Agent checker did not produce check-result.json")
        return read_json(report_path)

    def create_submission(self, filename: str, payload: bytes) -> dict[str, object]:
        if not filename.lower().endswith(".zip"):
            raise SubmissionError("Agent submission filename must end in .zip")
        if len(payload) > self.limits.upload_bytes:
            raise SubmissionError("Agent ZIP exceeds the development upload limit")

        submission_id = new_submission_id()
        created = utc_now()
        record: dict[str, object] = {
            "schema_version": "0.1",
            "id": submission_id,
            "filename": Path(filename).name,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "created_at": created,
            "updated_at": created,
            "status": "checking",
            "message": "Static checks are running.",
            "agent": None,
            "check": {"status": "running", "started_at": created},
            "smoke": {"status": "not_started"},
            "full_evaluation": {"status": "not_started"},
        }
        self.store.create(record)
        submission_dir = self.store.submission_dir(submission_id)
        archive_path = submission_dir / "agent-submission.zip"
        archive_path.write_bytes(payload)
        agent_dir = submission_dir / "agent"
        check_log = submission_dir / "check.log"

        try:
            safe_extract_zip(archive_path, agent_dir, self.limits)
            report = self.checker(agent_dir, check_log)
            make_agent_read_only(agent_dir)
            record = self.store.update(
                submission_id,
                {
                    "status": "qualified",
                    "message": "Agent bundle passed static checks.",
                    "agent": {
                        "name": report.get("agent_name"),
                        "version": report.get("agent_version"),
                    },
                    "check": {
                        "status": "passed",
                        "finished_at": utc_now(),
                        "file_count": report.get("file_count"),
                        "total_bytes": report.get("total_bytes"),
                    },
                },
            )
        except SubmissionError as error:
            check_log.write_text(str(error) + "\n", encoding="utf-8")
            record = self.store.update(
                submission_id,
                {
                    "status": "check_failed",
                    "message": str(error),
                    "check": {
                        "status": "failed",
                        "finished_at": utc_now(),
                    },
                },
            )
        except Exception as error:
            check_log.write_text(
                f"{type(error).__name__}: {error}\n",
                encoding="utf-8",
            )
            record = self.store.update(
                submission_id,
                {
                    "status": "infrastructure_error",
                    "message": "Static check service failed; organizers may rerun it.",
                    "check": {
                        "status": "infrastructure_error",
                        "finished_at": utc_now(),
                    },
                },
            )
        return self.public_record(record)

    def public_record(self, record: dict[str, object]) -> dict[str, object]:
        submission_id = str(record["id"])
        directory = self.store.submission_dir(submission_id)
        public = json.loads(json.dumps(record))
        smoke = dict(public.get("smoke") or {})
        smoke.pop("run_dir", None)
        smoke["summary"] = sanitize_smoke_summary(smoke.get("summary"))
        public["smoke"] = smoke

        public["check_log_tail"] = self._redact_log(
            directory,
            tail_text(directory / "check.log"),
        )
        public["smoke_log_tail"] = self._redact_log(
            directory,
            tail_text(directory / "smoke" / "console.log")
        )
        return public

    def _redact_log(self, directory: Path, content: str) -> str:
        return (
            content.replace(str(self.starter_kit), "<starter-kit>")
            .replace(str(directory), "<submission>")
        )

    def log_text(self, submission_id: str) -> tuple[str, str]:
        self.store.get(submission_id)
        directory = self.store.submission_dir(submission_id)
        candidates = (
            (directory / "smoke" / "console.log", "smoke-test"),
            (directory / "check.log", "static-check"),
        )
        for path, label in candidates:
            if not path.is_file():
                continue
            raw = path.read_bytes()
            truncated = len(raw) > MAX_PUBLIC_LOG_BYTES
            if truncated:
                raw = raw[-MAX_PUBLIC_LOG_BYTES:]
            content = raw.decode("utf-8", errors="replace")
            if truncated:
                content = (
                    "[Earlier log output omitted by the public viewer.]\n"
                    + content
                )
            filename = f"{label}-{submission_id}.log"
            return filename, self._redact_log(directory, content)
        return f"submission-{submission_id}.log", "No log is available yet.\n"

    def get(self, submission_id: str) -> dict[str, object]:
        return self.public_record(self.store.get(submission_id))

    def list(self) -> list[dict[str, object]]:
        return [self.public_record(record) for record in self.store.list()]


class HostedSmokeQueue:
    def __init__(
        self,
        service: SubmissionService,
        max_workers: int = 2,
        runner: SmokeRunner | None = None,
    ):
        if max_workers < 1:
            raise ValueError("max_workers must be positive")
        self.service = service
        self.runner = runner or self._default_runner
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="buildbench-smoke",
        )

    def request(self, submission_id: str) -> dict[str, object]:
        record = self.service.store.get(submission_id)
        if record.get("status") not in SMOKE_RETRY_STATES:
            raise SubmissionConflict(
                f"Smoke Test cannot start from status {record.get('status')}"
            )
        queued_at = utc_now()
        record = self.service.store.update(
            submission_id,
            {
                "status": "smoke_queued",
                "message": "Hosted Smoke Test is queued.",
                "smoke": {
                    "status": "queued",
                    "queued_at": queued_at,
                },
            },
        )
        self.executor.submit(self._execute, submission_id)
        return self.service.public_record(record)

    def _execute(self, submission_id: str) -> None:
        record = self.service.store.get(submission_id)
        submission_dir = self.service.store.submission_dir(submission_id)
        smoke_dir = submission_dir / "smoke"
        smoke_dir.mkdir(parents=True, exist_ok=True)
        record = self.service.store.update(
            submission_id,
            {
                "status": "smoke_running",
                "message": "Hosted Smoke Test is running.",
                "smoke": {
                    **dict(record.get("smoke") or {}),
                    "status": "running",
                    "started_at": utc_now(),
                },
            },
        )
        try:
            outcome = self.runner(record, submission_dir / "agent", smoke_dir)
            terminal = (
                "smoke_passed"
                if outcome.status == "succeeded"
                else "smoke_failed"
            )
            self.service.store.update(
                submission_id,
                {
                    "status": terminal,
                    "message": outcome.message,
                    "smoke": {
                        **dict(record.get("smoke") or {}),
                        "status": (
                            "passed" if terminal == "smoke_passed" else "failed"
                        ),
                        "finished_at": utc_now(),
                        "summary": sanitize_smoke_summary(outcome.summary),
                        "run_id": (
                            Path(outcome.run_dir).name if outcome.run_dir else None
                        ),
                    },
                },
            )
        except Exception as error:
            with (smoke_dir / "console.log").open("a", encoding="utf-8") as log:
                log.write(f"\n{type(error).__name__}: {error}\n")
            self.service.store.update(
                submission_id,
                {
                    "status": "infrastructure_error",
                    "message": "Hosted Smoke Test infrastructure failed.",
                    "smoke": {
                        **dict(record.get("smoke") or {}),
                        "status": "infrastructure_error",
                        "finished_at": utc_now(),
                    },
                },
            )

    def _default_runner(
        self,
        record: dict[str, object],
        agent_dir: Path,
        smoke_dir: Path,
    ) -> SmokeOutcome:
        submission_id = str(record["id"])
        agent = dict(record.get("agent") or {})
        agent_name = str(agent.get("name") or "")
        if not agent_name:
            raise RuntimeError("qualified submission has no Agent name")
        run_id = f"hosted-{submission_id}"
        run_dir = (
            self.service.starter_kit
            / "runs"
            / "tests"
            / agent_name
            / run_id
        )
        environment = os.environ.copy()
        environment["BB_RUN_ID"] = run_id
        command = [
            str(self.service.starter_kit / "bb"),
            "test",
            "--agent",
            str(agent_dir),
        ]
        console = smoke_dir / "console.log"
        with console.open("w", encoding="utf-8") as log:
            result = subprocess.run(
                command,
                cwd=self.service.starter_kit,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=60 * 60,
                check=False,
            )

        summary_path = run_dir / "summary.json"
        if not summary_path.is_file():
            raise RuntimeError(
                f"Smoke runner exited {result.returncode} without summary.json"
            )
        summary = read_json(summary_path)
        shutil.copy2(summary_path, smoke_dir / "summary.json")
        if (run_dir / "progress.log").is_file():
            shutil.copy2(run_dir / "progress.log", smoke_dir / "progress.log")

        retained = smoke_dir / "cases"
        for case in list(summary.get("cases") or []):
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("case_id") or "")
            if not case_id:
                continue
            source = run_dir / "cases" / case_id
            target = retained / case_id
            target.mkdir(parents=True, exist_ok=True)
            for filename in (
                "initial-build-result.json",
                "agent-result.json",
                "repair.diff",
                "build-result.json",
                "initial-build.log",
                "build.log",
                "agent.log",
            ):
                if (source / filename).is_file():
                    shutil.copy2(source / filename, target / filename)

        succeeded = result.returncode == 0 and summary.get("status") == "succeeded"
        return SmokeOutcome(
            status="succeeded" if succeeded else "failed",
            message=(
                "Hosted Smoke Test passed."
                if succeeded
                else "Hosted Smoke Test completed with failures."
            ),
            summary=summary,
            run_dir=str(run_dir),
        )

    def shutdown(self) -> None:
        self.executor.shutdown(wait=True, cancel_futures=False)
