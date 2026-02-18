# Acceptance — 2026-02-mvp (US-001)

- **AT-001 (US-001):** пользователь создаёт монитор и выполняет `run once`; новые результаты приходят в Telegram и попадают в историю.
- **AT-002 (US-001, UC-003):** повторный запуск с теми же результатами не отправляет дубль-уведомления.
- **AT-003 (US-001, UC-001):** scheduler-trigger выполняет запуск без ручного вызова и фиксирует `trigger=interval`.
- **AT-004 (UC-001, NFR-002):** ошибка SearXNG (timeout/500) сохраняется как failed run; scheduler продолжает работу.
- **AT-005 (UC-005, NFR-001):** ошибка Telegram сохраняется в notifications со status `failed`; run завершается без потери history.
- **AT-006 (US-001, NFR-001):** `history` показывает для уведомления источник, время и причину.

## Способ прогона

- Автоматически: `pytest` (unit + integration-lite).
- Ручной smoke:
  1. `paip monitor add ...`
  2. `paip run once --monitor-id <id>`
  3. `paip history --monitor-id <id> --limit 10`
