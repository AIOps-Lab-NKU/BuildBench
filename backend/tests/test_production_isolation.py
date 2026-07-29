from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from backend.isolation import (
    IsolationError,
    IsolationReceipt,
    IsolatedJobEnvelope,
    QemuIsolationConfig,
    QemuIsolationProvider,
    canonical_json,
    sha256_file,
    stage_isolated_job,
    validate_output_tree,
)


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class ProductionIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.archive = self.root / "agent.zip"
        self.archive.write_bytes(b"agent")
        self.case = self.root / "case"
        self.case.mkdir()
        (self.case / "manifest.json").write_text("{}\n", encoding="utf-8")
        now = datetime.now(timezone.utc)
        self.envelope = IsolatedJobEnvelope(
            schema_version="0.1",
            job_id="JOB-12345678",
            evaluation_id="FE-1",
            case_run_id="CR-1",
            case_ordinal=1,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(hours=1)).isoformat(),
            submission_sha256=sha256_file(self.archive),
            case_snapshot_sha256=self._case_digest(),
            runtime_image_digest=digest(b"runtime"),
            validator_image_digest=digest(b"validator"),
            protocol_config_hash=digest(b"protocol"),
            guest_image_sha256=digest(b"guest"),
            nonce="nonce-12345678",
            agent_timeout_seconds=900,
            build_timeout_seconds=1800,
            build_attempt_limit=3,
            workspace_bytes=512 * 1024 * 1024,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _case_digest(self) -> str:
        value = hashlib.sha256()
        value.update(b"F\0manifest.json\0")
        value.update(bytes.fromhex(sha256_file(self.case / "manifest.json")[7:]))
        return "sha256:" + value.hexdigest()

    def test_staging_is_immutable_and_rejects_digest_or_symlink(self) -> None:
        job = self.root / "job"
        stage_isolated_job(
            job_root=job,
            envelope=self.envelope,
            submission_archive=self.archive,
            case_snapshot=self.case,
        )
        if os.name != "nt":
            self.assertEqual((job / "input").stat().st_mode & 0o777, 0o555)
            self.assertEqual((job / "output").stat().st_mode & 0o777, 0o777)
            self.assertEqual((job / "run").stat().st_mode & 0o777, 0o777)
            self.assertEqual(
                (job / "input" / "agent-submission.zip").stat().st_mode
                & 0o777,
                0o444,
            )
        with self.assertRaises(IsolationError):
            stage_isolated_job(
                job_root=self.root / "bad",
                envelope=replace(
                    self.envelope, submission_sha256=digest(b"different")
                ),
                submission_archive=self.archive,
                case_snapshot=self.case,
            )

    def test_qemu_command_never_mounts_host_docker_socket(self) -> None:
        guest = self.root / "guest.qcow2"
        guest.write_bytes(b"guest")
        config = QemuIsolationConfig(
            launcher_image="example/launcher@" + digest(b"launcher"),
            guest_image=guest,
            guest_image_sha256=sha256_file(guest),
        )
        provider = QemuIsolationProvider(config)
        job = self.root / "job"
        stage_isolated_job(
            job_root=job,
            envelope=replace(
                self.envelope, guest_image_sha256=sha256_file(guest)
            ),
            submission_archive=self.archive,
            case_snapshot=self.case,
        )
        command = provider.command(job)
        serialized = " ".join(command)
        self.assertIn(":/dev/kvm:rwm", serialized)
        self.assertIn("--network none", serialized)
        self.assertNotIn("/var/run/docker.sock", serialized)
        self.assertNotIn("--privileged", command)
        self.assertIn(str((job / "input").resolve()) + ":/job/input:ro", command)

    def test_receipt_is_bound_to_job_result_and_security_controls(self) -> None:
        job = self.root / "job"
        stage_isolated_job(
            job_root=job,
            envelope=self.envelope,
            submission_archive=self.archive,
            case_snapshot=self.case,
        )
        result = job / "output" / "case-run-result.json"
        result.write_text('{"status":"failed"}\n', encoding="utf-8")
        envelope_path = job / "input" / "job.json"
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "schema_version": "0.1",
            "job_id": self.envelope.job_id,
            "worker_id": "worker-1",
            "worker_boot_id": "boot-1",
            "started_at": now,
            "finished_at": now,
            "input_envelope_sha256": sha256_file(envelope_path),
            "result_sha256": sha256_file(result),
            "guest_image_sha256": self.envelope.guest_image_sha256,
            "validator_image_digest": self.envelope.validator_image_digest,
            "protocol_config_hash": self.envelope.protocol_config_hash,
            "docker_socket_exposed_to_agent": False,
            "host_docker_socket_mounted_in_worker": False,
            "host_case_store_mounted_in_worker": False,
            "worker_reused_between_cases": False,
            "network_mode": "none",
            "nonce": self.envelope.nonce,
        }
        payload["document_sha256"] = digest(canonical_json(payload))
        receipt = IsolationReceipt(**payload)
        receipt.validate(
            self.envelope,
            envelope_path=envelope_path,
            result_path=result,
        )
        with self.assertRaises(IsolationError):
            replace(receipt, host_docker_socket_mounted_in_worker=True).validate(
                self.envelope,
                envelope_path=envelope_path,
                result_path=result,
            )

    def test_output_allow_list_rejects_extra_or_symbolic_files(self) -> None:
        output = self.root / "output"
        output.mkdir()
        (output / "case-run-result.json").write_text("{}")
        validate_output_tree(output)
        (output / "secret.txt").write_text("bad")
        with self.assertRaises(IsolationError):
            validate_output_tree(output)

    def test_preflight_is_fail_closed(self) -> None:
        guest = self.root / "guest.qcow2"
        guest.write_bytes(b"guest")
        provider = QemuIsolationProvider(
            QemuIsolationConfig(
                launcher_image="example/launcher@" + digest(b"launcher"),
                guest_image=guest,
                guest_image_sha256=sha256_file(guest),
                kvm_device=self.root / "missing-kvm",
            )
        )
        with self.assertRaisesRegex(IsolationError, "KVM"):
            provider.preflight()

    def test_guest_console_is_exported_only_after_worker_starts(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "isolation_assets"
            / "qemu"
            / "guest"
            / "run-job.sh"
        ).read_text(encoding="utf-8")
        redirect = '>"$worker_console" 2>&1'
        export = 'cp "$worker_console" /mnt/bb-output/worker-console.log'
        self.assertIn("worker_console=/tmp/", script)
        self.assertIn(redirect, script)
        self.assertIn(export, script)
        self.assertLess(script.index(redirect), script.index(export))
        self.assertNotIn("runuser -u ubuntu", script)
        self.assertIn("python3 -m backend.isolated_case_worker", script)

    def test_guest_exports_contents_without_restoring_metadata(self) -> None:
        worker = (
            Path(__file__).resolve().parents[1] / "isolated_case_worker.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("shutil.copy2(", worker)
        self.assertIn("shutil.copyfile(source, output_root / name)", worker)
        self.assertIn("copy_function=shutil.copyfile", worker)
        self.assertIn('"validator-console.log"', worker)

    def test_guest_validator_uses_local_chroot_without_docker_socket(self) -> None:
        worker = (
            Path(__file__).resolve().parents[1] / "isolated_case_worker.py"
        ).read_text(encoding="utf-8")
        guest_runner = (
            Path(__file__).resolve().parents[1]
            / "isolation_assets"
            / "qemu"
            / "guest"
            / "run-job.sh"
        ).read_text(encoding="utf-8")
        self.assertIn('"BUILD_CASE_ISOLATED_WORKER": "1"', worker)
        self.assertIn('"BUILD_CASE_VM_TYPE": "chroot"', worker)
        self.assertIn(
            '"/opt/buildbench/docker-validator/bin/build-case"',
            guest_runner,
        )
        self.assertNotIn("build-case-docker", guest_runner)

    def test_guest_binds_offline_agent_tag_to_job_digest(self) -> None:
        worker = (
            Path(__file__).resolve().parents[1] / "isolated_case_worker.py"
        ).read_text(encoding="utf-8")
        self.assertIn("local_image_reference=agent_image", worker)
        self.assertIn("local_image_digest=agent_local_digest", worker)
        self.assertIn(
            "envelope.runtime_image_digest != agent_host_digest",
            worker,
        )
        self.assertIn("BB_MANAGED_AGENT_IMAGE", worker)

    def test_explicit_agent_identity_receives_writable_worktree(self) -> None:
        runner = (
            Path(__file__).resolve().parents[1] / "evaluation_runner.py"
        ).read_text(encoding="utf-8")
        self.assertIn('workspace / "work"', runner)
        self.assertIn('workspace / "output"', runner)
        self.assertIn("file_path.chmod(", runner)
        self.assertIn("stat.S_IWUSR", runner)

    def test_appliance_records_cross_daemon_agent_image_mapping(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "isolation_assets"
            / "qemu"
            / "build-appliance.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("buildbench-managed-agent-host-digest", script)
        self.assertIn("buildbench-managed-agent-local-digest", script)
        self.assertIn("record-managed-agent-image", script)

    def test_appliance_installs_pinned_obs_build_for_guest_chroot(self) -> None:
        script = (
            Path(__file__).resolve().parents[1]
            / "isolation_assets"
            / "qemu"
            / "build-appliance.sh"
        ).read_text(encoding="utf-8")
        self.assertIn("obs-build_20260623-1_all.deb", script)
        self.assertIn("install-validator-runtime", script)
        self.assertIn("sha256sum -c -", script)
        self.assertIn("patch-obs-build-deb.py", script)
        self.assertIn("test -x /usr/bin/build", script)


if __name__ == "__main__":
    unittest.main()
