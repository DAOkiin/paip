# 03. Domain Model

Ключевые сущности системы и их связи. Только MVP-scope.

---

## Сущности

### Source (Источник)
Конфигурация одного источника данных.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| type | enum | `searxng`, `twitter`, `website`, `rss` |
| name | string | Человекочитаемое имя |
| config | jsonb | Параметры адаптера (URL, query, selectors, credentials_ref) |
| schedule | string | Cron-выражение или interval |
| enabled | bool | Активен ли |
| created_at | timestamp | |

### Monitor (Монитор)
Задание на мониторинг — связывает источник с правилами обработки.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| name | string | "Крипто-новости", "Цена на iPhone" |
| source_id | FK → Source | |
| pipeline | jsonb | Ordered list of rule refs |
| notify_channel | string | `telegram:{chat_id}` |
| created_at | timestamp | |

### Job (Запуск)
Один конкретный запуск сбора данных.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| monitor_id | FK → Monitor | |
| status | enum | `pending`, `running`, `completed`, `failed` |
| started_at | timestamp | |
| finished_at | timestamp | |
| error | text | null если ok |
| stats | jsonb | `{fetched: 10, new: 3, dupes: 7}` |

### RawDocument (Сырой документ)
То, что вернул адаптер. Иммутабельный.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| job_id | FK → Job | |
| source_url | text | Оригинальный URL |
| content_type | string | `text/html`, `application/json`, `tweet` |
| raw_content | text | Сырой контент (HTML, JSON, ...) |
| metadata | jsonb | HTTP headers, fetch timestamp, etc. |
| content_hash | text | SHA-256 для быстрой дедупликации |
| fetched_at | timestamp | |

### Document (Нормализованный документ)
Результат обработки RawDocument. Единый формат.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| raw_document_id | FK → RawDocument | |
| monitor_id | FK → Monitor | |
| canonical_url | text | Канонический URL |
| title | text | |
| body | text | Чистый текст |
| published_at | timestamp | Дата публикации (из источника) |
| dedup_key | text | Fingerprint для similarity dedup |
| is_duplicate | bool | |
| duplicate_of_id | FK → Document | null если уникален |
| created_at | timestamp | |

### PriceSnapshot (Снимок цены)
Для UC-03: отслеживание цен.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| monitor_id | FK → Monitor | |
| price | decimal | |
| currency | string | |
| raw_document_id | FK → RawDocument | |
| captured_at | timestamp | |

### Notification (Уведомление)
Отправленное уведомление.

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | |
| monitor_id | FK → Monitor | |
| channel | string | `telegram:{chat_id}` |
| payload | jsonb | Содержание сообщения |
| sent_at | timestamp | |
| status | enum | `sent`, `failed` |

---

## Связи

```
Source 1──* Monitor
Monitor 1──* Job
Job 1──* RawDocument
RawDocument 1──1 Document
Monitor 1──* PriceSnapshot
Monitor 1──* Notification
Document *──1 Document (duplicate_of)
```

---

## Контракт адаптера

Каждый адаптер — функция с сигнатурой:

```python
class AdapterResult:
    url: str
    content_type: str
    raw_content: str | bytes
    metadata: dict  # произвольные метаданные источника

async def fetch(config: dict) -> list[AdapterResult]:
    """Один вызов адаптера = список сырых документов."""
```

Адаптер НЕ нормализует контент. Нормализация — отдельный шаг пайплайна.
