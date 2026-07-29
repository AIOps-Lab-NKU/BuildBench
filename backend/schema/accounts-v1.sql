PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS account_schema_versions (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

INSERT OR IGNORE INTO account_schema_versions(version, applied_at)
VALUES (1, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    email_normalized TEXT NOT NULL UNIQUE,
    institution TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'participant'
        CHECK (role IN ('participant', 'admin')),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'disabled')),
    email_verified_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teams (
    team_id TEXT PRIMARY KEY,
    competition_id TEXT NOT NULL,
    name TEXT NOT NULL,
    name_normalized TEXT NOT NULL,
    captain_user_id TEXT NOT NULL
        REFERENCES users(user_id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'disabled', 'disqualified')),
    members_locked_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (competition_id, name_normalized),
    UNIQUE (competition_id, captain_user_id)
);

CREATE TABLE IF NOT EXISTS team_members (
    member_id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL
        REFERENCES teams(team_id) ON DELETE CASCADE,
    competition_id TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    email_normalized TEXT NOT NULL,
    institution TEXT NOT NULL,
    is_captain INTEGER NOT NULL DEFAULT 0
        CHECK (is_captain IN (0, 1)),
    display_order INTEGER NOT NULL CHECK (display_order BETWEEN 1 AND 5),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (team_id, email_normalized),
    UNIQUE (team_id, display_order),
    UNIQUE (competition_id, email_normalized)
);

CREATE UNIQUE INDEX IF NOT EXISTS one_captain_member_per_team
ON team_members(team_id)
WHERE is_captain = 1;

CREATE TABLE IF NOT EXISTS competition_registrations (
    registration_id TEXT PRIMARY KEY,
    competition_id TEXT NOT NULL,
    team_id TEXT NOT NULL
        REFERENCES teams(team_id) ON DELETE CASCADE,
    accepted_rules_at TEXT NOT NULL,
    registered_at TEXT NOT NULL,
    UNIQUE (competition_id, team_id)
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL
        REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL,
    last_used_at TEXT NOT NULL,
    idle_expires_at TEXT NOT NULL,
    absolute_expires_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE INDEX IF NOT EXISTS sessions_user_active
ON sessions(user_id, revoked_at, absolute_expires_at);

CREATE TABLE IF NOT EXISTS account_audit_events (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_user_id TEXT,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS account_audit_target
ON account_audit_events(target_type, target_id, audit_id);
