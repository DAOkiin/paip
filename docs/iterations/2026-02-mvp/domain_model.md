# Domain Model (2026-02-mvp)

## Основные сущности

### WatchSpec

Сценарий, который настраивает пользователя: что отслеживаем, как часто и по какому правилу уведомлять.

Поля:
- `id`
- `title`
- `scope` (город, тема, репозиторий, ссылка)
- `trigger_type` (новизна/изменение/цена)
- `notification_mode` (push/digest)
- `priority`
- `owner` (человек/организация)

### Source

Источник данных, откуда приходит первичная информация.

Поля:
- `id`, `type`, `name`, `endpoint`, `credentials_ref`
- `status`

### IntakeRun

Запуск сценария в конкретный момент (по расписанию или вручную).

Поля:
- `id`, `watch_spec_id`, `started_at`, `trigger_reason`, `status`

### RawItem

Необработанный материал из источника, сохранённый для воспроизводимости.

Поля:
- `id`, `intake_run_id`, `source_payload_ref`, `captured_at`, `source_signature`

### CanonicalItem

Нормализованная единица, совместимая для поиска и сравнения.

Поля:
- `id`, `raw_item_id`, `title`, `summary`, `link`, `published_at`, `tags`, `place_city`

### ChangeSignal

Сигнал о новом/изменившемся материале, который уже готов к маршрутизации.

Поля:
- `id`, `canonical_item_id`, `watch_spec_id`, `signal_type`, `evidence_summary`, `confidence`

### Notification

Уведомление, отправленное пользователю, плюс связь на причину.

Поля:
- `id`, `watch_spec_id`, `channel`, `payload`, `sent_at`, `status`, `change_signal_id`

### Digest

Сводка по группе сигналов за период.

Поля:
- `id`, `watch_spec_id`, `from_ts`, `to_ts`, `items`, `state`

## Связи

- `WatchSpec` использует 1..* `Source`.
- `WatchSpec` запускает 1..* `IntakeRun`.
- `IntakeRun` порождает 0..* `RawItem`, потом 1..* `CanonicalItem`.
- `CanonicalItem` может создать 0..1 `ChangeSignal`.
- `ChangeSignal` может породить 0..* `Notification` и 0..* `Digest`.
