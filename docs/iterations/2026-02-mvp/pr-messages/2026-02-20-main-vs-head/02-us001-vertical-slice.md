# PR-02: US-001 vertical slice (event-level monitoring + DX)

## Goal

Реализовать рабочий end-to-end vertical slice US-001: от поиска источников через SearXNG до event-level дедупликации, уведомлений в Telegram и объяснимой истории, с CLI/DX-командами для операционного использования.

## Scope

- Коммиты: `3ee9820, b02d79f, 40efd0c, ec325b6, b5b3230, 77ae745`.
- Добавлены/обновлены основные модули runtime:
  - `src/paip/searx_client.py`
  - `src/paip/extractors.py`
  - `src/paip/models.py`
  - `src/paip/pipeline.py`
  - `src/paip/db.py`
  - `src/paip/notifier.py`
  - `src/paip/scheduler.py`
  - `src/paip/cli.py`, `src/paip/debug.py`
- Добавлены DX entrypoints:
  - `just monitor-add`, `just run-once`, `just history`, `just logs`, `just stats`, `just telegram-preview`.
- Обновлены iteration docs по текущему срезу (`docs/iterations/2026-02-mvp/*`) и требованиям.
- Добавлены тесты vertical slice (`tests/test_vertical_slice.py`).
- Public API/интерфейсы:
  - CLI сценарий мониторинга и истории реализован как основной пользовательский интерфейс.
  - `history` отражает event-level поля (title/city/venue/date/source/reason/time).

## Requirement coverage

- US: `US-001`.
- UC: `UC-001`, `UC-002`, `UC-003`, `UC-005`.
- NFR: `NFR-001`, `NFR-002`, `NFR-006`.
- AT: `AT-001`, `AT-002`, `AT-003`, `AT-004`, `AT-005`, `AT-006`, `AT-007`, `AT-008`, `AT-009`, `AT-010`.

## How to run checks

```bash
just test
```

## Summary

- Реализован E2E-поток `SearXNG -> extraction -> event dedup/resolution -> Telegram -> history`.
- Введена event-level модель с детерминированной логикой по новым/обновлённым/дублирующим событиям.
- Добавлены scheduler/manual trigger сценарии с записью run-результатов и ошибок.
- Добавлены DX-команды для запуска, отладки и просмотра payload/истории без ручного SQL.
- Итерационные документы и traceability обновлены под фактическую архитектуру US-001.
- Тестовый пакет покрывает ключевые acceptance сценарии vertical slice.

## Evidence

- `just test`:
  - ожидаемый результат: `exit code 0`, тесты vertical slice проходят.
- Проверено по коду и тестам:
  - pipeline корректно обрабатывает `new_events`, `updated_events`, `duplicates`,
  - ошибки внешних интеграций фиксируются в run/history без остановки scheduler lifecycle,
  - `history` выводит event-level поля и объяснимые причины уведомлений.

## Risks

- Интеграционная устойчивость зависит от внешних сервисов (SearXNG/Telegram) и их SLA.
- Изменения затрагивают большой runtime-контур (pipeline/db/cli/scheduler), что повышает риск регрессий при дальнейших правках.
- При росте объёма данных потребуется оптимизация запросов и индексов для history/run retrieval.

## Follow-ups

- Добавить smoke/contract тесты, выполняемые на реальном SearXNG sandbox.
- Усилить мониторинг scheduler (метрики duration/failure rate на монитор).
- Подготовить отдельный документ с операционными runbook-сценариями для on-call.

