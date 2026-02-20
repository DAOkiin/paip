# PR-03: Query Catalog bootstrap и governance baseline

## Goal

Ввести базовый governance-контур Query Catalog: стандарты, схему, политику валидации, CI-скрипты и карту артефактов, чтобы query-контракты были проверяемыми и трассируемыми.

## Scope

- Коммиты: `1770cd7, afe585d, 0524eb8`.
- Добавлены/обновлены артефакты Query Catalog:
  - `query-catalog/query-catalog.schema.json`
  - `query-catalog/policy.template.yaml`
  - `query-catalog/query-catalog.yaml`
  - `query-catalog/README.md`
  - `query-catalog/requirements-qc.txt`
  - `docs/_meta/QC-STANDARD.md`
  - `skills/query-catalog-steward.md`
- Добавлены валидационные entrypoints:
  - `scripts/qc_validate.py`
  - `scripts/qc_validate_ci.sh`
  - команды в `justfile`.
- Документы с устаревшими notes перемещены в архив (`docs/_archive/.../docs_and_sdlc_arch/*`).
- Public API: **No public API change (tooling/governance only)**.

## Requirement coverage

- US/UC/NFR: `N/A (tooling/governance)`.
- AT: `N/A`.

## How to run checks

```bash
just qc-setup
just qc-validate
bash scripts/qc_validate_ci.sh
just test
```

## Summary

- Формализован стандарт Query Catalog как источник истины для query-контрактов.
- Введены schema/policy проверки для предотвращения дрейфа между кодом и реестром.
- Обновлён `query-catalog.yaml` с регистрацией runtime/debug query IDs.
- Подготовлены CI-ориентированные сценарии валидации.
- Архивированы устаревшие docs-notes, чтобы снизить шум в актуальном контуре.

## Evidence

- `just qc-setup`:
  - ожидаемый результат: зависимости QC установлены.
- `just qc-validate`:
  - ожидаемый результат: `OK: Query Catalog validation passed.`.
- `bash scripts/qc_validate_ci.sh`:
  - ожидаемый результат: CI-валидация проходит с `exit code 0`.
- `just test`:
  - ожидаемый результат: основной тестовый набор проходит.

## Risks

- Неконсистентность между кодом и `query-catalog.yaml` может возвращаться при изменениях без обновления реестра.
- Скриптовая валидация требует дисциплины запуска локально до пуша.
- При ужесточении policy возможен рост количества false-positive предупреждений на переходном этапе.

## Follow-ups

- Постепенно включить stricter QC-проверки (usage/drift) как обязательные в CI.
- Добавить короткий how-to по обновлению query registry для разработчиков.
- Вынести QC-checks в pre-merge workflow (если не включено на уровне CI-конфига).

