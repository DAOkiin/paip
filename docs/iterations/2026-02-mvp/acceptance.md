# Acceptance — 2026-02-mvp (US-001 event-level)

- **AT-001 (US-001):** пользователь создаёт монитор и выполняет `run once`; новые события приходят в Telegram и попадают в history.
- **AT-002 (US-001, UC-003):** повторный запуск с теми же событиями не отправляет дубль-уведомления (`new_events=0`, `duplicates>0`).
- **AT-003 (US-001, UC-001):** scheduler-trigger выполняет запуск без ручного вызова и фиксирует `trigger=interval`.
- **AT-004 (UC-001, NFR-002):** ошибка SearXNG (timeout/500) сохраняется как failed run; scheduler продолжает работу.
- **AT-005 (UC-005, NFR-001):** ошибка Telegram сохраняется в notifications со status `failed`; run/history сохраняются.
- **AT-006 (US-001, NFR-001):** `history` показывает event-level поля: title/city/venue/date/source/reason/time.
- **AT-007 (UC-002):** claim без обязательных полей не попадает в `events`.
- **AT-008 (UC-003):** изменение даты или venue для того же `source_url` фиксируется как `updated_event`.
- **AT-009 (UC-001):** unsupported source учитывается в `unsupported_sources`, run завершается `completed`.
- **AT-010 (NFR-006):** DX-команды (`just monitor-add/run-once/history/stats/telegram-preview`) выполняют E2E-path без ручного `source`.

## Способ прогона

- Автоматически: `just test`.
- Ручной smoke:
  1. `just monitor-add ...`
  2. `just run-once <id>`
  3. `just stats <id> 10`
  4. `just telegram-preview <id> 10`
  5. `just history <id> 20`
