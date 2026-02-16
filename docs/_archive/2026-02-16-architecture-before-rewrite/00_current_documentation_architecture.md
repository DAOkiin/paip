# Архитектура документации на момент архивации (до переработки с нуля)

Дата фиксации: `2026-02-16`.

## 1) Ключевая модель организации

Была реализована многослойная структура:

- `docs/product/*` — продуктовые артефакты и целевые требования.
- `docs/research/*` — сырые материалы, черновики, внешние/внутренние исследования.
- `docs/iterations/*` — артефакты по конкретным итерациям и трассируемости.
- `docs/_meta/*` — мета-правила и шаблоны управления документацией.
- `docs/ops/*` — эксплуатационная документация.
- `docs/_archive/*` — исторические версии и ранее удалённые шаблоны.

Перед архивированием в корне документации также был файл `docs/README.md` как точка входа в навигацию.

## 2) Полная структура файлов на момент фиксации

### 2.1 Корень

- На момент архивирования:
  - `docs/README.md` (перенесён в архив).

### 2.2 Продуктовый слой (`docs/product`)

- `docs/product/global_vision.md` (оставлен как базовый `global_*` артефакт)
- `docs/product/global_user_stories.md` (оставлен как базовый `global_*` артефакт)
- `docs/product/global_use_cases.md` (оставлен как базовый `global_*` артефакт)
- `docs/product/needs.md`
- `docs/product/glossary.md`
- `docs/product/nfr.md`
- `docs/product/personas.md`
- `docs/product/risks_and_assumptions.md`

### 2.3 Архивный слой (`docs/_archive`)

- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/01_vision.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/02_use_cases.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/03_domain_model.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/04_architecture.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/05_event_model.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/06_data_model.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_archive/docs_legacy_2026-02-15/07_mvp_plan.md`

### 2.4 Мета-документы (`docs/_meta`)

- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/doc_map.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/doc_system.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/documentation_structure.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/glossary_policy.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/naming_and_ids.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/review_and_baselines.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/templates.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/_meta/traceability_policy.md`

### 2.5 Итерационный слой (`docs/iterations`)

- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/README.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/current.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/README.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/scope.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/selected_requirements.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/architecture.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/domain_model.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/event_model.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/data_model.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/acceptance.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/traceability.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/plan.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/open_questions.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/iterations/2026-02-mvp/release_notes.md`

### 2.6 Эксплуатационный слой (`docs/ops`)

- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/ops/README.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/ops/installation.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/ops/runbooks.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/ops/observability.md`

### 2.7 Исследовательский слой (`docs/research`)

- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw_research.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/01_requirements.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/system_goals_and_arch.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Natural_Language_интерфейс.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Второе_Исследование_решений_для_парсинга.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Исследование_решений_для_парсинга.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Категоризация_веб-страниц.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Основные_концепции_AJTBD.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Проектирование_системы_агентов.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Проектирование_системы_парсинга.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Сбор_use-кейсов_проекта.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Системные_требования_Temporal.md`
- `docs/_archive/2026-02-16-architecture-before-rewrite/previous_documents/research/raw/exports/ChatGPT-Структура_парсинга_данных.md`

## 3) Что было назначение каждого слоя

- **Product**: единство продуктовой логики — vision, user stories, use cases, personas, glossary, NFR и риски.
- **Research**: накопление сырых идей и источников для повторного использования и проверки гипотез.
- **Iterations**: формализация требований в рабочих итерациях и связь с трассируемостью (scope/AC/plan).
- **Meta**: правила ведения требований, ID и структуру документации.
- **Ops**: эксплуатационный контур (подготовлен, но не развёрнут под production).
- **Archive**: историческая прослеживаемость предыдущих версий.

## 4) Внутренние зависимости

- `docs/product/global_vision.md` — базовое основание для `global_*` и остальных продуктовых артефактов.
- `docs/product/global_user_stories.md` и `docs/product/global_use_cases.md` — ориентиры для `iterations/*/selected_requirements.md`, `scope.md`, `acceptance.md` и `traceability.md`.
- `docs/research/raw_research.md` — индексировал сырой материал и связывал его с ранее построенными артефактами.
- `docs/_meta/doc_system.md` и `docs/_meta/doc_map.md` описывали «правила и карту» всей документации.

## 5) Причины архивирования текущего состояния

- Пользовательская задача — пересобрать документацию с нуля (кроме `docs/product/global_*`) для снижения шума и перезапуска структуры в более удобной форме.
- Важно сохранить это описание, чтобы не потерять память о том, какая архитектура была построена и какие зависимости уже существовали.
