# Traceability — 2026-02-mvp

| Requirement | Design (section/module) | Acceptance (AT) | Notes |
|---|---|---|---|
| US-001 | `04_architecture.md` + `src/paip/cli.py` + `src/paip/pipeline.py` | AT-001, AT-002, AT-003, AT-006 | City/topic monitoring with history |
| UC-001 | `src/paip/searx_client.py`, `src/paip/pipeline.py`, `src/paip/scheduler.py` | AT-001, AT-003, AT-004 | Data collection by manual and interval runs |
| UC-002 | `src/paip/models.py` (`SearchHit`, `CanonicalItem`) | AT-001 | Unified normalized shape |
| UC-003 | `src/paip/pipeline.py`, `src/paip/db.py` unique checks | AT-002 | Exact dedup by canonical URL |
| UC-005 | `src/paip/notifier.py`, `src/paip/db.py` (`notifications`, history query) | AT-001, AT-005, AT-006 | Notification delivery + history |
| NFR-001 | `src/paip/db.py` history fields (`source`, `created_at`, `reason`) | AT-005, AT-006 | Explainable signal history |
| NFR-002 | `src/paip/pipeline.py` run error handling + dedup determinism | AT-002, AT-004 | Predictable reruns and failures |
| NFR-006 | `src/paip/cli.py` commands for add/list/run/history | AT-001 | No-code operation via CLI |
