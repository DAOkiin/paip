# Reviews & Baselines — 2026-02-mvp

## Requirements Baseline (Design Input)
- [x] Выбранные US/UC/NFR перечислены в `01_vision.md`
- [x] Acceptance отражает event-level сценарии (`new_event`, `event_updated`, `duplicate`)
- [x] `traceability.md` заполнен по цепочке `US/UC/NFR -> Design -> AT`
- [x] Scope ограничен MVP без расширения global-требований

Sign-off: @codex  Date: 2026-02-19

## Design Baseline (Design Output)
- [x] `04_architecture.md` описывает event-centric контур и контракты
- [x] БД-схема в коде соответствует документации (`source_hits`, `event_claims`, `events`, `notifications`)
- [x] Дедуп/резолв формализован event key v1 + update по `source_url`
- [x] Local tooling зафиксирован: `justfile` для setup/test/run/history/stats

Sign-off: @codex  Date: 2026-02-19

## Validation Baseline
- [x] Acceptance покрывает event-level scope итерации
- [x] Unit/Pipeline тесты зелёные (`just test`)
- [x] Ручной smoke определён (`monitor-add -> run-once -> stats -> telegram-preview -> history`)
- [x] Evidence обновлён по текущей модели, без промежуточных narrative-артефактов

Evidence:
- `.venv/bin/pytest -q` -> `13 passed`
- `just test` -> `13 passed`
- smoke: `just monitor-add` -> monitor `id=1`, `just run-once 1` -> `new_events=36`, `duplicates=103`, `unsupported_sources=1`
- smoke inspect: `just stats 1 5`, `just logs 1 5`, `just telegram-preview 1 3`

Sign-off: @codex  Date: 2026-02-19
