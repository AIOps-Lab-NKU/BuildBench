"""Authentication and production isolation gates for Build-Bench."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


class AuthenticationError(ValueError):
    """A participant-safe authentication or authorization failure."""


@dataclass(frozen=True)
class RequestIdentity:
    owner_id: str
    team_id: str
    display_name: str
    role: str = "participant"
    authentication_method: str = "bearer"
    session_id: str = ""

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class TokenAuthenticator:
    """Small bearer-token provider suitable for the one-server MVP.

    Production deployments should place the website behind TLS and may replace
    this provider with an OIDC-aware reverse proxy. Raw tokens are never
    returned to application callers or written to audit events.
    """

    def __init__(
        self,
        identities: dict[str, RequestIdentity] | None = None,
        *,
        required: bool = False,
        development_identity: RequestIdentity | None = None,
    ):
        self._identities = dict(identities or {})
        self.required = required
        self.development_identity = development_identity or RequestIdentity(
            owner_id="development-team",
            team_id="development-team",
            display_name="Development Team",
            authentication_method="development",
        )
        if required and not self._identities:
            raise ValueError("authentication is required but no tokens are configured")

    @classmethod
    def from_environment(cls, default_owner_id: str) -> "TokenAuthenticator":
        required = os.environ.get("BB_AUTH_REQUIRED", "0") == "1"
        raw = os.environ.get("BB_AUTH_TOKENS_JSON", "").strip()
        token_file = os.environ.get("BB_AUTH_TOKENS_FILE", "").strip()
        if raw and token_file:
            raise ValueError(
                "configure BB_AUTH_TOKENS_JSON or BB_AUTH_TOKENS_FILE, not both"
            )
        if token_file:
            raw = Path(token_file).read_text(encoding="utf-8")
        identities: dict[str, RequestIdentity] = {}
        if raw:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("authentication token configuration must be an object")
            for token, value in payload.items():
                if not isinstance(token, str) or len(token) < 24:
                    raise ValueError("configured bearer tokens must be at least 24 chars")
                if not isinstance(value, dict):
                    raise ValueError("authentication identity must be an object")
                owner_id = str(value.get("owner_id") or "").strip()
                team_id = str(value.get("team_id") or owner_id).strip()
                display_name = str(
                    value.get("display_name") or team_id or owner_id
                ).strip()
                role = str(value.get("role") or "participant").strip()
                if not owner_id or not team_id or role not in {
                    "participant",
                    "admin",
                }:
                    raise ValueError("authentication identity is invalid")
                identities[token] = RequestIdentity(
                    owner_id=owner_id,
                    team_id=team_id,
                    display_name=display_name,
                    role=role,
                )
        development = RequestIdentity(
            owner_id=default_owner_id,
            team_id=default_owner_id,
            display_name=os.environ.get(
                "BB_DEV_TEAM_NAME", "Development Team"
            ).strip()
            or "Development Team",
            authentication_method="development",
        )
        return cls(
            identities,
            required=required,
            development_identity=development,
        )

    def authenticate(
        self,
        authorization: str | None,
        *,
        require_admin: bool = False,
    ) -> RequestIdentity:
        header = (authorization or "").strip()
        if not header:
            if self.required:
                raise AuthenticationError("Authentication is required.")
            identity = self.development_identity
        else:
            scheme, separator, token = header.partition(" ")
            if not separator or scheme.lower() != "bearer" or not token.strip():
                raise AuthenticationError("Use a Bearer token.")
            candidate = token.strip()
            identity = None
            for configured, configured_identity in self._identities.items():
                if hmac.compare_digest(configured, candidate):
                    identity = configured_identity
            if identity is None:
                raise AuthenticationError("Authentication failed.")
        if require_admin and not identity.is_admin:
            raise AuthenticationError("Administrator authorization is required.")
        return identity


SAFE_VALIDATOR_ISOLATION_MODES = frozenset(
    {"dedicated_vm", "ephemeral_vm", "confidential_vm"}
)


def validate_isolation_attestation(
    *,
    isolation_mode: str,
    attestation_path: str | Path | None,
    validator_image_digest: str,
    protocol_config_hash: str,
    launcher_image_digest: str = "",
    guest_image_sha256: str = "",
) -> str | None:
    """Return a readiness error, or None for a valid production attestation."""

    if isolation_mode not in SAFE_VALIDATOR_ISOLATION_MODES:
        return (
            "Validator isolation must use a dedicated disposable VM/Worker "
            "before untrusted official evaluation is enabled."
        )
    if not attestation_path:
        return "Validator isolation attestation is not configured."
    path = Path(attestation_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return "Validator isolation attestation cannot be verified."
    if not isinstance(payload, dict):
        return "Validator isolation attestation is invalid."
    required = {
        "schema_version": "0.2",
        "isolation_mode": isolation_mode,
        "provider": "qemu_kvm",
        "validator_image_digest": validator_image_digest,
        "protocol_config_hash": protocol_config_hash,
        "launcher_image_digest": launcher_image_digest,
        "guest_image_sha256": guest_image_sha256,
        "kvm_acceleration": True,
        "docker_socket_exposed_to_agent": False,
        "host_docker_socket_mounted_in_worker": False,
        "hidden_case_store_mounted_in_validator_vm": False,
        "worker_reused_between_cases": False,
        "worker_overlay_discarded": True,
        "job_input_scope": "single_case",
        "output_scope": "dedicated_directory",
        "network_mode": "none",
    }
    if not launcher_image_digest or not guest_image_sha256:
        return "Validator isolation runtime identity is incomplete."
    for key, expected in required.items():
        if payload.get(key) != expected:
            return f"Validator isolation attestation does not match {key}."
    approved_by = str(payload.get("approved_by") or "").strip()
    approved_at = str(payload.get("approved_at") or "").strip()
    expires_at = str(payload.get("expires_at") or "").strip()
    if not approved_by or not approved_at or not expires_at:
        return "Validator isolation attestation approval metadata is incomplete."
    try:
        expires = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return "Validator isolation attestation expiry is invalid."
    if expires <= datetime.now(timezone.utc):
        return "Validator isolation attestation has expired."
    expected_digest = str(payload.get("document_sha256") or "").strip()
    unsigned = dict(payload)
    unsigned.pop("document_sha256", None)
    actual_digest = hashlib.sha256(
        json.dumps(
            unsigned,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    if not expected_digest or not hmac.compare_digest(
        expected_digest, actual_digest
    ):
        return "Validator isolation attestation digest is invalid."
    return None
