"""SQLite-backed persistence for Full Evaluation lifecycle state."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from backend.evaluation_models import (
    ACTIVE_EVALUATION_STATUSES,
    CASE_RUN_STATUSES,
    EVALUATION_STATUSES,
    SCORED_FAILURE_CASE_RUN_STATUSES,
    TERMINAL_CASE_RUN_STATUSES,
    EvaluationConflict,
    EvaluationNotFound,
    new_case_run_id,
    new_evaluation_id,
    utc_now,
    validate_transition,
)


class EvaluationStore:
    """Durable state store designed for a web process plus Worker processes."""

    def __init__(self, database_path: Path):
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._schema_path = (
            Path(__file__).resolve().parent / "schema" / "evaluations-v1.sql"
        )
        self._init_lock = threading.Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    def _initialize(self) -> None:
        with self._init_lock:
            schema = self._schema_path.read_text(encoding="utf-8")
            with self._connect() as connection:
                connection.execute("PRAGMA journal_mode = WAL")
                connection.execute("PRAGMA synchronous = NORMAL")
                connection.executescript(schema)
                columns = {
                    str(row["name"])
                    for row in connection.execute(
                        "PRAGMA table_info(evaluation_case_runs)"
                    ).fetchall()
                }
                if "retry_after" not in columns:
                    connection.execute(
                        "ALTER TABLE evaluation_case_runs "
                        "ADD COLUMN retry_after TEXT"
                    )
                if "build_attempts" not in columns:
                    connection.execute(
                        "ALTER TABLE evaluation_case_runs "
                        "ADD COLUMN build_attempts INTEGER"
                    )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO evaluation_schema_versions(
                        version, applied_at
                    ) VALUES (2, ?)
                    """,
                    (utc_now(),),
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO evaluation_schema_versions(
                        version, applied_at
                    ) VALUES (3, ?)
                    """,
                    (utc_now(),),
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO evaluation_schema_versions(
                        version, applied_at
                    ) VALUES (4, ?)
                    """,
                    (utc_now(),),
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO evaluation_schema_versions(
                        version, applied_at
                    ) VALUES (5, ?)
                    """,
                    (utc_now(),),
                )

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    @staticmethod
    def _record(row: sqlite3.Row | None) -> dict[str, object] | None:
        return dict(row) if row is not None else None

    @staticmethod
    def _event_payload(raw: str) -> dict[str, object]:
        try:
            payload = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def create(
        self,
        *,
        submission_id: str,
        owner_id: str,
        idempotency_key: str,
        request_hash: str,
        submission_sha256: str,
        agent_name: str,
        agent_version: str,
        case_ids: tuple[str, ...],
        case_set_version: str,
        case_set_digest: str,
        runtime_image_digest: str,
        validator_image_digest: str,
        protocol_version: str,
        protocol_config_hash: str,
        feedback_policy: str,
    ) -> tuple[dict[str, object], bool]:
        now = utc_now()
        evaluation_id = new_evaluation_id()
        try:
            with self._transaction() as connection:
                replay = connection.execute(
                    """
                    SELECT * FROM full_evaluations
                    WHERE owner_id = ? AND idempotency_key = ?
                    """,
                    (owner_id, idempotency_key),
                ).fetchone()
                if replay is not None:
                    if replay["request_hash"] != request_hash:
                        raise EvaluationConflict(
                            "Idempotency-Key was already used for another request."
                        )
                    return dict(replay), False

                connection.execute(
                    """
                    INSERT INTO full_evaluations (
                        evaluation_id,
                        submission_id,
                        owner_id,
                        kind,
                        idempotency_key,
                        request_hash,
                        status,
                        submission_sha256,
                        agent_name,
                        agent_version,
                        case_set_version,
                        case_set_digest,
                        runtime_image_digest,
                        validator_image_digest,
                        protocol_version,
                        protocol_config_hash,
                        feedback_policy,
                        total_cases,
                        completed_cases,
                        successful_cases,
                        running_cases,
                        infrastructure_retries,
                        score,
                        queued_at,
                        created_at,
                        updated_at
                    ) VALUES (
                        ?, ?, ?, 'official', ?, ?, 'queued',
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        0, 0, 0, 0, NULL, ?, ?, ?
                    )
                    """,
                    (
                        evaluation_id,
                        submission_id,
                        owner_id,
                        idempotency_key,
                        request_hash,
                        submission_sha256,
                        agent_name,
                        agent_version,
                        case_set_version,
                        case_set_digest,
                        runtime_image_digest,
                        validator_image_digest,
                        protocol_version,
                        protocol_config_hash,
                        feedback_policy,
                        len(case_ids),
                        now,
                        now,
                        now,
                    ),
                )
                for ordinal, case_id in enumerate(case_ids, start=1):
                    connection.execute(
                        """
                        INSERT INTO evaluation_case_runs (
                            case_run_id,
                            evaluation_id,
                            case_snapshot_id,
                            case_ordinal,
                            status,
                            attempt_count,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, ?, ?, 'queued', 0, ?, ?)
                        """,
                        (
                            new_case_run_id(),
                            evaluation_id,
                            case_id,
                            ordinal,
                            now,
                            now,
                        ),
                    )
                self._append_event(
                    connection,
                    evaluation_id,
                    "snapshot",
                    {
                        "status": "queued",
                        "total_cases": len(case_ids),
                        "completed_cases": 0,
                    },
                    now,
                )
                self._append_event(
                    connection,
                    evaluation_id,
                    "phase",
                    {"status": "queued"},
                    now,
                )
                row = connection.execute(
                    "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                    (evaluation_id,),
                ).fetchone()
                return dict(row), True
        except sqlite3.IntegrityError as error:
            with self._connect() as connection:
                existing_submission = connection.execute(
                    """
                    SELECT 1 FROM full_evaluations
                    WHERE submission_id = ? AND kind = 'official'
                    """,
                    (submission_id,),
                ).fetchone()
                active_owner = connection.execute(
                    """
                    SELECT 1 FROM full_evaluations
                    WHERE owner_id = ?
                      AND status IN ('queued', 'preparing', 'evaluating', 'finalizing')
                    """,
                    (owner_id,),
                ).fetchone()
            if existing_submission is not None:
                raise EvaluationConflict(
                    "This Agent version already has an official Full Evaluation."
                ) from None
            if active_owner is not None:
                raise EvaluationConflict(
                    "Another Full Evaluation is already active for this team."
                ) from None
            message = str(error).lower()
            if "full_evaluations.submission_id" in message:
                raise EvaluationConflict(
                    "This Agent version already has an official Full Evaluation."
                ) from None
            if (
                "one_active_full_evaluation_per_owner" in message
                or "full_evaluations.owner_id" in message
            ):
                raise EvaluationConflict(
                    "Another Full Evaluation is already active for this team."
                ) from None
            raise EvaluationConflict(
                "Full Evaluation could not be created because it conflicts "
                "with an existing request."
            ) from error

    @staticmethod
    def _append_event(
        connection: sqlite3.Connection,
        evaluation_id: str,
        event_type: str,
        payload: dict[str, object],
        created_at: str | None = None,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO evaluation_events (
                evaluation_id, event_type, payload_json, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                evaluation_id,
                event_type,
                json.dumps(payload, separators=(",", ":"), sort_keys=True),
                created_at or utc_now(),
            ),
        )
        return int(cursor.lastrowid)

    def get(self, evaluation_id: str) -> dict[str, object]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
        if row is None:
            raise EvaluationNotFound("Full Evaluation not found.")
        return dict(row)

    def get_for_submission(
        self, submission_id: str, owner_id: str
    ) -> dict[str, object] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM full_evaluations
                WHERE submission_id = ? AND owner_id = ? AND kind = 'official'
                """,
                (submission_id, owner_id),
            ).fetchone()
        return self._record(row)

    def list(self, owner_id: str) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM full_evaluations
                WHERE owner_id = ?
                ORDER BY created_at DESC, evaluation_id DESC
                """,
                (owner_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def events(
        self,
        evaluation_id: str,
        owner_id: str,
        after_event_id: int = 0,
    ) -> list[dict[str, object]]:
        self.require_owner(evaluation_id, owner_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT event_id, evaluation_id, event_type, payload_json, created_at
                FROM evaluation_events
                WHERE evaluation_id = ? AND event_id > ?
                ORDER BY event_id ASC
                """,
                (evaluation_id, max(after_event_id, 0)),
            ).fetchall()
        return [
            {
                "id": int(row["event_id"]),
                "evaluation_id": row["evaluation_id"],
                "type": row["event_type"],
                "payload": self._event_payload(row["payload_json"]),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def require_owner(
        self, evaluation_id: str, owner_id: str
    ) -> dict[str, object]:
        record = self.get(evaluation_id)
        if record["owner_id"] != owner_id:
            # Do not disclose whether another team owns the identifier.
            raise EvaluationNotFound("Full Evaluation not found.")
        return record

    def transition(
        self,
        evaluation_id: str,
        *,
        expected_status: str,
        target_status: str,
        event_payload: dict[str, object] | None = None,
        system_message: str | None = None,
    ) -> dict[str, object]:
        validate_transition(expected_status, target_status)
        now = utc_now()
        values: dict[str, object | None] = {
            "updated_at": now,
            "system_message": system_message,
        }
        if target_status in {"preparing", "evaluating"}:
            values["started_at"] = now
        if target_status in {"completed", "cancelled", "system_error"}:
            values["finished_at"] = now
        assignments = ["status = ?", "updated_at = ?", "system_message = ?"]
        parameters: list[object | None] = [
            target_status,
            values["updated_at"],
            values["system_message"],
        ]
        if "started_at" in values:
            assignments.append("started_at = COALESCE(started_at, ?)")
            parameters.append(values["started_at"])
        if "finished_at" in values:
            assignments.append("finished_at = ?")
            parameters.append(values["finished_at"])
        parameters.extend((evaluation_id, expected_status))
        with self._transaction() as connection:
            cursor = connection.execute(
                f"""
                UPDATE full_evaluations
                SET {", ".join(assignments)}
                WHERE evaluation_id = ? AND status = ?
                """,
                parameters,
            )
            if cursor.rowcount != 1:
                current = connection.execute(
                    "SELECT status FROM full_evaluations WHERE evaluation_id = ?",
                    (evaluation_id,),
                ).fetchone()
                if current is None:
                    raise EvaluationNotFound("Full Evaluation not found.")
                raise EvaluationConflict(
                    "Evaluation status changed before this operation completed."
                )
            event_type = (
                "completed"
                if target_status == "completed"
                else "system_error"
                if target_status == "system_error"
                else "phase"
            )
            self._append_event(
                connection,
                evaluation_id,
                event_type,
                event_payload or {"status": target_status},
                now,
            )
            row = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
        return dict(row)

    def list_by_status(
        self,
        *statuses: str,
    ) -> list[dict[str, object]]:
        if not statuses:
            return []
        if any(status not in EVALUATION_STATUSES for status in statuses):
            raise EvaluationConflict("Evaluation status filter is invalid.")
        placeholders = ",".join("?" for _ in statuses)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT * FROM full_evaluations
                WHERE status IN ({placeholders})
                ORDER BY queued_at ASC, evaluation_id ASC
                """,
                statuses,
            ).fetchall()
        return [dict(row) for row in rows]

    def list_case_runs(
        self,
        evaluation_id: str,
    ) -> list[dict[str, object]]:
        self.get(evaluation_id)
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM evaluation_case_runs
                WHERE evaluation_id = ?
                ORDER BY case_ordinal ASC
                """,
                (evaluation_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _future_timestamp(seconds: int) -> str:
        return (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            + timedelta(seconds=max(seconds, 1))
        ).isoformat()

    def claim_case_run(
        self,
        *,
        worker_id: str,
        lease_seconds: int,
    ) -> dict[str, object] | None:
        """Atomically claim one queued or expired CaseRun.

        A reclaimed job receives a new attempt directory. The prior attempt is
        retained as evidence and is never overwritten.
        """
        worker_id = worker_id.strip()
        if not worker_id:
            raise EvaluationConflict("Worker identity is required.")
        if lease_seconds <= 0:
            raise EvaluationConflict("CaseRun lease must be positive.")
        now = utc_now()
        lease_until = self._future_timestamp(lease_seconds)
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT cr.*
                FROM evaluation_case_runs AS cr
                JOIN full_evaluations AS evaluation
                  ON evaluation.evaluation_id = cr.evaluation_id
                WHERE evaluation.status = 'evaluating'
                  AND (
                    (
                      cr.status = 'queued'
                      AND (
                        cr.retry_after IS NULL
                        OR cr.retry_after <= ?
                      )
                    )
                    OR
                    (
                      cr.status IN (
                        'agent_running',
                        'canonicalizing',
                        'final_validating'
                      )
                      AND cr.lease_until IS NOT NULL
                      AND cr.lease_until <= ?
                    )
                  )
                ORDER BY
                  evaluation.queued_at ASC,
                  cr.case_ordinal ASC
                LIMIT 1
                """,
                (now, now),
            ).fetchone()
            if row is None:
                return None
            cursor = connection.execute(
                """
                UPDATE evaluation_case_runs
                SET status = 'agent_running',
                    attempt_count = attempt_count + 1,
                    lease_owner = ?,
                    lease_until = ?,
                    heartbeat_at = ?,
                    retry_after = NULL,
                    started_at = COALESCE(started_at, ?),
                    finished_at = NULL,
                    updated_at = ?
                WHERE case_run_id = ?
                  AND (
                    (
                      status = 'queued'
                      AND (
                        retry_after IS NULL
                        OR retry_after <= ?
                      )
                    )
                    OR
                    (
                      status IN (
                        'agent_running',
                        'canonicalizing',
                        'final_validating'
                      )
                      AND lease_until IS NOT NULL
                      AND lease_until <= ?
                    )
                  )
                """,
                (
                    worker_id,
                    lease_until,
                    now,
                    now,
                    now,
                    row["case_run_id"],
                    now,
                    now,
                ),
            )
            if cursor.rowcount != 1:
                return None
            self._refresh_progress(
                connection,
                str(row["evaluation_id"]),
                now,
            )
            claimed = connection.execute(
                """
                SELECT * FROM evaluation_case_runs
                WHERE case_run_id = ?
                """,
                (row["case_run_id"],),
            ).fetchone()
        return dict(claimed)

    def register_worker(
        self,
        *,
        worker_id: str,
        concurrency: int,
        case_set_version: str,
        case_set_digest: str,
        runtime_image_digest: str,
        validator_image_digest: str,
        protocol_version: str,
        protocol_config_hash: str,
        isolation_mode: str,
    ) -> dict[str, object]:
        worker_id = worker_id.strip()
        if not worker_id:
            raise EvaluationConflict("Worker identity is required.")
        if concurrency <= 0:
            raise EvaluationConflict("Worker concurrency must be positive.")
        required = {
            "Case-set version": case_set_version,
            "Case-set digest": case_set_digest,
            "Agent runtime image digest": runtime_image_digest,
            "Validator image digest": validator_image_digest,
            "Evaluation protocol version": protocol_version,
            "Evaluation protocol hash": protocol_config_hash,
            "Validator isolation mode": isolation_mode,
        }
        missing = [label for label, value in required.items() if not value.strip()]
        if missing:
            raise EvaluationConflict(
                "Worker compatibility metadata is incomplete: "
                + ", ".join(missing)
            )
        now = utc_now()
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO evaluation_workers (
                    worker_id,
                    status,
                    concurrency,
                    case_set_version,
                    case_set_digest,
                    runtime_image_digest,
                    validator_image_digest,
                    protocol_version,
                    protocol_config_hash,
                    isolation_mode,
                    started_at,
                    heartbeat_at,
                    stopped_at,
                    updated_at
                ) VALUES (?, 'online', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?)
                ON CONFLICT(worker_id) DO UPDATE SET
                    status = 'online',
                    concurrency = excluded.concurrency,
                    case_set_version = excluded.case_set_version,
                    case_set_digest = excluded.case_set_digest,
                    runtime_image_digest = excluded.runtime_image_digest,
                    validator_image_digest = excluded.validator_image_digest,
                    protocol_version = excluded.protocol_version,
                    protocol_config_hash = excluded.protocol_config_hash,
                    isolation_mode = excluded.isolation_mode,
                    started_at = excluded.started_at,
                    heartbeat_at = excluded.heartbeat_at,
                    stopped_at = NULL,
                    updated_at = excluded.updated_at
                """,
                (
                    worker_id,
                    concurrency,
                    case_set_version,
                    case_set_digest,
                    runtime_image_digest,
                    validator_image_digest,
                    protocol_version,
                    protocol_config_hash,
                    isolation_mode,
                    now,
                    now,
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM evaluation_workers WHERE worker_id = ?",
                (worker_id,),
            ).fetchone()
        assert row is not None
        return dict(row)

    def heartbeat_worker(self, worker_id: str) -> bool:
        now = utc_now()
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE evaluation_workers
                SET heartbeat_at = ?,
                    updated_at = ?
                WHERE worker_id = ?
                  AND status = 'online'
                """,
                (now, now, worker_id),
            )
        return cursor.rowcount == 1

    def stop_worker(self, worker_id: str) -> bool:
        now = utc_now()
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE evaluation_workers
                SET status = 'stopped',
                    stopped_at = ?,
                    updated_at = ?
                WHERE worker_id = ?
                  AND status = 'online'
                """,
                (now, now, worker_id),
            )
        return cursor.rowcount == 1

    def worker_readiness(
        self,
        *,
        case_set_version: str,
        case_set_digest: str,
        runtime_image_digest: str,
        validator_image_digest: str,
        protocol_version: str,
        protocol_config_hash: str,
        isolation_mode: str,
        stale_after_seconds: int,
    ) -> dict[str, object]:
        if stale_after_seconds <= 0:
            raise EvaluationConflict(
                "Worker heartbeat expiry must be positive."
            )
        cutoff = (
            datetime.now(timezone.utc).replace(microsecond=0)
            - timedelta(seconds=stale_after_seconds)
        ).isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(*) AS worker_count,
                    COALESCE(SUM(concurrency), 0) AS capacity,
                    MAX(heartbeat_at) AS latest_heartbeat_at
                FROM evaluation_workers
                WHERE status = 'online'
                  AND heartbeat_at >= ?
                  AND case_set_version = ?
                  AND case_set_digest = ?
                  AND runtime_image_digest = ?
                  AND validator_image_digest = ?
                  AND protocol_version = ?
                  AND protocol_config_hash = ?
                  AND isolation_mode = ?
                """,
                (
                    cutoff,
                    case_set_version,
                    case_set_digest,
                    runtime_image_digest,
                    validator_image_digest,
                    protocol_version,
                    protocol_config_hash,
                    isolation_mode,
                ),
            ).fetchone()
        assert row is not None
        worker_count = int(row["worker_count"] or 0)
        return {
            "available": worker_count > 0,
            "worker_count": worker_count,
            "capacity": int(row["capacity"] or 0),
            "latest_heartbeat_at": row["latest_heartbeat_at"],
            "stale_after_seconds": stale_after_seconds,
        }

    def heartbeat_case_run(
        self,
        *,
        case_run_id: str,
        worker_id: str,
        lease_seconds: int,
    ) -> bool:
        """Extend a live lease without reviving an expired or reclaimed job."""
        now = utc_now()
        lease_until = self._future_timestamp(lease_seconds)
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE evaluation_case_runs
                SET lease_until = ?,
                    heartbeat_at = ?,
                    updated_at = ?
                WHERE case_run_id = ?
                  AND lease_owner = ?
                  AND status IN (
                    'agent_running',
                    'canonicalizing',
                    'final_validating'
                  )
                  AND lease_until > ?
                """,
                (
                    lease_until,
                    now,
                    now,
                    case_run_id,
                    worker_id,
                    now,
                ),
            )
        return cursor.rowcount == 1

    def complete_claim(
        self,
        *,
        case_run_id: str,
        worker_id: str,
        result: dict[str, object],
        result_internal_path: str,
        infrastructure_retry_limit: int,
        retry_backoff_seconds: int,
    ) -> dict[str, object]:
        """Persist one attempt and either score it or queue an infra retry."""
        status = str(result.get("status") or "")
        if status not in TERMINAL_CASE_RUN_STATUSES:
            raise EvaluationConflict("CaseRun result status is invalid.")
        if infrastructure_retry_limit < 0:
            raise EvaluationConflict(
                "Infrastructure retry limit must not be negative."
            )
        now = utc_now()
        with self._transaction() as connection:
            case_run = connection.execute(
                """
                SELECT * FROM evaluation_case_runs
                WHERE case_run_id = ?
                """,
                (case_run_id,),
            ).fetchone()
            if case_run is None:
                raise EvaluationNotFound("CaseRun not found.")
            if (
                case_run["lease_owner"] != worker_id
                or case_run["status"]
                not in {"agent_running", "canonicalizing", "final_validating"}
            ):
                raise EvaluationConflict(
                    "CaseRun lease is no longer owned by this Worker."
                )
            evaluation_id = str(case_run["evaluation_id"])
            attempt_count = int(case_run["attempt_count"])
            shared_values = (
                str(result.get("agent_status") or ""),
                (
                    str(result.get("validator_status"))
                    if result.get("validator_status") is not None
                    else None
                ),
                max(int(result.get("duration_seconds") or 0), 0),
                max(int(result.get("agent_duration_seconds") or 0), 0),
                max(int(result.get("build_duration_seconds") or 0), 0),
                max(int(result.get("build_attempts") or 0), 0),
                max(int(result.get("repair_size_bytes") or 0), 0),
                max(int(result.get("modified_files") or 0), 0),
                result_internal_path,
                str(result.get("message") or "")[:1000],
            )
            should_retry = (
                status == "infrastructure_error"
                and attempt_count <= infrastructure_retry_limit
            )
            if should_retry:
                delay = max(retry_backoff_seconds, 0) * (
                    2 ** max(attempt_count - 1, 0)
                )
                retry_after = (
                    self._future_timestamp(delay)
                    if delay > 0
                    else now
                )
                connection.execute(
                    """
                    UPDATE evaluation_case_runs
                    SET status = 'queued',
                        agent_status = ?,
                        validator_status = ?,
                        duration_seconds = ?,
                        agent_duration_seconds = ?,
                        build_duration_seconds = ?,
                        build_attempts = ?,
                        repair_size_bytes = ?,
                        modified_files = ?,
                        result_internal_path = ?,
                        message_internal = ?,
                        lease_owner = NULL,
                        lease_until = NULL,
                        heartbeat_at = NULL,
                        retry_after = ?,
                        updated_at = ?
                    WHERE case_run_id = ?
                    """,
                    (
                        *shared_values,
                        retry_after,
                        now,
                        case_run_id,
                    ),
                )
                connection.execute(
                    """
                    UPDATE full_evaluations
                    SET infrastructure_retries =
                            infrastructure_retries + 1,
                        updated_at = ?
                    WHERE evaluation_id = ?
                    """,
                    (now, evaluation_id),
                )
                action = "retry"
            else:
                connection.execute(
                    """
                    UPDATE evaluation_case_runs
                    SET status = ?,
                        agent_status = ?,
                        validator_status = ?,
                        duration_seconds = ?,
                        agent_duration_seconds = ?,
                        build_duration_seconds = ?,
                        build_attempts = ?,
                        repair_size_bytes = ?,
                        modified_files = ?,
                        result_internal_path = ?,
                        message_internal = ?,
                        lease_owner = NULL,
                        lease_until = NULL,
                        heartbeat_at = NULL,
                        retry_after = NULL,
                        finished_at = ?,
                        updated_at = ?
                    WHERE case_run_id = ?
                    """,
                    (
                        status,
                        *shared_values,
                        now,
                        now,
                        case_run_id,
                    ),
                )
                action = "terminal"
            self._refresh_progress(connection, evaluation_id, now)
            stored = connection.execute(
                """
                SELECT * FROM evaluation_case_runs
                WHERE case_run_id = ?
                """,
                (case_run_id,),
            ).fetchone()
        return {
            "action": action,
            "case_run": dict(stored),
        }

    def set_case_run_terminal(
        self,
        evaluation_id: str,
        case_ordinal: int,
        *,
        status: str,
        agent_status: str | None = None,
        validator_status: str | None = None,
        duration_seconds: int = 0,
    ) -> dict[str, object]:
        """Persist a terminal Case result; used by future Workers and tests."""
        if status not in TERMINAL_CASE_RUN_STATUSES:
            raise EvaluationConflict("CaseRun terminal status is invalid.")
        now = utc_now()
        with self._transaction() as connection:
            evaluation = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
            if evaluation is None:
                raise EvaluationNotFound("Full Evaluation not found.")
            if evaluation["status"] not in {"evaluating", "finalizing"}:
                raise EvaluationConflict(
                    "CaseRun result cannot be recorded in the current phase."
                )
            cursor = connection.execute(
                """
                UPDATE evaluation_case_runs
                SET status = ?,
                    agent_status = ?,
                    validator_status = ?,
                    duration_seconds = ?,
                    finished_at = ?,
                    updated_at = ?,
                    lease_owner = NULL,
                    lease_until = NULL
                WHERE evaluation_id = ?
                  AND case_ordinal = ?
                  AND status NOT IN (
                      'succeeded',
                      'failed',
                      'unresolvable',
                      'timeout',
                      'no_fix',
                      'agent_error',
                      'invalid_patch',
                      'infrastructure_error'
                  )
                """,
                (
                    status,
                    agent_status,
                    validator_status,
                    max(duration_seconds, 0),
                    now,
                    now,
                    evaluation_id,
                    case_ordinal,
                ),
            )
            if cursor.rowcount != 1:
                raise EvaluationConflict(
                    "CaseRun is missing or already has a terminal result."
                )
            self._refresh_progress(connection, evaluation_id, now)
            row = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
        return dict(row)

    def _refresh_progress(
        self,
        connection: sqlite3.Connection,
        evaluation_id: str,
        now: str,
    ) -> None:
        placeholders = ",".join("?" for _ in TERMINAL_CASE_RUN_STATUSES)
        terminal_parameters = tuple(sorted(TERMINAL_CASE_RUN_STATUSES))
        row = connection.execute(
            f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status IN ({placeholders}) THEN 1 ELSE 0 END)
                    AS completed,
                SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END)
                    AS succeeded,
                SUM(CASE WHEN status IN (
                    'agent_running', 'canonicalizing', 'final_validating'
                ) THEN 1 ELSE 0 END) AS running,
                SUM(CASE WHEN status = 'infrastructure_error' THEN 1 ELSE 0 END)
                    AS infrastructure_errors
            FROM evaluation_case_runs
            WHERE evaluation_id = ?
            """,
            (*terminal_parameters, evaluation_id),
        ).fetchone()
        completed = int(row["completed"] or 0)
        succeeded = int(row["succeeded"] or 0)
        running = int(row["running"] or 0)
        connection.execute(
            """
            UPDATE full_evaluations
            SET completed_cases = ?,
                successful_cases = ?,
                running_cases = ?,
                updated_at = ?
            WHERE evaluation_id = ?
            """,
            (completed, succeeded, running, now, evaluation_id),
        )
        self._append_event(
            connection,
            evaluation_id,
            "progress",
            {
                "completed_cases": completed,
                "successful_cases_hidden": True,
                "running_cases": running,
                "total_cases": int(row["total"]),
            },
            now,
        )

    def finalize(self, evaluation_id: str) -> dict[str, object]:
        """Freeze a complete score exactly once."""
        now = utc_now()
        with self._transaction() as connection:
            evaluation = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
            if evaluation is None:
                raise EvaluationNotFound("Full Evaluation not found.")
            if evaluation["status"] == "completed":
                return dict(evaluation)
            if evaluation["status"] != "finalizing":
                raise EvaluationConflict(
                    "Evaluation must be finalizing before its score is frozen."
                )
            rows = connection.execute(
                """
                SELECT status FROM evaluation_case_runs
                WHERE evaluation_id = ?
                """,
                (evaluation_id,),
            ).fetchall()
            statuses = [str(row["status"]) for row in rows]
            if len(statuses) != int(evaluation["total_cases"]):
                raise EvaluationConflict("Evaluation CaseRun set is incomplete.")
            if any(status == "infrastructure_error" for status in statuses):
                raise EvaluationConflict(
                    "Infrastructure errors must be resolved before finalization."
                )
            allowed = {"succeeded", *SCORED_FAILURE_CASE_RUN_STATUSES}
            if any(status not in allowed for status in statuses):
                raise EvaluationConflict(
                    "All CaseRuns must have scored terminal results."
                )
            succeeded = sum(status == "succeeded" for status in statuses)
            score = succeeded / len(statuses)
            cursor = connection.execute(
                """
                UPDATE full_evaluations
                SET status = 'completed',
                    completed_cases = total_cases,
                    successful_cases = ?,
                    running_cases = 0,
                    score = ?,
                    finished_at = ?,
                    updated_at = ?
                WHERE evaluation_id = ? AND status = 'finalizing'
                """,
                (succeeded, score, now, now, evaluation_id),
            )
            if cursor.rowcount != 1:
                raise EvaluationConflict(
                    "Evaluation changed before finalization completed."
                )
            self._append_event(
                connection,
                evaluation_id,
                "completed",
                {
                    "status": "completed",
                    "completed_cases": len(statuses),
                    "total_cases": len(statuses),
                },
                now,
            )
            row = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
        return dict(row)

    def audit(
        self,
        *,
        actor_id: str,
        actor_role: str,
        action: str,
        target_type: str,
        target_id: str,
        details: dict[str, object] | None = None,
    ) -> int:
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                INSERT INTO evaluation_audit_events (
                    actor_id,
                    actor_role,
                    action,
                    target_type,
                    target_id,
                    details_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    actor_id,
                    actor_role,
                    action,
                    target_type,
                    target_id,
                    json.dumps(
                        details or {},
                        ensure_ascii=False,
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                    utc_now(),
                ),
            )
        return int(cursor.lastrowid)

    def list_audit_events(
        self,
        *,
        target_type: str,
        target_id: str,
    ) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM evaluation_audit_events
                WHERE target_type = ? AND target_id = ?
                ORDER BY audit_id ASC
                """,
                (target_type, target_id),
            ).fetchall()
        result: list[dict[str, object]] = []
        for row in rows:
            item = dict(row)
            item["details"] = self._event_payload(str(item.pop("details_json")))
            result.append(item)
        return result

    def admin_detail(self, evaluation_id: str) -> dict[str, object]:
        record = self.get(evaluation_id)
        record["case_runs"] = self.list_case_runs(evaluation_id)
        record["audit_events"] = self.list_audit_events(
            target_type="evaluation",
            target_id=evaluation_id,
        )
        return record

    def recover_system_error(
        self,
        evaluation_id: str,
        *,
        actor_id: str,
    ) -> dict[str, object]:
        now = utc_now()
        with self._transaction() as connection:
            evaluation = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
            if evaluation is None:
                raise EvaluationNotFound("Full Evaluation not found.")
            if evaluation["status"] != "system_error":
                raise EvaluationConflict(
                    "Only a system_error Evaluation can be recovered."
                )
            connection.execute(
                """
                UPDATE evaluation_case_runs
                SET status = 'queued',
                    agent_status = NULL,
                    validator_status = NULL,
                    duration_seconds = NULL,
                    agent_duration_seconds = NULL,
                    build_duration_seconds = NULL,
                    build_attempts = NULL,
                    repair_size_bytes = NULL,
                    modified_files = NULL,
                    result_internal_path = NULL,
                    message_internal = NULL,
                    lease_owner = NULL,
                    lease_until = NULL,
                    heartbeat_at = NULL,
                    retry_after = NULL,
                    finished_at = NULL,
                    updated_at = ?
                WHERE evaluation_id = ?
                  AND status = 'infrastructure_error'
                """,
                (now, evaluation_id),
            )
            connection.execute(
                """
                UPDATE full_evaluations
                SET status = 'preparing',
                    running_cases = 0,
                    score = NULL,
                    system_message = NULL,
                    finished_at = NULL,
                    updated_at = ?
                WHERE evaluation_id = ? AND status = 'system_error'
                """,
                (now, evaluation_id),
            )
            self._append_event(
                connection,
                evaluation_id,
                "phase",
                {"status": "preparing", "recovered": True},
                now,
            )
            connection.execute(
                """
                INSERT INTO evaluation_audit_events (
                    actor_id, actor_role, action, target_type, target_id,
                    details_json, created_at
                ) VALUES (?, 'admin', 'recover', 'evaluation', ?, '{}', ?)
                """,
                (actor_id, evaluation_id, now),
            )
            row = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
        return dict(row)

    def publish_leaderboard(
        self,
        evaluation_id: str,
        *,
        team_name: str,
        actor_id: str,
    ) -> dict[str, object]:
        now = utc_now()
        entry_id = f"LB-{uuid.uuid4().hex[:16]}"
        with self._transaction() as connection:
            evaluation = connection.execute(
                "SELECT * FROM full_evaluations WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
            if evaluation is None:
                raise EvaluationNotFound("Full Evaluation not found.")
            if evaluation["status"] != "completed" or evaluation["score"] is None:
                raise EvaluationConflict(
                    "Only a completed Full Evaluation can be published."
                )
            existing = connection.execute(
                "SELECT * FROM leaderboard_entries WHERE evaluation_id = ?",
                (evaluation_id,),
            ).fetchone()
            if existing is not None:
                if existing["revoked_at"] is not None:
                    connection.execute(
                        """
                        UPDATE leaderboard_entries
                        SET revoked_at = NULL, published_at = ?, team_name = ?
                        WHERE evaluation_id = ?
                        """,
                        (now, team_name, evaluation_id),
                    )
                row = connection.execute(
                    "SELECT * FROM leaderboard_entries WHERE evaluation_id = ?",
                    (evaluation_id,),
                ).fetchone()
                return dict(row)
            started = str(
                evaluation["started_at"] or evaluation["queued_at"] or now
            )
            finished = str(evaluation["finished_at"] or now)
            try:
                duration = max(
                    int(
                        (
                            datetime.fromisoformat(finished)
                            - datetime.fromisoformat(started)
                        ).total_seconds()
                    ),
                    0,
                )
            except ValueError:
                duration = 0
            connection.execute(
                """
                INSERT INTO leaderboard_entries (
                    entry_id,
                    evaluation_id,
                    owner_id,
                    team_name,
                    agent_name,
                    agent_version,
                    score,
                    successful_cases,
                    total_cases,
                    duration_seconds,
                    case_set_version,
                    case_set_digest,
                    protocol_version,
                    protocol_config_hash,
                    published_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    evaluation_id,
                    evaluation["owner_id"],
                    team_name,
                    evaluation["agent_name"],
                    evaluation["agent_version"],
                    evaluation["score"],
                    evaluation["successful_cases"],
                    evaluation["total_cases"],
                    duration,
                    evaluation["case_set_version"],
                    evaluation["case_set_digest"],
                    evaluation["protocol_version"],
                    evaluation["protocol_config_hash"],
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO evaluation_audit_events (
                    actor_id, actor_role, action, target_type, target_id,
                    details_json, created_at
                ) VALUES (?, 'admin', 'publish_leaderboard', 'evaluation', ?,
                          ?, ?)
                """,
                (
                    actor_id,
                    evaluation_id,
                    json.dumps(
                        {"entry_id": entry_id},
                        separators=(",", ":"),
                        sort_keys=True,
                    ),
                    now,
                ),
            )
            row = connection.execute(
                "SELECT * FROM leaderboard_entries WHERE entry_id = ?",
                (entry_id,),
            ).fetchone()
        return dict(row)

    def revoke_leaderboard(
        self,
        evaluation_id: str,
        *,
        actor_id: str,
    ) -> None:
        now = utc_now()
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE leaderboard_entries SET revoked_at = ?
                WHERE evaluation_id = ? AND revoked_at IS NULL
                """,
                (now, evaluation_id),
            )
            if cursor.rowcount != 1:
                raise EvaluationNotFound("Published leaderboard entry not found.")
            connection.execute(
                """
                INSERT INTO evaluation_audit_events (
                    actor_id, actor_role, action, target_type, target_id,
                    details_json, created_at
                ) VALUES (?, 'admin', 'revoke_leaderboard', 'evaluation', ?,
                          '{}', ?)
                """,
                (actor_id, evaluation_id, now),
            )

    def leaderboard(
        self,
        *,
        case_set_version: str | None = None,
        protocol_version: str | None = None,
    ) -> list[dict[str, object]]:
        filters = ["revoked_at IS NULL"]
        parameters: list[object] = []
        if case_set_version:
            filters.append("case_set_version = ?")
            parameters.append(case_set_version)
        if protocol_version:
            filters.append("protocol_version = ?")
            parameters.append(protocol_version)
        where = " AND ".join(filters)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                WITH ranked AS (
                    SELECT *,
                           ROW_NUMBER() OVER (
                               PARTITION BY owner_id, case_set_version,
                                            protocol_version
                               ORDER BY score DESC,
                                        successful_cases DESC,
                                        duration_seconds ASC,
                                        published_at ASC
                           ) AS owner_rank
                    FROM leaderboard_entries
                    WHERE {where}
                )
                SELECT * FROM ranked
                WHERE owner_rank = 1
                ORDER BY score DESC,
                         successful_cases DESC,
                         duration_seconds ASC,
                         published_at ASC
                """,
                parameters,
            ).fetchall()
        result: list[dict[str, object]] = []
        for rank, row in enumerate(rows, start=1):
            item = dict(row)
            item.pop("owner_rank", None)
            item.pop("case_set_digest", None)
            item.pop("protocol_config_hash", None)
            item.pop("revoked_at", None)
            item["rank"] = rank
            result.append(item)
        return result

    def terminal_evaluations_before(
        self,
        finished_before: str,
    ) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT evaluation_id, status, finished_at
                FROM full_evaluations
                WHERE status IN ('completed', 'cancelled', 'system_error')
                  AND finished_at IS NOT NULL
                  AND finished_at < ?
                ORDER BY finished_at ASC
                """,
                (finished_before,),
            ).fetchall()
        return [dict(row) for row in rows]
