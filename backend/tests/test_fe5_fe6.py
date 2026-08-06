from __future__ import annotations

import hashlib
import http.client
import json
import sqlite3
import subprocess
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from backend.evaluation_models import EvaluationConfig, stable_digest
from backend.evaluation_runner import DockerAgentConfig, DockerAgentExecutor
from backend.evaluation_service import EvaluationService
from backend.evaluation_store import EvaluationStore
from backend.retention import prune_evaluation_outputs
from backend.security import (
    RequestIdentity,
    TokenAuthenticator,
    validate_isolation_attestation,
)
from backend.server import create_server
from backend.submissions import ArchiveLimits, SubmissionService, SubmissionStore
from backend.tests.test_evaluations import qualified_submission
from backend.tests.test_submissions import accepted_checker, valid_agent_zip


def _config(owner: str, cases: tuple[str, ...] = ("hidden-a",)) -> EvaluationConfig:
    return EvaluationConfig(
        enabled=True,
        owner_id=owner,
        case_ids=cases,
        case_set_version="hidden-v1",
        case_set_digest=stable_digest(cases),
        runtime_image_digest="sha256:" + "a" * 64,
        validator_image_digest="sha256:" + "b" * 64,
        protocol_version="0.1",
        protocol_config_hash="c" * 64,
        feedback_policy="hidden",
        allow_unsafe_validator=True,
    )


def _complete(store: EvaluationStore, evaluation_id: str, succeeded: bool = True) -> None:
    store.transition(
        evaluation_id,
        expected_status="queued",
        target_status="preparing",
    )
    store.transition(
        evaluation_id,
        expected_status="preparing",
        target_status="evaluating",
    )
    store.set_case_run_terminal(
        evaluation_id,
        1,
        status="succeeded" if succeeded else "failed",
        agent_status="completed",
        validator_status="succeeded" if succeeded else "failed",
        duration_seconds=2,
    )
    store.transition(
        evaluation_id,
        expected_status="evaluating",
        target_status="finalizing",
    )
    store.finalize(evaluation_id)


