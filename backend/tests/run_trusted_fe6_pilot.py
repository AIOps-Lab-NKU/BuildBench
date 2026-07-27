#!/usr/bin/env python3
"""Run a real hidden-policy FE-6 pilot on organizer-controlled assets.

This proves API, hidden feedback, durable Worker execution, publication and
leaderboard integration. It deliberately uses the trusted-development
Validator override and is not a production isolation approval.
"""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from backend.evaluation_models import EvaluationConfig, stable_digest
from backend.security import RequestIdentity, TokenAuthenticator
from backend.server import create_server
from backend.submissions import ArchiveLimits, SmokeOutcome


def controlled_smoke_precondition(
    record: dict[str, object],
    agent_dir: Path,
    smoke_dir: Path,
) -> SmokeOutcome:
    """Satisfy the already-tested Smoke prerequisite for the FE-6 pilot.

    FE-3 covers the real Hosted Smoke execution. FE-6 deliberately spends its
    real Docker budget on hidden CaseRuns, publication and leaderboard checks.
    """
    del record, agent_dir
    smoke_dir.mkdir(parents=True, exist_ok=True)
    (smoke_dir / "console.log").write_text(
        "Controlled FE-6 prerequisite: Hosted Smoke behavior was validated "
        "separately by the FE-3 pilot.\n",
        encoding="utf-8",
    )
    return SmokeOutcome(
        status="succeeded",
        message="Controlled FE-6 Smoke prerequisite passed.",
        summary={
            "schema_version": "0.1",
            "status": "succeeded",
            "case_count": 0,
            "succeeded": 0,
            "failed": 0,
            "cases": [],
            "precondition": "controlled-fe6-fixture",
        },
        run_dir=None,
    )


