# PAIP

Коротко: система мониторинга/агрегации изменений из источников с дедупликацией, историей и уведомлениями.

## US-001 vertical slice (текущий этап)

Реализован путь: `SearXNG -> normalize -> exact dedup -> history -> Telegram`.

## Быстрый старт (dev)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Env:

```bash
export SEARXNG_BASE_URL="https://your-searxng.example"
export TELEGRAM_BOT_TOKEN="<telegram-bot-token>"
# optional
export PAIP_DB_PATH="./tmp/paip.db"
export PAIP_LOG_LEVEL="INFO"
export SEARXNG_API_KEY=""
```

Создать монитор:

```bash
paip monitor add \
  --title "Bangkok events" \
  --city "Bangkok" \
  --topic "tech" \
  --query "events" \
  --interval-min 30 \
  --chat-id "<telegram-chat-id>"
```

Список мониторов:

```bash
paip monitor list
```

Ручной запуск:

```bash
paip run once --monitor-id 1
```

Плановые запуски:

```bash
paip run scheduler
```

История уведомлений:

```bash
paip history --monitor-id 1 --limit 20
```

## Проверки

```bash
pytest
```

## Документация (источник истины)

- SDLC: `SDLC.md` (подробно: `docs/_meta/sdlc.md`)
- Vision: `docs/product/global_vision.md`
- User Stories: `docs/product/global_user_stories.md`
- Use Cases: `docs/product/global_use_cases.md`
- NFR: `docs/product/nfr.md`
- Current iteration: `docs/iterations/2026-02-mvp/`
- ADR: `docs/adr/`
