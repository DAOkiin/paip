# PR-01: docs foundation и реструктуризация документации

## Goal

Сформировать единый фундамент документации проекта: зафиксировать структуру product/iteration/SDLC документов, архивировать устаревшие материалы и подготовить трассируемую базу для последующих продуктовых и инженерных PR.

## Scope

- Блок документационных коммитов `5baa475 .. 5497a62`.
- Обновлены и/или добавлены ключевые документы:
  - `SDLC.md`
  - `docs/product/*`
  - `docs/iterations/2026-02-mvp/*`
  - `docs/research/raw*`
  - `docs/_archive/2026-02-16-architecture-before-rewrite/*`
- Обновлены навигационные точки входа в `README.md` и `AGENTS.md`.
- Public API: **No public API change (docs-only)**.

## Requirement coverage

- US/UC/NFR: `N/A (docs-only)`.
- AT: `N/A`.

## How to run checks

```bash
just readme-links-check
just just-docs-check
```

## Summary

- Собрана и нормализована структура документации для текущего этапа (`2026-02-mvp`).
- Вынесены и сохранены исторические материалы в `_archive`, чтобы не терять контекст решений.
- Уточнены продуктовые документы (vision, user stories, use cases, NFR, glossary).
- Сформированы iteration-артефакты (`01_vision`, `04_architecture`, `acceptance`, `traceability`, `reviews`).
- Зафиксированы точки входа в процессы SDLC и требования для агентов.

## Evidence

- `just readme-links-check`:
  - ожидаемый результат: `exit code 0`, все ссылки в `README.md` валидны.
- `just just-docs-check`:
  - ожидаемый результат: `exit code 0`, документация по `just` синхронизирована с `justfile`.
- Проверено вручную:
  - архивные документы перемещены в `docs/_archive/...`,
  - актуальные документы доступны по новым путям в `docs/product` и `docs/iterations/2026-02-mvp`.

## Risks

- Большой объём документационных изменений затрудняет ревью без пофайлового прохода.
- Возможны устаревшие внутренние ссылки в редко используемых архивных документах.
- Перенос исторических материалов может создать ложное впечатление, что они активны, если не соблюдать entrypoints из `README.md`.

## Follow-ups

- Добавить регулярный docs-link check для основных документационных каталогов, не только `README.md`.
- Зафиксировать короткий style-guide по именованию будущих research export файлов.
- В следующем PR держать изменения docs и code максимально раздельно, чтобы уменьшать diff и ускорять ревью.

