# 05. Event Model

События и переходы состояний в системе.

---

## Job Lifecycle

```
         schedule/manual trigger
                  │
                  ▼
┌─────────┐  start   ┌─────────┐  success  ┌───────────┐
│ PENDING │─────────▶│ RUNNING │──────────▶│ COMPLETED │
└─────────┘          └─────────┘           └───────────┘
                          │
                          │ error
                          ▼
                     ┌─────────┐  retry (automatic)  ┌─────────┐
                     │ FAILED  │────────────────────▶│ RUNNING │
                     └─────────┘                     └─────────┘
```

Temporal управляет retry: каждый Activity имеет retry policy (3 attempts, backoff).

---

## Системные события (для логирования и будущих расширений)

### Ingestion Events

| Event | Когда | Payload |
|-------|-------|---------|
| `job.started` | Запуск сбора | `{job_id, monitor_id, source_type}` |
| `job.completed` | Успешный сбор | `{job_id, stats: {fetched, new, dupes}}` |
| `job.failed` | Ошибка сбора | `{job_id, error, attempt}` |
| `document.fetched` | Получен сырой документ | `{raw_doc_id, url, content_hash}` |
| `document.normalized` | Документ нормализован | `{doc_id, raw_doc_id}` |
| `document.duplicate` | Обнаружен дубль | `{doc_id, duplicate_of_id, method}` |
| `document.new` | Новый уникальный документ | `{doc_id, monitor_id, title}` |

### Price Events

| Event | Когда | Payload |
|-------|-------|---------|
| `price.captured` | Снят snapshot цены | `{monitor_id, price, currency}` |
| `price.changed` | Цена изменилась | `{monitor_id, old_price, new_price, diff_pct}` |
| `price.alert` | Цена ниже порога | `{monitor_id, price, threshold}` |

### Notification Events

| Event | Когда | Payload |
|-------|-------|---------|
| `notification.sent` | Уведомление отправлено | `{notification_id, channel, monitor_id}` |
| `notification.failed` | Ошибка отправки | `{notification_id, error}` |

---

## MVP реализация

В MVP события — это **записи в таблицу `events`** в PostgreSQL. Не Kafka, не Redis Streams. Простой append-only лог.

```sql
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,           -- 'document.new', 'price.changed', etc.
    payload JSONB NOT NULL,
    monitor_id UUID REFERENCES monitors(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_monitor ON events(monitor_id);
CREATE INDEX idx_events_created ON events(created_at);
```

Позже, при необходимости, заменяем на Kafka/NATS без изменения бизнес-логики.

---

## Идемпотентность

Каждый Activity должен быть idempotent:

| Activity | Idempotency key | Метод |
|----------|-----------------|-------|
| Fetch | `(monitor_id, scheduled_time)` | Пропуск если Job уже exists |
| Normalize | `raw_document_id` | Upsert by raw_doc_id |
| Dedup | `content_hash` | Check before insert |
| Notify | `(monitor_id, digest_period)` | Check if notification already sent |
