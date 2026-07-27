"""Durable Evaluation activation and exactly-once finalization."""

from __future__ import annotations

from collections.abc import Callable

from backend.evaluation_models import (
    SCORED_FAILURE_CASE_RUN_STATUSES,
    TERMINAL_CASE_RUN_STATUSES,
    EvaluationConflict,
)
from backend.evaluation_store import EvaluationStore


ResourcePreparer = Callable[[dict[str, object]], None]


class EvaluationScheduler:
    """Advance short lifecycle transitions outside the website process."""

    def __init__(
        self,
        store: EvaluationStore,
        resource_preparer: ResourcePreparer,
    ):
        self.store = store
        self.resource_preparer = resource_preparer

    def activate_ready(self) -> int:
        """Validate immutable resources, then make queued CaseRuns claimable."""
        activated = 0
        candidates = self.store.list_by_status("queued", "preparing")
        for candidate in candidates:
            evaluation_id = str(candidate["evaluation_id"])
            status = str(candidate["status"])
            try:
                if status == "queued":
                    candidate = self.store.transition(
                        evaluation_id,
                        expected_status="queued",
                        target_status="preparing",
                    )
                self.resource_preparer(candidate)
                self.store.transition(
                    evaluation_id,
                    expected_status="preparing",
                    target_status="evaluating",
                )
                activated += 1
            except EvaluationConflict:
                # Another Worker won the same compare-and-swap transition.
                continue
            except Exception:
                # Public records receive a stable message; detailed exceptions
                # belong in organizer logs, not participant responses.
                try:
                    self.store.transition(
                        evaluation_id,
                        expected_status="preparing",
                        target_status="system_error",
                        system_message=(
                            "Evaluation resources could not be prepared. "
                            "The organizers will review this run."
                        ),
                    )
                except EvaluationConflict:
                    pass
        return activated

    def finalize_ready(self) -> int:
        """Finalize complete Evaluations without releasing partial scores."""
        finalized = 0
        for evaluation in self.store.list_by_status(
            "evaluating",
            "finalizing",
        ):
            evaluation_id = str(evaluation["evaluation_id"])
            status = str(evaluation["status"])
            if status == "evaluating":
                case_runs = self.store.list_case_runs(evaluation_id)
                statuses = [str(item["status"]) for item in case_runs]
                if (
                    len(statuses) != int(evaluation["total_cases"])
                    or any(
                        item not in TERMINAL_CASE_RUN_STATUSES
                        for item in statuses
                    )
                ):
                    continue
                if "infrastructure_error" in statuses:
                    try:
                        self.store.transition(
                            evaluation_id,
                            expected_status="evaluating",
                            target_status="system_error",
                            system_message=(
                                "The platform could not complete every Case. "
                                "No partial score was published."
                            ),
                        )
                    except EvaluationConflict:
                        pass
                    continue
                allowed = {"succeeded", *SCORED_FAILURE_CASE_RUN_STATUSES}
                if any(item not in allowed for item in statuses):
                    continue
                try:
                    self.store.transition(
                        evaluation_id,
                        expected_status="evaluating",
                        target_status="finalizing",
                    )
                except EvaluationConflict:
                    continue
            try:
                self.store.finalize(evaluation_id)
                finalized += 1
            except EvaluationConflict:
                # A concurrent finalizer completed it or the Case set changed.
                continue
        return finalized

    def maintain(self) -> tuple[int, int]:
        return self.activate_ready(), self.finalize_ready()
