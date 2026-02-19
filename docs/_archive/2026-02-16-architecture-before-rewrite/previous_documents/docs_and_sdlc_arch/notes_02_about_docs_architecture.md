# Сверка плана артефактов с IEEE 12207 / INCOSE (лёгкий режим, с трассируемостью)

## Кратко (что меняется после чтения `cs460 ieee12207.pdf` и lifecycle-диаграммы)
Твой исходный замысел **полностью согласуется** с SDLC-подходом из IEEE 12207/INCOSE: иметь “global” слой (needs/requirements) и выбирать из него **итерационный scope**, который становится “design input requirements” для архитектуры и дизайна.

После сверки я предлагаю 3 усиления к моему предыдущему плану, чтобы ближе попасть в INCOSE-логику “Design Inputs/Outputs + V&V” без оборонной избыточности:

1) Явно выделить **Needs / Integrated set of needs** (отдельный артефакт, над User Stories/Use Cases).  
2) Явно добавить **V&V гейты** (validation vs verification) как чеклисты/ревью-ритуал (аналог walkthrough/inspection/review из PDF), а не как толстые “records”.  
3) Явно разделить на итерации: **Design Input Requirements (scope)** → **Architecture & Design** → **Acceptance (validation)**, со сквозной матрицей.

Ты выбрал:
- **Строгость:** лёгкий режим
- **Ops/installation:** отложить до деплоя

---

## 1) Минимальный набор артефактов (сопоставление с IEEE 12207 терминами)

### 1.1 Global слой (постоянный “источник истины”)
Папка: `docs/product/`

1) `docs/product/needs.md`  *(новый, лёгкий)*  
   Роль: **Integrated Set of Needs** / stakeholder expectations в терминах INCOSE.  
   Содержимое:
   - кто пользователь(и) и какие “реальные ожидания”
   - какой outcome и какие метрики на уровне продукта
   - ключевые принципы (например “claims vs facts” как смысловая ось)
   - список “не делаем” (глобальные запреты/границы)
   - ссылки на `global_vision.md`, `global_user_stories.md`, `nfr.md`

2) `docs/product/global_user_stories.md`  
   Роль: **SRS-lite** (System Requirements Specification в практическом виде).  
   Содержимое: полный реестр **реальных продуктовых историй** с ID `US-0001…` + acceptance criteria (MVP/Later) + ссылки на UC.

3) `docs/product/global_use_cases.md`  
   Роль: каталог “возможностей системы” (в IEEE-таблице ближе к requirements allocation/описаниям поведения).  
   Содержимое: полный реестр `UC-0001…` (цель, акторы, основной сценарий, альтернативы, постусловия) + ссылки на US.

4) `docs/product/nfr.md`  
   Роль: non-functional requirements (в IEEE-логике это часть требований).  
   Содержимое: наблюдаемость/качество данных/latency/стоимость/надёжность/ограничения.

5) `docs/product/glossary.md`  
   Роль: единая терминология для требований и дизайна.

6) `docs/product/traceability_policy.md` *(новый, маленький)*  
   Роль: “как вести IDs/ссылки/изменения”.  
   Содержимое: правила ID, как ссылаться из документов, что считать baseline, как делать change-log.

---

### 1.2 Итерации (Design Input Requirements → Design Outputs → Validation)
Папка: `docs/iterations/<iteration_id>/`  
Рекомендованный ID: `docs/iterations/2026-02-mvp/`

Внутри оставляем текущий набор “01..07” (как у тебя уже есть), но трактуем их в IEEE/INCOSE-логике:

- `01_vision.md` → **Design Input Requirements (для итерации)**: выбранный scope (US/UC/NFR), IN/OUT, wedge-сценарий, метрики, допущения.
- `02_use_cases.md` → UC, которые входят в итерацию (подмножество глобальных, без дублирования: ссылки по ID).
- `03_domain_model.md`, `05_event_model.md`, `06_data_model.md` → **Design Output Specifications / Detailed Design** (в терминах PDF это SAD/SDD/DDD/… в “лёгкой упаковке”).
- `04_architecture.md` → **SAD-lite** (Software Architecture Description): компоненты, поток, решения, tradeoffs, привязка к требованиям.
- `07_mvp_plan.md` → план реализации (не требования, а delivery plan).

Добавляем 3 тонких файла для V&V и трассируемости (без оборонной бюрократии):

1) `docs/iterations/2026-02-mvp/traceability.md`  
   Матрица: `US/UC/NFR → архитектура/домены/ивенты/таблицы → acceptance tests`.

2) `docs/iterations/2026-02-mvp/acceptance.md`  
   Это твой **TVPL/TVPR-lite**: продуктовые acceptance-сценарии `AT-0001…`, каждый ссылается на `US-xxxx`.

