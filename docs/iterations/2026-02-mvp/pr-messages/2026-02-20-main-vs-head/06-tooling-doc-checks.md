# PR-06: tooling checks для README и just-документации

## Goal

Закрыть пробелы в документационном качестве: автоматизировать проверку ссылок в `README` и синхронизацию описаний `just`-рецептов с фактическим `justfile`.

## Scope

- Коммиты: `f2e50b1, 0b90544`.
- Добавлены tooling-скрипты:
  - `scripts/check_readme_links.py`
  - `scripts/check_just_docs.py`
- Добавлены/обновлены docs:
  - `docs/_meta/JUST-COMMANDS.md`
  - разделы в `README.md`.
- Добавлены команды в `justfile`:
  - `readme-links-check`
  - `just-docs-check`
- Public API: **No public API change (tooling/docs only)**.

## Requirement coverage

- US/UC/NFR: `N/A (tooling/docs)`.
- AT: `N/A`.

## How to run checks

```bash
just readme-links-check
just just-docs-check
```

## Summary

- Введена автоматическая валидация ссылок README против файловой структуры проекта.
- Добавлена проверка полноты документации `just`-команд относительно `justfile`.
- Сформирован отдельный справочник `JUST-COMMANDS.md` с I/O-контрактами.
- Обновлены точки входа в README для developer workflow.
- Снижен риск устаревания документации при добавлении новых рецептов.

## Evidence

- `just readme-links-check`:
  - ожидаемый результат: `exit code 0`, битых ссылок в `README.md` нет.
- `just just-docs-check`:
  - ожидаемый результат: `exit code 0`, команды в `docs/_meta/JUST-COMMANDS.md` соответствуют `justfile`.
- Проверено вручную:
  - документ `docs/_meta/JUST-COMMANDS.md` покрывает текущие recipes и назначение.

## Risks

- Любые переименования файлов без обновления README начнут валить check и требуют синхронных правок.
- Возможны ложные срабатывания link-check при нестандартных markdown-ссылках.
- Рост числа `just`-команд повышает стоимость ручного ревью без обновления справочника.

## Follow-ups

- Включить оба checks в стандартный pre-PR локальный прогон.
- Добавить эти проверки в CI-stage, если не включены централизованно.
- Договориться о правиле: новые `just`-команды добавлять только вместе с обновлением `JUST-COMMANDS.md`.

