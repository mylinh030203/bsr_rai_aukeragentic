-- BSR Market Intelligence — initial schema.
-- Classification rank: public < internal < confidential < restricted.

PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('leadership','mi','internal')),
    department TEXT NOT NULL,
    max_classification TEXT NOT NULL CHECK (max_classification IN ('public','internal','confidential','restricted')),
    can_view_restricted INTEGER NOT NULL DEFAULT 0,
    can_export INTEGER NOT NULL DEFAULT 0,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE sessions (
    token_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

CREATE TABLE rate_limits (
    limit_key TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0,
    window_start TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE INDEX idx_rate_limits_expires ON rate_limits(expires_at);

CREATE TABLE sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('market','news','internal','analytical')),
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted')),
    licence_note TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE formulas (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    expression TEXT NOT NULL,
    input_instruments TEXT NOT NULL,
    allow_mixed_price_types INTEGER NOT NULL DEFAULT 0,
    unit TEXT NOT NULL,
    created_at TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE instruments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    ticker TEXT NOT NULL,
    group_name TEXT NOT NULL,
    unit TEXT NOT NULL,
    price_type TEXT NOT NULL CHECK (price_type IN ('futures','physical','index','calculated')),
    decimals INTEGER NOT NULL DEFAULT 2,
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted')),
    description TEXT,
    formula_id TEXT REFERENCES formulas(id),
    display_order INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_instruments_group ON instruments(group_name, display_order);

CREATE TABLE market_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instrument_id TEXT NOT NULL REFERENCES instruments(id),
    source_id TEXT NOT NULL REFERENCES sources(id),
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    market_time TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    data_status TEXT NOT NULL CHECK (data_status IN ('real-time','delayed','eod','manual')),
    quality_status TEXT NOT NULL CHECK (quality_status IN ('valid','pending','rejected','corrected')),
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted')),
    formula_id TEXT REFERENCES formulas(id),
    calculation_inputs TEXT,
    calculated_at TEXT,
    created_by TEXT REFERENCES users(id),
    UNIQUE (instrument_id, source_id, market_time)
);
CREATE INDEX idx_obs_instrument_time ON market_observations(instrument_id, market_time DESC);
CREATE INDEX idx_obs_classification ON market_observations(classification);
CREATE INDEX idx_obs_source ON market_observations(source_id);

CREATE TABLE news_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(id),
    published_at TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    body TEXT NOT NULL,
    summary TEXT,
    insight TEXT,
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted')),
    processing_status TEXT NOT NULL CHECK (processing_status IN ('processing','processed','duplicate_candidate','failed')),
    relevance INTEGER CHECK (relevance IS NULL OR (relevance >= 0 AND relevance <= 100)),
    duplicate_of TEXT REFERENCES news_items(id),
    coverage_note TEXT,
    created_by TEXT REFERENCES users(id),
    created_at TEXT NOT NULL
);
CREATE INDEX idx_news_published ON news_items(published_at DESC);
CREATE INDEX idx_news_classification ON news_items(classification);
CREATE INDEX idx_news_status ON news_items(processing_status);
CREATE INDEX idx_news_duplicate ON news_items(duplicate_of);

CREATE TABLE topics (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL UNIQUE
);

CREATE TABLE news_topics (
    news_id TEXT NOT NULL REFERENCES news_items(id) ON DELETE CASCADE,
    topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    PRIMARY KEY (news_id, topic_id)
);
CREATE INDEX idx_news_topics_topic ON news_topics(topic_id);

CREATE TABLE news_instruments (
    news_id TEXT NOT NULL REFERENCES news_items(id) ON DELETE CASCADE,
    instrument_id TEXT NOT NULL REFERENCES instruments(id),
    PRIMARY KEY (news_id, instrument_id)
);
CREATE INDEX idx_news_instruments_instrument ON news_instruments(instrument_id);

CREATE TABLE news_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    news_id TEXT NOT NULL REFERENCES news_items(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id),
    kind TEXT NOT NULL CHECK (kind IN ('important','comment')),
    body TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_news_feedback_news ON news_feedback(news_id);

CREATE TABLE events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    event_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    source_id TEXT REFERENCES sources(id),
    status TEXT NOT NULL CHECK (status IN ('confirmed','developing')),
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted'))
);
CREATE INDEX idx_events_occurred ON events(occurred_at DESC);

CREATE TABLE event_instruments (
    event_id TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    instrument_id TEXT NOT NULL REFERENCES instruments(id),
    PRIMARY KEY (event_id, instrument_id)
);
CREATE INDEX idx_event_instruments_instrument ON event_instruments(instrument_id);

CREATE TABLE event_news (
    event_id TEXT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    news_id TEXT NOT NULL REFERENCES news_items(id) ON DELETE CASCADE,
    PRIMARY KEY (event_id, news_id)
);

