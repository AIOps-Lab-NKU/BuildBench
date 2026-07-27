from __future__ import annotations

import http.client
import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from backend.server import create_server
from backend.submissions import ArchiveLimits, SmokeOutcome
from backend.tests.test_evaluations import evaluation_config
from backend.tests.test_submissions import accepted_checker, valid_agent_zip


class EvaluationApiTests(unittest.TestCase):
    def test_create_list_detail_events_and_result_readiness(self) -> None:
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
                (smoke_dir / "console.log").write_text(
                    "passed\n", encoding="utf-8"
                )
                return SmokeOutcome(
                    "succeeded",
                    "Hosted Smoke Test passed.",
                    {"status": "succeeded", "case_count": 1, "succeeded": 1},
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
                evaluation_config=evaluation_config(("hidden-a", "hidden-b")),
            )
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            connection = http.client.HTTPConnection(
                "127.0.0.1",
                server.server_port,
                timeout=5,
            )
            try:
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
                submission = json.load(response)

                connection.request(
                    "POST",
                    f"/api/submissions/{submission['id']}/smoke-test",
                    body=b"",
                    headers={"Content-Length": "0"},
                )
                response = connection.getresponse()
                response.read()
                deadline = time.time() + 5
                while time.time() < deadline:
                    connection.request(
                        "GET", f"/api/submissions/{submission['id']}"
                    )
                    response = connection.getresponse()
                    submission = json.load(response)
                    if submission["status"] == "smoke_passed":
                        break
                    time.sleep(0.02)
                self.assertEqual(submission["status"], "smoke_passed")

                route = (
                    f"/api/submissions/{submission['id']}/full-evaluations"
                )
                connection.request(
                    "POST",
                    route,
                    body=b"",
                    headers={
                        "Content-Length": "0",
                        "Idempotency-Key": "api-request-0001",
                    },
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 201)
                evaluation = json.load(response)
                self.assertEqual(evaluation["status"], "queued")
                self.assertNotIn("hidden-a", repr(evaluation))

                connection.request(
                    "POST",
                    route,
                    body=b"",
                    headers={
                        "Content-Length": "0",
                        "Idempotency-Key": "api-request-0001",
                    },
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                replay = json.load(response)
                self.assertEqual(
                    replay["evaluation_id"],
                    evaluation["evaluation_id"],
                )

                connection.request("GET", "/api/full-evaluations")
                response = connection.getresponse()
                listed = json.load(response)["evaluations"]
                self.assertEqual(len(listed), 1)

                evaluation_id = evaluation["evaluation_id"]
                connection.request(
                    "GET", f"/api/full-evaluations/{evaluation_id}"
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(
                    json.load(response)["evaluation_id"],
                    evaluation_id,
                )

                connection.request(
                    "GET",
                    f"/api/full-evaluations/{evaluation_id}/events?once=1",
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertTrue(
                    response.getheader("Content-Type").startswith(
                        "text/event-stream"
                    )
                )
                event_text = response.read().decode("utf-8")
                self.assertIn("event: snapshot", event_text)
                self.assertNotIn("hidden-a", event_text)

                connection.request(
                    "GET",
                    f"/api/full-evaluations/{evaluation_id}/result",
                )
                response = connection.getresponse()
                self.assertEqual(response.status, 409)
                response.read()
            finally:
                connection.close()
                server.shutdown()
                server.server_close()
                server.smoke_queue.shutdown()  # type: ignore[attr-defined]
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()

