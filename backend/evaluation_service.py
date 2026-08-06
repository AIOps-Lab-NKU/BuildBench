"""Participant-safe Full Evaluation application service."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from backend.evaluation_models import (
    IDEMPOTENCY_KEY,
    TERMINAL_EVALUATION_STATUSES,
    EvaluationConfig,
    EvaluationConflict,
    EvaluationResultNotReady,
    EvaluationUnavailable,
    normalized_case_ids,
    stable_digest,
)
from backend.evaluation_store import EvaluationStore
from backend.submissions import SubmissionNotFound, SubmissionService


class EvaluationService:
    def __init__(
        self,
        store: EvaluationStore,
        submissions: SubmissionService,
        config: EvaluationConfig,
        team_member_resolver: Callable[[str], list[str]] | None = None,
    ):
        self.store = store
        self.submissions = submissions
        self.config = config
        self.team_member_resolver = team_member_resolver

    def readiness(self) -> dict[str, object]:
        error = self.config.readiness_error()
        worker = {
            "required": self.config.require_live_worker,
            "available": False,
            "worker_count": 0,
            "capacity": 0,
            "latest_heartbeat_at": None,
            "stale_after_seconds": self.config.worker_stale_seconds,
        }
        if error is None and self.config.require_live_worker:
            worker = self.store.worker_readiness(
                case_set_version=self.config.case_set_version,
                case_set_digest=self.config.case_set_digest,
                runtime_image_digest=self.config.runtime_image_digest,
                validator_image_digest=self.config.validator_image_digest,
                protocol_version=self.config.protocol_version,
                protocol_config_hash=self.config.protocol_config_hash,
                isolation_mode=self.config.validator_isolation,
                stale_after_seconds=self.config.worker_stale_seconds,
            )
            if not worker["available"]:
                error = (
                    "No compatible Full Evaluation Worker is currently "
                    "available. Please try again shortly."
                )
        return {
            "enabled": self.config.enabled,
            "ready": error is None,
            "message": error or "Full Evaluation is ready.",
            "worker": worker,
        }

    def create(
        self,
        submission_id: str,
        idempotency_key: str,
        owner_id: str | None = None,
    ) -> tuple[dict[str, object], bool]:
        readiness = self.readiness()
        if not readiness["ready"]:
            raise EvaluationUnavailable(str(readiness["message"]))
        if not IDEMPOTENCY_KEY.fullmatch(idempotency_key):
            raise EvaluationConflict(
                "Idempotency-Key must be 8-128 safe ASCII characters."
            )
        try:
            submission = self.submissions.store.get(submission_id)
        except SubmissionNotFound:
            raise
        owner = owner_id or self.config.owner_id
        # Direct service callers from the pre-authentication development API
        # remain compatible. HTTP callers always pass an authenticated owner.
        if owner_id is not None:
            self.submissions._require_owner(submission, owner)
        if submission.get("status") != "smoke_passed":
            raise EvaluationConflict(
                "Agent version must pass the Hosted Smoke Test first."
            )
        archive = (
            self.submissions.store.submission_dir(submission_id)
            / "agent-submission.zip"
        )
        if not archive.is_file():
            raise EvaluationUnavailable(
                "The immutable Agent archive is unavailable."
            )
        actual_sha = self._sha256(archive)
        expected_sha = str(submission.get("sha256") or "")
        if not expected_sha or actual_sha != expected_sha:
            raise EvaluationUnavailable(
                "The immutable Agent archive failed integrity verification."
            )
        agent = dict(submission.get("agent") or {})
        agent_name = str(agent.get("name") or "").strip()
        agent_version = str(agent.get("version") or "").strip()
        if not agent_name or not agent_version:
            raise EvaluationUnavailable(
                "The qualified Agent metadata is incomplete."
            )
        case_ids = normalized_case_ids(self.config.case_ids)
        request_hash = stable_digest(
            {
                "owner_id": owner,
                "submission_id": submission_id,
                "kind": "official",
            }
        )
        record, created = self.store.create(
            submission_id=submission_id,
            owner_id=owner,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
            submission_sha256=actual_sha,
            agent_name=agent_name,
            agent_version=agent_version,
            case_ids=case_ids,
            case_set_version=self.config.case_set_version,
            case_set_digest=self.config.case_set_digest,
            runtime_image_digest=self.config.runtime_image_digest,
            validator_image_digest=self.config.validator_image_digest,
            protocol_version=self.config.protocol_version,
            protocol_config_hash=self.config.protocol_config_hash,
            feedback_policy=self.config.feedback_policy,
        )
        return self._public(record), created

    def list(self, owner_id: str | None = None) -> list[dict[str, object]]:
        owner = owner_id or self.config.owner_id
        return [
            self._public(record)
            for record in self.store.list(owner)
        ]

    def get(
        self,
        evaluation_id: str,
        owner_id: str | None = None,
    ) -> dict[str, object]:
        owner = owner_id or self.config.owner_id
        record = self.store.require_owner(
            evaluation_id, owner
        )
        return self._public(record)

    def for_submission(
        self,
        submission_id: str,
        owner_id: str | None = None,
    ) -> dict[str, object] | None:
        owner = owner_id or self.config.owner_id
        record = self.store.get_for_submission(
            submission_id, owner
        )
        return self._public(record) if record else None

    def events(
        self,
        evaluation_id: str,
        after_event_id: int = 0,
        owner_id: str | None = None,
    ) -> list[dict[str, object]]:
        owner = owner_id or self.config.owner_id
        return self.store.events(
            evaluation_id,
            owner,
            after_event_id,
        )

    def result(
        self,
        evaluation_id: str,
        owner_id: str | None = None,
    ) -> dict[str, object]:
        owner = owner_id or self.config.owner_id
        record = self.store.require_owner(
            evaluation_id, owner
        )
        if record["status"] != "completed":
            raise EvaluationResultNotReady(
                "Full Evaluation result is not available yet."
            )
        return {
            "schema_version": "0.1",
            "evaluation_id": record["evaluation_id"],
            "status": "completed",
            "score": record["score"],
            "metric": "build_success_rate",
            "successful_cases": record["successful_cases"],
            "evaluated_cases": record["total_cases"],
            "finished_at": record["finished_at"],
            "case_set_version": record["case_set_version"],
            "protocol_version": record["protocol_version"],
        }

    def admin_detail(self, evaluation_id: str) -> dict[str, object]:
        return self.store.admin_detail(evaluation_id)

    def admin_recover(
        self,
        evaluation_id: str,
        *,
        actor_id: str,
    ) -> dict[str, object]:
        return self.store.recover_system_error(
            evaluation_id,
            actor_id=actor_id,
        )

    def admin_publish(
        self,
        evaluation_id: str,
        *,
        team_name: str,
        actor_id: str,
    ) -> dict[str, object]:
        return self.store.publish_leaderboard(
            evaluation_id,
            team_name=team_name,
            actor_id=actor_id,
        )

    def admin_revoke(
        self,
        evaluation_id: str,
        *,
        actor_id: str,
    ) -> None:
        self.store.revoke_leaderboard(
            evaluation_id,
            actor_id=actor_id,
        )

    def leaderboard(
        self,
        *,
        case_set_version: str | None = None,
        protocol_version: str | None = None,
    ) -> dict[str, object]:
        selected_case_set = case_set_version or self.config.case_set_version or None
        selected_protocol = (
            protocol_version or self.config.protocol_version or None
        )
        stored_entries = self.store.leaderboard(
            case_set_version=selected_case_set,
            protocol_version=selected_protocol,
        )
        entries = []
        for stored in stored_entries:
            owner_id = str(stored.get("owner_id", ""))
            entries.append(
                {
                    "rank": stored["rank"],
                    "team_name": stored["team_name"],
                    "members": (
                        self.team_member_resolver(owner_id)
                        if self.team_member_resolver and owner_id
                        else []
                    ),
                    "score": stored["score"],
                    "successful_cases": stored["successful_cases"],
                    "total_cases": stored["total_cases"],
                }
            )
        return {
            "schema_version": "0.1",
            "metric": "build_success_rate",
            "case_set_version": selected_case_set,
            "protocol_version": selected_protocol,
            "entries": entries,
        }

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _duration_seconds(record: dict[str, object]) -> int | None:
        start = record.get("started_at") or record.get("queued_at")
        end = record.get("finished_at")
        if not start:
            return None
        try:
            start_at = datetime.fromisoformat(str(start))
            end_at = datetime.fromisoformat(str(end)) if end else datetime.now(
                start_at.tzinfo
            )
        except ValueError:
            return None
        return max(int((end_at - start_at).total_seconds()), 0)

    def _public(self, record: dict[str, object]) -> dict[str, object]:
        completed = int(record.get("completed_cases") or 0)
        total = int(record.get("total_cases") or 0)
        progress = round((completed / total) * 100, 1) if total else 0.0
        status = str(record["status"])
        public: dict[str, object] = {
            "schema_version": "0.1",
            "evaluation_id": record["evaluation_id"],
            "submission_id": record["submission_id"],
            "status": status,
            "agent": {
                "name": record["agent_name"],
                "version": record["agent_version"],
            },
            "submission_sha256": str(record["submission_sha256"])[:12],
            "snapshot": {
                "case_set_version": record["case_set_version"],
                "runtime_image_digest": record["runtime_image_digest"],
                "validator_image_digest": record["validator_image_digest"],
                "protocol_version": record["protocol_version"],
                "feedback_policy": record["feedback_policy"],
            },
            "progress": {
                "completed": completed,
                "total": total,
                "percent": progress,
                "running": int(record.get("running_cases") or 0),
                "infrastructure_retries": int(
                    record.get("infrastructure_retries") or 0
                ),
            },
            "queued_at": record["queued_at"],
            "started_at": record.get("started_at"),
            "finished_at": record.get("finished_at"),
            "duration_seconds": self._duration_seconds(record),
            "score": (
                record.get("score")
                if status == "completed"
                else None
            ),
            "system_message": (
                record.get("system_message")
                if status in TERMINAL_EVALUATION_STATUSES
                else None
            ),
        }
        return public
