# Raw research (`docs/research/raw/**`)

Цель: законспектировать “рыхлые” документы из `docs/research/raw/` и разложить их по будущим артефактам:

- `01_vision.md`
- `02_use_cases.md`
- `03_domain_model.md`
- `04_architecture.md`
- `05_event_model.md`
- `06_data_model.md`
- `07_mvp_plan.md`

Ограничение: файлы `docs/0*.md` **не открывались** (по правилу).

---

## Рекомендуемый порядок углублённого чтения raw (чтобы быстрее собрать артефакты)

1. `docs/research/raw/01_requirements.md` — видение + стартовый каталог кейсов.
2. `docs/research/raw/exports/ChatGPT-Структура_парсинга_данных.md` — сквозная структура системы + сущности + таксономия use cases.
3. `docs/research/raw/exports/ChatGPT-Проектирование_системы_парсинга.md` — SDLC-структура + DDL-first + event-driven crawling паттерны.
4. `docs/research/raw/exports/ChatGPT-Категоризация_веб-страниц.md` — как хранить/получать `page_type` (оси классификации, сигналы).
5. `docs/research/raw/exports/ChatGPT-Проектирование_системы_агентов.md` — границы MVP, компоненты, кандидаты стека, план на сегодня.
6. `docs/research/raw/system_goals_and_arch.md` — A4-canvas (goal/scope/use cases/stack/plan/risks).
7. `docs/research/raw/exports/ChatGPT-Сбор_use-кейсов_проекта.md` — шаблон “карточек” + приоритизация P0/P1/P2.
8. `docs/research/raw/exports/ChatGPT-Natural_Language_интерфейс.md` — NL→DSL, versioned context, validation/guardrails.
9. `docs/research/raw/exports/ChatGPT-Системные_требования_Temporal.md` — инфраструктурные/перфоманс-ограничения Temporal.
10. `docs/research/raw/exports/ChatGPT-Исследование_решений_для_парсинга.md` — ландшафт инструментов + статьи/кейсы Temporal.
11. `docs/research/raw/exports/ChatGPT-Второе_Исследование_решений_для_парсинга.md` — расширенное исследование + pain points + гайды Temporal/Agents.

---

## Реестр файлов (суть + привязка)

