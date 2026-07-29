from __future__ import annotations

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from backend.account_store import AccountStore
from backend.auth_service import AuthConfig, AuthService, PasswordHasher
from backend.security import RequestIdentity, TokenAuthenticator
from backend.server import create_server
from backend.submissions import ArchiveLimits
from backend.tests.test_submissions import accepted_checker, valid_agent_zip


def registration_payload(
    *,
    captain_email: str = "captain@example.org",
    team_name: str = "Example Team",
    member_email: str = "member@example.org",
) -> dict[str, object]:
    return {
        "captain": {
            "name": "Captain Example",
            "email": captain_email,
            "institution": "Example University",
            "password": "correct horse battery staple",
        },
        "team": {
            "name": team_name,
            "members": [
                {
                    "name": "Member Example",
                    "email": member_email,
                    "institution": "Example University",
                }
            ],
        },
        "accept_rules": True,
    }


class AuthApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        website = root / "website"
        website.mkdir()
        (website / "index.html").write_text("ok", encoding="utf-8")
        starter = root / "starter"
        starter.mkdir()
        (starter / "bb").write_text("#!/bin/sh\n", encoding="utf-8")
        store = AccountStore(root / "accounts.sqlite3")
        auth_service = AuthService(
            store,
            hasher=PasswordHasher(n=2**10, r=8, p=1),
            config=AuthConfig(
                registration_limit=100,
                login_limit=100,
                csrf_secret="auth-api-test-secret",
            ),
        )
        bearer = TokenAuthenticator(
            {
                "a" * 32: RequestIdentity(
                    owner_id="admin",
                    team_id="organizers",
                    display_name="Organizer",
                    role="admin",
                )
            },
            required=True,
        )
        self.server = create_server(
            "127.0.0.1",
            0,
            website,
            starter,
            root / "data",
            1,
            ArchiveLimits(),
            authenticator=bearer,
            auth_service=auth_service,
            checker=accepted_checker,
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        self.connection = http.client.HTTPConnection(
            "127.0.0.1",
            self.server.server_port,
            timeout=5,
        )

    def tearDown(self) -> None:
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.server.smoke_queue.shutdown()  # type: ignore[attr-defined]
        self.thread.join(timeout=5)
        self.temporary.cleanup()

    def request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, dict[str, object], http.client.HTTPMessage]:
        body = (
            json.dumps(payload).encode("utf-8")
            if payload is not None
            else b""
        )
        request_headers = dict(headers or {})
        if payload is not None:
            request_headers.update(
                {
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                }
            )
        else:
            request_headers.setdefault("Content-Length", "0")
        self.connection.request(
            method,
            path,
            body=body,
            headers=request_headers,
        )
        response = self.connection.getresponse()
        result = json.loads(response.read().decode("utf-8"))
        return response.status, result, response.headers

    def register(
        self,
    ) -> tuple[str, str, dict[str, object]]:
        status, body, headers = self.request_json(
            "POST",
            "/api/auth/register",
            registration_payload(),
            headers={"Origin": f"http://127.0.0.1:{self.server.server_port}"},
        )
        self.assertEqual(status, 201)
        cookie = str(headers.get("Set-Cookie")).split(";", 1)[0]
        self.assertIn("bb_session=", cookie)
        return cookie, str(body["csrf_token"]), body

    def test_register_me_team_and_logout(self) -> None:
        cookie, csrf, registered = self.register()
        self.assertEqual(registered["team"]["name"], "Example Team")
        self.assertNotIn("_session_token", registered)

        status, me, _ = self.request_json(
            "GET",
            "/api/auth/me",
            headers={"Cookie": cookie},
        )
        self.assertEqual(status, 200)
        self.assertEqual(me["user"]["email"], "captain@example.org")

        status, team, _ = self.request_json(
            "GET",
            "/api/team",
            headers={"Cookie": cookie},
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(team["members"]), 2)

        status, _, headers = self.request_json(
            "POST",
            "/api/auth/logout",
            headers={"Cookie": cookie, "X-CSRF-Token": csrf},
        )
        self.assertEqual(status, 200)
        self.assertIn("Max-Age=0", headers.get("Set-Cookie"))
        status, _, _ = self.request_json(
            "GET",
            "/api/auth/me",
            headers={"Cookie": cookie},
        )
        self.assertEqual(status, 401)

    def test_team_mutation_requires_csrf_and_preserves_captain(self) -> None:
        cookie, csrf, registered = self.register()
        status, _, _ = self.request_json(
            "POST",
            "/api/team/members",
            {
                "name": "Third Member",
                "email": "third@example.org",
                "institution": "Another University",
            },
            headers={"Cookie": cookie},
        )
        self.assertEqual(status, 403)

        status, team, _ = self.request_json(
            "POST",
            "/api/team/members",
            {
                "name": "Third Member",
                "email": "third@example.org",
                "institution": "Another University",
            },
            headers={"Cookie": cookie, "X-CSRF-Token": csrf},
        )
        self.assertEqual(status, 201)
        self.assertEqual(len(team["members"]), 3)

        captain_id = registered["team"]["members"][0]["member_id"]
        status, _, _ = self.request_json(
            "DELETE",
            f"/api/team/members/{captain_id}",
            headers={"Cookie": cookie, "X-CSRF-Token": csrf},
        )
        self.assertEqual(status, 409)

    def test_member_email_cannot_appear_in_different_teams(self) -> None:
        self.register()
        status, body, _ = self.request_json(
            "POST",
            "/api/auth/register",
            registration_payload(
                captain_email="captain-two@example.org",
                team_name="Second Team",
                member_email="MEMBER@example.org",
            ),
            headers={"Origin": f"http://127.0.0.1:{self.server.server_port}"},
        )
        self.assertEqual(status, 409)
        self.assertIn("already registered", str(body["error"]))

    def test_cross_site_registration_and_unauthenticated_team_are_rejected(
        self,
    ) -> None:
        status, _, _ = self.request_json(
            "POST",
            "/api/auth/register",
            registration_payload(),
            headers={"Sec-Fetch-Site": "cross-site"},
        )
        self.assertEqual(status, 403)
        status, _, _ = self.request_json("GET", "/api/team")
        self.assertEqual(status, 401)

    def test_session_upload_requires_csrf_and_is_isolated_by_captain(
        self,
    ) -> None:
        cookie, csrf, _ = self.register()
        archive = valid_agent_zip()
        self.connection.request(
            "POST",
            "/api/submissions",
            body=archive,
            headers={
                "Cookie": cookie,
                "Content-Type": "application/zip",
                "Content-Length": str(len(archive)),
            },
        )
        response = self.connection.getresponse()
        self.assertEqual(response.status, 403)
        response.read()

        self.connection.request(
            "POST",
            "/api/submissions",
            body=archive,
            headers={
                "Cookie": cookie,
                "X-CSRF-Token": csrf,
                "Content-Type": "application/zip",
                "Content-Length": str(len(archive)),
                "X-Agent-Filename": "agent-submission.zip",
            },
        )
        response = self.connection.getresponse()
        self.assertEqual(response.status, 201)
        submission = json.load(response)

        status, second, second_headers = self.request_json(
            "POST",
            "/api/auth/register",
            registration_payload(
                captain_email="other-captain@example.org",
                team_name="Other Team",
                member_email="other-member@example.org",
            ),
            headers={"Origin": f"http://127.0.0.1:{self.server.server_port}"},
        )
        self.assertEqual(status, 201)
        second_cookie = str(second_headers.get("Set-Cookie")).split(";", 1)[0]
        status, _, _ = self.request_json(
            "GET",
            f"/api/submissions/{submission['id']}",
            headers={"Cookie": second_cookie},
        )
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
