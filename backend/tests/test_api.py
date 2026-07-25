from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from backend.server import create_server
from backend.submissions import ArchiveLimits, SmokeOutcome
from backend.tests.test_submissions import accepted_checker, valid_agent_zip


class ApiTests(unittest.TestCase):
    def test_health_upload_list_and_smoke_request(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            website = root / "website"
            website.mkdir()
            (website / "index.html").write_text("ok", encoding="utf-8")
            starter = root / "starter"
            starter.mkdir()
            (starter / "bb").write_text("#!/bin/sh\n", encoding="utf-8")

            def smoke_runner(
                _record: dict[str, object],
                _agent: Path,
                smoke_dir: Path,
            ) -> SmokeOutcome:
                (smoke_dir / "console.log").write_text("passed\n", encoding="utf-8")
                return SmokeOutcome(
                    "succeeded",
                    "Hosted Smoke Test passed.",
                    {"status": "succeeded"},
                    "/fake/run",
                )

            server = create_server(
                "127.0.0.1",
                0,
                website,
                starter,
                root / "data",
                1,
                ArchiveLimits(),
                checker=accepted_checker,
                smoke_runner=smoke_runner,
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            connection = http.client.HTTPConnection(
                "127.0.0.1",
                server.server_port,
                timeout=5,
            )
            try:
                connection.request("GET", "/api/health")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.load(response)["status"], "ok")

                payload = valid_agent_zip()
                connection.request(
                    "POST",
                    "/api/submissions",
                    body=payload,
                    headers={
                        "Content-Type": "application/zip",
                        "Content-Length": str(len(payload)),
                        "X-Agent-Filename": "agent-submission.zip",
                    },
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 201)
                record = json.load(response)
                self.assertEqual(record["status"], "qualified")

                connection.request(
                    "GET",
                    f"/api/submissions/{record['id']}/log",
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertTrue(
                    response.getheader("Content-Type").startswith("text/plain")
                )
                self.assertEqual(
                    response.read().decode("utf-8").replace("\r\n", "\n"),
                    "valid\n",
                )

                connection.request(
                    "GET",
                    f"/api/submissions/{record['id']}/log?download=1",
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn(
                    "attachment;",
                    response.getheader("Content-Disposition"),
                )
                response.read()

                connection.request("GET", "/api/submissions")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(len(json.load(response)["submissions"]), 1)

                connection.request(
                    "POST",
                    f"/api/submissions/{record['id']}/smoke-test",
                    body=b"",
                    headers={"Content-Length": "0"},
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 202)
                body = json.load(response)
                self.assertNotIn("/fake/run", json.dumps(body))
            finally:
                connection.close()
                server.shutdown()
                server.server_close()
                server.smoke_queue.shutdown()  # type: ignore[attr-defined]
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