|  # | Файл                                                                    | Суть (1–2 предложения)                                                                                                                                                                | Потенциальные артефакты                                                                                                                  |
|---:|-------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
|  1 | `docs/research/raw/01_requirements.md`                                           | “Universal Data Ingestion & Synthesis Platform”: конструктор ingestion-пайплайнов (адаптеры + правила) + реестр use cases (monitoring/aggregation/knowledge/trends/syndication).      | `01_vision.md`, `02_use_cases.md`, `03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`, `07_mvp_plan.md` |
|  2 | `docs/research/raw/system_goals_and_arch.md`                                     | Шаблон A4 Project Canvas: цель/метрики, MVP in/out, 5–9 use cases, “mental model” архитектуры и стек, план+риски.                                                                     | `01_vision.md`, `02_use_cases.md`, `04_architecture.md`, `07_mvp_plan.md`                                                                |
|  3 | `docs/research/raw/exports/ChatGPT-Natural_Language_интерфейс.md`               | Идея NL-интерфейса для агентов: читаемый лог + формальный JSON/DSL, “поставка контекста” (схемы+код) с версионированием и валидацией.                                                 | `03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`                                                      |
|  4 | `docs/research/raw/exports/ChatGPT-Второе_Исследование_решений_для_парсинга.md` | Обзор OSS-инструментов для пайплайнов + “pain points/вопросы” для выбора стека; далее — заметки про async-стек OpenAI (как claim) и подборка гайдов Temporal для агентских сценариев. | `04_architecture.md`, `05_event_model.md`, `07_mvp_plan.md`                                                                              |
|  5 | `docs/research/raw/exports/ChatGPT-Исследование_решений_для_парсинга.md`        | Подбор OSS-компонентов (Scrapy/Pyspider/Airbyte/dlt/Temporal) + разбор статей/кейсов “Temporal для scraping/пайплайнов/агентов” на уровне компонентов.                                | `04_architecture.md`, `05_event_model.md`, `07_mvp_plan.md`                                                                              |
|  6 | `docs/research/raw/exports/ChatGPT-Категоризация_веб-страниц.md`                 | Исследование “page type”: schema.org WebPage subtypes + main entity type + topic taxonomy; академические жанровые таксономии; сигналы в HTML (schema.org/OG).                         | `03_domain_model.md`, `06_data_model.md`, `04_architecture.md`                                                                           |
|  7 | `docs/research/raw/exports/ChatGPT-Проектирование_системы_агентов.md`            | “Рабочий документ v0.1”: MVP границы, скелет use cases, компоненты event-driven pipeline, кандидаты стека, план/вопросы; затем — валидация vision и список близких OSS-решений.       | `01_vision.md`, `02_use_cases.md`, `04_architecture.md`, `06_data_model.md`, `07_mvp_plan.md`                                            |
|  8 | `docs/research/raw/exports/ChatGPT-Проектирование_системы_парсинга.md`           | SDLC-структура артефактов + DDL-first подход (DDL как контракт, queries/fixtures/tests) + ресёрч event-driven crawling архитектур (frontier, politeness, URL state, topics).          | `03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`, `07_mvp_plan.md`                                    |
|  9 | `docs/research/raw/exports/ChatGPT-Сбор_use-кейсов_проекта.md`                  | Шаблон “карточек” use cases + универсальный каталог сценариев по стадиям пайплайна + приоритизация P0/P1/P2.                                                                          | `02_use_cases.md`, `07_mvp_plan.md`                                                                                                      |
| 10 | `docs/research/raw/exports/ChatGPT-Системные_требования_Temporal.md`             | Зависимости/ресурсы Temporal Server, bottlenecks, shards; ориентиры latency/throughput и как бенчмаркать; сравнение Temporal vs Dagster по “скорости оркестрации”.                    | `04_architecture.md`, `07_mvp_plan.md`                                                                                                   |
| 11 | `docs/research/raw/exports/ChatGPT-Структура_парсинга_данных.md`                 | Короткая декомпозиция системы (мониторинг→нормализация→diff/dedup→rules→notifications) + расширения (поисковик событий, корпус эссе) + структурная таксономия use cases (10 блоков).  | `01_vision.md`, `02_use_cases.md`, `03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`                   |

---

## 1) `docs/research/raw/01_requirements.md`

### Суть

Видение “платформы-инжеста”: не один парсер, а конструктор пайплайнов. Источники подключаются адаптерами, обработка собирается из переиспользуемых “правил/инструментов”.

### Ключевые идеи

- Event-driven платформа для сбора, нормализации, анализа и синдикации из Web/RSS/API/Social.
- Пайплайн формирует пользователь (человек/агент) под кейс.
- “Правила” = инструменты (extraction, NER, категоризация, дедупликация, …).
- Цель — из потока данных получить структурированные знания/инсайты/контент.

Use cases (сгруппированы):

- Monitoring/alerting: скидки, GitHub search → триггеры → уведомления.
- Aggregation/indexing: агрегатор событий → нормализация + entity resolution → единая витрина/API.
- Knowledge corpus: философские эссе → классификация + NER → граф знаний.
- Narrative tracking: крипто-нарративы → кластеризация/частоты/тональность → отчёты.
- Syndication: генерация статей/сценариев на базе собранных фактов.

### Потенциальные артефакты

