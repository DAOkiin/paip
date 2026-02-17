# SDLC + трассируемость требований: структура артефактов для PAIP

## Кратко (что получится)
- **Global уровень**: `global_vision.md` + 2 реестра (все **User Stories** и все **Use Cases**), с постоянными ID (`US-0001`, `UC-0001`).
- **Итерации**: отдельная папка на итерацию (MVP/спринт), где фиксируются **scope**, **архитектура**, **модели**, **план** и **матрица трассируемости**.
- **Трассируемость**: одна Markdown-матрица на итерацию, которая связывает `US/UC → Architecture/Data/Event → Tests/Acceptance`.

---

## 1) Структура файлов (рекомендуемая, decision complete)

### 1.1. Global (всегда актуально, “источник истины” требований)
Создать:
- `docs/global_vision.md` (уже есть) — north star, философия/принципы/why.
- `docs/product/global_user_stories.md` — полный реестр продуктовых историй (реальные сценарии).
- `docs/product/global_use_cases.md` — полный реестр use cases как “возможностей системы”.
- `docs/product/glossary.md` — единый словарь терминов (чтобы документы не расползались).
- `docs/product/nfr.md` — нефункциональные требования (скорость/качество/наблюдаемость/стоимость/ограничения).

### 1.2. Итерации (каждый раз — “baseline” для дизайна и реализации)
Создать папку итерации:
- `docs/iterations/2026-02-mvp/`

Внутри вести (перенести текущие `docs/01_*.md … docs/07_*.md` сюда, с обновлением ссылок):
- `docs/iterations/2026-02-mvp/01_vision.md` — MVP scope + метрики + decisions (коротко).
- `docs/iterations/2026-02-mvp/02_use_cases.md` — выбранные UC (только те, что входят в итерацию) + сценарии/варианты на уровне поведения.
- `docs/iterations/2026-02-mvp/03_domain_model.md`
- `docs/iterations/2026-02-mvp/04_architecture.md`
- `docs/iterations/2026-02-mvp/05_event_model.md`
- `docs/iterations/2026-02-mvp/06_data_model.md`
- `docs/iterations/2026-02-mvp/07_mvp_plan.md`
- `docs/iterations/2026-02-mvp/traceability.md` — матрица трассируемости (см. ниже).
- `docs/iterations/2026-02-mvp/acceptance.md` — acceptance criteria и тестовые сценарии на продукт-уровне (что проверяет пользователь).

### 1.3. Индекс
Обновить/создать:
- `docs/README.md` — “карта документов” (global vs iteration), чтобы быстро ориентироваться.

---

## 2) Как это согласуется с SDLC / IEEE 12207 (упрощённое отображение)

Таблица соответствия (без избыточности “оборонки”, но с сохранением духа):

- **Stakeholder Needs / Vision**  
  → `docs/global_vision.md` + краткая выжимка в `docs/iterations/.../01_vision.md`

- **System Requirements (SRS-уровень)**  
  → `docs/product/global_user_stories.md` + `docs/product/global_use_cases.md` + `docs/product/nfr.md`

- **Software Architecture (SAD-уровень)**  
  → `docs/iterations/.../04_architecture.md` (с явными ссылками на `US/UC/NFR`)

- **Detailed Design (SDD-уровень)**  
  → `03_domain_model.md`, `05_event_model.md`, `06_data_model.md` (с ссылками на `US/UC`)

- **Verification/Validation (тестовая часть)**  
  → `docs/iterations/.../acceptance.md` + ссылки из `traceability.md`

Ключ: мы не копируем сотню документов, а делаем **минимальный набор**, который даёт:
1) управление scope, 2) предсказуемый дизайн, 3) аудит изменений, 4) трассируемость до тестов.

---

## 3) Правила ID и как писать артефакты (чтобы трассируемость была дешёвой)

### 3.1. ID-схема (единый счётчик, всегда)
- User Stories: `US-0001`, `US-0002`, …
- Use Cases: `UC-0001`, `UC-0002`, …
- NFR: `NFR-0001`, …
- Acceptance tests/scenarios: `AT-0001`, …
- (опционально) Architecture sections: `ARCH-0001`, Data model tables: `DM-0001`, Events: `EV-0001` — если захочешь более “оборонную” строгость. Для старта можно ограничиться ссылками на заголовки.

### 3.2. Шаблон записи User Story (в `docs/product/global_user_stories.md`)
Каждая история **подробная**, но без техдеталей, и обязана иметь:
- **ID + название**
- **Контекст** (реальность: зачем, какая боль)
- **Что хочу** (в терминах пользователя)
- **Результат/ценность**
- **Acceptance criteria** (разделить на `MVP` и `Later`, чтобы не плодить дубликаты)
- **Связанные Use Cases**: список `UC-xxxx`
- **Статус**: `candidate | planned | in_progress | done | cut`
- **Примечания/границы** (что не входит)

