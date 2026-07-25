from __future__ import annotations

import io
import json
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path

from backend.submissions import (
    ArchiveLimits,
    HostedSmokeQueue,
    SmokeOutcome,
    SubmissionConflict,
    SubmissionError,
    SubmissionService,
    SubmissionStore,
    safe_extract_zip,
)


def valid_agent_zip(name: str = "test-agent") -> bytes:
    files = {
        "agent.yaml": f"""schema_version: "0.1"
agent:
  name: "{name}"
  version: "1.0.0"
runtime:
  type: "managed"
  profile: "python-3.11"
entrypoint:
  - "python"
  - "-m"
  - "src.main"
protocol:
  version: "0.1"
""",
        "src/__init__.py": "",
        "src/main.py": "print('test')\n",
        "requirements.lock": "",
        "README.md": "# Test Agent\n",
    }
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, content in files.items():
            archive.writestr(path, content)
    return stream.getvalue()


def accepted_checker(agent_dir: Path, log_path: Path) -> dict[str, object]:
    if not (agent_dir / "agent.yaml").is_file():
        raise SubmissionError("agent.yaml missing")
    log_path.write_text("valid\n", encoding="utf-8")
    return {
        "agent_name": "test-agent",
        "agent_version": "1.0.0",
        "file_count": 5,
        "total_bytes": 42,
    }


class ArchiveTests(unittest.TestCase):
    def test_rejects_path_traversal_before_writing_outside(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "bad.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../escape.txt", "escape")
            with self.assertRaisesRegex(SubmissionError, "unsafe ZIP"):
                safe_extract_zip(
                    archive_path,
                    root / "agent",
                    ArchiveLimits(),
                )
            self.assertFalse((root / "escape.txt").exists())

    def test_rejects_symlink_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "bad.zip"
            info = zipfile.ZipInfo("src/link")
            info.create_system = 3
            info.external_attr = (0o120777 << 16)
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(info, "target")
            with self.assertRaisesRegex(SubmissionError, "symbolic links"):
                safe_extract_zip(
                    archive_path,
                    root / "agent",
                    ArchiveLimits(),
                )


class SubmissionServiceTests(unittest.TestCase):
    def test_valid_upload_becomes_qualified_and_is_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = SubmissionService(
                SubmissionStore(root / "data"),
                root / "starter",
                checker=accepted_checker,
            )
            record = service.create_submission(
                "agent-submission.zip",
                valid_agent_zip(),
            )
            self.assertEqual(record["status"], "qualified")
            self.assertEqual(record["agent"]["name"], "test-agent")
            reloaded = service.get(str(record["id"]))
            self.assertEqual(reloaded["sha256"], record["sha256"])
            self.assertTrue(
                (
                    service.store.submission_dir(str(record["id"]))
                    / "agent-submission.zip"
                ).is_file()
            )

    def test_static_check_failure_is_recorded_without_smoke(self) -> None:
        def reject(_agent: Path, _log: Path) -> dict[str, object]:
            raise SubmissionError("manifest rejected")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = SubmissionService(
                SubmissionStore(root / "data"),
                root / "starter",
                checker=reject,
            )
            record = service.create_submission("agent.zip", valid_agent_zip())
            self.assertEqual(record["status"], "check_failed")
            self.assertEqual(record["smoke"]["status"], "not_started")

    def test_smoke_test_is_explicit_and_reaches_terminal_state(self) -> None:
        completed = threading.Event()

        def runner(
            _record: dict[str, object],
            _agent: Path,
            smoke_dir: Path,
        ) -> SmokeOutcome:
            (smoke_dir / "console.log").write_text("passed\n", encoding="utf-8")
            completed.set()
            return SmokeOutcome(
                status="succeeded",
                message="Hosted Smoke Test passed.",
                summary={"status": "succeeded", "case_count": 1},
                run_dir="/fake/run",
            )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            service = SubmissionService(
                SubmissionStore(root / "data"),
                root / "starter",
                checker=accepted_checker,
            )
            record = service.create_submission("agent.zip", valid_agent_zip())
            self.assertEqual(record["smoke"]["status"], "not_started")
            queue = HostedSmokeQueue(service, max_workers=1, runner=runner)
            try:
                queued = queue.request(str(record["id"]))
                self.assertIn(queued["status"], {"smoke_queued", "smoke_running"})
                self.assertTrue(completed.wait(timeout=5))
                deadline = time.time() + 5
                terminal = service.get(str(record["id"]))
                while terminal["status"] != "smoke_passed" and time.time() < deadline:
                    time.sleep(0.02)
                    terminal = service.get(str(record["id"]))
                self.assertEqual(terminal["status"], "smoke_passed")
                self.assertNotIn("run_dir", terminal["smoke"])
                self.assertEqual(terminal["smoke"]["run_id"], "run")
                filename, content = service.log_text(str(record["id"]))
                self.assertTrue(filename.startswith("smoke-test-"))
                self.assertEqual(content.replace("\r\n", "\n"), "passed\n")
                with self.assertRaises(SubmissionConflict):
                    queue.request(str(record["id"]))
            finally:
                queue.shutdown()


if __name__ == "__main__":
    unittest.main()