`01_vision.md`, `02_use_cases.md`, `03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Платформенная формула:** *adapters* + *pipelines* + *rules/tools*.
- **Триггерная модель:** “порог/условие” → уведомление.
- **Два режима продукта:** alerting (реактивный мониторинг) и indexing/search (витрина без дублей).
- **Entity Resolution как ядро агрегаторов** (особенно для событий).
- **Knowledge graph контур:** Author → Essay → Concept (+ пригодность под RAG).
- **Контент-пайплайн:** “сбор фактов” → “структурирование” → “синтез”.

---

## 2) `docs/research/raw/system_goals_and_arch.md`

### Суть

Шаблон “A4 Project Canvas” (5 блоков) для удержания проекта в рамках: цель, MVP границы, use cases, архитектурный mental model, план+риски.

### Ключевые идеи

- **MVP In/Out** как защита от расползания.
- **5–9 use cases**: “1 кейс = 1 ценность”, а не техоперация.
- Архитектура как поток `Source → Orchestrator → Fetch → Extract → NLP → Trends → Storage → Output`.
- План на сегодня и на 1–2 недели; 3 риска максимум.

### Потенциальные артефакты

`01_vision.md`, `02_use_cases.md`, `04_architecture.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Outcome/метрики:** явно зафиксировать “как понять, что работает”.
- **Scope-guard:** если задача не укладывается в блоки — её сейчас нет.
- **Сжатый стек (5–7 технологий):** язык, оркестрация, storage, scraping, NLP.

---

## 3) `docs/research/raw/exports/ChatGPT-Natural_Language_интерфейс.md`

### Суть

Идея интерфейса “естественный язык ↔ формальное действие” для агентов: один и тот же NL-запрос становится стабильным JSON/DSL-пакетом действий в рамках конкретной версии “поставки контекста”.

### Ключевые идеи

- У запроса агента есть 2 представления:
   - **читаемое** (для логов/аудита человеком),
   - **формальное** (JSON/код/DSL для выполнения системой).
- “Поставка контекста” = онтология/схемы/код, которые:
   - версионируются,
   - обеспечивают стабильное преобразование NL → action plan,
   - позволяют валидировать, что запрос “не выходит за контекст”.
- Плюсы: прозрачные логи, воспроизводимость, контроль рамок, помощь пользователю в понимании контекста.
- Подобные идеи/референсы: Rasa (domain.yml), DeepPavlov, DSL-SPA (NL→JSON DSL), OpenAI Agents SDK (function calls + guardrails), Pydantic AI (schema validation), Semantic Kernel (plugins/plans), Open Interpreter (NL→код с подтверждением), context.json (переносимый контекст).

### Потенциальные артефакты

`03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Domain:** `ContextPackage`/`ContextVersion`, `AgentRequest`, `FormalAction`, `ToolSchema`, `ValidationError`, `AuditLog`.
- **Версионирование контрактов:** “один и тот же NL при версии X → одинаковый JSON/DSL”.
- **Guardrails/валидация:** проверка полей/разрешённых инструментов/границ контекста.
- **Наблюдаемость:** трассировка “NL → tool calls → результат” как first-class.
- **HITL как вариант валидации:** подтверждение действий человеком (пример из Open Interpreter / HITL-гайдов).

---

## 4) `docs/research/raw/exports/ChatGPT-Второе_Исследование_решений_для_парсинга.md`

### Суть

Большой “комбинированный” документ: обзор OSS-инструментов для ingestion-пайплайнов, затем чеклист проблем/вопросов для выбора стека, затем заметки про async-стек OpenAI (как claim) и подборка гайдов по Temporal для агентских сценариев.

### Ключевые идеи

- Обзор инструментов/подходов:
   - **Scrapy** (web scraping),
   - **Airflow** (DAG/batch orchestration),
   - **NiFi/Camel** (flow/EIP, много коннекторов),
   - **Node-RED/n8n** (workflow automation),
   - **Airbyte/Singer(Meltano)/dlt** (коннекторы и EL(T)).
- “Pain points” для требования к системе:
   - адаптеры (polling vs push; raw vs normalized),
   - планирование/триггеры,
   - надёжность (retries, idempotency, checkpoints),
   - обработка контента (clean/extract/NER/LLM),
   - модель хранения (raw vs curated, версии),
   - ops (очереди, observability, multi-tenant),
   - антибот/право (для веба).
- Блок “OpenAI stack”: перечисляет Python/FastAPI/Postgres/Kafka/K8s/Temporal и т.п. **Важно:** часть утверждений опирается на вторичные источники/вакансии; лучше трактовать как *claim*, а не как факт.
- Temporal для агентов: набор гайдов и паттернов (HITL approvals, activities-as-tools, signals/updates/queries, case studies).

### Потенциальные артефакты

`04_architecture.md`, `05_event_model.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Вопрос “что возвращает адаптер” (контракт):**
   - raw bytes + метаданные,
   - нормализованный документ,
   - доменная сущность.
