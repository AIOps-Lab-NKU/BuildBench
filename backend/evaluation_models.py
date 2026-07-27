"""Full Evaluation contracts shared by the API, store, and workers."""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from backend.security import validate_isolation_attestation


EVALUATION_ID = re.compile(r"^FE-[0-9]{8}T[0-9]{6}Z-[a-f0-9]{8}$")
CASE_RUN_ID = re.compile(r"^CR-[a-f0-9]{16}$")
IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,127}$")

EVALUATION_STATUSES = frozenset(
    {
        "queued",
        "preparing",
        "evaluating",
        "finalizing",
        "completed",
        "cancelled",
        "system_error",
    }
)
ACTIVE_EVALUATION_STATUSES = frozenset(
    {"queued", "preparing", "evaluating", "finalizing"}
)
TERMINAL_EVALUATION_STATUSES = frozenset(
    {"completed", "cancelled", "system_error"}
)

CASE_RUN_STATUSES = frozenset(
    {
        "queued",
        "agent_running",
        "canonicalizing",
        "final_validating",
        "succeeded",
        "failed",
        "unresolvable",
        "timeout",
        "no_fix",
        "agent_error",
        "invalid_patch",
        "infrastructure_error",
    }
)
TERMINAL_CASE_RUN_STATUSES = frozenset(
    {
        "succeeded",
        "failed",
        "unresolvable",
        "timeout",
        "no_fix",
        "agent_error",
        "invalid_patch",
        "infrastructure_error",
    }
)
SCORED_FAILURE_CASE_RUN_STATUSES = frozenset(
    {
        "failed",
        "unresolvable",
        "timeout",
        "no_fix",
        "agent_error",
        "invalid_patch",
    }
)

