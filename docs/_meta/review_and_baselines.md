# Review и базовые артефакты

## Что проверяем в каждом цикле

- **Стабильность контекста**: `product/global_vision.md` и `product/global_user_stories.md` согласованы между собой.
- **Реальность итерации**: `iterations/current.md` указывает актуальную итерацию и причины.
- **Трассируемость**: все `selected_requirements` присутствуют в `traceability.md`.
- **Проверяемость**: все ключевые решений имеют связанный `AC-XXX` в `acceptance.md`.

## Базовые артефакты для запуска новой итерации

- Продуктовые:
  - `global_vision`, `global_user_stories`, `global_use_cases`
  - `needs`, `personas`, `glossary`
- Итерационные:
  - `scope`, `selected_requirements`, `architecture`, `traceability`, `acceptance`, `plan`, `open_questions`
- Операционные:
  - `ops/installation` и `ops/observability` (после первого рабочего релиза).

## Рекомендуемая периодичность

- Еженедельный мини-ревью архитектурных решений (перед планированием).
- После каждого завершения `status: done` — чек на traceability.
- Перед релизом: `acceptance` + `release_notes`.
