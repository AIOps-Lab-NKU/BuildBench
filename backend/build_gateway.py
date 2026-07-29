"""Capability-scoped build feedback for one active CaseRun."""

from __future__ import annotations

import hmac
import json
import os
import re
import secrets
import socket
import socketserver
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from backend.canonical_patch import (
    CanonicalPatchError,
    generate_canonical_patch,
    write_canonical_patch,
)


MAX_REQUEST_BYTES = 8 * 1024
MAX_LOG_CHARS = 12 * 1024
_CREDENTIAL_URL = re.compile(r"(?i)\bhttps?://[^/\s:@]+:[^/\s@]+@")
_TOKEN_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|authorization|token|password)\s*[:=]\s*\S+"
)


class BuildGatewayError(ValueError):
    pass


@dataclass(frozen=True)
class GatewayContext:
    original_case: Path
    worktree: Path
    output_root: Path
    allowed_prefixes: tuple[str, ...] = ("input/",)
    attempt_limit: int = 1


Validator = Callable[[Path, Path, Path], dict[str, object]]


def sanitize_log(
    text: str,
    *,
    sensitive_paths: tuple[Path, ...] = (),
    limit: int = MAX_LOG_CHARS,
) -> str:
    cleaned = text.replace("\x00", "")
    for path in sensitive_paths:
        value = str(path)
        if value:
            cleaned = cleaned.replace(value, "[internal-path]")
            cleaned = cleaned.replace(value.replace("\\", "/"), "[internal-path]")
    cleaned = _CREDENTIAL_URL.sub("https://[credential-redacted]@", cleaned)
    cleaned = _TOKEN_ASSIGNMENT.sub(r"\1=[redacted]", cleaned)
    if len(cleaned) > limit:
        cleaned = "[earlier output omitted]\n" + cleaned[-limit:]
    return cleaned


class BuildGateway:
    """Resolve build requests against a fixed, organizer-owned context."""

    def __init__(
        self,
        context: GatewayContext,
        validator: Validator,
        *,
        capability_token: str | None = None,
    ):
        if context.attempt_limit < 0:
            raise ValueError("attempt_limit must not be negative")
        self.context = context
        self.validator = validator
        self.capability_token = capability_token or secrets.token_urlsafe(32)
        self._attempts = 0
        self._lock = threading.Lock()

    @property
    def attempts(self) -> int:
        with self._lock:
            return self._attempts

    def _sensitive_paths(self) -> tuple[Path, ...]:
        """Cover both fixed work trees and their private per-job root."""

        return (
            self.context.original_case,
            self.context.worktree,
            self.context.output_root,
            self.context.original_case.parent,
            self.context.worktree.parent,
            self.context.output_root.parent,
        )

    def handle(
        self, request: object, *, capability_token: str
    ) -> dict[str, object]:
        if not hmac.compare_digest(capability_token, self.capability_token):
            raise BuildGatewayError("invalid build capability")
        if not isinstance(request, dict) or set(request) != {"action"}:
            raise BuildGatewayError(
                "build request must contain only action"
            )
        if request["action"] != "build":
            raise BuildGatewayError("unsupported build action")

        with self._lock:
            if self._attempts >= self.context.attempt_limit:
                return {
                    "schema_version": "0.1",
                    "ok": False,
                    "error": "attempt_limit_exceeded",
                    "attempt": self._attempts,
                    "attempt_limit": self.context.attempt_limit,
                }
            self._attempts += 1
            attempt = self._attempts

        attempt_root = self.context.output_root / f"attempt-{attempt:02d}"
        patch_path = attempt_root / "repair.diff"
        result_root = attempt_root / "validator"
        try:
            patch = generate_canonical_patch(
                self.context.original_case,
                self.context.worktree,
                allowed_prefixes=self.context.allowed_prefixes,
            )
            write_canonical_patch(patch_path, patch)
        except (OSError, UnicodeError, CanonicalPatchError) as error:
            return {
                "schema_version": "0.1",
                "ok": True,
                "attempt": attempt,
                "attempt_limit": self.context.attempt_limit,
                "status": "invalid_patch",
                "message": sanitize_log(
                    str(error),
                    sensitive_paths=self._sensitive_paths(),
                ),
                "log_excerpt": "",
            }

        result = self.validator(
            self.context.original_case,
            patch_path,
            result_root,
        )
        log_path = result_root / "build.log"
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            log_text = ""
        return {
            "schema_version": "0.1",
            "ok": True,
            "attempt": attempt,
            "attempt_limit": self.context.attempt_limit,
            "status": str(result.get("status") or "infrastructure_error"),
            "message": sanitize_log(
                str(result.get("message") or ""),
                sensitive_paths=self._sensitive_paths(),
            ),
            "log_excerpt": sanitize_log(
                log_text,
                sensitive_paths=self._sensitive_paths(),
            ),
        }


class _GatewayRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES or not raw.endswith(b"\n"):
            response = {"ok": False, "error": "invalid_request"}
        else:
            try:
                payload = json.loads(raw.decode("utf-8"))
                if not isinstance(payload, dict):
                    raise BuildGatewayError("request must be an object")
                token = payload.pop("capability_token", "")
                response = self.server.gateway.handle(  # type: ignore[attr-defined]
                    payload,
                    capability_token=str(token),
                )
            except (
                BuildGatewayError,
                UnicodeError,
                json.JSONDecodeError,
            ) as error:
                response = {
                    "schema_version": "0.1",
                    "ok": False,
                    "error": "invalid_request",
                    "message": sanitize_log(str(error), limit=500),
                }
        try:
            self.wfile.write(
                json.dumps(response, separators=(",", ":")).encode("utf-8")
                + b"\n"
            )
        except (BrokenPipeError, ConnectionResetError):
            # The Agent may hit its own wall-time while a build is finishing.
            pass


if hasattr(socketserver, "UnixStreamServer"):
    class _UnixServer(  # type: ignore[misc]
        socketserver.ThreadingMixIn,
        socketserver.UnixStreamServer,  # type: ignore[attr-defined]
    ):
        daemon_threads = True

        def __init__(self, path: str, gateway: BuildGateway):
            self.gateway = gateway
            super().__init__(path, _GatewayRequestHandler)
else:
    class _UnixServer:  # type: ignore[no-redef]
        def __init__(self, path: str, gateway: BuildGateway):
            del path, gateway
            raise RuntimeError("Unix Build Gateway requires a Linux worker")


class UnixBuildGatewayServer:
    """Expose a per-Case gateway through a Unix socket on Linux workers."""

    def __init__(self, gateway: BuildGateway, socket_path: Path):
        self.gateway = gateway
        self.socket_path = socket_path
        self._server: _UnixServer | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> "UnixBuildGatewayServer":
        if not hasattr(socket, "AF_UNIX") or os.name == "nt":
            raise RuntimeError("Unix Build Gateway requires a Linux worker")
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        self.socket_path.unlink(missing_ok=True)
        self._server = _UnixServer(str(self.socket_path), self.gateway)
        os.chmod(self.socket_path, 0o660)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="bb-build-gateway",
            daemon=True,
        )
        self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self.socket_path.unlink(missing_ok=True)
