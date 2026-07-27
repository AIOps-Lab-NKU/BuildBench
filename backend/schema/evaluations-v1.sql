PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS evaluation_schema_versions (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

INSERT OR IGNORE INTO evaluation_schema_versions(version, applied_at)
VALUES (1, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'));

CREATE TABLE IF NOT EXISTS full_evaluations (
    evaluation_id TEXT PRIMARY KEY,
    submission_id TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'official'
        CHECK (kind = 'official'),
    idempotency_key TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN (
            'queued',
            'preparing',
            'evaluating',
            'finalizing',
            'completed',
            'cancelled',
            'system_error'
        )),
    submission_sha256 TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_version TEXT NOT NULL,
    case_set_version TEXT NOT NULL,
    case_set_digest TEXT NOT NULL,
    runtime_image_digest TEXT NOT NULL,
    validator_image_digest TEXT NOT NULL,
    protocol_version TEXT NOT NULL,
    protocol_config_hash TEXT NOT NULL,
    feedback_policy TEXT NOT NULL
        CHECK (feedback_policy IN ('public_validation', 'hidden')),
    total_cases INTEGER NOT NULL CHECK (total_cases > 0),
    completed_cases INTEGER NOT NULL DEFAULT 0
        CHECK (completed_cases >= 0 AND completed_cases <= total_cases),
    successful_cases INTEGER NOT NULL DEFAULT 0
        CHECK (successful_cases >= 0 AND successful_cases <= total_cases),
    running_cases INTEGER NOT NULL DEFAULT 0
        CHECK (running_cases >= 0 AND running_cases <= total_cases),
    infrastructure_retries INTEGER NOT NULL DEFAULT 0
        CHECK (infrastructure_retries >= 0),
    score REAL,
    system_message TEXT,
    queued_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (submission_id, kind),
    UNIQUE (owner_id, idempotency_key),
    CHECK (
        (status = 'completed' AND score IS NOT NULL AND finished_at IS NOT NULL)
        OR
        (status <> 'completed' AND score IS NULL)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_full_evaluation_per_owner
ON full_evaluations(owner_id)
WHERE status IN ('queued', 'preparing', 'evaluating', 'finalizing');

CREATE INDEX IF NOT EXISTS full_evaluations_owner_created
ON full_evaluations(owner_id, created_at DESC);

CREATE TABLE IF NOT EXISTS evaluation_case_runs (
    case_run_id TEXT PRIMARY KEY,
    evaluation_id TEXT NOT NULL
        REFERENCES full_evaluations(evaluation_id) ON DELETE CASCADE,
    case_snapshot_id TEXT NOT NULL,
    case_ordinal INTEGER NOT NULL CHECK (case_ordinal > 0),
    status TEXT NOT NULL
        CHECK (status IN (
            'queued',
            'agent_running',
            'canonicalizing',
            'final_validating',
            'succeeded',
            'failed',
            'unresolvable',
            'timeout',
            'no_fix',
            'agent_error',
            'invalid_patch',
            'infrastructure_error'
        )),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    agent_status TEXT,
    validator_status TEXT,
    duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
    agent_duration_seconds INTEGER
        CHECK (agent_duration_seconds IS NULL OR agent_duration_seconds >= 0),
    build_duration_seconds INTEGER
        CHECK (build_duration_seconds IS NULL OR build_duration_seconds >= 0),
    build_attempts INTEGER
        CHECK (build_attempts IS NULL OR build_attempts >= 0),
    repair_size_bytes INTEGER
        CHECK (repair_size_bytes IS NULL OR repair_size_bytes >= 0),
    modified_files INTEGER
        CHECK (modified_files IS NULL OR modified_files >= 0),
    result_internal_path TEXT,
    message_internal TEXT,
    lease_owner TEXT,
    lease_until TEXT,
    heartbeat_at TEXT,
    retry_after TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    updated_at TEXT NOT NULL,
    UNIQUE (evaluation_id, case_snapshot_id),
    UNIQUE (evaluation_id, case_ordinal)
);

CREATE INDEX IF NOT EXISTS case_runs_claimable
ON evaluation_case_runs(status, lease_until, created_at);

CREATE INDEX IF NOT EXISTS case_runs_evaluation
ON evaluation_case_runs(evaluation_id, case_ordinal);

CREATE TABLE IF NOT EXISTS evaluation_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_id TEXT NOT NULL
        REFERENCES full_evaluations(evaluation_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL
        CHECK (event_type IN (
            'snapshot',
            'phase',
            'progress',
            'heartbeat',
            'completed',
            'system_error'
        )),
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS evaluation_events_stream
ON evaluation_events(evaluation_id, event_id);

CREATE TABLE IF NOT EXISTS evaluation_audit_events (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS evaluation_audit_target
ON evaluation_audit_events(target_type, target_id, audit_id);

CREATE TABLE IF NOT EXISTS leaderboard_entries (
    entry_id TEXT PRIMARY KEY,
    evaluation_id TEXT NOT NULL UNIQUE
        REFERENCES full_evaluations(evaluation_id) ON DELETE RESTRICT,
    owner_id TEXT NOT NULL,
    team_name TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_version TEXT NOT NULL,
    score REAL NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
    successful_cases INTEGER NOT NULL CHECK (successful_cases >= 0),
    total_cases INTEGER NOT NULL CHECK (total_cases > 0),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds >= 0),
    case_set_version TEXT NOT NULL,
    case_set_digest TEXT NOT NULL,
    protocol_version TEXT NOT NULL,
    protocol_config_hash TEXT NOT NULL,
    published_at TEXT NOT NULL,
    revoked_at TEXT
);

CREATE INDEX IF NOT EXISTS leaderboard_version_rank
ON leaderboard_entries(
    case_set_version,
    protocol_version,
    revoked_at,
    score DESC,
    successful_cases DESC,
    duration_seconds ASC,
    published_at ASC
);
