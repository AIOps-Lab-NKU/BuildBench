from __future__ import annotations

import argparse
import json
import os
import re
import time
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from backend.account_store import (
    AccountConflict,
    AccountError,
    AccountLocked,
    AccountNotFound,
    AccountStore,
    AccountValidationError,
    DEFAULT_COMPETITION_ID,
)
from backend.auth_service import (
    AuthConflict,
    AuthError,
    AuthRateLimited,
    AuthService,
    AuthValidationError,
    HybridAuthenticator,
    InvalidCredentials,
)
from backend.evaluation_models import (
    TERMINAL_EVALUATION_STATUSES,
    EvaluationConfig,
    EvaluationConflict,
    EvaluationNotFound,
    EvaluationResultNotReady,
    EvaluationUnavailable,
)
from backend.evaluation_service import EvaluationService
from backend.evaluation_store import EvaluationStore
from backend.security import (
    AuthenticationError,
    RequestIdentity,
    TokenAuthenticator,
)
from backend.submissions import (
    ArchiveLimits,
    Checker,
    HostedSmokeQueue,
    SmokeRunner,
    SubmissionConflict,
    SubmissionError,
    SubmissionNotFound,
    SubmissionService,
    SubmissionStore,
)


DETAIL_ROUTE = re.compile(r"^/api/submissions/([^/]+)$")
LOG_ROUTE = re.compile(r"^/api/submissions/([^/]+)/log$")
SMOKE_ROUTE = re.compile(r"^/api/submissions/([^/]+)/smoke-test$")
EVALUATION_CREATE_ROUTE = re.compile(
    r"^/api/submissions/([^/]+)/full-evaluations$"
)
EVALUATION_DETAIL_ROUTE = re.compile(r"^/api/full-evaluations/([^/]+)$")
EVALUATION_EVENTS_ROUTE = re.compile(
    r"^/api/full-evaluations/([^/]+)/events$"
)
EVALUATION_RESULT_ROUTE = re.compile(
    r"^/api/full-evaluations/([^/]+)/result$"
)
ADMIN_EVALUATION_ROUTE = re.compile(
    r"^/api/admin/full-evaluations/([^/]+)$"
)
ADMIN_EVALUATION_ACTION_ROUTE = re.compile(
    r"^/api/admin/full-evaluations/([^/]+)/(recover|publish|revoke)$"
)
TEAM_MEMBER_ROUTE = re.compile(r"^/api/team/members/([^/]+)$")
BLOCKED_STATIC_PREFIXES = (
    "/backend/",
    "/runtime-data/",
    "/.git/",
    "/.planning/",
)


