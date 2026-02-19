# Traceability — 2026-02-mvp

| Requirement | Design (section/module) | Acceptance (AT) | Notes |
|---|---|---|---|
| US-001 | `/Users/daokiin/projects/daokiin/paip/docs/iterations/2026-02-mvp/04_architecture.md`, `/Users/daokiin/projects/daokiin/paip/src/paip/cli.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/pipeline.py` | AT-001, AT-002, AT-003, AT-006, AT-008 | Event-level monitoring + history |
| UC-001 | `/Users/daokiin/projects/daokiin/paip/src/paip/searx_client.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/pipeline.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/scheduler.py` | AT-001, AT-003, AT-004, AT-009 | Discovery + manual/interval run |
| UC-002 | `/Users/daokiin/projects/daokiin/paip/src/paip/extractors.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/models.py` (`EventClaim`, `Event`) | AT-007 | Event claim normalization and validation |
| UC-003 | `/Users/daokiin/projects/daokiin/paip/src/paip/pipeline.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/utils.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/db.py` (`events`) | AT-002, AT-008 | Event-level dedup/resolution |
| UC-005 | `/Users/daokiin/projects/daokiin/paip/src/paip/notifier.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/db.py` (`notifications`, `get_history`) | AT-001, AT-005, AT-006 | Notification delivery + history |
| NFR-001 | `/Users/daokiin/projects/daokiin/paip/src/paip/db.py`, `/Users/daokiin/projects/daokiin/paip/src/paip/cli.py` (`history`) | AT-005, AT-006 | Explainable signal history |
| NFR-002 | `/Users/daokiin/projects/daokiin/paip/src/paip/pipeline.py` error handling + deterministic event key | AT-002, AT-004, AT-009 | Predictable reruns and failures |
| NFR-006 | `/Users/daokiin/projects/daokiin/paip/src/paip/cli.py`, `/Users/daokiin/projects/daokiin/paip/justfile` | AT-010 | No-code operation via CLI/just |
