# PR Message Archive: 2026-02-20 (`main..HEAD`)

Архив готовых PR-сообщений для разбиения текущей длинной ветки на последовательный стек из 7 PR.

- Scope: полный диапазон `main..HEAD` на дату `2026-02-20`.
- Режим источника истины: markdown-файлы + `git notes` (`refs/notes/commits`).
- Язык сообщений: русский.

## Stack map

| PR | Message file | PR branch | Base branch | Source commits |
|---|---|---|---|---|
| PR-01 | `01-docs-foundation.md` | `codex/pr1-docs-foundation` | `main` | `5baa475 .. 5497a62` |
| PR-02 | `02-us001-vertical-slice.md` | `codex/pr2-us001-vertical-slice` | `codex/pr1-docs-foundation` | `3ee9820, b02d79f, 40efd0c, ec325b6, b5b3230, 77ae745` |
| PR-03 | `03-qc-bootstrap.md` | `codex/pr3-qc-bootstrap` | `codex/pr2-us001-vertical-slice` | `1770cd7, afe585d, 0524eb8` |
| PR-04 | `04-qc-observability-pagination.md` | `codex/pr4-qc-observability-pagination` | `codex/pr3-qc-bootstrap` | `1d6f9f1, 56332bc` |
| PR-05 | `05-pr-notes-workflow.md` | `codex/pr5-pr-notes-workflow` | `codex/pr4-qc-observability-pagination` | `c9a60fc, 951323d` |
| PR-06 | `06-tooling-doc-checks.md` | `codex/pr6-tooling-doc-checks` | `codex/pr5-pr-notes-workflow` | `f2e50b1, 0b90544` |
| PR-07 | `07-research-state-report.md` | `codex/pr7-research-state-report` | `codex/pr6-tooling-doc-checks` | `c4a05ee` |

## No-op checkpoints

В истории присутствуют два checkpoint-коммита без изменений файлов:

- `9124d01` (`chore: checkpoint before US-001 vertical slice`)
- `e1ef4a3` (`chore: checkpoint before event-level rebuild`)

Под них отдельные PR-сообщения не создаются.

## How to sync each message with git notes

1. Определить SHA целевого коммита в соответствующей PR-ветке.
2. Добавить или обновить note из файла сообщения:

```bash
git notes --ref refs/notes/commits add -f -F <absolute-path-to-message-file.md> <sha>
```

3. Обновить markdown-реестр notes:

```bash
just notes-registry-refresh
```

4. Проверить консистентность:

```bash
just notes-registry-lint
```

5. При `squash/rebase`-merge перевесить тот же текст на итоговый merge SHA.