def request_json(
    port: int,
    method: str,
    path: str,
    *,
    token: str | None = None,
    body: bytes = b"",
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, object]]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    merged = dict(headers or {})
    merged.setdefault("Content-Length", str(len(body)))
    if token:
        merged["Authorization"] = f"Bearer {token}"
    try:
        connection.request(method, path, body=body, headers=merged)
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        return response.status, payload
    finally:
        connection.close()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    default_root = Path.home() / "buildbench_competition"
    parser.add_argument("--competition-root", type=Path, default=default_root)
    parser.add_argument("--port", type=int, default=8876)
    parser.add_argument("--case-count", type=int, default=3)
    args = parser.parse_args()
    root = args.competition_root.resolve()
    website = root / "buildbench-website"
    starter = root / "buildbench-starter-kit"
    validator = root / "docker-validator" / "bin" / "build-case-docker"
    source_case = root / "workspaces" / "linyihang" / "fe3-pilot" / "case"
    agent_zip = starter / "dist" / "milestone-b-first.zip"
    agent_image_path = (
        root / "workspaces" / "linyihang" / "fe3-pilot" / "agent-image.txt"
    )
    for required in (
        website / "backend" / "server.py",
        starter / "bb",
        validator,
        source_case / "manifest.json",
        agent_zip,
        agent_image_path,
    ):
        if not required.exists():
            raise SystemExit(f"missing FE-6 pilot input: {required}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = root / "workspaces" / "linyihang" / "fe6-pilot" / stamp
    case_root = run_root / "hidden-case-store"
    data_root = run_root / "runtime-data"
    output_root = run_root / "evaluation-output"
    for directory in (case_root, data_root, output_root):
        directory.mkdir(parents=True, exist_ok=True)
    case_ids = tuple(
        f"hidden-fe6-{index:02d}" for index in range(1, args.case_count + 1)
    )
    for case_id in case_ids:
        target = case_root / case_id
        shutil.copytree(source_case, target)
        manifest_path = target / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["case_id"] = case_id
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    agent_image = agent_image_path.read_text(encoding="utf-8").strip()
    validator_image = subprocess.check_output(
        [
            "docker",
            "image",
            "inspect",
            "buildbench-validator-runtime:v0",
            "--format",
            "{{.Id}}",
        ],
        text=True,
    ).strip()
    participant_token = "p" * 48
    admin_token = "a" * 48
    authenticator = TokenAuthenticator(
        {
            participant_token: RequestIdentity(
                "fe6-pilot-team", "fe6-pilot-team", "FE-6 Pilot Team"
            ),
            admin_token: RequestIdentity(
                "fe6-pilot-admin",
                "fe6-pilot-admin",
                "FE-6 Pilot Admin",
                "admin",
            ),
        },
        required=True,
    )
    protocol_hash = stable_digest(
        {"version": "0.1", "case_timeout": 700, "build_attempt_limit": 1}
    )
    config = EvaluationConfig(
        enabled=True,
        owner_id="fe6-pilot-team",
        case_ids=case_ids,
        case_set_version=f"hidden-trusted-pilot-{stamp}",
        case_set_digest=stable_digest(
            {"version": stamp, "case_ids": case_ids}
        ),
        runtime_image_digest=agent_image,
        validator_image_digest=validator_image,
        protocol_version="0.1",
        protocol_config_hash=protocol_hash,
        feedback_policy="hidden",
        allow_unsafe_validator=True,
    )
    database = data_root / "evaluations.sqlite3"
    server = create_server(
        "127.0.0.1",
        args.port,
        website,
        starter,
        data_root,
        1,
        ArchiveLimits(),
        evaluation_config=config,
        evaluation_database=database,
        authenticator=authenticator,
        smoke_runner=controlled_smoke_precondition,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        archive = agent_zip.read_bytes()
        status, submission = request_json(
            server.server_port,
            "POST",
            "/api/submissions",
            token=participant_token,
            body=archive,
            headers={
                "Content-Type": "application/zip",
                "X-Agent-Filename": "agent-submission.zip",
            },
        )
        assert status == 201, submission
        submission_id = str(submission["id"])
        status, _ = request_json(
            server.server_port,
            "POST",
            f"/api/submissions/{submission_id}/smoke-test",
            token=participant_token,
        )
        assert status == 202
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            status, submission = request_json(
                server.server_port,
                "GET",
                f"/api/submissions/{submission_id}",
                token=participant_token,
            )
            assert status == 200
            if submission["status"] == "smoke_passed":
                break
            if submission["status"] in {
                "check_failed",
                "smoke_failed",
                "infrastructure_error",
            }:
                raise RuntimeError(str(submission))
            time.sleep(2)
        else:
            raise RuntimeError("Hosted Smoke Test timed out")

        status, evaluation = request_json(
            server.server_port,
            "POST",
            f"/api/submissions/{submission_id}/full-evaluations",
            token=participant_token,
            headers={"Idempotency-Key": f"fe6-pilot-{stamp}"},
        )
        assert status == 201, evaluation
        evaluation_id = str(evaluation["evaluation_id"])
        self_env = os.environ.copy()
        self_env["BB_EVALUATION_DB"] = str(database)
        self_env["BB_WEB_DATA_ROOT"] = str(data_root)
        self_env["BB_CASE_SET_ROOT"] = str(case_root)
        self_env["BB_EVALUATION_OUTPUT_ROOT"] = str(output_root)
        self_env["BB_STARTER_KIT_ROOT"] = str(starter)
        self_env["BB_VALIDATOR_COMMAND"] = str(validator)
        self_env["BB_ALLOW_UNSAFE_VALIDATOR"] = "1"
        worker_log = run_root / "worker.log"
        with worker_log.open("w", encoding="utf-8") as log:
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "backend.evaluation_worker",
                    "--concurrency",
                    str(args.case_count),
                    "--agent-timeout",
                    "700",
                    "--build-timeout",
                    "600",
                    "--build-attempt-limit",
                    "1",
                    "--infra-retry-limit",
                    "1",
                    "--trusted-development",
                    "--until-idle",
                ],
                cwd=website,
                env=self_env,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=1800,
            )
        if completed.returncode != 0:
            raise RuntimeError(f"FE-6 Worker exited {completed.returncode}")

        status, final = request_json(
            server.server_port,
            "GET",
            f"/api/full-evaluations/{evaluation_id}",
            token=participant_token,
        )
        assert status == 200 and final["status"] == "completed", final
        serialized = json.dumps(final)
        assert not any(case_id in serialized for case_id in case_ids)

        status, published = request_json(
            server.server_port,
            "POST",
            f"/api/admin/full-evaluations/{evaluation_id}/publish",
            token=admin_token,
            headers={"X-BuildBench-Team-Name": "FE-6 Pilot Team"},
        )
        assert status == 200, published
        status, board = request_json(
            server.server_port,
            "GET",
            "/api/leaderboard",
        )
        assert status == 200 and len(board["entries"]) == 1, board
        assert board["entries"][0]["evaluation_id"] == evaluation_id

        evidence = {
            "schema_version": "0.1",
            "security_scope": "organizer-trusted-orchestration-only",
            "production_isolation_approved": False,
            "submission_id": submission_id,
            "submission_sha256": sha256(agent_zip),
            "evaluation_id": evaluation_id,
            "participant_view": final,
            "published_entry": published,
            "leaderboard": board,
        }
        (run_root / "pilot-summary.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        latest = run_root.parent / "latest.txt"
        latest.write_text(str(run_root) + "\n", encoding="utf-8")
        print(json.dumps(evidence, indent=2, sort_keys=True))
        print(f"FE-6 trusted hidden pilot: {run_root}")
        return 0
    finally:
        server.shutdown()
        server.server_close()
        server.smoke_queue.shutdown()  # type: ignore[attr-defined]
        thread.join(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
