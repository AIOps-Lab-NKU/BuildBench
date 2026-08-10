from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.account_store import AccountStore
from backend.auth_service import (
    AuthConfig,
    AuthService,
    HybridAuthenticator,
    InvalidCredentials,
    PasswordHasher,
)
from backend.security import AuthenticationError, RequestIdentity, TokenAuthenticator


CAPTAIN = {
    "name": "Captain Example",
    "email": "captain@example.org",
    "institutional_email": "captain@example.edu",
    "institution": "Example University",
    "password": "correct horse battery staple",
}


class AuthServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = AccountStore(self.root / "accounts.sqlite3")
        self.config = AuthConfig(
            cookie_secure=False,
            registration_limit=100,
            login_limit=100,
            csrf_secret="test-csrf-secret",
        )
        self.service = AuthService(
            self.store,
            hasher=PasswordHasher(n=2**10, r=8, p=1),
            config=self.config,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def payload(self) -> dict[str, object]:
        return {
            "captain": dict(CAPTAIN),
            "team": {
                "name": "Example Team",
                "members": [
                    {
                        "name": "Member Two",
                        "email": "member2@example.org",
                        "institutional_email": "member2@example.edu",
                        "institution": "Example University",
                    }
                ],
            },
            "accept_rules": True,
        }

    def test_register_hashes_password_and_creates_session(self) -> None:
        result = self.service.register(self.payload(), client_ip="127.0.0.1")
        self.assertEqual(result["team"]["name"], "Example Team")
        self.assertIn("csrf_token", result)
        token = str(result["_session_token"])
        cookie = f"bb_session={token}"
        me = self.service.me(cookie)
        self.assertEqual(me["user"]["email"], CAPTAIN["email"])
        with sqlite3.connect(self.store.database_path) as connection:
            password_hash = connection.execute(
                "SELECT password_hash FROM users"
            ).fetchone()[0]
        self.assertNotIn(str(CAPTAIN["password"]), password_hash)
        self.assertTrue(
            self.service.hasher.verify(CAPTAIN["password"], password_hash)
        )

    def test_login_uses_generic_failure_and_rotates_session(self) -> None:
        registered = self.service.register(
            self.payload(),
            client_ip="127.0.0.1",
        )
        with self.assertRaisesRegex(
            InvalidCredentials,
            "Email or password is incorrect",
        ):
            self.service.login(
                {"email": CAPTAIN["email"], "password": "wrong password"},
                client_ip="127.0.0.2",
            )
        logged_in = self.service.login(
            {
                "email": CAPTAIN["email"],
                "password": CAPTAIN["password"],
            },
            client_ip="127.0.0.3",
        )
        self.assertNotEqual(
            registered["_session_token"],
            logged_in["_session_token"],
        )

    def test_csrf_cookie_and_logout(self) -> None:
        result = self.service.register(self.payload(), client_ip="127.0.0.1")
        token = str(result["_session_token"])
        cookie = f"bb_session={token}"
        csrf = str(result["csrf_token"])
        self.service.verify_csrf(cookie, csrf)
        with self.assertRaises(AuthenticationError):
            self.service.verify_csrf(cookie, "wrong")
        self.assertIn("HttpOnly", self.service.set_cookie_header(token))
        self.assertNotIn("Secure", self.service.set_cookie_header(token))
        self.service.logout(cookie)
        with self.assertRaises(AuthenticationError):
            self.service.me(cookie)

    def test_hybrid_auth_preserves_bearer_admin_and_session_participant(self) -> None:
        result = self.service.register(self.payload(), client_ip="127.0.0.1")
        token = "a" * 32
        bearer = TokenAuthenticator(
            {
                token: RequestIdentity(
                    owner_id="admin",
                    team_id="organizers",
                    display_name="Organizer",
                    role="admin",
                )
            },
            required=True,
        )
        hybrid = HybridAuthenticator(bearer, self.service)
        admin = hybrid.authenticate(f"Bearer {token}", None, require_admin=True)
        self.assertTrue(admin.is_admin)
        participant = hybrid.authenticate(
            None,
            f"bb_session={result['_session_token']}",
        )
        self.assertEqual(participant.team_id, result["team"]["team_id"])
        self.assertEqual(participant.authentication_method, "session")


if __name__ == "__main__":
    unittest.main()
