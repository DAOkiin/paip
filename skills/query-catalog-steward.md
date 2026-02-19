---
name: query-catalog-steward
description: |
  Use this skill when adding or changing data-access operations. Keep Query Registry entries accurate,
  pass validator checks, and preserve traceability between use-cases, query IDs, and data objects.
---

# Query Catalog Steward

Short map-first playbook for safe Query Catalog changes.

## Source of truth map

- Standard (normative): `docs/_meta/QC-STANDARD.md`
- Registry schema: `query-catalog/query-catalog.schema.json`
- Registry data: `query-catalog/query-catalog.yaml` or `query-catalog/entries/*.yaml`
- Policy template: `query-catalog/policy.template.yaml`
- Validator: `scripts/qc_validate.py`

## When to use

- New query/data-access operation is introduced.
- Existing query contract, source, security, or lifecycle changes.
- Data schema change affects touched objects.
- Incident/performance work requires Query ID traceability updates.

## Operational checklist

- [ ] Query ID follows `Domain.Action[.Qualifier]` and stays stable.
- [ ] Entry has `id`, `owner`, `purpose`, `source`, `contract`, `data_objects`, `lifecycle.status`.
- [ ] List queries have pagination (or explicit bounded exception per policy).
- [ ] `security` and `observability.log_query_id = true` are present.
- [ ] `links.use_cases` or `links.call_sites` are updated for traceability.
- [ ] Validation passes before PR.

## Commands

```bash
# Install validator deps
just qc-setup

# Local validation
just qc-validate

# Optional stricter check
python3 scripts/qc_validate.py --root . --policy query-catalog/policy.template.yaml --strict

# CI-equivalent script (path-aware)
bash scripts/qc_validate_ci.sh
```

## PR notes

Include in PR:
- What Query IDs were added/changed/deprecated.
- Validation evidence (commands + key output).
- Any explicit deviations from `docs/_meta/QC-STANDARD.md`.
