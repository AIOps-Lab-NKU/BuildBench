#!/usr/bin/env python3
"""Publish a completed trusted FE-6 run through the real HTTP boundaries."""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path

from backend.evaluation_models import EvaluationConfig
from backend.evaluation_store import EvaluationStore
from backend.security import RequestIdentity, TokenAuthenticator
from backend.server import create_server
from backend.submissions import ArchiveLimits
from backend.tests.run_trusted_fe6_pilot import request_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--competition-root", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8877)
    args = parser.parse_args()
    run_root = args.run_root.resolve()
    competition_root = args.competition_root.resolve()
    database = run_root / "runtime-data" / "evaluations.sqlite3"
    store = EvaluationStore(database)
    evaluations = store.list("fe6-pilot-team")
    if len(evaluations) != 1:
        raise SystemExit(f"expected one FE-6 Evaluation, found {len(evaluations)}")
    evaluation = evaluations[0]
    if evaluation["status"] != "completed":
        raise SystemExit(f"Evaluation is not completed: {evaluation['status']}")
    evaluation_id = str(evaluation["evaluation_id"])
    case_runs = store.list_case_runs(evaluation_id)
    case_ids = tuple(str(item["case_snapshot_id"]) for item in case_runs)
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
    config = EvaluationConfig(
        enabled=True,
        owner_id="fe6-pilot-team",
        case_ids=case_ids,
        case_set_version=str(evaluation["case_set_version"]),
        case_set_digest=str(evaluation["case_set_digest"]),
        runtime_image_digest=str(evaluation["runtime_image_digest"]),
        validator_image_digest=str(evaluation["validator_image_digest"]),
        protocol_version=str(evaluation["protocol_version"]),
        protocol_config_hash=str(evaluation["protocol_config_hash"]),
        feedback_policy=str(evaluation["feedback_policy"]),
        allow_unsafe_validator=True,
    )
    server = create_server(
        "127.0.0.1",
        args.port,
        competition_root / "buildbench-website",
        competition_root / "buildbench-starter-kit",
        run_root / "runtime-data",
        1,
        ArchiveLimits(),
        evaluation_config=config,
        evaluation_database=database,
        authenticator=authenticator,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, participant = request_json(
            server.server_port,
            "GET",
            f"/api/full-evaluations/{evaluation_id}",
            token=participant_token,
        )
        if status != 200:
            raise RuntimeError(participant)
        serialized = json.dumps(participant, sort_keys=True)
        if any(case_id in serialized for case_id in case_ids):
            raise RuntimeError("participant response leaked a hidden Case ID")
        status, published = request_json(
            server.server_port,
            "POST",
            f"/api/admin/full-evaluations/{evaluation_id}/publish",
            token=admin_token,
            headers={"X-BuildBench-Team-Name": "FE-6 Pilot Team"},
        )
        if status != 200:
            raise RuntimeError(published)
        status, board = request_json(
            server.server_port,
            "GET",
            "/api/leaderboard",
        )
        if status != 200 or len(board.get("entries", [])) != 1:
            raise RuntimeError(board)
        public_serialized = json.dumps(board, sort_keys=True)
        forbidden = (*case_ids, "case_set_digest", "protocol_config_hash")
        if any(value in public_serialized for value in forbidden):
            raise RuntimeError("public leaderboard leaked an internal field")
        summary = {
            "schema_version": "0.1",
            "evaluation_id": evaluation_id,
            "status": evaluation["status"],
            "score": evaluation["score"],
            "successful_cases": evaluation["successful_cases"],
            "total_cases": evaluation["total_cases"],
            "case_attempts": [item["attempt_count"] for item in case_runs],
            "participant_hidden_case_ids_redacted": True,
            "leaderboard_entry": board["entries"][0],
            "security": {
                "mode": "organizer-trusted-orchestration-only",
                "production_isolation_approved": False,
            },
        }
        (run_root / "pilot-summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        latest = run_root.parent / "latest.txt"
        latest.write_text(str(run_root) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
    finally:
        server.shutdown()
        server.server_close()
        server.smoke_queue.shutdown()  # type: ignore[attr-defined]
        thread.join(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