EVALUATION_TRANSITIONS: dict[str, frozenset[str]] = {
    "queued": frozenset({"preparing", "cancelled", "system_error"}),
    "preparing": frozenset({"evaluating", "cancelled", "system_error"}),
    "evaluating": frozenset({"finalizing", "cancelled", "system_error"}),
    "finalizing": frozenset({"completed", "cancelled", "system_error"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
    # Organizer recovery reuses the same evaluation_id.
    "system_error": frozenset({"preparing"}),
}


class EvaluationError(ValueError):
    """Base class for participant-safe Full Evaluation errors."""


class EvaluationNotFound(EvaluationError):
    pass


class EvaluationConflict(EvaluationError):
    pass


class EvaluationUnavailable(EvaluationError):
    pass


class EvaluationResultNotReady(EvaluationError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_evaluation_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"FE-{stamp}-{uuid.uuid4().hex[:8]}"


def new_case_run_id() -> str:
    return f"CR-{uuid.uuid4().hex[:16]}"


def stable_digest(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_transition(current: str, target: str) -> None:
    if current not in EVALUATION_TRANSITIONS:
        raise EvaluationConflict(f"unknown evaluation status: {current}")
    if target not in EVALUATION_TRANSITIONS[current]:
        raise EvaluationConflict(
            f"evaluation cannot transition from {current} to {target}"
        )


def normalized_case_ids(values: Iterable[str]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = raw.strip()
        if not value:
            continue
        if value in seen:
            raise EvaluationUnavailable("official Case set contains duplicates")
        seen.add(value)
        result.append(value)
    if not result:
        raise EvaluationUnavailable("official Case set is not configured")
    return tuple(result)


@dataclass(frozen=True)
class EvaluationConfig:
    """Organizer-controlled Full Evaluation configuration snapshot source."""

    enabled: bool = False
    owner_id: str = "development-team"
    case_ids: tuple[str, ...] = ()
    case_set_version: str = ""
    case_set_digest: str = ""
    runtime_image_digest: str = ""
    validator_image_digest: str = ""
    protocol_version: str = "0.1"
    protocol_config_hash: str = ""
    feedback_policy: str = "hidden"
    allow_unsafe_validator: bool = False
    validator_isolation: str = "unsafe_privileged"
    isolation_attestation: str = ""

    @classmethod
    def from_environment(cls, data_root: Path) -> "EvaluationConfig":
        raw_cases = os.environ.get("BB_CASE_SET_CASES", "")
        case_ids = tuple(
            value.strip() for value in raw_cases.split(",") if value.strip()
        )
        case_version = os.environ.get("BB_CASE_SET_VERSION", "")
        case_digest = os.environ.get("BB_CASE_SET_DIGEST", "")
        if case_ids and case_version and not case_digest:
            case_digest = stable_digest(
                {"version": case_version, "case_ids": case_ids}
            )
        protocol_version = os.environ.get("BB_EVALUATION_PROTOCOL_VERSION", "0.1")
        protocol_hash = os.environ.get("BB_EVALUATION_PROTOCOL_HASH", "")
        if not protocol_hash:
            protocol_hash = stable_digest(
                {
                    "version": protocol_version,
                    "case_timeout": os.environ.get(
                        "BB_CASE_TIMEOUT_SECONDS", "TBA"
                    ),
                    "build_attempt_limit": os.environ.get(
                        "BB_BUILD_ATTEMPT_LIMIT", "TBA"
                    ),
                }
            )
        return cls(
            enabled=os.environ.get("BB_FULL_EVALUATION_ENABLED", "0") == "1",
            owner_id=os.environ.get("BB_DEV_OWNER_ID", "development-team"),
            case_ids=case_ids,
            case_set_version=case_version,
            case_set_digest=case_digest,
            runtime_image_digest=os.environ.get(
                "BB_AGENT_RUNTIME_IMAGE_DIGEST", ""
            ),
            validator_image_digest=os.environ.get(
                "BB_VALIDATOR_IMAGE_DIGEST", ""
            ),
            protocol_version=protocol_version,
            protocol_config_hash=protocol_hash,
            feedback_policy=os.environ.get(
                "BB_EVALUATION_FEEDBACK_POLICY", "hidden"
            ),
            allow_unsafe_validator=(
                os.environ.get("BB_ALLOW_UNSAFE_VALIDATOR", "0") == "1"
            ),
            validator_isolation=os.environ.get(
                "BB_VALIDATOR_ISOLATION", "unsafe_privileged"
            ).strip(),
            isolation_attestation=os.environ.get(
                "BB_VALIDATOR_ISOLATION_ATTESTATION", ""
            ).strip(),
        )

    @property
    def database_path(self) -> Path | None:
        raw = os.environ.get("BB_EVALUATION_DB")
        return Path(raw) if raw else None

    def readiness_error(self) -> str | None:
        if not self.enabled:
            return "Full Evaluation is not enabled."
        if not self.owner_id.strip():
            return "Full Evaluation owner identity is not configured."
        try:
            normalized_case_ids(self.case_ids)
        except EvaluationUnavailable as error:
            return str(error)
        required = {
            "Case-set version": self.case_set_version,
            "Case-set digest": self.case_set_digest,
            "Agent runtime image digest": self.runtime_image_digest,
            "Validator image digest": self.validator_image_digest,
            "Evaluation protocol version": self.protocol_version,
            "Evaluation protocol hash": self.protocol_config_hash,
        }
        missing = [label for label, value in required.items() if not value.strip()]
        if missing:
            return "Full Evaluation configuration is incomplete: " + ", ".join(
                missing
            )
        if self.feedback_policy not in {"public_validation", "hidden"}:
            return "Full Evaluation feedback policy is invalid."
        isolation_error = validate_isolation_attestation(
            isolation_mode=self.validator_isolation,
            attestation_path=self.isolation_attestation,
            validator_image_digest=self.validator_image_digest,
            protocol_config_hash=self.protocol_config_hash,
        )
        if isolation_error and not self.allow_unsafe_validator:
            return isolation_error
        return None
