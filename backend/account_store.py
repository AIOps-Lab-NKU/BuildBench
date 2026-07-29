"""SQLite persistence for participant accounts and paper-style teams."""

from __future__ import annotations

import json
import re
import sqlite3
import threading
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Sequence


MAX_TEAM_MEMBERS = 5
DEFAULT_COMPETITION_ID = "buildbench-icse-2027"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AccountError(ValueError):
    """Base class for participant-safe account errors."""


class AccountValidationError(AccountError):
    pass


class AccountConflict(AccountError):
    pass


class AccountNotFound(AccountError):
    pass


class AccountLocked(AccountError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


def normalize_text(value: object, label: str, *, maximum: int) -> str:
    normalized = " ".join(
        unicodedata.normalize("NFKC", str(value or "")).strip().split()
    )
    if not normalized:
        raise AccountValidationError(f"{label} is required.")
    if len(normalized) > maximum:
        raise AccountValidationError(f"{label} is too long.")
    return normalized


def normalize_email(value: object) -> tuple[str, str]:
    display = unicodedata.normalize("NFKC", str(value or "")).strip()
    if not display:
        raise AccountValidationError("Email is required.")
    if len(display) > 254 or not EMAIL_PATTERN.fullmatch(display):
        raise AccountValidationError("Enter a valid email address.")
    return display, display.casefold()


def normalize_team_name(value: object) -> tuple[str, str]:
    display = normalize_text(value, "Team name", maximum=100)
    return display, display.casefold()


def _public_user(row: sqlite3.Row) -> dict[str, object]:
    return {
        "user_id": row["user_id"],
        "name": row["name"],
        "email": row["email"],
        "institution": row["institution"],
        "role": row["role"],
        "status": row["status"],
        "email_verified": bool(row["email_verified_at"]),
    }


def _public_member(row: sqlite3.Row) -> dict[str, object]:
    return {
        "member_id": row["member_id"],
        "name": row["name"],
        "email": row["email"],
        "institution": row["institution"],
        "is_captain": bool(row["is_captain"]),
        "display_order": int(row["display_order"]),
    }


class AccountStore:
    """Durable account store for the one-server competition platform."""

    def __init__(
        self,
        database_path: Path,
        *,
        competition_id: str = DEFAULT_COMPETITION_ID,
    ):
        self.database_path = database_path.resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.competition_id = normalize_text(
            competition_id,
            "Competition ID",
            maximum=100,
        )
        self._schema_path = (
            Path(__file__).resolve().parent / "schema" / "accounts-v1.sql"
        )
        self._init_lock = threading.Lock()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path,
            timeout=30,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        return connection

    def _initialize(self) -> None:
        with self._init_lock:
            schema = self._schema_path.read_text(encoding="utf-8")
            with self._connect() as connection:
                connection.execute("PRAGMA journal_mode = WAL")
                connection.execute("PRAGMA synchronous = NORMAL")
                connection.executescript(schema)

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    @staticmethod
    def _audit(
        connection: sqlite3.Connection,
        *,
        actor_user_id: str | None,
        action: str,
        target_type: str,
        target_id: str,
        details: dict[str, object] | None = None,
        created_at: str | None = None,
    ) -> None:
        connection.execute(
            """
            INSERT INTO account_audit_events(
                actor_user_id, action, target_type, target_id,
                details_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                actor_user_id,
                action,
                target_type,
                target_id,
                json.dumps(
                    details or {},
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ),
                created_at or utc_now(),
            ),
        )

    @staticmethod
    def _raise_integrity(error: sqlite3.IntegrityError) -> None:
        message = str(error).casefold()
        if "teams.competition_id, teams.name_normalized" in message:
            raise AccountConflict(
                "That team name is already registered for this competition."
            ) from error
        if "users.email_normalized" in message:
            raise AccountConflict(
                "That captain email is already registered."
            ) from error
        if (
            "team_members.competition_id, team_members.email_normalized"
            in message
        ):
            raise AccountConflict(
                "That member email is already registered for this competition."
            ) from error
        if "team_members.team_id, team_members.email_normalized" in message:
            raise AccountConflict(
                "A member email cannot appear twice in one team."
            ) from error
        raise AccountConflict("The account or team conflicts with existing data.") from error

    @staticmethod
    def _normalized_member(
        payload: dict[str, object],
    ) -> dict[str, str]:
        if not isinstance(payload, dict):
            raise AccountValidationError("Each team member must be an object.")
        email, email_normalized = normalize_email(payload.get("email"))
        return {
            "name": normalize_text(
                payload.get("name"),
                "Member name",
                maximum=100,
            ),
            "email": email,
            "email_normalized": email_normalized,
            "institution": normalize_text(
                payload.get("institution"),
                "Member institution",
                maximum=200,
            ),
        }

    def create_registration(
        self,
        *,
        captain: dict[str, object],
        team_name: object,
        members: Sequence[dict[str, object]],
        password_hash: str,
        accept_rules: bool,
    ) -> dict[str, object]:
        if not isinstance(captain, dict):
            raise AccountValidationError("Captain details are required.")
        if not accept_rules:
            raise AccountValidationError(
                "You must accept the competition rules."
            )
        if len(members) > MAX_TEAM_MEMBERS - 1:
            raise AccountValidationError(
                f"A team may contain at most {MAX_TEAM_MEMBERS} members."
            )
        captain_email, captain_email_normalized = normalize_email(
            captain.get("email")
        )
        captain_member = {
            "name": normalize_text(
                captain.get("name"),
                "Captain name",
                maximum=100,
            ),
            "email": captain_email,
            "email_normalized": captain_email_normalized,
            "institution": normalize_text(
                captain.get("institution"),
                "Captain institution",
                maximum=200,
            ),
        }
        normalized_members = [
            self._normalized_member(dict(member)) for member in members
        ]
        all_emails = [
            captain_email_normalized,
            *(member["email_normalized"] for member in normalized_members),
        ]
        if len(set(all_emails)) != len(all_emails):
            raise AccountConflict(
                "A member email cannot appear twice in one team."
            )
        display_team_name, normalized_team_name = normalize_team_name(team_name)
        if not password_hash:
            raise AccountValidationError("Password hash is required.")

        now = utc_now()
        user_id = _new_id("USR")
        team_id = _new_id("TEAM")
        registration_id = _new_id("REG")
        try:
            with self._transaction() as connection:
                connection.execute(
                    """
                    INSERT INTO users(
                        user_id, name, email, email_normalized, institution,
                        password_hash, role, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'participant', 'active', ?, ?)
                    """,
                    (
                        user_id,
                        captain_member["name"],
                        captain_member["email"],
                        captain_member["email_normalized"],
                        captain_member["institution"],
                        password_hash,
                        now,
                        now,
                    ),
                )
                connection.execute(
                    """
                    INSERT INTO teams(
                        team_id, competition_id, name, name_normalized,
                        captain_user_id, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
                    """,
                    (
                        team_id,
                        self.competition_id,
                        display_team_name,
                        normalized_team_name,
                        user_id,
                        now,
                        now,
                    ),
                )
                for index, member in enumerate(
                    [captain_member, *normalized_members],
                    start=1,
                ):
                    connection.execute(
                        """
                        INSERT INTO team_members(
                            member_id, team_id, competition_id, name, email,
                            email_normalized, institution, is_captain,
                            display_order, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            _new_id("MEM"),
                            team_id,
                            self.competition_id,
                            member["name"],
                            member["email"],
                            member["email_normalized"],
                            member["institution"],
                            1 if index == 1 else 0,
                            index,
                            now,
                            now,
                        ),
                    )
                connection.execute(
                    """
                    INSERT INTO competition_registrations(
                        registration_id, competition_id, team_id,
                        accepted_rules_at, registered_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        registration_id,
                        self.competition_id,
                        team_id,
                        now,
                        now,
                    ),
                )
                self._audit(
                    connection,
                    actor_user_id=user_id,
                    action="register_team",
                    target_type="team",
                    target_id=team_id,
                    details={"member_count": 1 + len(normalized_members)},
                    created_at=now,
                )
        except sqlite3.IntegrityError as error:
            self._raise_integrity(error)
        return self.context_for_user(user_id)

    def context_for_user(self, user_id: str) -> dict[str, object]:
        with self._connect() as connection:
            user = connection.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()
            if user is None or user["status"] != "active":
                raise AccountNotFound("Account not found.")
            team = connection.execute(
                """
                SELECT * FROM teams
                WHERE competition_id = ? AND captain_user_id = ?
                """,
                (self.competition_id, user_id),
            ).fetchone()
            if team is None:
                raise AccountNotFound("Team not found.")
            members = connection.execute(
                """
                SELECT * FROM team_members
                WHERE team_id = ?
                ORDER BY display_order
                """,
                (team["team_id"],),
            ).fetchall()
            return {
                "user": _public_user(user),
                "team": {
                    "team_id": team["team_id"],
                    "competition_id": team["competition_id"],
                    "name": team["name"],
                    "status": team["status"],
                    "members_locked": bool(team["members_locked_at"]),
                    "members_locked_at": team["members_locked_at"],
                    "members": [_public_member(member) for member in members],
                },
            }

    def credential_by_email(self, email: object) -> dict[str, object] | None:
        _, normalized = normalize_email(email)
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT user_id, password_hash, status
                FROM users WHERE email_normalized = ?
                """,
                (normalized,),
            ).fetchone()
            return dict(row) if row is not None else None

    def _captain_team(
        self,
        connection: sqlite3.Connection,
        *,
        user_id: str,
        team_id: str | None = None,
    ) -> sqlite3.Row:
        query = """
            SELECT * FROM teams
            WHERE competition_id = ? AND captain_user_id = ?
        """
        parameters: list[object] = [self.competition_id, user_id]
        if team_id is not None:
            query += " AND team_id = ?"
            parameters.append(team_id)
        team = connection.execute(query, tuple(parameters)).fetchone()
        if team is None:
            raise AccountNotFound("Team not found.")
        return team

    @staticmethod
    def _require_unlocked(team: sqlite3.Row) -> None:
        if team["members_locked_at"]:
            raise AccountLocked("The team roster is locked.")

    def update_team_name(
        self,
        *,
        user_id: str,
        team_id: str,
        name: object,
    ) -> dict[str, object]:
        display, normalized = normalize_team_name(name)
        now = utc_now()
        try:
            with self._transaction() as connection:
                team = self._captain_team(
                    connection,
                    user_id=user_id,
                    team_id=team_id,
                )
                self._require_unlocked(team)
                connection.execute(
                    """
                    UPDATE teams SET name = ?, name_normalized = ?, updated_at = ?
                    WHERE team_id = ?
                    """,
                    (display, normalized, now, team_id),
                )
                self._audit(
                    connection,
                    actor_user_id=user_id,
                    action="update_team",
                    target_type="team",
                    target_id=team_id,
                    created_at=now,
                )
        except sqlite3.IntegrityError as error:
            self._raise_integrity(error)
        return self.context_for_user(user_id)["team"]  # type: ignore[return-value]

    def add_member(
        self,
        *,
        user_id: str,
        team_id: str,
        member: dict[str, object],
    ) -> dict[str, object]:
        normalized = self._normalized_member(member)
        now = utc_now()
        member_id = _new_id("MEM")
        try:
            with self._transaction() as connection:
                team = self._captain_team(
                    connection,
                    user_id=user_id,
                    team_id=team_id,
                )
                self._require_unlocked(team)
                count = int(
                    connection.execute(
                        "SELECT COUNT(*) FROM team_members WHERE team_id = ?",
                        (team_id,),
                    ).fetchone()[0]
                )
                if count >= MAX_TEAM_MEMBERS:
                    raise AccountValidationError(
                        f"A team may contain at most {MAX_TEAM_MEMBERS} members."
                    )
                connection.execute(
                    """
                    INSERT INTO team_members(
                        member_id, team_id, competition_id, name, email,
                        email_normalized, institution, is_captain,
                        display_order, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
                    """,
                    (
                        member_id,
                        team_id,
                        self.competition_id,
                        normalized["name"],
                        normalized["email"],
                        normalized["email_normalized"],
                        normalized["institution"],
                        count + 1,
                        now,
                        now,
                    ),
                )
                self._audit(
                    connection,
                    actor_user_id=user_id,
                    action="add_team_member",
                    target_type="team_member",
                    target_id=member_id,
                    details={"team_id": team_id},
                    created_at=now,
                )
        except sqlite3.IntegrityError as error:
            self._raise_integrity(error)
        return self.context_for_user(user_id)["team"]  # type: ignore[return-value]

    def update_member(
        self,
        *,
        user_id: str,
        team_id: str,
        member_id: str,
        member: dict[str, object],
    ) -> dict[str, object]:
        normalized = self._normalized_member(member)
        now = utc_now()
        try:
            with self._transaction() as connection:
                team = self._captain_team(
                    connection,
                    user_id=user_id,
                    team_id=team_id,
                )
                self._require_unlocked(team)
                existing = connection.execute(
                    """
                    SELECT * FROM team_members
                    WHERE team_id = ? AND member_id = ?
                    """,
                    (team_id, member_id),
                ).fetchone()
                if existing is None:
                    raise AccountNotFound("Team member not found.")
                if existing["is_captain"]:
                    raise AccountConflict(
                        "Captain details cannot be changed from the team roster."
                    )
                connection.execute(
                    """
                    UPDATE team_members
                    SET name = ?, email = ?, email_normalized = ?,
                        institution = ?, updated_at = ?
                    WHERE member_id = ?
                    """,
                    (
                        normalized["name"],
                        normalized["email"],
                        normalized["email_normalized"],
                        normalized["institution"],
                        now,
                        member_id,
                    ),
                )
                self._audit(
                    connection,
                    actor_user_id=user_id,
                    action="update_team_member",
                    target_type="team_member",
                    target_id=member_id,
                    details={"team_id": team_id},
                    created_at=now,
                )
        except sqlite3.IntegrityError as error:
            self._raise_integrity(error)
        return self.context_for_user(user_id)["team"]  # type: ignore[return-value]

    def delete_member(
        self,
        *,
        user_id: str,
        team_id: str,
        member_id: str,
    ) -> dict[str, object]:
        now = utc_now()
        with self._transaction() as connection:
            team = self._captain_team(
                connection,
                user_id=user_id,
                team_id=team_id,
            )
            self._require_unlocked(team)
            existing = connection.execute(
                """
                SELECT * FROM team_members
                WHERE team_id = ? AND member_id = ?
                """,
                (team_id, member_id),
            ).fetchone()
            if existing is None:
                raise AccountNotFound("Team member not found.")
            if existing["is_captain"]:
                raise AccountConflict("The team captain cannot be removed.")
            connection.execute(
                "DELETE FROM team_members WHERE member_id = ?",
                (member_id,),
            )
            remaining = connection.execute(
                """
                SELECT member_id FROM team_members
                WHERE team_id = ? ORDER BY display_order
                """,
                (team_id,),
            ).fetchall()
            for order, row in enumerate(remaining, start=1):
                connection.execute(
                    """
                    UPDATE team_members
                    SET display_order = ?, updated_at = ?
                    WHERE member_id = ?
                    """,
                    (order, now, row["member_id"]),
                )
            self._audit(
                connection,
                actor_user_id=user_id,
                action="delete_team_member",
                target_type="team_member",
                target_id=member_id,
                details={"team_id": team_id},
                created_at=now,
            )
        return self.context_for_user(user_id)["team"]  # type: ignore[return-value]

    def create_session(
        self,
        *,
        user_id: str,
        token_hash: str,
        idle_seconds: int,
        absolute_seconds: int,
    ) -> dict[str, str]:
        now_dt = datetime.now(timezone.utc).replace(microsecond=0)
        now = now_dt.isoformat()
        session_id = _new_id("SES")
        idle_expiry = (
            now_dt + timedelta(seconds=idle_seconds)
        ).isoformat()
        absolute_expiry = (
            now_dt + timedelta(seconds=absolute_seconds)
        ).isoformat()
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO sessions(
                    session_id, user_id, token_hash, created_at, last_used_at,
                    idle_expires_at, absolute_expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_id,
                    token_hash,
                    now,
                    now,
                    idle_expiry,
                    absolute_expiry,
                ),
            )
            self._audit(
                connection,
                actor_user_id=user_id,
                action="create_session",
                target_type="session",
                target_id=session_id,
                created_at=now,
            )
        return {
            "session_id": session_id,
            "idle_expires_at": idle_expiry,
            "absolute_expires_at": absolute_expiry,
        }

    def session_for_token_hash(
        self,
        token_hash: str,
        *,
        idle_seconds: int,
    ) -> dict[str, object] | None:
        now_dt = datetime.now(timezone.utc).replace(microsecond=0)
        now = now_dt.isoformat()
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT s.*, u.status AS user_status
                FROM sessions s
                JOIN users u ON u.user_id = s.user_id
                WHERE s.token_hash = ? AND s.revoked_at IS NULL
                """,
                (token_hash,),
            ).fetchone()
            if row is None:
                return None
            if (
                row["user_status"] != "active"
                or row["idle_expires_at"] <= now
                or row["absolute_expires_at"] <= now
            ):
                connection.execute(
                    """
                    UPDATE sessions SET revoked_at = ?
                    WHERE session_id = ? AND revoked_at IS NULL
                    """,
                    (now, row["session_id"]),
                )
                return None
            next_idle = min(
                now_dt + timedelta(seconds=idle_seconds),
                datetime.fromisoformat(row["absolute_expires_at"]),
            ).isoformat()
            connection.execute(
                """
                UPDATE sessions
                SET last_used_at = ?, idle_expires_at = ?
                WHERE session_id = ?
                """,
                (now, next_idle, row["session_id"]),
            )
            return dict(row)

    def revoke_session(self, session_id: str, *, actor_user_id: str) -> None:
        now = utc_now()
        with self._transaction() as connection:
            connection.execute(
                """
                UPDATE sessions SET revoked_at = ?
                WHERE session_id = ? AND user_id = ? AND revoked_at IS NULL
                """,
                (now, session_id, actor_user_id),
            )
            self._audit(
                connection,
                actor_user_id=actor_user_id,
                action="revoke_session",
                target_type="session",
                target_id=session_id,
                created_at=now,
            )

    def audit_events(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM account_audit_events ORDER BY audit_id"
                ).fetchall()
            ]
