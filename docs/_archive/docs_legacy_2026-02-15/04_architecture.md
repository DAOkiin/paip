# 04. Architecture

## Tech Stack (MVP)

| Слой | Технология | Почему |
|------|-----------|--------|
| Language | Python 3.12+ | Экосистема, скорость прототипирования |
| API | FastAPI | Async, автодоки, быстро |
| Orchestration | Temporal | Durable workflows, retries, visibility |
| Database | PostgreSQL | JSONB, full-text search, надёжность |
| HTTP Scraping | aiohttp + BeautifulSoup | Лёгкий, async |
| JS Rendering | Playwright | Когда нужен headless browser |
| Telegram | aiogram 3 | Async Telegram bot framework |
| Containerization | Docker Compose | Локальный деплой всего стека |
| Testing | pytest + pgTAP | App tests + DB-level tests |

---

## Data Flow

```
┌─────────────┐     ┌───────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│   Sources   │────▶│  Fetch    │────▶│ Normalize│────▶│ Dedup     │────▶│  Store   │
│ SearXNG     │     │ (Adapter) │     │          │     │           │     │ Postgres │
│ Twitter     │     └───────────┘     └──────────┘     └───────────┘     └──────────┘
│ Websites    │                                                                │
└─────────────┘                                                                │
                                                                               ▼
                    ┌───────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
                    │ Telegram  │◀────│ Format   │◀────│ Filter /  │◀────│ Diff /   │
                    │ Bot       │     │ Digest   │     │ Alert     │     │ Detect   │
                    └───────────┘     └──────────┘     └───────────┘     └──────────┘
```

---

## Компоненты

### 1. Scheduler (Temporal)
- Запускает Workflows по расписанию (cron)
- Каждый Monitor = Temporal Schedule → CollectWorkflow
- Visibility API для мониторинга статусов

### 2. CollectWorkflow (Temporal Workflow)
Основной workflow:
```
CollectWorkflow(monitor_id):
  1. Activity: fetch(source_config) → list[RawDocument]
  2. Activity: normalize(raw_docs) → list[Document]
  3. Activity: dedup(documents) → list[Document] (новые)
  4. Activity: detect_changes(documents, previous_snapshot) → list[Change]
  5. Activity: notify(changes, channel) → Notification
```

Каждый Activity — idempotent, с retry policy.

### 3. Adapters (Activities)
- `SearxngAdapter` — HTTP GET к SearXNG API, парсинг JSON
- `TwitterAdapter` — Twitter API v2, bearer token auth
- `WebsiteAdapter` — aiohttp/Playwright + CSS selectors или LLM extraction
- Каждый адаптер возвращает `list[AdapterResult]`

### 4. Processing Pipeline (Activities)
- `NormalizeActivity` — raw → unified Document format
- `DedupActivity` — content_hash exact match + simhash для near-dupes
- `DiffActivity` — сравнение с предыдущим snapshot (для цен и изменений)
- `AlertActivity` — проверка правил (цена < порог, новый документ)

### 5. Notification (Activity)
- `TelegramNotifyActivity` — форматирование + отправка через aiogram
- Форматы: single alert, digest (batch)

### 6. API (FastAPI) — минимальный
- `POST /monitors` — создать монитор
- `GET /monitors` — список мониторов
- `GET /monitors/{id}/results` — результаты
- `POST /monitors/{id}/run` — ручной запуск
- Telegram-бот как основной UI (команды: /add, /list, /run, /digest)

---

## Deployment (MVP)

```yaml
# docker-compose.yml (концепт)
services:
  postgres:       # PostgreSQL 16
  temporal:       # Temporal dev server (all-in-one)
  worker:         # Python Temporal worker (все Activities)
  api:            # FastAPI app
  telegram-bot:   # aiogram bot (может быть частью api)
```

---

## Решения по архитектуре

| Вопрос | Решение | Почему |
|--------|---------|--------|
| Temporal как SoR? | Нет. PostgreSQL = source of truth. Temporal = оркестратор | Проще запрашивать данные, меньше coupling |
| Kafka нужен? | Нет в MVP. Temporal Schedules достаточно | Меньше инфры, быстрее старт |
| Отдельные микросервисы? | Нет. Монолит с модулями | MVP скорость > масштабирование |
| Как хранить raw HTML? | В PostgreSQL (text column) | До ~100K документов норм, потом S3 |
| Real-time vs polling? | Polling (Temporal Schedules) | Проще, предсказуемо, достаточно для MVP |
