# 01 Vision — 2026-02-mvp

## Scope этой итерации

### Selected Requirements
- US-001
- UC-001, UC-002, UC-003, UC-005
- NFR-001, NFR-002, NFR-006

### In
- Один вертикальный сценарий US-001: мониторинг уникальных событий по городу/теме.
- Discovery источников: SearXNG через внешний endpoint (`SEARXNG_BASE_URL`).
- Extraction: Eventbrite-style adapter (MVP), формирование `EventClaim`.
- Event-level дедуп и резолв в `Event` (new/update/duplicate).
- Ручной и interval запуск (`run once`, `run scheduler`).
- Telegram уведомления по `new_event` и `event_updated`.
- История уведомлений в SQLite с event-level причиной.

### Out
- Temporal orchestration (следующий этап).
- Multi-tenant и авторизация.
- UI/дашборд.
- Near-duplicate и advanced entity resolution.
- Второй extractor beyond Eventbrite-style (следующий этап).

## Wedge

Пользователь добавляет монитор по Бангкоку/теме, запускает pipeline, получает сигналы по уникальным событиям, видит историю с причиной (`new_event`/`event_updated`) и источником.

## Метрики итерации

- E2E: `monitor add -> run once -> telegram notification -> history` проходит без правки кода.
- Event novelty: повторный запуск на тех же данных не отправляет дубли (`duplicates > 0`, `new_events = 0`).
- Event update: при изменении даты/venue для того же источника фиксируется `updated_events > 0`.
- Explainability: у каждого уведомления есть `source_name`, `source_url`, `reason`, `created_at`.
- Stability: ошибка SearXNG или Telegram фиксируется в истории run/notifications без падения scheduler.
