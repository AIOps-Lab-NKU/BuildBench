"""Password, session and hybrid request authentication for Build-Bench."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import threading
import time
from dataclasses import dataclass
from http.cookies import CookieError, SimpleCookie
from typing import Callable

from backend.account_store import (
    AccountConflict,
    AccountNotFound,
    AccountStore,
    AccountValidationError,
)
from backend.security import (
    AuthenticationError,
    RequestIdentity,
    TokenAuthenticator,
)


class AuthError(ValueError):
    """Base class for participant-safe authentication errors."""


class AuthValidationError(AuthError):
    pass


class AuthConflict(AuthError):
    pass


class AuthRateLimited(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


@dataclass(frozen=True)
class PasswordHasher:
    """Versioned scrypt password hashing with configurable test costs."""

    n: int = 2**15
    r: int = 8
    p: int = 3
    dklen: int = 32
    maxmem: int = 128 * 1024 * 1024

    def hash(self, password: str) -> str:
        encoded = self._validate_password(password)
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(
            encoded,
            salt=salt,
            n=self.n,
            r=self.r,
            p=self.p,
            dklen=self.dklen,
            maxmem=self.maxmem,
        )
        return "$".join(
            (
                "scrypt",
                "1",
                str(self.n),
                str(self.r),
                str(self.p),
                base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
                base64.urlsafe_b64encode(digest).decode("ascii").rstrip("="),
            )
        )

    @staticmethod
    def _decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)

    @staticmethod
    def _validate_password(password: object) -> bytes:
        if not isinstance(password, str):
            raise AuthValidationError("Password is required.")
        if len(password) < 12:
            raise AuthValidationError(
                "Password must contain at least 12 characters."
            )
        if len(password) > 256:
            raise AuthValidationError("Password is too long.")
        return password.encode("utf-8")

    def verify(self, password: object, encoded_hash: str) -> bool:
        if not isinstance(password, str) or len(password) > 256:
            return False
        try:
            algorithm, version, n, r, p, salt, expected = encoded_hash.split(
                "$"
            )
            if algorithm != "scrypt" or version != "1":
                return False
            cost_n, cost_r, cost_p = int(n), int(r), int(p)
            if (
                cost_n < 2
                or cost_n > 2**20
                or cost_r < 1
                or cost_r > 64
                or cost_p < 1
                or cost_p > 32
            ):
                return False
            expected_bytes = self._decode(expected)
            actual = hashlib.scrypt(
                password.encode("utf-8"),
                salt=self._decode(salt),
                n=cost_n,
                r=cost_r,
                p=cost_p,
                dklen=len(expected_bytes),
                maxmem=max(self.maxmem, 128 * cost_n * cost_r * 2),
            )
            return hmac.compare_digest(expected_bytes, actual)
        except (ValueError, TypeError, MemoryError):
            return False


class SlidingWindowLimiter:
    """Small in-memory limiter for the single-server MVP."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._events: dict[str, list[float]] = {}

    def require(
        self,
        key: str,
        *,
        limit: int,
        window_seconds: int,
    ) -> None:
        now = self._clock()
        floor = now - window_seconds
        with self._lock:
            recent = [
                event for event in self._events.get(key, []) if event > floor
            ]
            if len(recent) >= limit:
                self._events[key] = recent
                raise AuthRateLimited(
                    "Too many attempts. Wait before trying again."
                )
            recent.append(now)
            self._events[key] = recent


@dataclass(frozen=True)
class AuthConfig:
    cookie_secure: bool = False
    session_idle_seconds: int = 12 * 60 * 60
    session_absolute_seconds: int = 7 * 24 * 60 * 60
    registration_limit: int = 5
    login_limit: int = 10
    rate_window_seconds: int = 10 * 60
    csrf_secret: str = ""

    @classmethod
    def from_environment(cls) -> "AuthConfig":
        return cls(
            cookie_secure=os.environ.get("BB_COOKIE_SECURE", "0") == "1",
            session_idle_seconds=int(
                os.environ.get("BB_SESSION_IDLE_SECONDS", str(12 * 60 * 60))
            ),
            session_absolute_seconds=int(
                os.environ.get(
                    "BB_SESSION_ABSOLUTE_SECONDS",
                    str(7 * 24 * 60 * 60),
                )
            ),
            registration_limit=int(
                os.environ.get("BB_REGISTRATION_RATE_LIMIT", "5")
            ),
            login_limit=int(os.environ.get("BB_LOGIN_RATE_LIMIT", "10")),
            rate_window_seconds=int(
                os.environ.get("BB_AUTH_RATE_WINDOW_SECONDS", str(10 * 60))
            ),
            csrf_secret=os.environ.get("BB_CSRF_SECRET", ""),
        )

    @property
    def cookie_name(self) -> str:
        return "__Host-bb_session" if self.cookie_secure else "bb_session"


