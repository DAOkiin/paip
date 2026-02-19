# Query Catalog

Map-first entrypoints:

- Standard (source of truth): `docs/_meta/QC-STANDARD.md`
- Registry schema: `query-catalog/query-catalog.schema.json`
- Registry data: `query-catalog/query-catalog.yaml`
- Service policy template: `query-catalog/policy.template.yaml`
- Validator: `scripts/qc_validate.py`
- Steward skill: `skills/query-catalog-steward.md`

## Local checks

```bash
just qc-setup
just qc-validate
.venv/bin/python scripts/qc_validate.py --root . --policy query-catalog/policy.template.yaml --check-call-sites
```

## CI-equivalent check

```bash
bash scripts/qc_validate_ci.sh
```

## Optional local policy copy

```bash
cp query-catalog/policy.template.yaml query-catalog/policy.yaml
.venv/bin/python scripts/qc_validate.py --root . --policy query-catalog/policy.yaml
```
