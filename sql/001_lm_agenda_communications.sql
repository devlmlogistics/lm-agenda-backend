CREATE SCHEMA IF NOT EXISTS lm_agenda;

CREATE TABLE IF NOT EXISTS lm_agenda.users (
    id BIGSERIAL PRIMARY KEY,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('DRIVER', 'OPERATIONS', 'SUPERVISOR')),
    driver_code TEXT,
    driver_name TEXT,
    access_token_hash TEXT UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS users_driver_code_unique
    ON lm_agenda.users (upper(trim(driver_code)))
    WHERE driver_code IS NOT NULL;

CREATE TABLE IF NOT EXISTS lm_agenda.messages (
    id BIGSERIAL PRIMARY KEY,
    delivery_order TEXT NOT NULL,
    author_user_id BIGINT NOT NULL REFERENCES lm_agenda.users(id),
    body TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ,
    CHECK (body IS NULL OR length(body) <= 10000)
);

CREATE INDEX IF NOT EXISTS messages_order_created_idx
    ON lm_agenda.messages (delivery_order, created_at, id);

CREATE TABLE IF NOT EXISTS lm_agenda.attachments (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL REFERENCES lm_agenda.messages(id) ON DELETE CASCADE,
    object_key TEXT NOT NULL UNIQUE,
    original_filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes > 0 AND size_bytes <= 15728640),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS lm_agenda.message_reads (
    message_id BIGINT NOT NULL REFERENCES lm_agenda.messages(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL REFERENCES lm_agenda.users(id) ON DELETE CASCADE,
    read_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (message_id, user_id)
);

CREATE TABLE IF NOT EXISTS lm_agenda.push_subscriptions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES lm_agenda.users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL UNIQUE,
    p256dh TEXT NOT NULL,
    auth TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_used_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS lm_agenda.settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_by BIGINT REFERENCES lm_agenda.users(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO lm_agenda.settings (key, value)
VALUES ('retention_days', '90')
ON CONFLICT (key) DO NOTHING;

CREATE TABLE IF NOT EXISTS lm_agenda.audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor_user_id BIGINT REFERENCES lm_agenda.users(id),
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

