# Just Command Reference

Source of truth for command behavior: `justfile`.

This page documents each `just` recipe with quick input/output contracts so it is clear what each command expects and returns.

## Conventions

- `just` loads variables from shell and `.env` (`set dotenv-load := true`).
- Most commands assume virtualenv already exists (`just setup`).
- Non-zero exit code means command failed and should be treated as blocking for CI/process.

## Recipes

### `just help`
- Input: no arguments.
- Output: prints available recipe names (equivalent to `just --list`).
- Side effects: none.

### `just setup`
- Input: no arguments.
- Output: creates `.venv` and installs project in editable mode with dev extras.
- Side effects: writes `.venv/` and installs Python dependencies.

### `just test`
- Input: no arguments.
- Output: runs `pytest -q` and prints test summary (`passed/failed`).
- Side effects: reads tests and may create local pytest cache.

### `just qc-setup`
- Input: no arguments.
- Output: installs Query Catalog validator dependencies from `query-catalog/requirements-qc.txt`.
- Side effects: updates packages in `.venv`.

### `just qc-validate`
- Input: no arguments.
- Output: validates Query Catalog (`query-catalog/query-catalog.yaml`) against policy/template and prints `OK` or `ERROR`.
- Side effects: none (read-only validation).

### `just qc-validate-ci`
- Input: no arguments.
- Output: runs CI-equivalent QC validation flow and prints full validator output.
- Side effects: may install/confirm QC dependencies in `.venv`.

### `just hooks-install`
- Input: no arguments.
- Output: configures git hooks path and makes pre-push hook executable.
- Side effects: writes git config `core.hooksPath=.githooks`; changes file mode for `.githooks/pre-push`.

### `just notes-list`
- Input: no arguments.
- Output: lists git notes from `refs/notes/commits` as `<note_object_sha> <commit_sha>`.
- Side effects: none.

### `just notes-show SHA`
- Input: required `SHA` (commit hash that has a note).
- Output: prints markdown body of note attached to that commit.
- Side effects: none.

### `just notes-push REMOTE='origin'`
- Input: optional `REMOTE` (default `origin`).
- Output: pushes `refs/notes/commits` to selected remote.
- Side effects: updates remote notes ref.

### `just notes-registry-refresh`
- Input: no arguments.
- Output: regenerates markdown registry from git notes:
  `docs/_meta/pr-notes/index.md` and `docs/_meta/pr-notes/notes/*.md`.
- Side effects: rewrites generated files in `docs/_meta/pr-notes/`.

### `just notes-registry-lint`
- Input: no arguments.
- Output: checks consistency between `refs/notes/commits` and `docs/_meta/pr-notes/*`; prints `OK` or `ERROR`.
- Side effects: none (read-only).

### `just readme-links-check FILE='README.md'`
- Input: optional `FILE` (default `README.md`).
- Output: validates local markdown/map-first links and prints validation summary.
- Side effects: none (read-only).

### `just just-docs-check FILE='docs/_meta/JUST-COMMANDS.md'`
- Input: optional `FILE` path to command reference markdown.
- Output: verifies every recipe in `justfile` has a matching section with `Input/Output`; prints `OK` or `ERROR`.
- Side effects: none (read-only).

### `just monitor-add TITLE CITY TOPIC QUERY INTERVAL_MIN CHAT_ID`
- Input: required positional args:
  `TITLE`, `CITY`, `TOPIC`, `QUERY`, `INTERVAL_MIN`, `CHAT_ID`.
- Output: creates monitor and prints `Created monitor id=<id>`.
- Side effects: inserts row into monitors table in configured DB.

### `just monitor-list`
- Input: no arguments.
- Output: prints monitor rows (`id/title/city/topic/interval/enabled`) or `No monitors`.
- Side effects: none (read-only DB query).

### `just run-once MONITOR_ID`
- Input: required `MONITOR_ID`.
- Output: runs one pipeline iteration and prints JSON run result.
- Side effects: executes full pipeline (DB writes, network calls, optional Telegram send).

### `just run-scheduler`
- Input: no arguments.
- Output: starts blocking scheduler loop until interrupted.
- Side effects: repeatedly runs monitor pipelines by configured intervals.

### `just history MONITOR_ID LIMIT='20'`
- Input: required `MONITOR_ID`; optional `LIMIT` (default `20`).
- Output: prints notification/event history lines for monitor or `No history`.
- Side effects: none (read-only DB query).

### `just logs MONITOR_ID='1' LIMIT='20'`
- Input: optional `MONITOR_ID` (default `1`), optional `LIMIT` (default `20`).
- Output: same as `history` (alias to `paip history`), prints history lines.
- Side effects: none (read-only DB query).

### `just stats MONITOR_ID='1' LIMIT='10'`
- Input: optional `MONITOR_ID` (default `1`), optional `LIMIT` (default `10`), optional env `PAIP_DB_PATH`.
- Output: prints DB counters, recent runs/events/notifications for monitor.
- Side effects: none (read-only debug queries).

### `just telegram-preview MONITOR_ID='1' LIMIT='10' RUN_ID=''`
- Input: optional `MONITOR_ID`, `LIMIT`, optional `RUN_ID` (if empty, latest run with notifications is used).
- Output: prints rendered Telegram messages from stored notification payloads.
- Side effects: none (read-only debug queries).

### `just env-example`
- Input: no arguments.
- Output: prints required/optional environment variable template.
- Side effects: none.
