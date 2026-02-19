# AGENTS.md — инструкции для Codex/агентов в этом репозитории

Codex читает этот файл перед началом работы. Цель — чтобы изменения были предсказуемыми, тестируемыми и трассируемыми.

## Источник истины (обязательно читать перед работой)
1) Vision: docs/product/global_vision.md
2) Требования: docs/product/global_user_stories.md, docs/product/global_use_cases.md, docs/product/nfr.md
3) Глоссарий: docs/product/glossary.md
4) Текущая итерация: docs/iterations/<CURRENT>/ (01_vision.md, 04_architecture.md, acceptance.md, traceability.md, reviews.md)
5) SDLC: SDLC.md
6) Query Catalog standard: docs/_meta/QC-STANDARD.md
7) Query Catalog steward skill: skills/query-catalog-steward.md
8) PR notes process and registry: docs/_meta/PR-NOTES.md, docs/_meta/pr-notes/index.md

Если файлы лежат не в `docs/`, используй путь из README.md.

## Рабочие соглашения
- Одна задача = одна ветка = один PR (draft разрешён).
- Не меняй глобальные IDs (US/UC/NFR/AT/ADR) и их смысл без явного указания в задаче.
- Не меняй публичные контракты/схемы/форматы без ADR (docs/adr/ADR-####-*.md).
- Не добавляй новые прод-зависимости без явного разрешения (комментарий в PR/issue).
- Не делай “рефакторинг ради красоты”, если это не цель задачи.

## Перед началом
- Сделай git checkpoint (коммит/тег) перед значимыми изменениями, чтобы можно было откатиться.
- Убедись, что понимаешь acceptance критерии для US/AT.

## Обязательные проверки перед PR
Укажи в PR:
- Какие US/UC/NFR закрываешь (IDs)
- Какие AT покрываешь (IDs)
- Как запустить проверки

Запусти локально (подставь реальные команды проекта):
- `make lint` или `npm run lint`
- `make test` или `npm test`
- (если есть) `make typecheck`

## Формат результата (в конце PR-описания)
- Summary: 3–7 bullets
- Evidence: команды/логи тестов + что проверено
- Risks: что может сломаться
- Follow-ups: что НЕ сделано и почему