- **Набор ключевых не-функциональных решений:** частота, объём, SLA, стоимость, наблюдаемость.
- **Temporal agent patterns:** `Signals/Updates/Queries`, approvals/HITL, “tools = activities”, multi-agent orchestration.
- **Сегментация async:** очередь задач vs durable workflows vs stream processing.

---

## 5) `docs/research/raw/exports/ChatGPT-Исследование_решений_для_парсинга.md`

### Суть

Подбор OSS-компонентов под ingestion + Temporal (Scrapy/Pyspider/Airbyte/dlt/…) и отдельная часть — структурированный разбор статей/кейсов, где Temporal применяют для scraping/пайплайнов/агентов.

### Ключевые идеи

- Web scraping как компонент: Scrapy (лёгкий, кодовый) vs Pyspider (UI + встроенный scheduler, но старее и “перекрывает” Temporal по ответственности).
- Коннекторы для API-источников: Airbyte/Airbridge, Singer/Meltano, dlt — как способ быстро подключать YouTube/Twitter/RSS через SDK/коннекторы (с оверхедом, иногда через Docker).
- Рекомендация “hybrid”: Temporal как backbone (оркестрация/расписания/ретраи) + адаптеры как Python-модули.
- В разборе статей повторяются паттерны:
   - workflow оркестрирует последовательность/параллельность activities,
   - child workflows для fan-out (например, по ссылкам),
   - signals для управления/паузы/остановки,
   - результаты лучше складывать во внешнее хранилище и передавать ссылки (не большие payload’ы).
- Минусы Temporal-подхода, которые нужно явно проектировать: инфраструктурный оверхед и **идемпотентность** side effects.

### Потенциальные артефакты

`04_architecture.md`, `05_event_model.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Temporal decomposition:** workflow = “код процесса”, activity = “single-purpose внешняя операция”.
- **Параллельность:** fan-out/fan-in через параллельные activities/child workflows.
- **Управление долгими задачами:** signals (pause/resume/stop), retries/timeouts/heartbeats.
- **Данные:** большие артефакты (HTML/JSON) → object storage; в event-поток/DB → только метаданные/ссылки/хэши.

---

## 6) `docs/research/raw/exports/ChatGPT-Категоризация_веб-страниц.md`

### Суть

Исследование того, как классифицировать страницы (page type/genre) и как лучше хранить это в БД: не одной категорией, а 2–3 осями.

### Ключевые идеи

- **Рекомендация для БД:** 2–3 оси вместо “одной категории”:
   1) Functional Page Type (роль/шаблон страницы, хорошо ложится на schema.org `WebPage` subtypes),
   2) Main Entity Type (что за сущность на странице: Product/Article/SocialMediaPosting/…),
   3) (опционально) Topic taxonomy (IAB, IPTC для новостей).
- Источники типизации:
   - schema.org (`ItemPage`, `CollectionPage`, `ProfilePage`, `SearchResultsPage`, `FAQPage`, … + `mainEntity`),
   - Open Graph `og:type`,
   - академические “web genre” таксономии и датасеты (KI‑04, Santini 7‑web, 20‑genre, CORE, Sharoff macro-genres),
   - e-commerce практические page types (PDP/PLP/cart/checkout/…).
- Типизация веба часто **multi-label** из-за гибридных/динамических страниц.

### Потенциальные артефакты

`03_domain_model.md`, `06_data_model.md`, `04_architecture.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Сущности/справочники:** `page_role`, `main_entity_type`, `topic_category`, `taxonomy_version`.
- **Сигналы извлечения:** schema.org JSON-LD, OG meta-теги, URL/DOM эвристики.
- **Multi-label стратегия:** хранить список тегов/вероятностей или “primary + secondary”.

