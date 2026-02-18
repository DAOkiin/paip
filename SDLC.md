# SDLC (v0) — процесс разработки

Этот файл — «входная дверь». Подробный SDLC: docs/_meta/sdlc.md (или _meta/sdlc.md — см. README).

## Цели
- Итерационная разработка (MVP → расширение).
- Трассируемость: OUT → US/UC/NFR → Design → AT → Evidence.
- Максимум параллельности через агентов при сохранении качества через PR-гейты.

## Основные правила
1) Global требования живут отдельно от итераций.
2) Итерация — это “Design Input → Design Output → Validation”.
3) Все изменения кода проходят через PR + тесты.
4) Любое существенное архитектурное решение фиксируется ADR.

## Гейты (Baselines)
- Requirements Baseline: scope итерации + acceptance/traceability заполнены.
- Design Baseline: архитектура/модели/контракты готовы, traceability связывает дизайн с требованиями.
- Validation Baseline: AT определены/покрыты, есть план прогона.

## Роли (минимум)
- Maintainer/Integrator (человек): принимает scope, мерджит PR, закрывает baselines.
- Agents (Codex): выполняют задачи в ветках по правилам AGENTS.md.

## Приложение A — Iteration Pack v0 (обязательные файлы)
В каждой итерации создаётся папка: `docs/iterations/<id>/` и файлы:
- 01_vision.md
- 04_architecture.md
- acceptance.md
- traceability.md
- reviews.md
- 07_mvp_plan.md (опционально, но полезно)

Содержимое и шаблоны — см. ниже.
