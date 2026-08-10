from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from backend.account_store import (
    AccountConflict,
    AccountStore,
    AccountValidationError,
)


CAPTAIN = {
    "name": "Captain Example",
    "email": "captain@example.org",
    "institutional_email": "captain@example.edu",
    "institution": "Example University",
}


def member(
    index: int,
    *,
    email: str | None = None,
    institutional_email: str | None = None,
) -> dict[str, object]:
    return {
        "name": f"Member {index}",
        "email": email if email is not None else f"member{index}@example.org",
        "institutional_email": (
            institutional_email
            if institutional_email is not None
            else f"member{index}@example.edu"
        ),
        "institution": "Example University",
    }


class AccountStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.store = AccountStore(self.root / "accounts.sqlite3")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def register(
        self,
        *,
        captain: dict[str, object] | None = None,
        team_name: str = "Example Team",
        members: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        return self.store.create_registration(
            captain=captain or dict(CAPTAIN),
            team_name=team_name,
            members=members or [],
            password_hash="test-password-hash",
            accept_rules=True,
        )

    def test_registration_is_atomic_and_persists_team_context(self) -> None:
        context = self.register(members=[member(2), member(3)])
        self.assertEqual(context["user"]["email"], CAPTAIN["email"])
        self.assertEqual(
            context["user"]["institutional_email"],
            CAPTAIN["institutional_email"],
        )
        self.assertEqual(context["team"]["name"], "Example Team")
        self.assertEqual(len(context["team"]["members"]), 3)
        self.assertTrue(context["team"]["members"][0]["is_captain"])
        restored = self.store.context_for_user(context["user"]["user_id"])
        self.assertEqual(restored, context)

        names = self.store.public_member_names(str(context["team"]["team_id"]))
        self.assertEqual(names, ["Captain Example", "Member 2", "Member 3"])
        self.assertEqual(self.store.public_member_names("missing-team"), [])

    def test_team_is_limited_to_five_and_all_emails_are_required(self) -> None:
        with self.assertRaisesRegex(AccountValidationError, "at most 5"):
            self.register(members=[member(index) for index in range(2, 7)])
        with self.assertRaisesRegex(AccountValidationError, "Email is required"):
            self.register(members=[member(2, email="")])
        with self.assertRaisesRegex(
            AccountValidationError,
            "Institutional email is required",
        ):
            self.register(members=[member(2, institutional_email="")])

    def test_team_name_is_unique_case_insensitively(self) -> None:
        self.register(team_name="Benchmark Builders")
        second_captain = {
            "name": "Second Captain",
            "email": "captain2@example.org",
            "institutional_email": "captain2@example.edu",
            "institution": "Another University",
        }
        with self.assertRaisesRegex(AccountConflict, "team name"):
            self.register(
                captain=second_captain,
                team_name="benchmark builders",
            )

    def test_member_email_can_belong_to_only_one_team(self) -> None:
        self.register(members=[member(2, email="shared@example.org")])
        second_captain = {
            "name": "Second Captain",
            "email": "captain2@example.org",
            "institutional_email": "captain2@example.edu",
            "institution": "Another University",
        }
        with self.assertRaisesRegex(AccountConflict, "already registered"):
            self.register(
                captain=second_captain,
                team_name="Second Team",
                members=[member(3, email="SHARED@example.org")],
            )
        self.assertIsNone(
            self.store.credential_by_email("captain2@example.org")
        )

    def test_institutional_email_can_belong_to_only_one_participant(self) -> None:
        self.register(
            members=[
                member(
                    2,
                    institutional_email="shared@university.edu",
                )
            ]
        )
        second_captain = {
            "name": "Second Captain",
            "email": "captain2@example.org",
            "institutional_email": "captain2@example.edu",
            "institution": "Another University",
        }
        with self.assertRaisesRegex(AccountConflict, "institutional email"):
            self.register(
                captain=second_captain,
                team_name="Second Team",
                members=[
                    member(
                        3,
                        email="different@example.org",
                        institutional_email="SHARED@university.edu",
                    )
                ],
            )
        self.assertIsNone(
            self.store.credential_by_email("captain2@example.org")
        )

    def test_captain_cannot_be_deleted_or_changed_from_roster(self) -> None:
        context = self.register(members=[member(2)])
        team_id = str(context["team"]["team_id"])
        user_id = str(context["user"]["user_id"])
        captain_member = context["team"]["members"][0]
        with self.assertRaisesRegex(AccountConflict, "cannot be removed"):
            self.store.delete_member(
                user_id=user_id,
                team_id=team_id,
                member_id=str(captain_member["member_id"]),
            )
        with self.assertRaisesRegex(AccountConflict, "cannot be changed"):
            self.store.update_member(
                user_id=user_id,
                team_id=team_id,
                member_id=str(captain_member["member_id"]),
                member=member(4),
            )

    def test_add_update_delete_member_and_global_email_constraint(self) -> None:
        context = self.register()
        team_id = str(context["team"]["team_id"])
        user_id = str(context["user"]["user_id"])
        team = self.store.add_member(
            user_id=user_id,
            team_id=team_id,
            member=member(2),
        )
        added = team["members"][1]
        team = self.store.update_member(
            user_id=user_id,
            team_id=team_id,
            member_id=str(added["member_id"]),
            member={
                "name": "Updated Member",
                "email": "updated@example.org",
                "institutional_email": "updated@example.edu",
                "institution": "Updated University",
            },
        )
        self.assertEqual(team["members"][1]["name"], "Updated Member")
        self.assertEqual(
            team["members"][1]["institutional_email"],
            "updated@example.edu",
        )
        team = self.store.delete_member(
            user_id=user_id,
            team_id=team_id,
            member_id=str(added["member_id"]),
        )
        self.assertEqual(len(team["members"]), 1)


class AccountStoreMigrationTests(unittest.TestCase):
    def test_v1_database_backfills_institutional_email_and_adds_index(
        self,
    ) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        database = Path(temporary.name) / "accounts.sqlite3"
        with sqlite3.connect(database) as connection:
            connection.executescript(
                    """
                    CREATE TABLE users (
                        user_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        email_normalized TEXT NOT NULL UNIQUE,
                        institution TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        role TEXT NOT NULL,
                        status TEXT NOT NULL,
                        email_verified_at TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    CREATE TABLE teams (
                        team_id TEXT PRIMARY KEY,
                        competition_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        name_normalized TEXT NOT NULL,
                        captain_user_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        members_locked_at TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE (competition_id, name_normalized),
                        UNIQUE (competition_id, captain_user_id)
                    );
                    CREATE TABLE team_members (
                        member_id TEXT PRIMARY KEY,
                        team_id TEXT NOT NULL,
                        competition_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        email_normalized TEXT NOT NULL,
                        institution TEXT NOT NULL,
                        is_captain INTEGER NOT NULL,
                        display_order INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE (team_id, email_normalized),
                        UNIQUE (team_id, display_order),
                        UNIQUE (competition_id, email_normalized)
                    );
                    INSERT INTO users VALUES (
                        'USR-legacy', 'Legacy Captain',
                        'legacy@example.org', 'legacy@example.org',
                        'Legacy University', 'hash', 'participant', 'active',
                        NULL, '2026-01-01T00:00:00Z',
                        '2026-01-01T00:00:00Z'
                    );
                    INSERT INTO teams VALUES (
                        'TEAM-legacy', 'buildbench-icse-2027',
                        'Legacy Team', 'legacy team', 'USR-legacy', 'active',
                        NULL, '2026-01-01T00:00:00Z',
                        '2026-01-01T00:00:00Z'
                    );
                    INSERT INTO team_members VALUES (
                        'MEM-legacy', 'TEAM-legacy',
                        'buildbench-icse-2027', 'Legacy Captain',
                        'legacy@example.org', 'legacy@example.org',
                        'Legacy University', 1, 1,
                        '2026-01-01T00:00:00Z',
                        '2026-01-01T00:00:00Z'
                    );
                    """
            )

        store = AccountStore(database)
        context = store.context_for_user("USR-legacy")
        self.assertEqual(
            context["user"]["institutional_email"],
            "legacy@example.org",
        )
        self.assertEqual(
            context["team"]["members"][0]["institutional_email"],
            "legacy@example.org",
        )
        with sqlite3.connect(database) as connection:
            versions = {
                row[0]
                for row in connection.execute(
                    "SELECT version FROM account_schema_versions"
                )
            }
        self.assertIn(2, versions)
        with self.assertRaisesRegex(AccountConflict, "institutional email"):
            store.add_member(
                user_id="USR-legacy",
                team_id="TEAM-legacy",
                member=member(
                    2,
                    email="new@example.org",
                    institutional_email="LEGACY@example.org",
                ),
            )


if __name__ == "__main__":
    unittest.main()
