# Трассируемость (2026-02-mvp)

## Матрица трассируемости

| Требование | Тип        | Решение в итерации                                                      | AC         | Ответственный | Status  |
|------------|------------|-------------------------------------------------------------------------|------------|---------------|---------|
| US-001     | User Story | `selected_requirements`, `domain_model`, `architecture`, `history view` | AC-US-001  | TBD           | planned |
| US-002     | User Story | `selected_requirements`, `domain_model`, `canonical pipeline`           | AC-US-002  | TBD           | planned |
| US-004     | User Story | `scope`, `domain_model`, `data_model`                                   | AC-US-004  | TBD           | planned |
| US-005     | User Story | `event_model`, `data_model`                                             | AC-US-005  | TBD           | planned |
| US-006     | User Story | `event_model`, `change_signals`                                         | AC-US-006  | TBD           | planned |
| US-007     | User Story | `digest flow`, `architecture`, `acceptance`                             | AC-US-007  | TBD           | planned |
| US-008     | User Story | `manual trigger`, `architecture`, `plan`                                | AC-US-008  | TBD           | planned |
| US-009     | User Story | `scope`, `iterations/..` setup, `global_use_cases`                      | AC-US-009  | TBD           | planned |
| UC-001     | Use Case   | `architecture`, `sources abstraction`                                   | AC-UC-001  | TBD           | planned |
| UC-002     | Use Case   | `domain_model`, `data_model`                                            | AC-UC-002  | TBD           | planned |
| UC-003     | Use Case   | `change detection rules`, `data_model`                                  | AC-UC-003  | TBD           | planned |
| UC-004     | Use Case   | `routing rules`, `scope`                                                | AC-UC-004  | TBD           | planned |
| UC-005     | Use Case   | `notification history`, `architecture`                                  | AC-UC-005  | TBD           | planned |
| NFR-001    | NFR        | `notification explanation`, `traceability policy`                       | AC-NFR-001 | TBD           | planned |

## Принципы поддержания

- Каждая запись должна иметь владельца до старта реализации.
- При изменении статуса любой записи в `status` обновляется в этом файле и в `open_questions.md`, если есть блокер.
- Если пользовательская история переопределяется по бизнес-приоритету — переносится в следующую итерацию с обоснованием.
