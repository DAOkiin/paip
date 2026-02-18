# 04 Architecture — 2026-02-mvp (US-001 slice)

## Контур

```text
MonitorSpec (CLI)
  -> APScheduler (manual/interval trigger)
    -> SearXNG client (search)
      -> Normalizer (SearchHit)
        -> Canonicalizer + exact dedup
          -> SQLite (raw_hits, canonical_items, runs)
            -> Telegram notifier
              -> notifications + history
```

## Технические решения

- Язык/рантайм: Python.
- Хранилище: SQLite (`PAIP_DB_PATH`).
- Оркестрация: `APScheduler` на этом этапе; Temporal запланирован позже.
- Source adapter: SearXNG JSON API (`SEARXNG_BASE_URL`).
- Уведомления: Telegram bot token (`TELEGRAM_BOT_TOKEN`), fallback в stdout.

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
  - `TELEGRAM_BOT_TOKEN` (required for delivery)
  - `PAIP_LOG_LEVEL` (default `INFO`)

## Модули

- `paip.db`: schema + CRUD + history queries.
- `paip.searx_client`: поиск и нормализация сырого результата в `SearchHit`.
- `paip.pipeline`: run lifecycle, dedup, notification routing.
- `paip.notifier`: Telegram отправка и обработка ошибок.
- `paip.scheduler`: interval jobs по `monitors.interval_min`.
- `paip.cli`: пользовательский entrypoint.

## Трассируемые решения

- UC-001: ingestion через `searx_client` и `pipeline`.
- UC-002: единый `SearchHit` и `CanonicalItem`.
- UC-003: dedup в `pipeline` + уникальность `(monitor_id, canonical_url)`.
- UC-005: `notifications` + `history` query.
- NFR-001: история содержит source/time/reason.
- NFR-002: повторный run не создаёт дубли.
- NFR-006: все операции доступны через CLI.
