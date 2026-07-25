from __future__ import annotations

import argparse
import json
import os
import re
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

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
    def max_upload_bytes(self) -> int:
        return self.server.max_upload_bytes  # type: ignore[attr-defined]

    def _json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
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

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/api/health":
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
                },
            )
            return
        if path == "/api/submissions":
            self._json(HTTPStatus.OK, {"submissions": self.service.list()})
            return
        match = LOG_ROUTE.fullmatch(path)
        if match:
            try:
                filename, content = self.service.log_text(unquote(match.group(1)))
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
                self._json(HTTPStatus.OK, self.service.get(unquote(match.group(1))))
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
        if path == "/api/submissions":
            self._upload_submission()
            return
        match = SMOKE_ROUTE.fullmatch(path)
        if match:
            try:
                record = self.smoke_queue.request(unquote(match.group(1)))
                self._json(HTTPStatus.ACCEPTED, record)
            except SubmissionNotFound as error:
                self._error(HTTPStatus.NOT_FOUND, str(error))
            except SubmissionConflict as error:
                self._error(HTTPStatus.CONFLICT, str(error))
            return
        self._error(HTTPStatus.NOT_FOUND, "API route not found")

    def _upload_submission(self) -> None:
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
            record = self.service.create_submission(filename, payload)
            self._json(HTTPStatus.CREATED, record)
        except SubmissionError as error:
            self._error(HTTPStatus.BAD_REQUEST, str(error))

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
    handler = partial(BuildBenchHandler, directory=str(website_root.resolve()))
    server = ThreadingHTTPServer((host, port), handler)
    server.submission_service = service  # type: ignore[attr-defined]
    server.smoke_queue = queue  # type: ignore[attr-defined]
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
    )
    print(
        f"Build-Bench website: http://{args.host}:{server.server_port}/",
        flush=True,
    )
    print(f"Starter Kit: {args.starter_kit.resolve()}", flush=True)
    print(f"Runtime data: {args.data_root.resolve()}", flush=True)
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
