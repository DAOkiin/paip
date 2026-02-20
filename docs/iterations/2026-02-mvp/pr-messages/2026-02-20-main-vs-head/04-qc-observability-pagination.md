# PR-04: query observability + pagination hardening

## Goal

Закрыть операционные риски Query Catalog слоя: добавить runtime correlation через `query_id`-логи и убрать unbounded list-запросы за счёт пагинации в DB/CLI/scheduler контуре.

## Scope

- Коммиты: `1d6f9f1, 56332bc`.
- Runtime observability:
  - `src/paip/db.py`: emission `query_id` в store data-access paths.
  - `src/paip/debug.py`: emission `query_id` в debug SQL paths.
- Pagination:
  - `Store.list_monitors(..., limit, offset)`
  - `Store.list_runs(..., limit, offset)`
  - `Store.list_notifications(..., limit, offset)`
  - paging loop в `src/paip/scheduler.py`.
- CLI изменения:
  - `paip monitor list --limit --offset` в `src/paip/cli.py`.
- Обновлён `query-catalog/query-catalog.yaml`:
  - параметры `limit/offset`,
  - `contract.pagination`,
  - убраны `allow_unbounded*` исключения.
- Добавлены тесты пагинации и query_id correlation (`tests/test_vertical_slice.py`).
- Public API/интерфейсы:
  - добавлены CLI-флаги `--limit` и `--offset`,
  - query-contract для list operations стал пагинированным.

## Requirement coverage

- US/UC/NFR: `N/A (infra/runtime quality)`.
- AT: `N/A`.

## How to run checks

```bash
just qc-validate
bash scripts/qc_validate_ci.sh
just test
```

## Summary

- Добавлены runtime-emitted `query_id` логи для трассировки DB/debug paths.
- Удалены unbounded list операции: внедрена сквозная пагинация в store/scheduler/cli.
- Query Catalog синхронизирован с фактическими контрактами list-запросов.
- Добавлены тесты на пагинацию и корреляцию логов.
- Поведение pipeline по бизнес-логике не изменено, усилено только наблюдение и масштабируемость.

## Evidence

- `just qc-validate`:
  - ожидаемый результат: `OK: Query Catalog validation passed.`.
- `bash scripts/qc_validate_ci.sh`:
  - ожидаемый результат: CI-режим QC-валидации проходит.
- `just test`:
  - ожидаемый результат: тесты проходят, включая пагинационные кейсы.
- Проверено по контрактам:
  - `query-catalog.yaml` и call sites согласованы по `limit/offset`.

## Risks

- Изменение дефолтных лимитов может повлиять на ожидаемое поведение внешних automation-скриптов.
- При некорректном использовании offset paging возможны пропуски или дубли в нестабильных выборках.
- Увеличенный объём runtime-логов с `query_id` может потребовать корректировки log retention.

## Follow-ups

- Ввести централизованную политику default limits для всех list endpoints.
- Добавить нагрузочные тесты на paging-loop scheduler при большом числе monitors.
- Подготовить dashboard/alerts по query_id-correlated ошибкам доступа к БД.

