#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

RECIPE_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_-]*)(?:\s+[^:]*)?:\s*$")
SECTION_RE = re.compile(r"^###\s+`just\s+([A-Za-z0-9][A-Za-z0-9_-]*)(?:\s+[^`]*)?`\s*$")


def parse_just_recipes(path: Path) -> list[str]:
    recipes: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith(" ") or line.startswith("\t"):
            continue
        if ":=" in line:
            continue
        if stripped.startswith("set "):
            continue

        match = RECIPE_RE.match(line)
        if not match:
            continue
        recipes.append(match.group(1))
    return recipes


def parse_doc_sections(path: Path) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None

    for raw in path.read_text(encoding="utf-8").splitlines():
        match = SECTION_RE.match(raw.strip())
        if match:
            current = match.group(1)
            if current in sections:
                raise ValueError(f"Duplicate documentation section for recipe '{current}'")
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(raw)
    return sections


def has_io_markers(lines: list[str]) -> tuple[bool, bool]:
    input_ok = any(line.strip().lower().startswith("- input:") for line in lines)
    output_ok = any(line.strip().lower().startswith("- output:") for line in lines)
    return input_ok, output_ok


def validate_docs(justfile: Path, docs: Path) -> int:
    if not justfile.exists():
        print(f"ERROR: justfile not found: {justfile}")
        return 1
    if not docs.exists():
        print(f"ERROR: docs file not found: {docs}")
        return 1

    recipes = parse_just_recipes(justfile)
    sections = parse_doc_sections(docs)

    missing_sections = [name for name in recipes if name not in sections]
    extra_sections = [name for name in sections if name not in recipes]

    marker_errors: list[str] = []
    for name in recipes:
        lines = sections.get(name)
        if lines is None:
            continue
        input_ok, output_ok = has_io_markers(lines)
        if not input_ok:
            marker_errors.append(f"recipe '{name}' section has no '- Input:' line")
        if not output_ok:
            marker_errors.append(f"recipe '{name}' section has no '- Output:' line")

    if missing_sections or extra_sections or marker_errors:
        print("ERROR: just command documentation validation failed.")
        if missing_sections:
            print("Missing recipe sections:")
            for name in missing_sections:
                print(f"  - {name}")
        if extra_sections:
            print("Unknown recipe sections (not present in justfile):")
            for name in extra_sections:
                print(f"  - {name}")
        if marker_errors:
            print("Missing required IO markers:")
            for err in marker_errors:
                print(f"  - {err}")
        return 1

    print(
        "OK: just command documentation is complete "
        f"(recipes={len(recipes)}, docs_sections={len(sections)})."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that each just recipe has docs with Input/Output markers."
    )
    parser.add_argument("--justfile", default="justfile", help="Path to justfile.")
    parser.add_argument(
        "--docs",
        default="docs/_meta/JUST-COMMANDS.md",
        help="Path to markdown doc with recipe sections.",
    )
    args = parser.parse_args()

    return validate_docs(Path(args.justfile), Path(args.docs))


if __name__ == "__main__":
    raise SystemExit(main())
