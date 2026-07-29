from __future__ import annotations

import sqlite3
import tempfile
import threading
import time
import unittest
from pathlib import Path

from backend.evaluation_models import stable_digest
from backend.evaluation_scheduler import EvaluationScheduler
from backend.evaluation_service import EvaluationService
from backend.evaluation_store import EvaluationStore
from backend.evaluation_worker import (
    EvaluationWorker,
    EvaluationWorkerPool,
    WorkerConfig,
)
from backend.submissions import SubmissionService, SubmissionStore
from backend.tests.test_evaluations import (
    evaluation_config,
    qualified_submission,
)
from backend.tests.test_submissions import accepted_checker


def result(
    status: str,
    *,
    duration: int = 1,
) -> dict[str, object]:
    validator = status if status in {
        "succeeded",
        "failed",
        "unresolvable",
        "timeout",
        "invalid_patch",
        "infrastructure_error",
    } else None
    return {
        "status": status,
        "agent_status": (
            "completed"
            if status not in {"agent_error", "infrastructure_error"}
            else "agent_error"
        ),
        "validator_status": validator,
        "message": f"{status} fixture",
        "duration_seconds": duration,
        "agent_duration_seconds": duration,
        "build_duration_seconds": 0,
        "build_attempts": 0,
        "repair_size_bytes": 10 if status == "succeeded" else 0,
        "modified_files": 1 if status == "succeeded" else 0,
    }


class FakeExecutor:
    def __init__(
        self,
        outcomes: dict[int, list[str]],
        *,
        gate_ordinal: int | None = None,
    ):
        self.outcomes = outcomes
        self.gate_ordinal = gate_ordinal
        self.release = threading.Event()
        self.other_two_completed = threading.Event()
        self._lock = threading.Lock()
        self._active = 0
        self.max_active = 0
        self.calls: dict[int, int] = {}
        self.finished: list[int] = []

    def prepare(self, evaluation: dict[str, object]) -> None:
        del evaluation

    def run(
        self,
        *,
        claim: dict[str, object],
        evaluation: dict[str, object],
        attempt_root: Path,
    ) -> dict[str, object]:
        del evaluation
        attempt_root.mkdir(parents=True, exist_ok=True)
        ordinal = int(claim["case_ordinal"])
        with self._lock:
            self._active += 1
            self.max_active = max(self.max_active, self._active)
            call = self.calls.get(ordinal, 0)
            self.calls[ordinal] = call + 1
        try:
            if ordinal == self.gate_ordinal:
                self.release.wait(timeout=30)
            else:
                time.sleep(0.05)
            status_list = self.outcomes.get(ordinal, ["succeeded"])
            status = status_list[min(call, len(status_list) - 1)]
            with self._lock:
                self.finished.append(ordinal)
                if len(
                    [
                        item
                        for item in self.finished
                        if item != self.gate_ordinal
                    ]
                ) >= 2:
                    self.other_two_completed.set()
            return result(status)
        finally:
            with self._lock:
                self._active -= 1


class EvaluationWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.submissions = SubmissionService(
            SubmissionStore(self.root / "runtime"),
            self.root / "starter",
            checker=accepted_checker,
        )
        self.store = EvaluationStore(
            self.root / "runtime" / "evaluations.sqlite3"
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _evaluation(
        self,
        case_ids: tuple[str, ...] = ("case-a", "case-b", "case-c"),
    ) -> str:
        service = EvaluationService(
            self.store,
            self.submissions,
            evaluation_config(case_ids),
        )
        submission = qualified_submission(self.submissions)
        record, _ = service.create(str(submission["id"]), "worker-test-0001")
        return str(record["evaluation_id"])

    def _config(
        self,
        *,
        concurrency: int = 3,
        infra_retries: int = 1,
    ) -> WorkerConfig:
        return WorkerConfig(
            database_path=self.store.database_path,
            submission_root=self.root / "runtime",
            case_set_root=self.root / "cases",
            output_root=self.root / "outputs",
            starter_kit_root=self.root / "starter",
            validator_command=("validator",),
            cleanup_image="cleanup:test",
            concurrency=concurrency,
            lease_seconds=10,
            heartbeat_seconds=1,
            poll_seconds=0.01,
            agent_timeout_seconds=10,
            build_timeout_seconds=10,
            build_attempt_limit=1,
            infrastructure_retry_limit=infra_retries,
            retry_backoff_seconds=0,
            allow_unsafe_validator=True,
        )

    def test_three_cases_run_concurrently_and_score_freezes_once(self) -> None:
        evaluation_id = self._evaluation()
        executor = FakeExecutor(
            {
                1: ["succeeded"],
                2: ["failed"],
                3: ["no_fix"],
            }
        )
        pool = EvaluationWorkerPool(
            store=self.store,
            executor=executor,
            config=self._config(),
            instance_id="concurrency-test",
        )
        processed = pool.run_until_idle(idle_cycles=1)
        record = self.store.get(evaluation_id)
        self.assertEqual(processed, 3)
        self.assertGreaterEqual(executor.max_active, 2)
        self.assertEqual(record["status"], "completed")
        self.assertAlmostEqual(float(record["score"]), 1 / 3)
        frozen = self.store.get(evaluation_id)
        pool.scheduler.finalize_ready()
        self.assertEqual(self.store.get(evaluation_id)["score"], frozen["score"])

    def test_one_blocked_case_does_not_stop_other_cases(self) -> None:
        evaluation_id = self._evaluation()
        executor = FakeExecutor(
            {1: ["succeeded"], 2: ["failed"], 3: ["succeeded"]},
            gate_ordinal=1,
        )
        pool = EvaluationWorkerPool(
            store=self.store,
            executor=executor,
            config=self._config(),
            instance_id="blocked-test",
        )
        thread = threading.Thread(
            target=pool.run_until_idle,
            kwargs={"idle_cycles": 1},
        )
        thread.start()
        try:
            self.assertTrue(executor.other_two_completed.wait(timeout=5))
            deadline = time.monotonic() + 5
            while (
                int(self.store.get(evaluation_id)["completed_cases"]) < 2
                and time.monotonic() < deadline
            ):
                time.sleep(0.02)
            interim = self.store.get(evaluation_id)
            self.assertEqual(interim["status"], "evaluating")
            self.assertEqual(interim["completed_cases"], 2)
        finally:
            executor.release.set()
            thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(self.store.get(evaluation_id)["status"], "completed")

    def test_expired_lease_is_reclaimed_after_worker_loss(self) -> None:
        evaluation_id = self._evaluation(("case-a",))
        executor = FakeExecutor({1: ["succeeded"]})
        scheduler = EvaluationScheduler(self.store, executor.prepare)
        scheduler.activate_ready()
        dead_claim = self.store.claim_case_run(
            worker_id="dead-worker",
            lease_seconds=60,
        )
        self.assertIsNotNone(dead_claim)
        assert dead_claim is not None
        with sqlite3.connect(self.store.database_path) as connection:
            connection.execute(
                """
                UPDATE evaluation_case_runs
                SET lease_until = '2000-01-01T00:00:00+00:00'
                WHERE case_run_id = ?
                """,
                (dead_claim["case_run_id"],),
            )
        worker = EvaluationWorker(
            store=self.store,
            scheduler=scheduler,
            executor=executor,
            config=self._config(concurrency=1),
            worker_id="recovery-worker",
        )
        self.assertTrue(worker.run_once())
        case_run = self.store.list_case_runs(evaluation_id)[0]
        self.assertEqual(case_run["attempt_count"], 2)
        self.assertEqual(case_run["status"], "succeeded")
        self.assertEqual(self.store.get(evaluation_id)["status"], "completed")

    def test_infrastructure_error_retries_without_scoring_failure(self) -> None:
        evaluation_id = self._evaluation(("case-a",))
        executor = FakeExecutor(
            {1: ["infrastructure_error", "succeeded"]}
        )
        pool = EvaluationWorkerPool(
            store=self.store,
            executor=executor,
            config=self._config(concurrency=1, infra_retries=1),
            instance_id="retry-test",
        )
        self.assertEqual(pool.run_until_idle(idle_cycles=1), 2)
        evaluation = self.store.get(evaluation_id)
        case_run = self.store.list_case_runs(evaluation_id)[0]
        self.assertEqual(evaluation["status"], "completed")
        self.assertEqual(evaluation["infrastructure_retries"], 1)
        self.assertEqual(case_run["attempt_count"], 2)
        self.assertEqual(case_run["status"], "succeeded")

    def test_exhausted_infrastructure_error_publishes_no_score(self) -> None:
        evaluation_id = self._evaluation(("case-a",))
        executor = FakeExecutor({1: ["infrastructure_error"]})
        pool = EvaluationWorkerPool(
            store=self.store,
            executor=executor,
            config=self._config(concurrency=1, infra_retries=1),
            instance_id="exhausted-test",
        )
        self.assertEqual(pool.run_until_idle(idle_cycles=1), 2)
        evaluation = self.store.get(evaluation_id)
        self.assertEqual(evaluation["status"], "system_error")
        self.assertIsNone(evaluation["score"])

    def test_schema_v1_database_receives_retry_column_migration(self) -> None:
        legacy_database = self.root / "legacy-evaluations.sqlite3"
        schema = (
            Path(__file__).resolve().parents[1]
            / "schema"
            / "evaluations-v1.sql"
        ).read_text(encoding="utf-8")
        schema = schema.replace(
            "    build_attempts INTEGER\n"
            "        CHECK (build_attempts IS NULL OR build_attempts >= 0),\n",
            "",
        ).replace(
            "    retry_after TEXT,\n",
            "",
        )
        with sqlite3.connect(legacy_database) as connection:
            connection.executescript(schema)
            connection.execute(
                "DELETE FROM evaluation_schema_versions WHERE version > 1"
            )
        migrated = EvaluationStore(legacy_database)
        columns = {
            str(row[1])
            for row in sqlite3.connect(migrated.database_path).execute(
                "PRAGMA table_info(evaluation_case_runs)"
            )
        }
        self.assertIn("retry_after", columns)
        self.assertIn("build_attempts", columns)
        versions = {
            int(row[0])
            for row in sqlite3.connect(migrated.database_path).execute(
                "SELECT version FROM evaluation_schema_versions"
            )
        }
        self.assertIn(2, versions)
        self.assertIn(3, versions)
        self.assertIn(5, versions)
        tables = {
            str(row[0])
            for row in sqlite3.connect(migrated.database_path).execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        self.assertIn("evaluation_workers", tables)

    def test_until_idle_worker_registration_is_stopped_on_exit(self) -> None:
        evaluation_id = self._evaluation(("case-a",))
        config = evaluation_config(("case-a",))
        pool = EvaluationWorkerPool(
            store=self.store,
            executor=FakeExecutor({1: ["succeeded"]}),
            config=self._config(concurrency=1),
            instance_id="bounded-worker",
            evaluation_config=config,
        )
        self.assertEqual(pool.run_until_idle(idle_cycles=1), 1)
        self.assertEqual(self.store.get(evaluation_id)["status"], "completed")
        readiness = self.store.worker_readiness(
            case_set_version=config.case_set_version,
            case_set_digest=config.case_set_digest,
            runtime_image_digest=config.runtime_image_digest,
            validator_image_digest=config.validator_image_digest,
            protocol_version=config.protocol_version,
            protocol_config_hash=config.protocol_config_hash,
            isolation_mode=config.validator_isolation,
            stale_after_seconds=15,
        )
        self.assertFalse(readiness["available"])


if __name__ == "__main__":
    unittest.main()
