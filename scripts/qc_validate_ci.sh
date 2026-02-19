#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

should_run=1
if [[ -n "${QC_CHANGED_FILES:-}" ]]; then
  should_run=0
  while IFS= read -r file; do
    [[ -z "${file}" ]] && continue
    case "${file}" in
      query-catalog/*|scripts/qc_validate.py|scripts/qc_validate_ci.sh|docs/_meta/QC-STANDARD.md|src/*)
        should_run=1
        break
        ;;
    esac
  done <<< "${QC_CHANGED_FILES}"
fi

if [[ "${should_run}" -eq 0 ]]; then
  echo "SKIP: no Query Catalog related changes detected."
  exit 0
fi

if [[ -n "${PYTHON_BIN:-}" ]]; then
  python_bin="${PYTHON_BIN}"
elif [[ -x ".venv/bin/python" ]]; then
  python_bin=".venv/bin/python"
else
  python_bin="python3"
fi

"${python_bin}" -m pip install --disable-pip-version-check -r query-catalog/requirements-qc.txt
"${python_bin}" scripts/qc_validate.py --root . --policy query-catalog/policy.template.yaml
