from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.evaluation_models import (
    EvaluationConfig,
    EvaluationConflict,
    EvaluationResultNotReady,
    stable_digest,
)
from backend.evaluation_service import EvaluationService
from backend.evaluation_store import EvaluationStore
from backend.submissions import SubmissionService, SubmissionStore
from backend.tests.test_submissions import accepted_checker, valid_agent_zip


def evaluation_config(case_ids: tuple[str, ...] = ("case-a", "case-b")):
    return EvaluationConfig(
        enabled=True,
        owner_id="team-test",
        case_ids=case_ids,
        case_set_version="dev-2026-07",
        case_set_digest=stable_digest(case_ids),
        runtime_image_digest="sha256:" + "a" * 64,
        validator_image_digest="sha256:" + "b" * 64,
        protocol_version="0.1",
        protocol_config_hash="c" * 64,
        feedback_policy="hidden",
        # Tests use no Validator; production still defaults to blocked.
        allow_unsafe_validator=True,
    )


def qualified_submission(
    service: SubmissionService, name: str = "test-agent"
) -> dict[str, object]:
    record = service.create_submission(
        f"{name}.zip",
        valid_agent_zip(name),
    )
    return service.store.update(
        str(record["id"]),
        {
            "status": "smoke_passed",
            "message": "Hosted Smoke Test passed.",
            "smoke": {
                "status": "passed",
                "summary": {
                    "status": "succeeded",
                    "case_count": 1,
                    "succeeded": 1,
                    "failed": 0,
                },
            },
        },
    )


class EvaluationLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.submissions = SubmissionService(
            SubmissionStore(root / "runtime"),
            root / "starter",
            checker=accepted_checker,
        )
        self.store = EvaluationStore(root / "runtime" / "evaluations.sqlite3")
        self.service = EvaluationService(
            self.store,
            self.submissions,
            evaluation_config(),
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_create_is_idempotent_and_one_official_run_per_submission(self) -> None:
        submission = qualified_submission(self.submissions)
        created, was_created = self.service.create(
            str(submission["id"]),
            "request-0001",
        )
        replay, replay_created = self.service.create(
            str(submission["id"]),
            "request-0001",
        )
        self.assertTrue(was_created)
        self.assertFalse(replay_created)
        self.assertEqual(replay["evaluation_id"], created["evaluation_id"])
        with self.assertRaisesRegex(
            EvaluationConflict,
            "already has an official",
        ):
            self.service.create(str(submission["id"]), "request-0002")

    def test_active_team_constraint_and_new_version_after_completion(self) -> None:
        first = qualified_submission(self.submissions, "agent-one")
        first_eval, _ = self.service.create(str(first["id"]), "request-1001")
        second = qualified_submission(self.submissions, "agent-two")
        with self.assertRaisesRegex(EvaluationConflict, "already active"):
            self.service.create(str(second["id"]), "request-1002")

        evaluation_id = str(first_eval["evaluation_id"])
        self.store.transition(
            evaluation_id,
            expected_status="queued",
            target_status="preparing",
        )
        self.store.transition(
            evaluation_id,
            expected_status="preparing",
            target_status="evaluating",
        )
        self.store.set_case_run_terminal(
            evaluation_id,
            1,
            status="succeeded",
            agent_status="completed",
            validator_status="succeeded",
            duration_seconds=3,
        )
        self.store.set_case_run_terminal(
            evaluation_id,
            2,
            status="failed",
            agent_status="completed",
            validator_status="failed",
            duration_seconds=4,
        )
        self.store.transition(
            evaluation_id,
            expected_status="evaluating",
            target_status="finalizing",
        )
        completed = self.store.finalize(evaluation_id)
        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["score"], 0.5)

        second_eval, created = self.service.create(
            str(second["id"]),
            "request-1002",
        )
        self.assertTrue(created)
        self.assertNotEqual(
            second_eval["evaluation_id"],
            first_eval["evaluation_id"],
        )

    def test_public_contract_hides_cases_and_partial_score(self) -> None:
        submission = qualified_submission(self.submissions)
        record, _ = self.service.create(
            str(submission["id"]),
            "request-2001",
        )
        serialized = repr(record)
        self.assertNotIn("case-a", serialized)
        self.assertNotIn("case-b", serialized)
        self.assertIsNone(record["score"])
        self.assertEqual(
            record["progress"],
            {
                "completed": 0,
                "total": 2,
                "percent": 0.0,
                "running": 0,
                "infrastructure_retries": 0,
            },
        )
        with self.assertRaises(EvaluationResultNotReady):
            self.service.result(str(record["evaluation_id"]))
        events = self.service.events(str(record["evaluation_id"]))
        self.assertEqual([event["type"] for event in events], ["snapshot", "phase"])
        self.assertNotIn("case-a", repr(events))

    def test_infrastructure_error_cannot_be_scored(self) -> None:
        submission = qualified_submission(self.submissions)
        record, _ = self.service.create(
            str(submission["id"]),
            "request-3001",
        )
        evaluation_id = str(record["evaluation_id"])
        self.store.transition(
            evaluation_id,
            expected_status="queued",
            target_status="preparing",
        )
        self.store.transition(
            evaluation_id,
            expected_status="preparing",
            target_status="evaluating",
        )
        self.store.set_case_run_terminal(
            evaluation_id,
            1,
            status="succeeded",
        )
        self.store.set_case_run_terminal(
            evaluation_id,
            2,
            status="infrastructure_error",
        )
        self.store.transition(
            evaluation_id,
            expected_status="evaluating",
            target_status="finalizing",
        )
        with self.assertRaisesRegex(
            EvaluationConflict,
            "Infrastructure errors",
        ):
            self.store.finalize(evaluation_id)


if __name__ == "__main__":
    unittest.main()

