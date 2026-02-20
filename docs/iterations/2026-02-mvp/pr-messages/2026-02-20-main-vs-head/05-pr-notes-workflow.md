# PR-05: PR notes workflow и markdown registry

## Goal

Сделать PR-описания трассируемыми и воспроизводимыми через `git notes`, с удобным markdown-реестром и автоматизацией синхронизации/проверки в локальном workflow.

## Scope

- Коммиты: `c9a60fc, 951323d`.
- Добавлены и настроены process-артефакты:
  - `docs/_meta/PR-NOTES.md`
  - `docs/_meta/pr-notes/index.md`
  - `docs/_meta/pr-notes/notes/*.md`
  - `scripts/pr_notes_registry.py`
  - `.githooks/pre-push`
  - рецепты в `justfile` (`notes-*`, `notes-registry-*`).
- Обновлены entrypoints в `README.md` и `AGENTS.md`.
- Public API: **No public API change (process/docs only)**.

## Requirement coverage

- US/UC/NFR: `N/A (process/docs)`.
- AT: `N/A`.

## How to run checks

```bash
just notes-registry-refresh
just notes-registry-lint
```

## Summary

- Зафиксирован единый процесс хранения PR-описаний в `refs/notes/commits`.
- Добавлен генератор markdown-реестра notes с one-note-per-file представлением.
- Внедрён pre-push hook для синхронизации notes и раннего фейла при проблемах.
- Добавлены just-команды для чтения/обновления/push notes.
- В реестр внесены стартовые заметки по ключевым коммитам.

## Evidence

- `just notes-registry-refresh`:
  - ожидаемый результат: обновлён `docs/_meta/pr-notes/index.md` и `notes/*.md`.
- `just notes-registry-lint`:
  - ожидаемый результат: `OK: PR notes registry is consistent with git notes.`.
- Проверено вручную:
  - `git notes --ref refs/notes/commits list` показывает notes entries,
  - index содержит ссылки на соответствующие файлы notes.

## Risks

- `git notes` не всегда пушатся автоматически вместе с веткой без отдельного push refs/notes.
- При squash/rebase необходимо повторно навешивать notes на новые SHA.
- Ошибка конфигурации hooks path (`core.hooksPath`) может отключить pre-push guard.

## Follow-ups

- Добавить напоминание о `git push <remote> refs/notes/commits:refs/notes/commits` в PR template.
- Зафиксировать правила пере-привязки notes после squash merge.
- Рассмотреть CI-проверку консистентности реестра notes на PR-пайплайне.

