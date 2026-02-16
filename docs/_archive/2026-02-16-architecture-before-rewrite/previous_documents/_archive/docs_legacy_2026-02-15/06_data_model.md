# 06. Data Model (DDL-first)

DDL-first: схема — source of truth. Тестируется до application code.

---

## Schema

```sql
-- ============================================================
-- Extensions
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";     -- gen_random_uuid()

-- ============================================================
-- ENUM types
-- ============================================================
CREATE TYPE source_type AS ENUM ('searxng', 'twitter', 'website', 'rss');
CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed');
CREATE TYPE notification_status AS ENUM ('sent', 'failed');

-- ============================================================
-- Sources
-- ============================================================
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type source_type NOT NULL,
    name TEXT NOT NULL,
    config JSONB NOT NULL DEFAULT '{}',
    schedule TEXT,                                -- cron expression: '*/30 * * * *'
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- Monitors
-- ============================================================
CREATE TABLE monitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    pipeline JSONB NOT NULL DEFAULT '[]',        -- ordered list of processing steps
    notify_channel TEXT,                          -- 'telegram:123456789'
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_monitors_source ON monitors(source_id);

-- ============================================================
-- Jobs (collection runs)
-- ============================================================
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    monitor_id UUID NOT NULL REFERENCES monitors(id) ON DELETE CASCADE,
    status job_status NOT NULL DEFAULT 'pending',
    temporal_workflow_id TEXT,                    -- reference to Temporal
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error TEXT,
    stats JSONB DEFAULT '{}',                    -- {fetched, new, dupes}
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_jobs_monitor ON jobs(monitor_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at);

-- ============================================================
-- Raw Documents (immutable)
-- ============================================================
CREATE TABLE raw_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    source_url TEXT NOT NULL,
    content_type TEXT NOT NULL,                   -- 'text/html', 'application/json', 'tweet'
    raw_content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    content_hash TEXT NOT NULL,                   -- SHA-256
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_raw_docs_job ON raw_documents(job_id);
CREATE INDEX idx_raw_docs_hash ON raw_documents(content_hash);

-- ============================================================
-- Documents (normalized, deduplicated)
-- ============================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_document_id UUID UNIQUE NOT NULL REFERENCES raw_documents(id),
    monitor_id UUID NOT NULL REFERENCES monitors(id),
    canonical_url TEXT,
    title TEXT,
    body TEXT,
    published_at TIMESTAMPTZ,
    dedup_key TEXT,                               -- simhash or similar fingerprint
    is_duplicate BOOLEAN NOT NULL DEFAULT false,
    duplicate_of_id UUID REFERENCES documents(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_docs_monitor ON documents(monitor_id);
CREATE INDEX idx_docs_dedup ON documents(dedup_key);
CREATE INDEX idx_docs_created ON documents(created_at);
CREATE INDEX idx_docs_not_dupes ON documents(monitor_id, created_at) WHERE NOT is_duplicate;

-- ============================================================
-- Price Snapshots
-- ============================================================
CREATE TABLE price_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    monitor_id UUID NOT NULL REFERENCES monitors(id) ON DELETE CASCADE,
    price NUMERIC(12, 2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    raw_document_id UUID REFERENCES raw_documents(id),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_prices_monitor ON price_snapshots(monitor_id, captured_at);

-- ============================================================
-- Events (append-only log)
-- ============================================================
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    payload JSONB NOT NULL,
    monitor_id UUID REFERENCES monitors(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_monitor ON events(monitor_id);
CREATE INDEX idx_events_created ON events(created_at);

-- ============================================================
-- Notifications
-- ============================================================
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    monitor_id UUID NOT NULL REFERENCES monitors(id),
    channel TEXT NOT NULL,
    payload JSONB NOT NULL,
    status notification_status NOT NULL DEFAULT 'sent',
    sent_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_monitor ON notifications(monitor_id);

-- ============================================================
-- updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sources_updated BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_monitors_updated BEFORE UPDATE ON monitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

---

## Ключевые запросы

```sql
-- Новые (не дублированные) документы за последние 24 часа для монитора
SELECT d.id, d.title, d.canonical_url, d.published_at
FROM documents d
WHERE d.monitor_id = :monitor_id
  AND d.is_duplicate = false
  AND d.created_at > now() - interval '24 hours'
ORDER BY d.created_at DESC;

-- Последняя цена и предыдущая (для определения изменения)
SELECT price, currency, captured_at
FROM price_snapshots
WHERE monitor_id = :monitor_id
ORDER BY captured_at DESC
LIMIT 2;

-- Проверка дубликата по exact hash
SELECT id FROM raw_documents
WHERE content_hash = :hash
LIMIT 1;

-- Статистика по монитору
SELECT
    count(*) FILTER (WHERE NOT is_duplicate) AS unique_docs,
    count(*) FILTER (WHERE is_duplicate) AS duplicates,
    max(created_at) AS last_doc_at
FROM documents
WHERE monitor_id = :monitor_id;
```

---

## Миграции

Используем **Alembic** (стандарт для Python + SQLAlchemy). Начальная миграция = весь DDL выше. Каждое изменение схемы — новая миграция.
