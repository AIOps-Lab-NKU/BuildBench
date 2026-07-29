"""Run exactly one staged Case inside a disposable evaluation appliance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from backend.evaluation_runner import (
    CommandValidatorExecutor,
    DockerAgentConfig,
    DockerAgentExecutor,
    FormalCaseRunner,
)
from backend.isolation import (
    IsolationError,
    IsolationReceipt,
    IsolatedJobEnvelope,
    canonical_json,
    sha256_file,
)
from backend.submissions import ArchiveLimits, make_agent_read_only, safe_extract_zip


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def entrypoint(agent_dir: Path, starter_kit: Path) -> tuple[str, ...]:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "runner.check_agent",
            "--agent",
            str(agent_dir),
            "--entrypoint",
        ],
        cwd=starter_kit,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )
    if completed.returncode != 0:
        raise IsolationError("Agent failed validation inside the worker.")
    result = tuple(line.strip() for line in completed.stdout.splitlines() if line.strip())
    if not result:
        raise IsolationError("Agent entrypoint is empty.")
    return result


def receipt_payload(
    envelope: IsolatedJobEnvelope,
    *,
    envelope_path: Path,
    result_path: Path,
    started_at: str,
) -> dict[str, object]:
    try:
        boot_id = Path("/proc/sys/kernel/random/boot_id").read_text(
            encoding="utf-8"
        ).strip()
    except OSError:
        boot_id = ""
    try:
        machine_id = Path("/etc/machine-id").read_text(encoding="utf-8").strip()
    except OSError:
        machine_id = ""
    payload: dict[str, object] = {
        "schema_version": "0.1",
        "job_id": envelope.job_id,
        "worker_id": hashlib.sha256(
            f"{machine_id}:{boot_id}:{envelope.job_id}".encode("utf-8")
        ).hexdigest()[:32],
        "worker_boot_id": boot_id,
        "started_at": started_at,
        "finished_at": utc_now(),
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
    payload["document_sha256"] = (
        "sha256:" + hashlib.sha256(canonical_json(payload)).hexdigest()
    )
    return payload


def run_job(
    *,
    input_root: Path,
    output_root: Path,
    starter_kit: Path,
    validator_command: tuple[str, ...],
    cleanup_image: str,
    agent_image: str,
    agent_host_digest: str,
    agent_local_digest: str,
) -> int:
    started_at = utc_now()
    envelope_path = input_root / "job.json"
    envelope = IsolatedJobEnvelope.read(envelope_path)
    archive = input_root / "agent-submission.zip"
    case_dir = input_root / "case"
    if sha256_file(archive) != envelope.submission_sha256:
        raise IsolationError("Staged Agent archive failed integrity verification.")
    if envelope.runtime_image_digest != agent_host_digest:
        raise IsolationError(
            "Managed Agent runtime does not match the appliance host digest."
        )
    for label, digest in (
        ("host", agent_host_digest),
        ("local", agent_local_digest),
    ):
        if not (
            digest.startswith("sha256:")
            and len(digest) == len("sha256:") + 64
        ):
            raise IsolationError(
                f"Managed Agent runtime {label} digest is invalid."
            )
    if any(output_root.iterdir()):
        raise IsolationError("Worker output directory is not empty.")

    private_root = Path("/var/tmp/buildbench-job") / envelope.job_id
    if private_root.exists():
        raise IsolationError("Disposable worker job directory was reused.")
    private_root.mkdir(parents=True, mode=0o700)
    try:
        agent_dir = private_root / "agent"
        safe_extract_zip(archive, agent_dir, ArchiveLimits())
        make_agent_read_only(agent_dir)
        agent = DockerAgentExecutor(
            DockerAgentConfig(
                image=envelope.runtime_image_digest,
                local_image_reference=agent_image,
                local_image_digest=agent_local_digest,
                entrypoint=entrypoint(agent_dir, starter_kit),
                timeout_seconds=envelope.agent_timeout_seconds,
                build_feedback_timeout_seconds=max(
                    min(
                        envelope.build_timeout_seconds,
                        envelope.agent_timeout_seconds - 30,
                    ),
                    1,
                ),
                workspace_bytes=envelope.workspace_bytes,
                run_as_uid=1000,
                run_as_gid=1000,
            ),
            Path(__file__).resolve().parent / "runner_assets" / "bb-build",
        )
        validator = CommandValidatorExecutor(
            validator_command,
            timeout_seconds=envelope.build_timeout_seconds,
            environment={
                "BUILD_CASE_RUNTIME_IMAGE": envelope.validator_image_digest,
                "BUILD_CASE_CLEANUP_IMAGE": cleanup_image,
                # The worker itself is a disposable QEMU/KVM guest. Run
                # obs-build directly in a guest-local chroot so the Validator
                # never needs a host or nested Docker socket.
                "BUILD_CASE_ISOLATED_WORKER": "1",
                "BUILD_CASE_VM_TYPE": "chroot",
            },
        )
        runner = FormalCaseRunner(
            agent,
            validator,
            build_attempt_limit=envelope.build_attempt_limit,
        )
        internal_output = private_root / "result"
        runner.run(
            case_run_id=envelope.case_run_id,
            case_ordinal=envelope.case_ordinal,
            case_dir=case_dir,
            agent_dir=agent_dir,
            output_dir=internal_output,
        )
        for name in (
            "case-run-result.json",
            "agent.log",
            "build.log",
            "repair.diff",
            "validator-console.log",
        ):
            source = internal_output / name
            if source.is_file():
                # The host result directory is exported through virtio-9p.
                # Unprivileged guest processes may create files there but are
                # not necessarily allowed to restore the source timestamps.
                # Copy only file contents; result integrity is bound by the
                # worker receipt rather than filesystem metadata.
                shutil.copyfile(source, output_root / name)
        artifacts = internal_output / "artifacts"
        if artifacts.is_dir():
            shutil.copytree(
                artifacts,
                output_root / "artifacts",
                copy_function=shutil.copyfile,
            )
        result_path = output_root / "case-run-result.json"
        if not result_path.is_file():
            raise IsolationError("Case runner did not produce a structured result.")
        receipt = receipt_payload(
            envelope,
            envelope_path=envelope_path,
            result_path=result_path,
            started_at=started_at,
        )
        (output_root / "worker-receipt.json").write_bytes(
            canonical_json(receipt) + b"\n"
        )
        IsolationReceipt(**receipt).validate(
            envelope,
            envelope_path=envelope_path,
            result_path=result_path,
        )
        return 0
    finally:
        shutil.rmtree(private_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("/mnt/bb-input"))
    parser.add_argument("--output", type=Path, default=Path("/mnt/bb-output"))
    parser.add_argument(
        "--starter-kit",
        type=Path,
        default=Path("/opt/buildbench/starter-kit"),
    )
    parser.add_argument(
        "--validator-command",
        default="/opt/buildbench/docker-validator/bin/build-case-docker",
    )
    parser.add_argument(
        "--cleanup-image",
        default=os.environ.get("BB_CLEANUP_IMAGE", "ubuntu:24.04"),
    )
    parser.add_argument(
        "--agent-image",
        default=os.environ.get(
            "BB_MANAGED_AGENT_IMAGE",
            "python:3.11.9-slim-bookworm",
        ),
    )
    parser.add_argument(
        "--agent-host-digest-file",
        type=Path,
        default=Path("/etc/buildbench-managed-agent-host-digest"),
    )
    parser.add_argument(
        "--agent-local-digest-file",
        type=Path,
        default=Path("/etc/buildbench-managed-agent-local-digest"),
    )
    args = parser.parse_args()
    return run_job(
        input_root=args.input.resolve(strict=True),
        output_root=args.output.resolve(strict=True),
        starter_kit=args.starter_kit.resolve(strict=True),
        validator_command=tuple(args.validator_command.split()),
        cleanup_image=args.cleanup_image,
        agent_image=args.agent_image,
        agent_host_digest=args.agent_host_digest_file.read_text(
            encoding="utf-8"
        ).strip(),
        agent_local_digest=args.agent_local_digest_file.read_text(
            encoding="utf-8"
        ).strip(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