### 3.3. Шаблон Use Case (в `docs/product/global_use_cases.md`)
Каждый UC описывает “возможность системы”:
- **ID + цель**
- **Актор(ы)**
- **Предусловия**
- **Основной сценарий (user-visible steps)**
- **Альтернативы/ошибки (на уровне поведения, не реализации)**
- **Постусловия / что должно быть видно пользователю**
- **Связанные User Stories**: список `US-xxxx`

---

## 4) Как выбирать MVP scope и не ломать требования

### 4.1. В `docs/iterations/2026-02-mvp/01_vision.md`
Добавить обязательный блок:
- **Selected for this iteration**
  - User Stories: `US-....`
  - Use Cases: `UC-....`
  - NFR: `NFR-....`

Плюс:
- **IN/OUT**
- **Wedge scenario** (один “сквозной” сценарий, который прокалывает систему)
- **Метрики успеха** (наблюдаемые)

### 4.2. Не копировать полные тексты историй в итерацию
В итерации не нужно дублировать весь реестр. Достаточно:
- ссылок на глобальные `US/UC`
- и “итерационных уточнений” (если в MVP реализуем только часть acceptance criteria).

---

## 5) Traceability (Markdown-матрица на итерацию)

Создать `docs/iterations/2026-02-mvp/traceability.md` с двумя таблицами:

### 5.1. Coverage Matrix (что именно делаем в итерации)
Колонки:
- `US ID`
- `US Title`
- `In MVP? (Y/N)`
- `UC IDs`
- `Acceptance IDs (AT-xxxx)`
- `Notes (что вырезано/упрощено)`

### 5.2. Design Trace (как требование “приземляется” в дизайн)
Колонки:
- `US/UC`
- `Architecture refs` (ссылка на разделы в `04_architecture.md`)
- `Domain refs` (`03_domain_model.md`)
- `Event refs` (`05_event_model.md`)
- `Data refs` (`06_data_model.md`)
- `Tests/Acceptance` (`acceptance.md`)

Правило: **ни один раздел архитектуры/моделей не должен существовать без ссылки хотя бы на один `US/UC/NFR`** (иначе это “дизайн ради дизайна”).

---

## 6) Acceptance (продуктовые проверки)
Создать `docs/iterations/2026-02-mvp/acceptance.md`:
- Список `AT-xxxx` сценариев в терминах пользователя.
- Каждый `AT` ссылается на `US-xxxx` (и при необходимости на `UC-xxxx`).

---

## 7) Процесс “baseline” (лёгкая версия оборонного SDLC)
Для каждой итерации фиксируем 3 контрольных точки (быстро и дешево):
1) **Requirements baseline**: выбраны `US/UC/NFR` в `01_vision.md`, заполнен coverage в `traceability.md`.
2) **Design baseline**: `04_architecture.md` + модели обновлены, и `traceability.md` заполнен до “Design Trace”.
3) **Validation baseline**: `acceptance.md` закрывает все `US` из scope, и в `07_mvp_plan.md` есть шаги/таски, которые явно ведут к `AT`.

(Опционально) git-тег на момент baselining: `baseline/2026-02-mvp`.

---

## 8) Конкретные шаги внедрения в текущем репо (по порядку)
1) Создать папки `docs/product/` и `docs/iterations/2026-02-mvp/`.
2) Перенести текущие `docs/01_*.md … docs/07_*.md` в `docs/iterations/2026-02-mvp/` (обновить ссылки внутри).
3) Создать `docs/product/global_user_stories.md` и внести туда полный реестр историй (включая “события”, “GitHub”, “скидки”, “нарративы”, “дайджесты/контент”, “корпус эссе”, “claims vs facts”, “история уведомлений” и т.д.) с `MVP/Later` acceptance criteria.
4) Создать `docs/product/global_use_cases.md` как системный каталог возможностей (переиспользуя и расширяя текущий `02_use_cases.md`, но в global реестр).
5) В `docs/iterations/2026-02-mvp/01_vision.md` добавить блок “Selected for this iteration” (с ID).
6) В `docs/iterations/2026-02-mvp/02_use_cases.md` оставить только UC, вошедшие в итерацию, и ссылаться на глобальный реестр.
7) Создать `docs/iterations/2026-02-mvp/traceability.md` и заполнить обе матрицы.
8) Создать `docs/iterations/2026-02-mvp/acceptance.md` и завести `AT-xxxx` так, чтобы каждый `US` из scope имел покрытие.
9) Обновить `docs/README.md` (индекс + правила ссылок/ID).

---

## Предположения (зафиксированы по умолчанию)
- Документы ведём на русском.
- Итерацию называем `2026-02-mvp` (можно переименовать позже без смены ID).
- Трассируемость держим в Markdown (без генераторов).
- ID `US/UC/NFR/AT` — единые и постоянные, итерации лишь выбирают подмножество и уточняют.

