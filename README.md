# PAIP

Event-centric monitoring MVP: поиск источников через SearXNG, извлечение event-claims, дедуп/резолв в уникальные события, уведомления в Telegram и история причин.

## US-001 vertical slice (текущий этап)

Рабочий путь:

`SearXNG discovery -> extractor (Eventbrite-style) -> EventClaim validation -> Event dedup/resolution -> Telegram -> history`

## Быстрый старт

```bash
just setup
```

Переменные окружения:

```bash
export SEARXNG_BASE_URL="https://your-searxng.example"
export TELEGRAM_BOT_TOKEN="<telegram-bot-token>"
# optional
export PAIP_DB_PATH="./tmp/paip.db"
export PAIP_LOG_LEVEL="INFO"
export SEARXNG_API_KEY=""
```

`just` берёт значения из shell и автоматически подгружает `.env`, если файл существует.

## Justfile workflow

Показать доступные команды:

```bash
just
```

Основные команды:

```bash
just test
just monitor-add "Bangkok events" "Bangkok" "tech" "eventbrite bangkok tech events" 30 "<telegram-chat-id>"
just monitor-list
just run-once 1
just history 1 20
just logs 1 20
just stats 1 10
just telegram-preview 1 10
```

Подсказка по env:

```bash
just env-example
```

## CLI (v0)

```bash
paip monitor add --title "Bangkok events" --city "Bangkok" --topic "tech" --query "eventbrite bangkok tech events" --interval-min 30 --chat-id "<telegram-chat-id>"
paip monitor list
paip run once --monitor-id 1
paip run scheduler
paip history --monitor-id 1 --limit 20
```

## Проверки

```bash
just test
just readme-links-check
just just-docs-check
```

## Документация

- SDLC entrypoint: `SDLC.md`
- Product requirements:
  - `docs/product/global_vision.md`
  - `docs/product/global_user_stories.md`
  - `docs/product/global_use_cases.md`
  - `docs/product/nfr.md`
- Current iteration pack: `docs/iterations/2026-02-mvp/`
- Query Catalog map:
  - Standard (source of truth): `docs/_meta/QC-STANDARD.md`
  - Steward skill: `skills/query-catalog-steward.md`
  - Registry entrypoint: `query-catalog/README.md`
- PR notes map:
  - Process guide: `docs/_meta/PR-NOTES.md`
  - Registry index: `docs/_meta/pr-notes/index.md`
- Just commands map:
  - Recipe reference (input/output): `docs/_meta/JUST-COMMANDS.md`
