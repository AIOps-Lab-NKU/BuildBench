from __future__ import annotations

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
    "institution": "Example University",
}


def member(index: int, *, email: str | None = None) -> dict[str, object]:
    return {
        "name": f"Member {index}",
        "email": email if email is not None else f"member{index}@example.org",
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
        self.assertEqual(context["team"]["name"], "Example Team")
        self.assertEqual(len(context["team"]["members"]), 3)
        self.assertTrue(context["team"]["members"][0]["is_captain"])
        restored = self.store.context_for_user(context["user"]["user_id"])
        self.assertEqual(restored, context)

    def test_team_is_limited_to_five_and_all_emails_are_required(self) -> None:
        with self.assertRaisesRegex(AccountValidationError, "at most 5"):
            self.register(members=[member(index) for index in range(2, 7)])
        with self.assertRaisesRegex(AccountValidationError, "Email is required"):
            self.register(members=[member(2, email="")])

    def test_team_name_is_unique_case_insensitively(self) -> None:
        self.register(team_name="Benchmark Builders")
        second_captain = {
            "name": "Second Captain",
            "email": "captain2@example.org",
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
                "institution": "Updated University",
            },
        )
        self.assertEqual(team["members"][1]["name"], "Updated Member")
        team = self.store.delete_member(
            user_id=user_id,
            team_id=team_id,
            member_id=str(added["member_id"]),
        )
        self.assertEqual(len(team["members"]), 1)


if __name__ == "__main__":
    unittest.main()
