# 07. MVP Plan

Цель: работающий прототип за 3-4 спринта (спринт = 1 неделя).

---

## Phase 1: Skeleton (неделя 1)

**Цель:** запускаемый стек, первый адаптер, данные в БД.

- [ ] Project scaffolding: pyproject.toml, src layout, pytest
- [ ] Docker Compose: PostgreSQL + Temporal dev server
- [ ] Alembic setup + initial migration (DDL из 06_data_model)
- [ ] Базовые модели (SQLAlchemy / dataclasses)
- [ ] Temporal worker skeleton (connect + register)
- [ ] SearXNG adapter: fetch → list[AdapterResult]
- [ ] CollectWorkflow v1: fetch → save raw_documents
- [ ] Ручной запуск workflow через CLI/script

**Результат:** `python -m paip.cli collect --query "bitcoin news"` → строки в `raw_documents`.

---

## Phase 2: Pipeline (неделя 2)

**Цель:** нормализация, дедупликация, scheduling.

- [ ] NormalizeActivity: raw → Document (title, body extraction)
- [ ] DedupActivity: SHA-256 exact + simhash near-duplicate
- [ ] PriceCaptureActivity: extract price → price_snapshots
- [ ] CollectWorkflow v2: fetch → normalize → dedup → save
- [ ] Temporal Schedules: cron-based периодический запуск
- [ ] Website adapter: aiohttp + CSS selectors
- [ ] Twitter adapter: API v2 basic

**Результат:** мониторы работают по расписанию, дубли фильтруются.

---

## Phase 3: Notifications (неделя 3)

**Цель:** Telegram-бот, алерты, дайджесты.

- [ ] Telegram-бот (aiogram 3): /start, /add, /list, /run
- [ ] TelegramNotifyActivity: отправка alert/digest
- [ ] AlertActivity: price threshold check, new document alert
- [ ] DigestActivity: агрегация за период, форматирование
- [ ] Telegram: inline-кнопки для управления мониторами

**Результат:** бот присылает дайджест новых новостей и алерты по ценам.

---

## Phase 4: Polish (неделя 4)

**Цель:** стабильность, удобство, документация.

- [ ] Минимальный FastAPI: CRUD monitors, manual trigger
- [ ] Error handling: graceful failures, retry tuning
- [ ] Logging: structured logging (structlog)
- [ ] Health checks
- [ ] README с инструкцией по запуску
- [ ] End-to-end тесты (docker compose up → create monitor → get digest)

**Результат:** систему можно показать и объяснить за 5 минут.

---

## Риски

| Риск | Митигация |
|------|-----------|
| Temporal learning curve | Начинаем с dev server (single binary), используем готовые примеры из temporal-community |
| Twitter API ограничения / стоимость | В MVP можно заменить на RSS/Nitter, Twitter как P1 |
| Дедупликация неточная | Начинаем с exact hash, simhash добавляем итеративно |

---

## Definition of Done (MVP)

- [ ] 3 адаптера работают (SearXNG, website scraper, Twitter/RSS)
- [ ] Мониторы запускаются по расписанию через Temporal
- [ ] Дубликаты фильтруются (exact match)
- [ ] Изменения цен детектятся
- [ ] Telegram-бот присылает дайджесты и алерты
- [ ] Запускается одной командой: `docker compose up`
