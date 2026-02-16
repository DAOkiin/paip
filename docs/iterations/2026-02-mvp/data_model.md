# Data Model (2026-02-mvp)

## Основные таблицы/коллекции

- `watch_specs`
  - пользовательские сценарии мониторинга.
- `sources`
  - справочник источников и их конфигураций.
- `intake_runs`
  - история запусков (плановый и ручной).
- `raw_items`
  - сырой материал для воспроизводимости.
- `canonical_items`
  - нормализованные события/объекты наблюдения.
- `change_signals`
  - зафиксированные факты новизны/изменений.
- `notifications`
  - отправленные сообщения и их статус.
- `digests`
  - сформированные пакетные сводки.
- `notification_history`
  - расширенная запись истории для пользователя и диагностики.

## Ключевые отношения

- `watch_specs` (1) ↔ `sources` (много)
- `watch_specs` (1) ↔ `intake_runs` (много)
- `intake_runs` (1) ↔ `raw_items` (много) ↔ `canonical_items` (много)
- `canonical_items` (1) ↔ `change_signals` (0..1)
- `change_signals` (1) ↔ (`notifications`, `digests`) (много)
- `watch_specs` (1) ↔ `notification_history` (много)

## Нормативы хранения

- `raw_items`: необработанные артефакты храним для трассируемости.
- `canonical_items`: хранение в удобном формате для поиска и дедупликации.
- `notification_history`: обязателен для пользовательского просмотра истории (US-001).