class BuildBenchHandler(SimpleHTTPRequestHandler):
    server_version = "BuildBenchCompetition/0.1"

    @property
    def service(self) -> SubmissionService:
        return self.server.submission_service  # type: ignore[attr-defined]

    @property
    def smoke_queue(self) -> HostedSmokeQueue:
        return self.server.smoke_queue  # type: ignore[attr-defined]

    @property
    def evaluation_service(self) -> EvaluationService:
        return self.server.evaluation_service  # type: ignore[attr-defined]

    @property
    def max_upload_bytes(self) -> int:
        return self.server.max_upload_bytes  # type: ignore[attr-defined]

    @property
    def authenticator(self) -> HybridAuthenticator:
        return self.server.authenticator  # type: ignore[attr-defined]

    @property
    def auth_service(self) -> AuthService:
        return self.server.auth_service  # type: ignore[attr-defined]

    @property
    def account_store(self) -> AccountStore:
        return self.server.account_store  # type: ignore[attr-defined]

    def _identity(
        self,
        *,
        admin: bool = False,
        csrf: bool = False,
    ) -> RequestIdentity | None:
        try:
            identity = self.authenticator.authenticate(
                self.headers.get("Authorization"),
                self.headers.get("Cookie"),
                require_admin=admin,
            )
            if csrf and identity.authentication_method == "session":
                self.auth_service.verify_csrf(
                    self.headers.get("Cookie"),
                    self.headers.get("X-CSRF-Token"),
                )
            return identity
        except AuthenticationError as error:
            self._error(
                (
                    HTTPStatus.FORBIDDEN
                    if admin or csrf
                    else HTTPStatus.UNAUTHORIZED
                ),
                str(error),
            )
            return None

    def _json(
        self,
        status: int,
        payload: object,
        *,
        headers: dict[str, str] | None = None,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def _text(
        self,
        status: int,
        content: str,
        filename: str | None = None,
    ) -> None:
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if filename:
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"',
            )
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(
        self,
        *,
        maximum: int = 64 * 1024,
    ) -> dict[str, object] | None:
        if self.headers.get_content_type() != "application/json":
            self._error(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "Content-Type must be application/json.",
            )
            return None
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._error(
                HTTPStatus.LENGTH_REQUIRED,
                "Content-Length is required.",
            )
            return None
        if length <= 0:
            self._error(HTTPStatus.BAD_REQUEST, "JSON body is required.")
            return None
        if length > maximum:
            self._error(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "JSON request is too large.",
            )
            return None
        try:
            payload = json.loads(self.rfile.read(length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._error(HTTPStatus.BAD_REQUEST, "Request body is not valid JSON.")
            return None
        if not isinstance(payload, dict):
            self._error(HTTPStatus.BAD_REQUEST, "JSON body must be an object.")
            return None
        return payload

    @staticmethod
    def _public_auth_result(
        result: dict[str, object],
    ) -> dict[str, object]:
        return {
            key: value
            for key, value in result.items()
            if not key.startswith("_")
        }

    def _require_auth_request_origin(self) -> bool:
        if self.headers.get("Sec-Fetch-Site", "").casefold() == "cross-site":
            self._error(HTTPStatus.FORBIDDEN, "Cross-site request rejected.")
            return False
        origin = self.headers.get("Origin", "").strip()
        host = self.headers.get("Host", "").strip().casefold()
        if origin:
            parsed = urlparse(origin)
            if parsed.scheme not in {"http", "https"} or parsed.netloc.casefold() != host:
                self._error(HTTPStatus.FORBIDDEN, "Request origin rejected.")
                return False
        return True

    def _auth_error(self, error: Exception) -> None:
        if isinstance(error, AuthRateLimited):
            self._error(HTTPStatus.TOO_MANY_REQUESTS, str(error))
        elif isinstance(error, (AuthConflict, AccountConflict, AccountLocked)):
            self._error(HTTPStatus.CONFLICT, str(error))
        elif isinstance(error, (AuthValidationError, AccountValidationError)):
            self._error(HTTPStatus.BAD_REQUEST, str(error))
        elif isinstance(error, (InvalidCredentials, AuthenticationError)):
            self._error(HTTPStatus.UNAUTHORIZED, str(error))
        elif isinstance(error, AccountNotFound):
            self._error(HTTPStatus.NOT_FOUND, str(error))
        else:
            self._error(HTTPStatus.BAD_REQUEST, str(error))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/health":
            evaluation = self.evaluation_service.readiness()
            worker = dict(evaluation.get("worker") or {})
            self._json(
                HTTPStatus.OK,
                {
                    "status": "ok",
                    "api_version": "0.1",
                    "starter_kit": str(self.service.starter_kit),
                    "starter_kit_available": (
                        self.service.starter_kit / "bb"
                    ).is_file(),
                    "smoke_test_available": (
                        self.service.starter_kit / "bb"
                    ).is_file(),
                    "full_evaluation_enabled": evaluation["enabled"],
                    "full_evaluation_ready": evaluation["ready"],
                    "full_evaluation_message": evaluation["message"],
                    "full_evaluation_worker_available": bool(
                        worker.get("available")
                    ),
                    "full_evaluation_worker_count": int(
                        worker.get("worker_count") or 0
                    ),
                    "full_evaluation_worker_capacity": int(
                        worker.get("capacity") or 0
                    ),
                    "full_evaluation_worker_heartbeat_at": worker.get(
                        "latest_heartbeat_at"
                    ),
                },
            )
            return
        if path == "/api/leaderboard":
            query = parse_qs(parsed.query)
            self._json(
                HTTPStatus.OK,
                self.evaluation_service.leaderboard(
                    case_set_version=query.get("case_set_version", [None])[0],
                    protocol_version=query.get("protocol_version", [None])[0],
                ),
            )
            return
        if path == "/api/auth/me":
            try:
                self._json(
                    HTTPStatus.OK,
                    self.auth_service.me(self.headers.get("Cookie")),
                )
            except AuthenticationError as error:
                self._error(HTTPStatus.UNAUTHORIZED, str(error))
            return
        match = ADMIN_EVALUATION_ROUTE.fullmatch(path)
        if match:
            if self._identity(admin=True) is None:
                return
            try:
                self._json(
                    HTTPStatus.OK,
                    self.evaluation_service.admin_detail(
                        unquote(match.group(1))
                    ),
                )
            except EvaluationNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            return
        identity: RequestIdentity | None = None
        if path.startswith("/api/"):
            identity = self._identity()
            if identity is None:
                return
        if path == "/api/team":
            try:
                self._json(
                    HTTPStatus.OK,
                    self.account_store.context_for_user(
                        identity.owner_id
                    )["team"],
                )
            except AccountError as error:
                self._auth_error(error)
            return
        if path == "/api/submissions":
            self._json(
                HTTPStatus.OK,
                {"submissions": self.service.list(identity.team_id)},
            )
            return
        if path == "/api/full-evaluations":
            self._json(
                HTTPStatus.OK,
                {
                    "evaluations": self.evaluation_service.list(
                        identity.team_id
                    )
                },
            )
            return
        match = EVALUATION_EVENTS_ROUTE.fullmatch(path)
        if match:
            self._evaluation_events(
                unquote(match.group(1)),
                parse_qs(parsed.query),
            )
            return
        match = EVALUATION_RESULT_ROUTE.fullmatch(path)
        if match:
            try:
                self._json(
                    HTTPStatus.OK,
                    self.evaluation_service.result(
                        unquote(match.group(1)), identity.team_id
                    ),
                )
            except EvaluationNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            except EvaluationResultNotReady as error:
                self._error(HTTPStatus.CONFLICT, str(error))
            return
        match = EVALUATION_DETAIL_ROUTE.fullmatch(path)
        if match:
            try:
                self._json(
                    HTTPStatus.OK,
                    self.evaluation_service.get(
                        unquote(match.group(1)), identity.team_id
                    ),
                )
            except EvaluationNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            return
        match = LOG_ROUTE.fullmatch(path)
        if match:
            try:
                filename, content = self.service.log_text(
                    unquote(match.group(1)), identity.team_id
                )
                download = parse_qs(parsed.query).get("download") == ["1"]
                self._text(
                    HTTPStatus.OK,
                    content,
                    filename=filename if download else None,
                )
            except SubmissionNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            return
        match = DETAIL_ROUTE.fullmatch(path)
        if match:
            try:
                self._json(
                    HTTPStatus.OK,
                    self.service.get(
                        unquote(match.group(1)), identity.team_id
                    ),
                )
            except SubmissionNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            return
        if path.startswith("/api/"):
            self._error(HTTPStatus.NOT_FOUND, "API route not found")
            return
        if path == "/":
            self.path = "/index.html"
        if any(path.startswith(prefix) for prefix in BLOCKED_STATIC_PREFIXES):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path in {"/api/auth/register", "/api/auth/login"}:
            if not self._require_auth_request_origin():
                return
            payload = self._read_json_body()
            if payload is None:
                return
            try:
                if path.endswith("/register"):
                    result = self.auth_service.register(
                        payload,
                        client_ip=self.client_address[0],
                    )
                    status = HTTPStatus.CREATED
                else:
                    result = self.auth_service.login(
                        payload,
                        client_ip=self.client_address[0],
                    )
                    status = HTTPStatus.OK
                self._json(
                    status,
                    self._public_auth_result(result),
                    headers={
                        "Set-Cookie": self.auth_service.set_cookie_header(
                            str(result["_session_token"])
                        )
                    },
                )
            except (AuthError, AccountError) as error:
                self._auth_error(error)
            return
        match = ADMIN_EVALUATION_ACTION_ROUTE.fullmatch(path)
        if match:
            identity = self._identity(admin=True)
            if identity is None:
                return
            self._admin_evaluation_action(
                unquote(match.group(1)),
                match.group(2),
                identity,
            )
            return
        identity = self._identity(csrf=True)
        if identity is None:
            return
        if path == "/api/auth/logout":
            self.auth_service.logout(self.headers.get("Cookie"))
            self._json(
                HTTPStatus.OK,
                {"status": "signed_out"},
                headers={
                    "Set-Cookie": self.auth_service.clear_cookie_header()
                },
            )
            return
        if path == "/api/team/members":
            payload = self._read_json_body()
            if payload is None:
                return
            try:
                member = self.account_store.add_member(
                    user_id=identity.owner_id,
                    team_id=identity.team_id,
                    member=payload,
                )
                self._json(HTTPStatus.CREATED, member)
            except AccountError as error:
                self._auth_error(error)
            return
        if path == "/api/submissions":
            self._upload_submission(identity)
            return
        match = SMOKE_ROUTE.fullmatch(path)
        if match:
            try:
                record = self.smoke_queue.request(
                    unquote(match.group(1)), identity.team_id
                )
                self._json(HTTPStatus.ACCEPTED, record)
            except SubmissionNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            except SubmissionConflict as error:
                self._error(HTTPStatus.CONFLICT, str(error))
            return
        match = EVALUATION_CREATE_ROUTE.fullmatch(path)
        if match:
            self._create_evaluation(unquote(match.group(1)), identity)
            return
        self._error(HTTPStatus.NOT_FOUND, "API route not found")

    def do_PATCH(self) -> None:
        path = urlparse(self.path).path
        identity = self._identity(csrf=True)
        if identity is None:
            return
        payload = self._read_json_body()
        if payload is None:
            return
        try:
            if path == "/api/team":
                self._json(
                    HTTPStatus.OK,
                    self.account_store.update_team_name(
                        user_id=identity.owner_id,
                        team_id=identity.team_id,
                        name=payload.get("name"),
                    ),
                )
                return
            match = TEAM_MEMBER_ROUTE.fullmatch(path)
            if match:
                self._json(
                    HTTPStatus.OK,
                    self.account_store.update_member(
                        user_id=identity.owner_id,
                        team_id=identity.team_id,
                        member_id=unquote(match.group(1)),
                        member=payload,
                    ),
                )
                return
        except AccountError as error:
            self._auth_error(error)
            return
        self._error(HTTPStatus.NOT_FOUND, "API route not found")

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        identity = self._identity(csrf=True)
        if identity is None:
            return
        match = TEAM_MEMBER_ROUTE.fullmatch(path)
        if match:
            try:
                self.account_store.delete_member(
                    user_id=identity.owner_id,
                    team_id=identity.team_id,
                    member_id=unquote(match.group(1)),
                )
                self._json(HTTPStatus.OK, {"status": "deleted"})
            except AccountError as error:
                self._auth_error(error)
            return
        self._error(HTTPStatus.NOT_FOUND, "API route not found")

    def _create_evaluation(
        self,
        submission_id: str,
        identity: RequestIdentity,
    ) -> None:
        idempotency_key = self.headers.get("Idempotency-Key", "").strip()
        if not idempotency_key:
            self._error(
                HTTPStatus.BAD_REQUEST,
                "Idempotency-Key is required.",
            )
            return
        try:
            record, created = self.evaluation_service.create(
                submission_id,
                idempotency_key,
                identity.team_id,
            )
            self._json(
                HTTPStatus.CREATED if created else HTTPStatus.OK,
                record,
            )
        except SubmissionNotFound as error:
            self._error(HTTPStatus.NOT_FOUND, str(error))
        except EvaluationConflict as error:
            self._error(HTTPStatus.CONFLICT, str(error))
        except EvaluationUnavailable as error:
            self._error(HTTPStatus.SERVICE_UNAVAILABLE, str(error))

    def _evaluation_events(
        self,
        evaluation_id: str,
        query: dict[str, list[str]],
    ) -> None:
        identity = self._identity()
        if identity is None:
            return
        try:
            header_value = self.headers.get("Last-Event-ID", "0")
            query_value = query.get("after", [header_value])[0]
            after_event_id = max(int(query_value), 0)
        except (TypeError, ValueError):
            self._error(HTTPStatus.BAD_REQUEST, "Invalid event cursor.")
            return
        try:
            self.evaluation_service.get(evaluation_id, identity.team_id)
        except EvaluationNotFound as error:
            self._error(HTTPStatus.NOT_FOUND, str(error))
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        # This bounded stream intentionally closes so EventSource reconnects
        # with Last-Event-ID. It also makes one-shot contract tests finite.
        self.send_header("Connection", "close")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        one_shot = query.get("once") == ["1"]
        deadline = time.monotonic() + (0 if one_shot else 20)
        last_heartbeat = 0.0
        try:
            while True:
                events = self.evaluation_service.events(
                    evaluation_id,
                    after_event_id,
                    identity.team_id,
                )
                for event in events:
                    after_event_id = int(event["id"])
                    payload = json.dumps(
                        event,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    )
                    message = (
                        f"id: {after_event_id}\n"
                        f"event: {event['type']}\n"
                        f"data: {payload}\n\n"
                    )
                    self.wfile.write(message.encode("utf-8"))
                now = time.monotonic()
                if events:
                    self.wfile.flush()
                record = self.evaluation_service.get(
                    evaluation_id, identity.team_id
                )
                if (
                    one_shot
                    or record["status"] in TERMINAL_EVALUATION_STATUSES
                    or now >= deadline
                ):
                    break
                if now - last_heartbeat >= 10:
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
                    last_heartbeat = now
                time.sleep(1)
        except (BrokenPipeError, ConnectionResetError):
            return
        finally:
            self.close_connection = True

    def _upload_submission(self, identity: RequestIdentity) -> None:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
        if content_type not in {"application/zip", "application/octet-stream"}:
            self._error(
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                "Upload an Agent ZIP as application/zip",
            )
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._error(HTTPStatus.LENGTH_REQUIRED, "Content-Length is required")
            return
        if length <= 0:
            self._error(HTTPStatus.BAD_REQUEST, "Agent ZIP is empty")
            return
        if length > self.max_upload_bytes:
            self._error(
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                "Agent ZIP exceeds the development upload limit",
            )
            return
        payload = self.rfile.read(length)
        if len(payload) != length:
            self._error(HTTPStatus.BAD_REQUEST, "Agent ZIP upload was incomplete")
            return
        filename = self.headers.get("X-Agent-Filename", "agent-submission.zip")
        try:
            record = self.service.create_submission(
                filename,
                payload,
                owner_id=identity.owner_id,
                team_id=identity.team_id,
            )
            self._json(HTTPStatus.CREATED, record)
        except SubmissionError as error:
            self._error(HTTPStatus.BAD_REQUEST, str(error))

    def _admin_evaluation_action(
        self,
        evaluation_id: str,
        action: str,
        identity: RequestIdentity,
    ) -> None:
        try:
            if action == "recover":
                record = self.evaluation_service.admin_recover(
                    evaluation_id,
                    actor_id=identity.owner_id,
                )
                self._json(HTTPStatus.OK, record)
                return
            if action == "publish":
                team_name = self.headers.get("X-BuildBench-Team-Name", "").strip()
                if not team_name:
                    self._error(
                        HTTPStatus.BAD_REQUEST,
                        "X-BuildBench-Team-Name is required.",
                    )
                    return
                record = self.evaluation_service.admin_publish(
                    evaluation_id,
                    team_name=team_name[:100],
                    actor_id=identity.owner_id,
                )
                self._json(HTTPStatus.OK, record)
                return
            if action == "revoke":
                self.evaluation_service.admin_revoke(
                    evaluation_id,
                    actor_id=identity.owner_id,
                )
                self._json(HTTPStatus.OK, {"status": "revoked"})
                return
        except EvaluationNotFound as error:
            self._error(HTTPStatus.NOT_FOUND, str(error))
        except EvaluationConflict as error:
            self._error(HTTPStatus.CONFLICT, str(error))

    def log_message(self, format: str, *args: object) -> None:
        print(
            f'{self.address_string()} - - [{self.log_date_time_string()}] {format % args}',
            flush=True,
        )


def create_server(
    host: str,
    port: int,
    website_root: Path,
    starter_kit: Path,
    data_root: Path,
    max_workers: int,
    limits: ArchiveLimits,
    checker: Checker | None = None,
    smoke_runner: SmokeRunner | None = None,
    evaluation_config: EvaluationConfig | None = None,
    evaluation_database: Path | None = None,
    authenticator: TokenAuthenticator | None = None,
    account_database: Path | None = None,
    auth_service: AuthService | None = None,
) -> ThreadingHTTPServer:
    store = SubmissionStore(data_root)
    store.recover_interrupted()
    service = SubmissionService(
        store,
        starter_kit,
        checker=checker,
        limits=limits,
    )
    queue = HostedSmokeQueue(
        service,
        max_workers=max_workers,
        runner=smoke_runner,
    )
    resolved_evaluation_config = (
        evaluation_config or EvaluationConfig.from_environment(data_root)
    )
    resolved_evaluation_database = (
        evaluation_database
        or Path(
            os.environ.get(
                "BB_EVALUATION_DB",
                data_root / "evaluations.sqlite3",
            )
        )
    )
    evaluation_store = EvaluationStore(resolved_evaluation_database)
    evaluation_service = EvaluationService(
        evaluation_store,
        service,
        resolved_evaluation_config,
    )
    resolved_token_authenticator = authenticator or TokenAuthenticator.from_environment(
        resolved_evaluation_config.owner_id
    )
    resolved_account_database = (
        account_database
        or Path(
            os.environ.get(
                "BB_ACCOUNT_DB",
                data_root / "accounts.sqlite3",
            )
        )
    )
    account_store = (
        auth_service.store
        if auth_service is not None
        else AccountStore(
            resolved_account_database,
            competition_id=os.environ.get(
                "BB_COMPETITION_ID",
                DEFAULT_COMPETITION_ID,
            ),
        )
    )
    resolved_auth_service = auth_service or AuthService(account_store)
    resolved_authenticator = HybridAuthenticator(
        resolved_token_authenticator,
        resolved_auth_service,
    )
    handler = partial(BuildBenchHandler, directory=str(website_root.resolve()))
    server = ThreadingHTTPServer((host, port), handler)
    server.submission_service = service  # type: ignore[attr-defined]
    server.smoke_queue = queue  # type: ignore[attr-defined]
    server.evaluation_store = evaluation_store  # type: ignore[attr-defined]
    server.evaluation_service = evaluation_service  # type: ignore[attr-defined]
    server.authenticator = resolved_authenticator  # type: ignore[attr-defined]
    server.auth_service = resolved_auth_service  # type: ignore[attr-defined]
    server.account_store = account_store  # type: ignore[attr-defined]
    server.max_upload_bytes = limits.upload_bytes  # type: ignore[attr-defined]
    return server


def main() -> int:
    website_root = Path(__file__).resolve().parents[1]
    default_starter = website_root.parent / "buildbench-starter-kit"
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("BB_WEB_HOST", "127.0.0.1"))
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("BB_WEB_PORT", "8765")),
    )
    parser.add_argument(
        "--website-root",
        type=Path,
        default=website_root,
    )
    parser.add_argument(
        "--starter-kit",
        type=Path,
        default=Path(os.environ.get("BB_STARTER_KIT_ROOT", default_starter)),
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(
            os.environ.get("BB_WEB_DATA_ROOT", website_root / "runtime-data")
        ),
    )
    parser.add_argument(
        "--smoke-workers",
        type=int,
        default=int(os.environ.get("BB_SMOKE_WORKERS", "2")),
    )
    parser.add_argument(
        "--evaluation-db",
        type=Path,
        default=None,
        help="SQLite database for durable Full Evaluation state",
    )
    parser.add_argument(
        "--account-db",
        type=Path,
        default=None,
        help="SQLite database for participant accounts and teams",
    )
    args = parser.parse_args()

    limits = ArchiveLimits()
    server = create_server(
        args.host,
        args.port,
        args.website_root,
        args.starter_kit,
        args.data_root,
        args.smoke_workers,
        limits,
        evaluation_database=args.evaluation_db,
        account_database=args.account_db,
    )
    print(
        f"Build-Bench website: http://{args.host}:{server.server_port}/",
        flush=True,
    )
    print(f"Starter Kit: {args.starter_kit.resolve()}", flush=True)
    print(f"Runtime data: {args.data_root.resolve()}", flush=True)
    print(
        "Full Evaluation: "
        + str(server.evaluation_service.readiness()["message"]),  # type: ignore[attr-defined]
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.smoke_queue.shutdown()  # type: ignore[attr-defined]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
