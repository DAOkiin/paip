# 01 Vision — 2026-02-mvp

## Scope этой подитерации

### Selected Requirements
- US-001
- UC-001, UC-002, UC-003, UC-005
- NFR-001, NFR-002, NFR-006

### In
- Один вертикальный сценарий US-001: мониторинг событий по городу/теме.
- Источник: SearXNG (внешний endpoint через env).
- Запуск: manual + interval scheduler.
- Exact dedup по canonical URL.
- Telegram уведомления и история сигналов в SQLite.

### Out
- Temporal orchestration (отложено на следующий этап).
- Multi-tenant и авторизация.
- UI/дашборд.
- Near-duplicate dedup и сложная explainability.

## Wedge

Пользователь создаёт монитор, запускает его вручную или по расписанию, получает уведомление в Telegram только по новым результатам, а затем видит историю с причиной срабатывания.

## Метрики

- E2E: `monitor add -> run once -> telegram notification` проходит без ручных правок кода.
- Dedup: повторный запуск с теми же результатами не создаёт новое уведомление.
- Traceability: для уведомления доступно `source/time/reason` в истории.
- Stability: ошибка поиска или Telegram фиксируется в run history без падения scheduler.