---

## 7) `docs/research/raw/exports/ChatGPT-Проектирование_системы_агентов.md`

### Суть

Большой “рабочий документ” для старта: MVP границы, use cases, компоненты пайплайна, кандидаты стека, план на сегодня, открытые вопросы. Плюс — проверка формулировки vision и список близких OSS-решений как референсов.

### Ключевые идеи

- MVP: web (+опц. RSS), адаптеры, pipeline fetch→extract→NER/signals→trends→storage, хранение raw+normalized, категоризация страниц.
- Компоненты (high-level): source registry → scheduler/orchestrator (Temporal) → fetch/render → extract/classify → NLP/enrichment → analytics (trends) → storage → API/query → syndication → observability.
- План на сегодня: зафиксировать use cases, стек, архитектурную диаграмму, настроить окружение для agentic dev.
- Open questions: фокус MVP, частота, типы источников, детализация таксономии страниц, семантика “значимого изменения”, форматы выходов.
- Референсы OSS “по духу”: Airbyte/Meltano/CloudQuery (коннекторы+пайплайны), NiFi (процессоры как правила), Scrapy (web ingestion ядро), ScrapeGraphAI (LLM extraction).

### Потенциальные артефакты

`01_vision.md`, `02_use_cases.md`, `04_architecture.md`, `06_data_model.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **MVP decisions list:** источники, storage, оркестрация, способы извлечения (static vs JS), observability.
- **Роли данных:** raw snapshots vs normalized documents vs derived analytics.
- **Список “компонентов уровня C4-L2”** (удобно как основа диаграммы).
- **Открытые вопросы** как обязательный раздел каждого артефакта (чтобы фиксировать неопределённости).

---

## 8) `docs/research/raw/exports/ChatGPT-Проектирование_системы_парсинга.md`

### Суть

Структурирование артефактов SDLC и отдельный сильный блок про DDL-first (DDL как контракт + библиотека запросов + фикстуры + SQL-тесты), плюс ресёрч типовых event-driven crawling архитектур и их “повторяющихся” сущностей.

### Ключевые идеи

- **DDL-first:** разбить модель на подсхемы (Users, Sources/Adapters, Tasks/Scheduling, Runs/Execution, Raw/Normalized, Dedup/Identity, Rules/Notifications).
- **DDL как контракт** + `/db/queries/*.sql` как “как код будет пользоваться БД”.
- **SQL-level tests:** DDL-инварианты, сценарные Given/When/Then, тесты типовых запросов (включая идемпотентность).
- Ресёрч crawling-пайплайнов (Mercator/Heritrix/Frontera/Scrapy Cluster/StormCrawler/AWS serverless/…):
   - URL frontier как отдельная подсистема,
   - politeness (per-host queues/partitioning),
   - состояния URL (discovered/fetched/error/next_fetch_at),
   - разделение “команды/управление” и “результаты crawl” по разным потокам/топикам,
   - важность event schemas/contracts,
   - ретраи/дубли как норма,
   - паттерн “decouple gathering from extraction” (immutable raw → поздний парсинг/пересчёт).

### Потенциальные артефакты

`03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Bounded contexts для БД:** Users/Auth, Sources/Adapters, Scheduling/Tasks, Execution/Runs, Raw/Curated, Dedup/Identity, Rules/Notifications.
- **State machines:** статусы task/run/notification как часть модели данных.
- **Change detection model:** “что считается изменением” как осевое решение.
- **Event surface:** команды (ingest requests) vs результаты (crawl artifacts) vs статусы (fetch errors, retries).
- **Frontier/URL state как домен:** очереди по хостам, next_fetch_at, seen-tests.
- **Decouple gather/extract:** raw артефакты неизменяемы, derived-результаты пересчитываемы.

---

## 9) `docs/research/raw/exports/ChatGPT-Сбор_use-кейсов_проекта.md`

### Суть

Помогает “упаковать” use cases: шаблон карточки + универсальный каталог сценариев по стадиям (ingestion → parsing → quality → output → ops) и приоритизация P0/P1/P2.

### Ключевые идеи

- Формат карточки use case: название, роль, 1 фраза процесса, вход→выход, ценность.
- Каталог сценариев: ingestion, extraction/normalization, HITL/валидация, экспорт/интеграции, наблюдаемость/аудит, versioning результата.
- Приоритизация: P0 (ядро), P1 (усилители), P2 (потом).

### Потенциальные артефакты

`02_use_cases.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Use case как value-unit:** описывать через результат и I/O.
- **HITL слой** как отдельный класс сценариев (если нужен).
- **Версионирование результата** как сценарий/требование.

---

## 10) `docs/research/raw/exports/ChatGPT-Системные_требования_Temporal.md`

### Суть

Конспект зависимостей и ресурсных “рычагов” Temporal Server + ориентиры по latency/throughput и как получать точные цифры бенчмарком; сравнение Temporal vs Dagster по задержке оркестрации.

### Ключевые идеи

- Temporal требует persistence DB (Postgres/MySQL/Cassandra; SQLite для dev).
- Visibility: для масштабов обычно рекомендуют Elasticsearch/OpenSearch.
- Server = несколько сервисов (frontend/history/matching/worker); bottleneck часто в DB и history.
- Shards — важный масштабный параметр (упоминается рекомендация для small prod).
- “Скорость workflow” = overhead оркестрации + время activities + DB/network.
- Для точных цифр: бенчмаркать (maru, benchmark-latency) на своём окружении.
- Temporal ≈ низкая задержка оркестрации (десятки/сотни мс), Dagster ≈ чаще батч/окна (секунды/минуты) из-за tick/scheduler/run launcher.

### Потенциальные артефакты

`04_architecture.md`, `07_mvp_plan.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Execution semantics:** идемпотентные activities, ретраи, timeouts, heartbeats.
- **Контроль роста history:** batching + ContinueAsNew/периодические workflows.
- **Обоснование выбора оркестратора:** near-real-time vs batch окна.

---

## 11) `docs/research/raw/exports/ChatGPT-Структура_парсинга_данных.md`

### Суть

Самая компактная “сквозная” декомпозиция домена: мониторинг источников по NL-запросу → ingestion → нормализация → diff/dedup → rules → notifications. Дальше документ расширяет модель на “поисковик событий” и “корпус эссе”, и заканчивает таксономией use cases (10 блоков).

### Ключевые идеи

- Минимальный пайплайн:
   1) NL → спецификация мониторинга,
   2) scheduler создаёт runs,
   3) adapters → raw artifacts,
   4) extract/normalize → entities,
   5) dedup + diff vs snapshots,
   6) rules → events,
   7) notifications.
- Базовые сущности: `Monitor/Intent`, `Source`, `Adapter`, `Job/Run`, `RawArtifact`, `NormalizedEntity`, `Snapshot/State`, `Rule`, `Event`, `Notification`.
- Для “агрегатора событий”: `CanonicalEvent`, `EventOccurrence`, `SourceListing` + отдельный компонент entity resolution + индекс.
- Для “корпуса эссе”: критерии → список → сбор эссе → разметка тем → граф концептов; перечислены артефакты хранения.
- Таксономия use cases (10 блоков): monitoring, change tracking, aggregation, dedup/entity resolution, classification/tagging, concept structures/graphs, narratives/trends, insights, triggers/notifications, syndication/content production.

### Потенциальные артефакты

`01_vision.md`, `02_use_cases.md`, `03_domain_model.md`, `04_architecture.md`, `05_event_model.md`, `06_data_model.md`.

### Концепты и потенциальные идеи (блоки для переноса)

- **Product modes:** Monitoring vs Index/Search vs Synthesis.
- **Canonical vs Source representation:** “каноническая сущность” и “как в источнике” (для трассировки и обновлений).
- **Use case taxonomy** как основа структуры `02_use_cases.md`.
- **Формула пайплайна:** “сбор → нормализация → дедуп → семантика → динамика → инсайты → синдикация”.

