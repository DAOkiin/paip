#!/usr/bin/env python3
"""
qc_validate.py — Query Catalog / Query Registry validator (schema + semantic rules).

Design goals:
- Mechanical enforcement of invariants (CI-friendly).
- Human- and agent-friendly error messages (remediation-oriented).
- Works with either:
  (A) one YAML file per query under query-catalog/entries/*.y(a)ml
  (B) a single YAML registry file (list of entries).

This is a reference implementation; adapt policy defaults to your repo.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

# --- Optional deps (kept explicit so failures are clear) ---
try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise

try:
    import jsonschema  # type: ignore
except Exception as e:  # pragma: no cover
    print("ERROR: jsonschema is required. Install with: pip install jsonschema", file=sys.stderr)
    raise


ID_RE = re.compile(r"^[A-Z][A-Za-z0-9]*(\.[A-Z][A-Za-z0-9]*){1,5}$")
PARAM_RE = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class Issue:
    severity: str  # "error" | "warn"
    code: str      # "QC-xx" or "SCHEMA"
    message: str
    file: Optional[str] = None
    json_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "json_path": self.json_path,
        }


def _load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _find_registry_files(root: Path, explicit_file: Optional[str]) -> Tuple[str, List[Path]]:
    """
    Returns (mode, files)
      mode: "entries" | "single"
    """
    if explicit_file:
        p = (root / explicit_file).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Registry file not found: {p}")
        return ("single", [p])

    entries_dir = root / "query-catalog" / "entries"
    if entries_dir.exists() and entries_dir.is_dir():
        files = sorted([p for p in entries_dir.glob("*.y*ml") if p.is_file()])
        if not files:
            raise FileNotFoundError(f"Found {entries_dir} but it has no *.yaml/*.yml files.")
        return ("entries", files)

    candidates = [
        root / "query-catalog" / "query-catalog.yaml",
        root / "query-catalog" / "query-catalog.yml",
        root / "query-catalog.yaml",
        root / "query-catalog.yml",
    ]
    for c in candidates:
        if c.exists():
            return ("single", [c])

    raise FileNotFoundError(
        "No registry found. Expected query-catalog/entries/*.yaml or query-catalog/query-catalog.yaml (or query-catalog.yaml)."
    )


def _extract_entries(mode: str, files: List[Path]) -> List[Tuple[Dict[str, Any], Path]]:
    """
    Returns list of (entry, source_file)
    """
    out: List[Tuple[Dict[str, Any], Path]] = []
    if mode == "entries":
        for f in files:
            doc = _load_yaml(f)
            if doc is None:
                continue
            if isinstance(doc, dict):
                out.append((doc, f))
            elif isinstance(doc, list):
                # allow multi-entry per file, but discouraged
                for item in doc:
                    if isinstance(item, dict):
                        out.append((item, f))
            else:
                raise ValueError(f"Unsupported YAML root type in {f}: {type(doc)}")
        return out

    # single-file mode
    f = files[0]
    doc = _load_yaml(f)
    if doc is None:
        return []
    if isinstance(doc, list):
        for item in doc:
            if isinstance(item, dict):
                out.append((item, f))
    elif isinstance(doc, dict):
        # support either: { queries: [ ... ] } or a single entry dict
        if "queries" in doc and isinstance(doc["queries"], list):
            for item in doc["queries"]:
                if isinstance(item, dict):
                    out.append((item, f))
        else:
            out.append((doc, f))
    else:
        raise ValueError(f"Unsupported YAML root type in {f}: {type(doc)}")
    return out


def _json_pointer_path(err: "jsonschema.ValidationError") -> str:
    parts = list(err.absolute_path)
    if not parts:
        return "$"
    buf = "$"
    for p in parts:
        if isinstance(p, int):
            buf += f"[{p}]"
        else:
            buf += f".{p}"
    return buf


def _default_policy() -> Dict[str, Any]:
    return {
        # severity controls:
        "require_links": "warn",              # off|warn|error
        "require_ordering_for_lists": "warn", # off|warn|error
        "tenant_unknown_is": "warn",          # warn|error
        "missing_security_is": "error",
        "missing_observability_is": "error",

        # semantic rules:
        "require_pagination_for_lists": True,
        "allow_unbounded_requires_reason": True,

        # optional allow-list (set in query-catalog/policy.yaml)
        "allowed_sources": None,  # list[str] | None
        "code_roots": ["src", "app", "services"],  # used for --check-usage (best-effort)
        "exclude_dirs": ["node_modules", ".git", "dist", "build", ".venv", "venv", "__pycache__"],
    }


def _load_policy(root: Path, policy_path: Optional[str]) -> Dict[str, Any]:
    if policy_path:
        p = (root / policy_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Policy file not found: {p}")
        doc = _load_yaml(p)
        if not isinstance(doc, dict):
            raise ValueError(f"Policy file must be a YAML mapping: {p}")
        pol = _default_policy()
        pol.update(doc)
        return pol

    # auto-detect
    for c in [root / "query-catalog" / "policy.yaml", root / "query-catalog" / "policy.yml"]:
        if c.exists():
            doc = _load_yaml(c)
            if isinstance(doc, dict):
                pol = _default_policy()
                pol.update(doc)
                return pol
    return _default_policy()


def _severity_gate(policy_value: str, issue: Issue) -> Optional[Issue]:
    """
    policy_value: off|warn|error
    If off -> suppress; if warn-> warn; if error-> error
    """
    if policy_value == "off":
        return None
    if policy_value == "error":
        return Issue("error", issue.code, issue.message, issue.file, issue.json_path)
    return issue  # keep original severity


def _is_list_cardinality(card: str) -> bool:
    return "N" in card


def _scan_code_for_ids(root: Path, ids: Sequence[str], policy: Dict[str, Any]) -> Dict[str, int]:
    """
    Best-effort usage scan: counts occurrences of each ID in code roots.
    This is intentionally simple (string search), meant for drift detection.
    """
    counts = {i: 0 for i in ids}

    # choose roots that exist; fallback to repo root
    code_roots: List[Path] = []
    for r in policy.get("code_roots", []):
        p = root / r
        if p.exists() and p.is_dir():
            code_roots.append(p)
    if not code_roots:
        code_roots = [root]

    exclude = set(policy.get("exclude_dirs", []))

    # Precompile bytes for faster scanning
    needles = {i: i.encode("utf-8") for i in ids}

    for base in code_roots:
        for dirpath, dirnames, filenames in os.walk(base):
            # prune excluded directories
            dirnames[:] = [d for d in dirnames if d not in exclude and not d.startswith(".")]
            for fn in filenames:
                if fn.startswith("."):
                    continue
                # skip common binaries
                if any(fn.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mov"]):
                    continue
                p = Path(dirpath) / fn
                try:
                    data = p.read_bytes()
                except Exception:
                    continue
                for i, needle in needles.items():
                    if needle in data:
                        # count occurrences roughly
                        counts[i] += data.count(needle)
    return counts


def validate(root: Path, schema_path: Path, policy: Dict[str, Any], *, check_call_sites: bool, check_usage: bool, strict: bool) -> Tuple[List[Issue], List[Issue]]:
    mode, files = _find_registry_files(root, None)
    entries_with_files = _extract_entries(mode, files)

    schema = _load_json(schema_path)
    validator = jsonschema.Draft202012Validator(schema)

    errors: List[Issue] = []
    warns: List[Issue] = []

    seen_ids: Dict[str, Path] = {}
    all_ids: List[str] = []

    # --- per-entry validation ---
    for entry, f in entries_with_files:
        # schema validation
        for err in sorted(validator.iter_errors(entry), key=lambda e: e.path):
            errors.append(Issue(
                severity="error",
                code="SCHEMA",
                message=f"{err.message}",
                file=str(f),
                json_path=_json_pointer_path(err),
            ))

        # continue with semantic checks even if schema errors exist; it's useful feedback.

        qid = entry.get("id")
        if isinstance(qid, str):
            all_ids.append(qid)

        # QC-01: Query ID
        if not isinstance(qid, str) or not qid.strip():
            errors.append(Issue("error", "QC-01", "Missing or empty Query ID (id).", str(f), "$.id"))
        elif not ID_RE.match(qid):
            errors.append(Issue("error", "QC-01", f"Invalid Query ID format: {qid}. Expected Domain.Action[.Qualifier] with PascalCase segments.", str(f), "$.id"))
        else:
            if qid in seen_ids:
                errors.append(Issue("error", "QC-01", f"Duplicate Query ID: {qid}. First seen in {seen_ids[qid]}.", str(f), "$.id"))
            else:
                seen_ids[qid] = f

        # file naming rule in per-entry mode
        if mode == "entries" and isinstance(qid, str) and qid.strip():
            expected = qid
            actual = f.stem
            if actual != expected:
                errors.append(Issue("error", "QC-01", f"Entry filename must match Query ID. Expected {expected}.yaml but got {f.name}.", str(f), "$.id"))

        # QC-10: lifecycle/status alias sanity
        lifecycle = entry.get("lifecycle") if isinstance(entry.get("lifecycle"), dict) else {}
        lifecycle_status = lifecycle.get("status")
        top_status = entry.get("status")

        if isinstance(top_status, str):
            if lifecycle_status is None:
                warns.append(Issue("warn", "QC-10", "Top-level 'status' is present but lifecycle.status is missing. Prefer lifecycle.status.", str(f), "$.status"))
            elif top_status != lifecycle_status:
                errors.append(Issue("error", "QC-10", f"status ({top_status}) does not match lifecycle.status ({lifecycle_status}). Remove alias or make them consistent.", str(f), "$.status"))
            else:
                warns.append(Issue("warn", "QC-10", "Top-level 'status' is a deprecated alias. Prefer lifecycle.status only.", str(f), "$.status"))

        # QC-02: purpose
        purpose = entry.get("purpose")
        if not isinstance(purpose, str) or len(purpose.strip()) < 10:
            errors.append(Issue("error", "QC-02", "purpose must be a non-trivial description (>= 10 chars).", str(f), "$.purpose"))

        # QC-04: data_objects non-empty (at least one touched object)
        data_objects = entry.get("data_objects") if isinstance(entry.get("data_objects"), dict) else {}
        read_objs = data_objects.get("read") if isinstance(data_objects.get("read"), list) else []
        write_objs = data_objects.get("write") if isinstance(data_objects.get("write"), list) else []
        if len(read_objs) + len(write_objs) == 0:
            errors.append(Issue("error", "QC-04", "data_objects.read/write are both empty. A query must declare what it touches.", str(f), "$.data_objects"))

        # QC-03: contract basics + list constraints
        contract = entry.get("contract") if isinstance(entry.get("contract"), dict) else {}
        returns = contract.get("returns") if isinstance(contract.get("returns"), dict) else {}
        card = returns.get("cardinality")
        ordering = contract.get("ordering", None)
        pagination = contract.get("pagination", None)

        if isinstance(card, str) and _is_list_cardinality(card):
            if policy.get("require_pagination_for_lists", True):
                allow_unbounded = False
                perf = entry.get("performance") if isinstance(entry.get("performance"), dict) else {}
                if isinstance(perf.get("allow_unbounded"), bool):
                    allow_unbounded = perf["allow_unbounded"]

                if pagination is None:
                    if allow_unbounded:
                        reason = perf.get("allow_unbounded_reason")
                        if policy.get("allow_unbounded_requires_reason", True) and (not isinstance(reason, str) or not reason.strip()):
                            errors.append(Issue("error", "QC-07", "List query is unbounded but performance.allow_unbounded_reason is missing.", str(f), "$.performance.allow_unbounded_reason"))
                        else:
                            warns.append(Issue("warn", "QC-07", "List query has no pagination but is explicitly marked allow_unbounded. Ensure this is safe.", str(f), "$.contract.pagination"))
                    else:
                        errors.append(Issue("error", "QC-07", "List query must define contract.pagination (or explicitly set performance.allow_unbounded=true with a reason).", str(f), "$.contract.pagination"))

            # ordering is recommended (policy-driven)
            if ordering is None:
                gate = policy.get("require_ordering_for_lists", "warn")
                maybe = _severity_gate(gate, Issue("warn", "QC-03", "List query should define contract.ordering for stable results.", str(f), "$.contract.ordering"))
                if maybe:
                    (errors if maybe.severity == "error" else warns).append(maybe)

        # QC-03: param name uniqueness
        params = contract.get("params") if isinstance(contract.get("params"), list) else []
        seen_param_names = set()
        for idx, p in enumerate(params):
            if not isinstance(p, dict):
                continue
            name = p.get("name")
            if isinstance(name, str):
                if name in seen_param_names:
                    errors.append(Issue("error", "QC-03", f"Duplicate parameter name: {name}.", str(f), f"$.contract.params[{idx}].name"))
                seen_param_names.add(name)
                if not PARAM_RE.match(name):
                    warns.append(Issue("warn", "QC-03", f"Parameter name '{name}' should be snake_case (a-z0-9_).", str(f), f"$.contract.params[{idx}].name"))

        # QC-06: security block required (policy-driven)
        security = entry.get("security") if isinstance(entry.get("security"), dict) else None
        if security is None:
            miss = policy.get("missing_security_is", "error")
            maybe = _severity_gate(miss, Issue("warn", "QC-06", "Missing security section (pii, tenant_boundary, access rules).", str(f), "$.security"))
            if maybe:
                (errors if maybe.severity == "error" else warns).append(maybe)
        else:
            if "pii" not in security or not isinstance(security.get("pii"), bool):
                errors.append(Issue("error", "QC-06", "security.pii must be set to true/false.", str(f), "$.security.pii"))
            tb = security.get("tenant_boundary")
            if not isinstance(tb, str):
                errors.append(Issue("error", "QC-06", "security.tenant_boundary must be set (enforced|not_applicable|unknown).", str(f), "$.security.tenant_boundary"))
            elif tb == "unknown":
                gate = policy.get("tenant_unknown_is", "warn")
                maybe = _severity_gate(gate, Issue("warn", "QC-06", "security.tenant_boundary is 'unknown'. Resolve or mark not_applicable.", str(f), "$.security.tenant_boundary"))
                if maybe:
                    (errors if maybe.severity == "error" else warns).append(maybe)

            pii = security.get("pii")
            if pii is True:
                access = security.get("access")
                if not isinstance(access, str) or not access.strip():
                    errors.append(Issue("error", "QC-06", "PII query must define security.access (who can call it).", str(f), "$.security.access"))

        # QC-08: observability required (policy-driven)
        obs = entry.get("observability") if isinstance(entry.get("observability"), dict) else None
        if obs is None:
            miss = policy.get("missing_observability_is", "error")
            maybe = _severity_gate(miss, Issue("warn", "QC-08", "Missing observability section (log_query_id / trace / sql_comment).", str(f), "$.observability"))
            if maybe:
                (errors if maybe.severity == "error" else warns).append(maybe)
        else:
            if obs.get("log_query_id") is not True:
                errors.append(Issue("error", "QC-08", "observability.log_query_id must be true for correlation.", str(f), "$.observability.log_query_id"))

        # QC-09: owner required by schema; still check non-empty
        owner = entry.get("owner")
        if not isinstance(owner, str) or not owner.strip():
            errors.append(Issue("error", "QC-09", "owner must be a non-empty string.", str(f), "$.owner"))

        # QC-10: lifecycle semantic requirements (schema checks most of it; keep friendly errors)
        status = lifecycle.get("status")
        if status == "deprecated":
            for k in ["replaced_by", "removal_by", "reason"]:
                if k not in lifecycle:
                    errors.append(Issue("error", "QC-10", f"Deprecated query must set lifecycle.{k}.", str(f), f"$.lifecycle.{k}"))
        if status == "removed":
            for k in ["removed_at", "reason"]:
                if k not in lifecycle:
                    errors.append(Issue("error", "QC-10", f"Removed query must set lifecycle.{k}.", str(f), f"$.lifecycle.{k}"))
            links = entry.get("links") if isinstance(entry.get("links"), dict) else {}
            if isinstance(links.get("call_sites"), list) and links["call_sites"]:
                errors.append(Issue("error", "QC-10", "Removed query must not list call_sites.", str(f), "$.links.call_sites"))
            if isinstance(links.get("use_cases"), list) and links["use_cases"]:
                errors.append(Issue("error", "QC-10", "Removed query must not list use_cases.", str(f), "$.links.use_cases"))

        # QC-03/QC-08: optional links presence
        links = entry.get("links") if isinstance(entry.get("links"), dict) else None
        has_links = False
        if links:
            uc = links.get("use_cases")
            cs = links.get("call_sites")
            if isinstance(uc, list) and len(uc) > 0:
                has_links = True
            if isinstance(cs, list) and len(cs) > 0:
                has_links = True

        gate = policy.get("require_links", "warn")
        if status in ("active", "deprecated") and not has_links:
            maybe = _severity_gate(gate, Issue("warn", "QC-03", "Active query should list at least one use_case or call_site for traceability.", str(f), "$.links"))
            if maybe:
                (errors if maybe.severity == "error" else warns).append(maybe)

        # allowed_sources check
        allowed_sources = policy.get("allowed_sources")
        if isinstance(allowed_sources, list):
            src = entry.get("source")
            if isinstance(src, str) and src not in allowed_sources:
                errors.append(Issue("error", "QC-04", f"source '{src}' is not in allowed_sources policy.", str(f), "$.source"))

        # call site path existence (optional)
        if check_call_sites and links and isinstance(links.get("call_sites"), list):
            for i, cs in enumerate(links["call_sites"]):
                if not isinstance(cs, str) or not cs.strip():
                    continue
                # format: path#anchor OR path:line OR path
                path_part = cs
                anchor = None
                if "#" in cs:
                    path_part, anchor = cs.split("#", 1)
                elif ":" in cs:
                    # only treat as path:line if RHS is int
                    left, right = cs.rsplit(":", 1)
                    if right.isdigit():
                        path_part, anchor = left, right

                p = root / path_part
                if not p.exists():
                    errors.append(Issue("error", "QC-03", f"call_site path not found: {path_part}", str(f), f"$.links.call_sites[{i}]"))
                elif anchor:
                    try:
                        text = p.read_text(encoding="utf-8", errors="ignore")
                        if anchor not in text:
                            warns.append(Issue("warn", "QC-03", f"call_site anchor '{anchor}' not found in {path_part} (best-effort check).", str(f), f"$.links.call_sites[{i}]"))
                    except Exception:
                        pass

    # --- usage scan (optional drift signal) ---
    if check_usage and all_ids:
        usage = _scan_code_for_ids(root, all_ids, policy)
        for qid, count in usage.items():
            # You can enforce stronger policies here (e.g., removed queries must have 0 uses).
            if count == 0:
                warns.append(Issue("warn", "DRIFT", f"Query ID '{qid}' was not found in code roots (best-effort). If you rely on query_id tags, ensure call sites include it.", None, None))

    # strict mode: promote warnings to errors
    if strict and warns:
        errors.extend([Issue("error", w.code, w.message, w.file, w.json_path) for w in warns])
        warns = []

    return errors, warns


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Validate Query Catalog / Query Registry entries.")
    ap.add_argument("--root", default=".", help="Repository root (default: .)")
    ap.add_argument("--schema", default="query-catalog/query-catalog.schema.json", help="Path to JSON schema (relative to root by default).")
    ap.add_argument("--policy", default=None, help="Path to policy YAML (optional). Auto-detects query-catalog/policy.yaml.")
    ap.add_argument("--check-call-sites", action="store_true", help="Verify that call_site file paths exist (best-effort).")
    ap.add_argument("--check-usage", action="store_true", help="Best-effort scan for Query IDs in code roots (drift signal).")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    schema_path = (root / args.schema).resolve() if not Path(args.schema).is_absolute() else Path(args.schema)
    if not schema_path.exists():
        print(f"ERROR: schema not found: {schema_path}", file=sys.stderr)
        return 2

    try:
        policy = _load_policy(root, args.policy)
    except Exception as e:
        print(f"ERROR: failed to load policy: {e}", file=sys.stderr)
        return 2

    try:
        errors, warns = validate(
            root=root,
            schema_path=schema_path,
            policy=policy,
            check_call_sites=args.check_call_sites,
            check_usage=args.check_usage,
            strict=args.strict,
        )
    except Exception as e:
        print(f"ERROR: validation failed: {e}", file=sys.stderr)
        return 2

    if args.format == "json":
        payload = {"errors": [e.to_dict() for e in errors], "warnings": [w.to_dict() for w in warns]}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        def _fmt(issue: Issue) -> str:
            loc = ""
            if issue.file:
                loc += f"{issue.file}"
            if issue.json_path:
                loc += f"::{issue.json_path}"
            if loc:
                loc = f"[{loc}] "
            return f"{issue.severity.upper():5} {issue.code}: {loc}{issue.message}"

        for w in warns:
            print(_fmt(w))
        for e in errors:
            print(_fmt(e))

        if not errors and not warns:
            print("OK: Query Catalog validation passed.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