CREATE TABLE forecasts (
    id TEXT PRIMARY KEY,
    instrument_id TEXT NOT NULL REFERENCES instruments(id),
    source_id TEXT NOT NULL REFERENCES sources(id),
    horizon TEXT NOT NULL,
    period TEXT NOT NULL,
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted')),
    created_at TEXT NOT NULL
);
CREATE INDEX idx_forecasts_instrument ON forecasts(instrument_id, horizon);

CREATE TABLE forecast_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_id TEXT NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    value REAL NOT NULL,
    methodology TEXT NOT NULL,
    published_at TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    created_by TEXT REFERENCES users(id),
    UNIQUE (forecast_id, version)
);
CREATE INDEX idx_forecast_versions_forecast ON forecast_versions(forecast_id, version DESC);

CREATE TABLE forecast_evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_version_id INTEGER NOT NULL UNIQUE REFERENCES forecast_versions(id) ON DELETE CASCADE,
    actual_observation_id INTEGER REFERENCES market_observations(id),
    absolute_error REAL,
    percentage_error REAL,
    note TEXT,
    evaluated_at TEXT NOT NULL
);

CREATE TABLE analyses (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    as_of TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft','published')),
    version INTEGER NOT NULL DEFAULT 1,
    created_by TEXT REFERENCES users(id),
    created_at TEXT NOT NULL
);

CREATE TABLE analysis_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('fact','calculation','assumption','recommendation')),
    label TEXT NOT NULL,
    value TEXT NOT NULL,
    method TEXT,
    source_ref TEXT,
    position INTEGER NOT NULL
);
CREATE INDEX idx_analysis_evidence_analysis ON analysis_evidence(analysis_id, position);

CREATE TABLE briefings (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE briefing_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    briefing_id TEXT NOT NULL REFERENCES briefings(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    generated_at TEXT NOT NULL,
    data_cutoff TEXT NOT NULL,
    headline TEXT NOT NULL,
    moves TEXT NOT NULL,
    drivers TEXT NOT NULL,
    watchlist TEXT NOT NULL,
    ai_execution_id INTEGER,
    UNIQUE (briefing_id, version)
);

CREATE TABLE briefing_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    briefing_version_id INTEGER NOT NULL REFERENCES briefing_versions(id) ON DELETE CASCADE,
    source_kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    label TEXT NOT NULL,
    position INTEGER NOT NULL
);
CREATE INDEX idx_briefing_sources_version ON briefing_sources(briefing_version_id, position);

CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    range_start TEXT NOT NULL,
    range_end TEXT NOT NULL,
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted')),
    created_by TEXT REFERENCES users(id),
    created_at TEXT NOT NULL
);
CREATE INDEX idx_reports_created ON reports(created_at DESC);

CREATE TABLE report_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    data_cutoff TEXT NOT NULL,
    requester_id TEXT REFERENCES users(id),
    created_at TEXT NOT NULL,
    UNIQUE (report_id, version)
);
CREATE INDEX idx_report_versions_report ON report_versions(report_id, version DESC);

CREATE TABLE report_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_version_id INTEGER NOT NULL REFERENCES report_versions(id) ON DELETE CASCADE,
    source_kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    label TEXT NOT NULL,
    position INTEGER NOT NULL
);
CREATE INDEX idx_report_sources_version ON report_sources(report_version_id, position);

CREATE TABLE ai_tasks (
    id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL CHECK (task_type IN ('market_briefing','news_summarization','chat_query','report_generation','analysis')),
    user_id TEXT REFERENCES users(id),
    permission_scope TEXT NOT NULL,
    input TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_ai_tasks_user ON ai_tasks(user_id);
CREATE INDEX idx_ai_tasks_type ON ai_tasks(task_type);

CREATE TABLE ai_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES ai_tasks(id) ON DELETE CASCADE,
    model TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    tools_used INTEGER NOT NULL,
    latency_ms INTEGER NOT NULL,
    cost_usd REAL NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('succeeded','fallback','failed','validation_failed')),
    validation TEXT NOT NULL,
    output TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_ai_executions_task ON ai_executions(task_id);
CREATE INDEX idx_ai_executions_created ON ai_executions(created_at DESC);

CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id TEXT REFERENCES users(id),
    actor_role TEXT,
    action TEXT NOT NULL,
    object_type TEXT,
    object_id TEXT,
    result TEXT NOT NULL,
    classification TEXT,
    detail TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);
CREATE INDEX idx_audit_actor ON audit_log(actor_id);
CREATE INDEX idx_audit_action ON audit_log(action);

CREATE TABLE drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL CHECK (group_name IN ('supply','demand','geopolitics','logistics','macro')),
    label TEXT NOT NULL,
    detail TEXT NOT NULL,
    direction TEXT NOT NULL,
    strength INTEGER NOT NULL,
    as_of TEXT NOT NULL,
    classification TEXT NOT NULL CHECK (classification IN ('public','internal','confidential','restricted'))
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    route TEXT NOT NULL,
    created_at TEXT NOT NULL,
    read_at TEXT
);
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