3) `docs/iterations/2026-02-mvp/reviews.md` *(новый)*  
   Это “walkthrough/inspection/review” из PDF, но в виде чеклистов и sign-off:
   - Needs Validation: “строим ли правильное?” (сверка `needs.md` ↔ `global_user_stories.md`)
   - Requirements Validation: “требования непротиворечивы/проверяемы?” (US/UC/NFR)
   - Design Validation: “дизайн покрывает требования?” (traceability заполнена, нет висячих разделов)
   - Design Verification: “дизайн реализуем/тестируем?” (есть acceptance, есть план)
   (Ops/maintenance/installation — TODO до деплоя, как ты выбрал.)

---

## 2) ID и правила трассируемости (жёстко и просто)
- `US-0001…` — глобальные продуктовые истории
- `UC-0001…` — глобальные use cases (возможности)
- `NFR-0001…` — нефункциональные требования
- `AT-0001…` — acceptance сценарии

Правило IEEE-стиля (минимальное):
- Любой раздел в `04_architecture.md` обязан ссылаться минимум на один `US/UC/NFR`.
- Любой `US` выбранный в итерацию обязан иметь минимум один `AT`.
- Любой `AT` обязан ссылаться на `US` (и опционально на `UC`).

---

## 3) Baseline-процесс (лёгкая версия “оборонных” baselines)
На каждую итерацию фиксируем 3 baselines (это отражает “Design Inputs/Outputs” + V&V логику диаграммы):

1) **Requirements Baseline (Iteration Input Baseline)**  
   Готово, когда:
   - `01_vision.md` содержит выбранные `US/UC/NFR`
   - `traceability.md` заполнен хотя бы Coverage-частью
   - `reviews.md`: Requirements Validation отмечено

2) **Design Baseline (Iteration Design Output Baseline)**  
   Готово, когда:
   - `04_architecture.md` + `03/05/06` заполнены
   - `traceability.md` заполнен до “design links”
   - `reviews.md`: Design Validation/Verification отмечены

3) **Validation Baseline (Ready-for-build / acceptance-defined)**  
   Готово, когда:
   - `acceptance.md` покрывает все `US` из scope
   - `07_mvp_plan.md` ссылается на `AT` (или на `US`, если хочешь проще)

(Опционально) git-теги: `baseline/2026-02-mvp/req`, `.../design`, `.../val`.

---

## 4) Что НЕ добавляем (осознанно, чтобы не утонуть в IEEE-избыточности)
Из PDF-матрицы мы **не заводим отдельно**: SOIP/SIP/SIAR/TVRR/FCA/PCA/records, пока у тебя нет команды/контрактов/аудитов.  
Их роль в нашем варианте выполняют:
- `reviews.md` (вместо walkthrough/inspection records)
- `acceptance.md` + CI/issue-tracker (вместо TVRR)
- git history + tags (вместо конфигурационных “records”)

---

## 5) Пошаговый план внедрения в текущем репо (без решений “на лету”)

1) Создать `docs/product/` и добавить 6 файлов: `needs.md`, `global_user_stories.md`, `global_use_cases.md`, `nfr.md`, `glossary.md`, `traceability_policy.md`.
2) Создать `docs/iterations/2026-02-mvp/`.
3) Переместить текущие `docs/01_*.md … docs/07_*.md` в `docs/iterations/2026-02-mvp/` (обновить ссылки в текстах).
4) Создать `docs/iterations/2026-02-mvp/traceability.md`, `acceptance.md`, `reviews.md`.
5) Заполнить `docs/product/global_user_stories.md` и `docs/product/global_use_cases.md` из уже собранного контекста (stories из “реальности”: события, GitHub, скидки, нарративы, дайджесты/контент, корпус эссе, доверие/claims, история уведомлений).
6) В `docs/iterations/2026-02-mvp/01_vision.md` выбрать подмножество `US/UC/NFR` и зафиксировать IN/OUT.
7) Заполнить `traceability.md` и `acceptance.md` для выбранного scope.
8) Обновить `docs/README.md` как индекс артефактов (global vs iteration) + правила ссылок.

---

## Предположения (явно зафиксированы)
- Ты продолжаешь вести требования как “реальные истории” (User Stories) и отдельный каталог возможностей (Use Cases) — это соответствует “needs → requirements → design inputs”.
- Сейчас важнее трассируемость до acceptance, чем формальные integration/installation/support артефакты (ты выбрал отложить ops).
- Любая избыточная “оборонная” форма заменяется чеклистами ревью + матрицей + git-тегами baseline.

