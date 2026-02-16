# Event Model (2026-02-mvp)

## Жизненные циклы

### IntakeRun lifecycle

`scheduled/manual` → `running` → `completed/failed` → `retired`

### ChangeSignal lifecycle

`detected` → `routed` → `notified | suppressed`

### Notification lifecycle

`queued` → `sent` → `read/archived`

## События системы (MVP)

- `watch.spec.created` — пользователь создаёт новый сценарий.
- `watch.spec.updated` — изменён состав мониторинга/порогов.
- `watch.spec.disabled` — сценарий временно неактивен.
- `intake.started` — старт сбора по источнику.
- `intake.failed` — ошибка сбора/недоступность источника.
- `canonical.generated` — формирование нормализованного элемента.
- `signal.detected` — найдено новое или изменившееся событие.
- `notification.queued` — решение попало в очередь уведомления.
- `notification.sent` — уведомление доставлено.
- `digest.generated` — сформирован сводный блок.
- `digest.delivered` — сводка отправлена пользователю.
- `signal.suppressed` — событие отсеяно как дубликат/неприоритетное.

## Логи истории для пользователя

- Каждое событие `signal.detected`, `notification.sent`, `digest.generated` должно иметь связь с:
  - источником,
  - временем,
  - объяснением причины,
  - входным `WatchSpec`.
- При недоступности источника фиксируется `intake.failed` с рекомендацией повторного запуска.
