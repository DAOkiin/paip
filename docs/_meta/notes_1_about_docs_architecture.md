Ниже — предлагаемая **структура документации** “с нуля”, с явными файлами, которые описывают *саму структуру*, правила и ответственность документов (чтобы через 6 месяцев не было путаницы).

## Принцип
- **Global слой**: “что и зачем строим” (needs/requirements) — живёт долго, меняется медленно.
- **Iteration слой**: “что делаем сейчас” (design inputs → design outputs → acceptance) — фиксируется как baseline на итерацию/релиз.
- **Traceability**: требования (US/UC/NFR) обязаны иметь связи с дизайном и acceptance.

---

## Дерево каталогов (рекомендуемое)

```
docs/
  README.md

  _meta/
    doc_system.md
    doc_map.md
    naming_and_ids.md
    traceability_policy.md
    review_and_baselines.md
    glossary_policy.md
    templates.md

  product/
    global_vision.md
    needs.md
    personas.md
    global_user_stories.md
    global_use_cases.md
    nfr.md
    glossary.md
    risks_and_assumptions.md

  iterations/
    README.md
    current.md
    2026-02-mvp/
      README.md
      scope.md
      selected_requirements.md
      architecture.md
      domain_model.md
      event_model.md
      data_model.md
      acceptance.md
      traceability.md
      plan.md
      open_questions.md
      release_notes.md

  adr/
    README.md
    ADR-0001-<slug>.md

  research/
    README.md
    raw/
      ...
    raw_research.md

  ops/
    README.md
    runbooks.md
    installation.md
    observability.md

  _archive/
    README.md
    <date>-<what>/
      ...
```

---

## Файлы, которые “объясняют документацию” (контекст структуры)

1) `docs/README.md`  
   Главная точка входа: “что читать в каком порядке” + ссылки на `product/` и `iterations/current`.

2) `docs/_meta/doc_system.md`  
   Зачем такая структура, какие слои существуют (global vs iteration vs ADR vs research), и какие документы считаются “истиной”.

3) `docs/_meta/doc_map.md`  
   Таблица “документ → ответственность → входы/выходы → кто владелец → что ссылается”. Это твой постоянный “навигатор”.

4) `docs/_meta/naming_and_ids.md`  
   Правила именования, схема ID (`US-0001`, `UC-0001`, `NFR-0001`, `AT-0001`, `ADR-0001`), правила ссылок.

5) `docs/_meta/traceability_policy.md`  
   Что обязано быть трассируемым и как: минимальные требования к матрице, какие связи обязательны (например: каждый выбранный US должен иметь AT).

6) `docs/_meta/review_and_baselines.md`  
   Лёгкие аналоги walkthrough/inspection/review: какие гейты на итерацию, что значит baseline, когда “замораживаем” документы.

7) `docs/_meta/glossary_policy.md`  
   Как добавлять термины, как не допускать “двух словарей”.

8) `docs/_meta/templates.md`  
   Список шаблонов/структур для US/UC/ADR/acceptance (не обязательно отдельные файлы-шаблоны; можно как секции).

---

## Global слой (requirements / needs)

- `docs/product/global_vision.md`  
  North star и принципы (у тебя уже есть аналог).

- `docs/product/needs.md`  
  “Integrated set of needs”: кто пользователь, какие ожидания, какие outcomes/метрики, глобальные границы (что мы точно не делаем).

- `docs/product/global_user_stories.md`  
  Полный реестр **реальных продуктовых историй** (с подробностями и acceptance criteria). Это не scope.

- `docs/product/global_use_cases.md`  
  Полный каталог **возможностей системы** (что система умеет в принципе).

- `docs/product/nfr.md`  
  НФТ: latency, качество данных, наблюдаемость, стоимость, надёжность, ограничения.

- `docs/product/glossary.md`  
  Единая терминология.

- `docs/product/risks_and_assumptions.md`  
  Глобальные риски/допущения (то, что влияет на дизайн, но не является требованием).

---

## Iteration слой (design inputs → design outputs → acceptance)

В каждой папке `docs/iterations/<iteration_id>/`:

- `README.md` — кратко: “что это за итерация”, дата, ссылки на selected US/UC.
- `scope.md` — IN/OUT, wedge-сценарий, метрики успеха.
- `selected_requirements.md` — список выбранных `US/UC/NFR` (только ID + ссылки + итерационные уточнения).
- `architecture.md` — архитектура для выбранного scope (обязательные ссылки на `US/UC/NFR`).
- `domain_model.md` — доменные понятия для итерации.
- `event_model.md` — события и переходы состояний (как часть дизайна).
- `data_model.md` — модель данных для итерации (DDL-first подход документально).
- `acceptance.md` — продуктовые acceptance сценарии `AT-xxxx` (каждый ссылается на `US-xxxx`).
- `traceability.md` — матрица: `US/UC/NFR → docs sections → AT`.
- `plan.md` — план работ (ссылки на AT/US/UC, чтобы план был трассируем).
- `open_questions.md` — вопросы без решения (явно, чтобы не растворились).
- `release_notes.md` — что фактически вошло (после завершения).

Сервисные файлы:
- `docs/iterations/README.md` — как заводить новую итерацию.
- `docs/iterations/current.md` — ссылка на “текущую” итерацию.

---

## ADR (решения и компромиссы)
- `docs/adr/ADR-0001-<slug>.md`  
  Каждое существенное архитектурное решение (например: “Temporal как оркестратор”, “claims vs facts модель”, “raw snapshots immutable”) фиксируется отдельно и потом просто цитируется в `architecture.md`.

---

## Research (сырьё и конспекты)
- `docs/research/raw/` — любые экспортированные/сырые материалы.
- `docs/research/raw_research.md` — конспект и разметка сырья (что из чего полезно).
- `docs/research/README.md` — правила: что сюда кладём, что является “истиной” (обычно: research не является истиной, это справочный слой).

---

## Ops (по твоему выбору — минимально и позже)
Сейчас можно держать `docs/ops/README.md` как заглушку с принципами, а реальные runbooks добавлять ближе к первому деплою.

---

## Главные правила, чтобы не “сломать” SDLC и трассируемость
- Global `US/UC/NFR` **не равны** scope: scope — только в `iterations/.../scope.md` + `selected_requirements.md`.
- Любой раздел в `architecture/domain/event/data` обязан ссылаться на `US/UC/NFR` (иначе это “дизайн без требования”).
- Любой выбранный `US` обязан иметь минимум один `AT` в `acceptance.md`.

Если хочешь, дальше я разложу твою существующую (уже сформулированную) подборку историй/юзкейсов по этой структуре: какие пойдут в `global_user_stories.md`, какие в `global_use_cases.md`, и как будет выглядеть `iterations/2026-02-mvp/scope.md` и `traceability.md` на примере 3–5 ключевых историй.