class AuthService:
    def __init__(
        self,
        store: AccountStore,
        *,
        hasher: PasswordHasher | None = None,
        config: AuthConfig | None = None,
        limiter: SlidingWindowLimiter | None = None,
    ):
        self.store = store
        self.hasher = hasher or PasswordHasher()
        self.config = config or AuthConfig.from_environment()
        self.limiter = limiter or SlidingWindowLimiter()
        secret = self.config.csrf_secret or secrets.token_urlsafe(48)
        self._csrf_secret = secret.encode("utf-8")
        # Equalize the expensive path for unknown users.
        self._dummy_hash = self.hasher.hash(
            "BuildBench-Dummy-Password-Not-For-Login"
        )

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _csrf_token(self, session_token: str) -> str:
        token_hash = self._token_hash(session_token)
        return hmac.new(
            self._csrf_secret,
            token_hash.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()

    def extract_session_token(self, cookie_header: str | None) -> str | None:
        if not cookie_header:
            return None
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
        except CookieError:
            return None
        morsel = cookie.get(self.config.cookie_name)
        if morsel is None:
            return None
        token = morsel.value.strip()
        return token or None

    def _new_session(
        self,
        user_id: str,
        context: dict[str, object],
    ) -> dict[str, object]:
        token = secrets.token_urlsafe(48)
        session = self.store.create_session(
            user_id=user_id,
            token_hash=self._token_hash(token),
            idle_seconds=self.config.session_idle_seconds,
            absolute_seconds=self.config.session_absolute_seconds,
        )
        return {
            **context,
            "csrf_token": self._csrf_token(token),
            "_session_token": token,
            "_session_id": session["session_id"],
        }

    def register(
        self,
        payload: object,
        *,
        client_ip: str,
    ) -> dict[str, object]:
        self.limiter.require(
            f"register:{client_ip}",
            limit=self.config.registration_limit,
            window_seconds=self.config.rate_window_seconds,
        )
        if not isinstance(payload, dict):
            raise AuthValidationError("Registration payload must be an object.")
        captain = payload.get("captain")
        team = payload.get("team")
        if not isinstance(captain, dict) or not isinstance(team, dict):
            raise AuthValidationError(
                "Captain and team details are required."
            )
        members = team.get("members", [])
        if not isinstance(members, list):
            raise AuthValidationError("Team members must be a list.")
        if any(not isinstance(member, dict) for member in members):
            raise AuthValidationError(
                "Each team member must be an object."
            )
        try:
            password_hash = self.hasher.hash(captain.get("password"))
            context = self.store.create_registration(
                captain=dict(captain),
                team_name=team.get("name"),
                members=[dict(member) for member in members],
                password_hash=password_hash,
                accept_rules=payload.get("accept_rules") is True,
            )
        except AccountValidationError as error:
            raise AuthValidationError(str(error)) from error
        except AccountConflict as error:
            raise AuthConflict(str(error)) from error
        user_id = str(context["user"]["user_id"])  # type: ignore[index]
        return self._new_session(user_id, context)

    def login(
        self,
        payload: object,
        *,
        client_ip: str,
    ) -> dict[str, object]:
        if not isinstance(payload, dict):
            raise AuthValidationError("Login payload must be an object.")
        email = str(payload.get("email") or "").strip().casefold()
        self.limiter.require(
            f"login:{client_ip}:{email[:254]}",
            limit=self.config.login_limit,
            window_seconds=self.config.rate_window_seconds,
        )
        password = payload.get("password")
        try:
            credential = self.store.credential_by_email(payload.get("email"))
        except AccountValidationError:
            credential = None
        encoded_hash = (
            str(credential["password_hash"])
            if credential is not None
            else self._dummy_hash
        )
        valid = self.hasher.verify(password, encoded_hash)
        if (
            credential is None
            or not valid
            or credential.get("status") != "active"
        ):
            raise InvalidCredentials("Email or password is incorrect.")
        user_id = str(credential["user_id"])
        context = self.store.context_for_user(user_id)
        return self._new_session(user_id, context)

    def session_context(
        self,
        cookie_header: str | None,
    ) -> tuple[dict[str, object], dict[str, object], str] | None:
        token = self.extract_session_token(cookie_header)
        if token is None:
            return None
        session = self.store.session_for_token_hash(
            self._token_hash(token),
            idle_seconds=self.config.session_idle_seconds,
        )
        if session is None:
            return None
        try:
            context = self.store.context_for_user(str(session["user_id"]))
        except AccountNotFound:
            return None
        return context, session, token

    def identity_for_cookie(
        self,
        cookie_header: str | None,
    ) -> RequestIdentity | None:
        resolved = self.session_context(cookie_header)
        if resolved is None:
            return None
        context, session, _token = resolved
        user = context["user"]  # type: ignore[assignment]
        team = context["team"]  # type: ignore[assignment]
        return RequestIdentity(
            owner_id=str(user["user_id"]),  # type: ignore[index]
            team_id=str(team["team_id"]),  # type: ignore[index]
            display_name=str(team["name"]),  # type: ignore[index]
            role=str(user["role"]),  # type: ignore[index]
            authentication_method="session",
            session_id=str(session["session_id"]),
        )

    def me(self, cookie_header: str | None) -> dict[str, object]:
        resolved = self.session_context(cookie_header)
        if resolved is None:
            raise AuthenticationError("Authentication is required.")
        context, _session, token = resolved
        return {**context, "csrf_token": self._csrf_token(token)}

    def verify_csrf(
        self,
        cookie_header: str | None,
        supplied_token: str | None,
    ) -> None:
        session_token = self.extract_session_token(cookie_header)
        if session_token is None or not supplied_token:
            raise AuthenticationError("CSRF validation failed.")
        expected = self._csrf_token(session_token)
        if not hmac.compare_digest(expected, supplied_token.strip()):
            raise AuthenticationError("CSRF validation failed.")

    def logout(self, cookie_header: str | None) -> None:
        resolved = self.session_context(cookie_header)
        if resolved is None:
            return
        context, session, _token = resolved
        self.store.revoke_session(
            str(session["session_id"]),
            actor_user_id=str(context["user"]["user_id"]),  # type: ignore[index]
        )

    def set_cookie_header(self, session_token: str) -> str:
        attributes = [
            f"{self.config.cookie_name}={session_token}",
            "Path=/",
            "HttpOnly",
            "SameSite=Lax",
        ]
        if self.config.cookie_secure:
            attributes.append("Secure")
        return "; ".join(attributes)

    def clear_cookie_header(self) -> str:
        attributes = [
            f"{self.config.cookie_name}=",
            "Path=/",
            "HttpOnly",
            "SameSite=Lax",
            "Max-Age=0",
        ]
        if self.config.cookie_secure:
            attributes.append("Secure")
        return "; ".join(attributes)


class HybridAuthenticator:
    """Authenticate browser sessions while preserving admin bearer tokens."""

    def __init__(
        self,
        token_authenticator: TokenAuthenticator,
        auth_service: AuthService,
    ):
        self.token_authenticator = token_authenticator
        self.auth_service = auth_service

    def authenticate(
        self,
        authorization: str | None,
        cookie_header: str | None,
        *,
        require_admin: bool = False,
    ) -> RequestIdentity:
        if (authorization or "").strip():
            return self.token_authenticator.authenticate(
                authorization,
                require_admin=require_admin,
            )
        session_identity = self.auth_service.identity_for_cookie(cookie_header)
        if session_identity is not None:
            if require_admin and not session_identity.is_admin:
                raise AuthenticationError(
                    "Administrator authorization is required."
                )
            return session_identity
        return self.token_authenticator.authenticate(
            None,
            require_admin=require_admin,
        )
