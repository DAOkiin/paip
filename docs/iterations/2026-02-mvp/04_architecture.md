# 04 Architecture — 2026-02-mvp (US-001 event slice)

## Контур

```text
MonitorSpec (CLI)
  -> APScheduler (manual/interval trigger)
    -> SearXNG client (source discovery)
      -> SourceHit
        -> Extractor registry
          -> Eventbrite-style extractor
            -> EventClaim validation
              -> Event resolver (new / updated / duplicate)
                -> SQLite (source_hits, event_claims, events, runs)
                  -> Telegram notifier
                    -> notifications + history
```

## Технические решения

- Язык/рантайм: Python.
- Хранилище: SQLite (`PAIP_DB_PATH`).
- Оркестрация: `APScheduler` в MVP; Temporal позже.
- Source discovery: SearXNG JSON API (`SEARXNG_BASE_URL`).
- Extraction: Eventbrite-style extractor (JSON-LD Event payloads).
- Уведомления: Telegram bot token (`TELEGRAM_BOT_TOKEN`), fallback в stdout.
- Локальный command runner: `justfile` (MVP dev workflow).

## Публичные контракты

- CLI:
  - `paip monitor add --title --city --topic --query --interval-min --chat-id`
  - `paip monitor list`
  - `paip run once --monitor-id`
  - `paip run scheduler`
  - `paip history --monitor-id --limit`

- ENV:
  - `PAIP_DB_PATH` (default `./tmp/paip.db`)
  - `SEARXNG_BASE_URL` (required)
  - `SEARXNG_API_KEY` (optional)
  - `TELEGRAM_BOT_TOKEN` (required для доставки)
  - `PAIP_LOG_LEVEL` (default `INFO`)

## Доменная модель MVP

- `EventClaim`: извлечённое утверждение из конкретного источника.
- `Event`: уникальная сущность события в рамках монитора.
- `Notification`: запись отправки по `event_id` с `reason` и `status`.

Обязательные поля `Event`: `title`, `city`, `venue`, `start_at|start_date`, `source_url`, `source_name`, `extracted_at`, `confidence`.

## Дедуп и резолв (v1)

- Event key v1: `normalize(title) + normalize(city) + normalize(venue) + start_date`.
- Полный матч ключа и без изменений атрибутов: `duplicate`.
- Совпадение по `source_url` с изменением атрибутов: `updated_event`.
- Новый ключ без существующего события: `new_event`.
- Unsupported domain: учитывается в `unsupported_sources`, run не падает.

## Run counters

`run once` возвращает:
- `fetched_sources`
- `claims_extracted`
- `new_events`
- `updated_events`
- `duplicates`
- `unsupported_sources`
- `status`, `error`

## Трассируемые решения

- UC-001: discovery + scheduler (`searx_client`, `pipeline`, `scheduler`).
- UC-002: нормализация в `EventClaim` и `Event`.
- UC-003: event-level dedup/resolution в `pipeline` + `events` unique key.
- UC-005: Telegram + `notifications` + event-level history query.
- NFR-001: history содержит `reason`, `source_name`, `source_url`, `created_at`.
- NFR-002: повторный run на тех же событиях не дублирует уведомления.
- NFR-006: все операции доступны через CLI/just workflow.