class SecurityGateTests(unittest.TestCase):
    def test_isolation_attestation_must_match_frozen_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "attestation.json"
            payload: dict[str, object] = {
                "schema_version": "0.2",
                "isolation_mode": "ephemeral_vm",
                "provider": "qemu_kvm",
                "validator_image_digest": "sha256:" + "b" * 64,
                "protocol_config_hash": "c" * 64,
                "launcher_image_digest": "sha256:" + "e" * 64,
                "guest_image_sha256": "sha256:" + "f" * 64,
                "kvm_acceleration": True,
                "docker_socket_exposed_to_agent": False,
                "host_docker_socket_mounted_in_worker": False,
                "hidden_case_store_mounted_in_validator_vm": False,
                "worker_reused_between_cases": False,
                "worker_overlay_discarded": True,
                "job_input_scope": "single_case",
                "output_scope": "dedicated_directory",
                "network_mode": "none",
                "approved_by": "security-reviewer",
                "approved_at": "2026-07-27T00:00:00+00:00",
                "expires_at": "2099-01-01T00:00:00+00:00",
            }
            payload["document_sha256"] = hashlib.sha256(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertIsNone(
                validate_isolation_attestation(
                    isolation_mode="ephemeral_vm",
                    attestation_path=path,
                    validator_image_digest="sha256:" + "b" * 64,
                    protocol_config_hash="c" * 64,
                    launcher_image_digest="sha256:" + "e" * 64,
                    guest_image_sha256="sha256:" + "f" * 64,
                )
            )
            self.assertIn(
                "validator_image_digest",
                validate_isolation_attestation(
                    isolation_mode="ephemeral_vm",
                    attestation_path=path,
                    validator_image_digest="sha256:" + "d" * 64,
                    protocol_config_hash="c" * 64,
                    launcher_image_digest="sha256:" + "e" * 64,
                    guest_image_sha256="sha256:" + "f" * 64,
                )
                or "",
            )

    def test_production_configuration_fails_closed_without_attestation(self) -> None:
        config = _config("team-a")
        config = EvaluationConfig(
            **{
                **config.__dict__,
                "allow_unsafe_validator": False,
                "validator_isolation": "host_docker",
                "isolation_attestation": None,
            }
        )
        self.assertIn("isolation", config.readiness_error() or "")

    def test_agent_command_exposes_no_network_or_docker_socket(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            client = root / "bb-build"
            client.write_text("#!/bin/sh\n", encoding="utf-8")
            for name in ("agent", "workspace/input", "workspace/work", "workspace/output", "gw"):
                (root / name).mkdir(parents=True, exist_ok=True)
            executor = DockerAgentExecutor(
                DockerAgentConfig(
                    image="sha256:" + "a" * 64,
                    entrypoint=("python", "-m", "src.main"),
                    timeout_seconds=30,
                ),
                client,
            )
            command = executor.command(
                agent_dir=root / "agent",
                workspace=root / "workspace",
                gateway_socket=root / "gw" / "gateway.sock",
                gateway_token="not-in-command",
                container_name="agent-test",
            )
            serialized = " ".join(command)
            self.assertIn("--network none", serialized)
            self.assertIn("--read-only", command)
            self.assertIn("--cap-drop ALL", serialized)
            self.assertIn("nofile=1024:1024", serialized)
            self.assertNotIn("/var/run/docker.sock", serialized)
            self.assertNotIn("not-in-command", serialized)

    def test_agent_cleanup_does_not_block_on_unhealthy_docker_daemon(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client = Path(temporary) / "bb-build"
            client.write_text("#!/bin/sh\n", encoding="utf-8")
            executor = DockerAgentExecutor(
                DockerAgentConfig(
                    image="sha256:" + "a" * 64,
                    entrypoint=("python", "-m", "src.main"),
                    timeout_seconds=30,
                ),
                client,
            )
            with mock.patch(
                "backend.evaluation_runner.subprocess.run",
                side_effect=subprocess.TimeoutExpired(["docker", "rm"], 10),
            ):
                executor._force_remove_container("not-created-yet")


class AuthorizationAndLeaderboardTests(unittest.TestCase):
    def test_bearer_owner_isolation_and_admin_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            website = root / "website"
            website.mkdir()
            (website / "index.html").write_text("ok", encoding="utf-8")
            starter = root / "starter"
            starter.mkdir()
            (starter / "bb").write_text("#!/bin/sh\n", encoding="utf-8")
            participant_a = "a" * 32
            participant_b = "b" * 32
            admin = "c" * 32
            authenticator = TokenAuthenticator(
                {
                    participant_a: RequestIdentity("team-a", "team-a", "A"),
                    participant_b: RequestIdentity("team-b", "team-b", "B"),
                    admin: RequestIdentity("admin", "admin", "Admin", "admin"),
                },
                required=True,
            )
            server = create_server(
                "127.0.0.1",
                0,
                website,
                starter,
                root / "data",
                1,
                ArchiveLimits(),
                checker=accepted_checker,
                evaluation_config=_config("team-a"),
                authenticator=authenticator,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_port, timeout=5
            )
            try:
                payload = valid_agent_zip()
                connection.request(
                    "POST",
                    "/api/submissions",
                    body=payload,
                    headers={
                        "Authorization": f"Bearer {participant_a}",
                        "Content-Type": "application/zip",
                        "Content-Length": str(len(payload)),
                        "X-Agent-Filename": "agent.zip",
                    },
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 201)
                submission = json.load(response)

                connection.request(
                    "GET",
                    f"/api/submissions/{submission['id']}",
                    headers={"Authorization": f"Bearer {participant_b}"},
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 404)
                response.read()

                connection.request(
                    "GET",
                    "/api/admin/full-evaluations/FE-missing",
                    headers={"Authorization": f"Bearer {participant_a}"},
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 403)
                response.read()
            finally:
                connection.close()
                server.shutdown()
                server.server_close()
                server.smoke_queue.shutdown()  # type: ignore[attr-defined]
                thread.join(timeout=5)

    def test_hidden_result_publication_ranking_and_retention(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            submissions = SubmissionService(
                SubmissionStore(root / "runtime"),
                root / "starter",
                checker=accepted_checker,
            )
            store = EvaluationStore(root / "runtime" / "evaluations.sqlite3")
            service = EvaluationService(
                store,
                submissions,
                _config("team-a"),
                team_member_resolver=lambda team_id: (
                    ["Captain A", "Member A"] if team_id == "team-a" else []
                ),
            )
            first = qualified_submission(submissions, "agent-one")
            first_record, _ = service.create(str(first["id"]), "publish-0001")
            first_id = str(first_record["evaluation_id"])
            _complete(store, first_id, succeeded=True)
            published = service.admin_publish(
                first_id,
                team_name="Team A",
                actor_id="admin",
            )
            self.assertEqual(published["evaluation_id"], first_id)
            board = service.leaderboard(
                case_set_version="hidden-v1",
                protocol_version="0.1",
            )
            self.assertEqual(len(board["entries"]), 1)
            entry = board["entries"][0]
            self.assertEqual(entry["rank"], 1)
            self.assertEqual(entry["team_name"], "Team A")
            self.assertEqual(entry["members"], ["Captain A", "Member A"])
            self.assertNotIn("owner_id", entry)
            self.assertNotIn("evaluation_id", entry)
            self.assertNotIn("entry_id", entry)
            self.assertNotIn("agent_name", entry)
            self.assertNotIn("agent_version", entry)
            self.assertNotIn("duration_seconds", entry)
            self.assertNotIn("case_set_digest", entry)
            self.assertNotIn("protocol_config_hash", entry)

            output_root = root / "outputs"
            artifact = output_root / first_id
            artifact.mkdir(parents=True)
            (artifact / "internal.log").write_text("secret", encoding="utf-8")
            old = (
                datetime.now(timezone.utc) - timedelta(days=40)
            ).replace(microsecond=0).isoformat()
            connection = sqlite3.connect(store.database_path)
            try:
                connection.execute(
                    "UPDATE full_evaluations SET finished_at = ? WHERE evaluation_id = ?",
                    (old, first_id),
                )
                connection.commit()
            finally:
                connection.close()
            preview = prune_evaluation_outputs(
                store=store,
                output_root=output_root,
                retention_days=30,
                dry_run=True,
            )
            self.assertTrue(preview[0]["exists"])
            self.assertTrue(artifact.exists())
            prune_evaluation_outputs(
                store=store,
                output_root=output_root,
                retention_days=30,
                dry_run=False,
            )
            self.assertFalse(artifact.exists())
            audit = store.list_audit_events(
                target_type="evaluation", target_id=first_id
            )
            self.assertEqual(
                [event["action"] for event in audit],
                ["publish_leaderboard", "delete_evaluation_artifacts"],
            )

    def test_admin_recovery_requeues_only_infrastructure_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            submissions = SubmissionService(
                SubmissionStore(root / "runtime"),
                root / "starter",
                checker=accepted_checker,
            )
            store = EvaluationStore(root / "runtime" / "evaluations.sqlite3")
            service = EvaluationService(store, submissions, _config("team-a"))
            submission = qualified_submission(submissions, "recover-agent")
            record, _ = service.create(str(submission["id"]), "recover-0001")
            evaluation_id = str(record["evaluation_id"])
            store.transition(
                evaluation_id,
                expected_status="queued",
                target_status="preparing",
            )
            store.transition(
                evaluation_id,
                expected_status="preparing",
                target_status="evaluating",
            )
            store.set_case_run_terminal(
                evaluation_id,
                1,
                status="infrastructure_error",
                agent_status="completed",
                validator_status="infrastructure_error",
                duration_seconds=3,
            )
            store.transition(
                evaluation_id,
                expected_status="evaluating",
                target_status="system_error",
                system_message="validator worker unavailable",
            )

            recovered = service.admin_recover(
                evaluation_id,
                actor_id="admin",
            )
            self.assertEqual(recovered["status"], "preparing")
            case_run = store.list_case_runs(evaluation_id)[0]
            self.assertEqual(case_run["status"], "queued")
            self.assertIsNone(case_run["validator_status"])
            self.assertEqual(
                store.list_audit_events(
                    target_type="evaluation", target_id=evaluation_id
                )[-1]["action"],
                "recover",
            )


if __name__ == "__main__":
    unittest.main()
