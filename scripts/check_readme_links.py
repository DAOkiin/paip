#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")

EXTERNAL_SCHEMES = {"http", "https", "mailto"}
PATH_SUFFIXES = (".md", ".yaml", ".yml", ".json", ".toml", ".py", ".sh")


@dataclass
class Reference:
    kind: str
    target: str
    line: int


def _strip_enclosing_angle_brackets(value: str) -> str:
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        return value[1:-1].strip()
    return value


def _normalize_target(raw: str) -> str:
    return _strip_enclosing_angle_brackets(raw).strip()


def _is_external(target: str) -> bool:
    parsed = urlparse(target)
    return parsed.scheme.lower() in EXTERNAL_SCHEMES


def _is_probable_path(value: str) -> bool:
    token = value.strip().rstrip(".,:;")
    if not token or " " in token:
        return False
    if _is_external(token):
        return False
    if token.startswith("#"):
        return True
    if "/" in token or token.startswith("."):
        return True
    return token.endswith(PATH_SUFFIXES)


def _slugify_heading(text: str) -> str:
    text = text.strip().lower()
    cleaned: list[str] = []
    for ch in text:
        if ch.isalnum() or ch in {" ", "-", "_"}:
            cleaned.append(ch)
    slug = "".join(cleaned).replace(" ", "-")
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def _anchors_for_markdown(md_path: Path) -> set[str]:
    seen: dict[str, int] = {}
    anchors: set[str] = set()

    for line in md_path.read_text(encoding="utf-8").splitlines():
        match = HEADING_RE.match(line)
        if not match:
            continue
        base = _slugify_heading(match.group(1))
        if not base:
            continue
        index = seen.get(base, 0)
        anchor = f"{base}-{index}" if index else base
        seen[base] = index + 1
        anchors.add(anchor)

    return anchors


def _iter_references(md_path: Path) -> list[Reference]:
    refs: list[Reference] = []
    in_fence = False

    for lineno, line in enumerate(md_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        for match in MARKDOWN_LINK_RE.finditer(line):
            refs.append(Reference(kind="markdown", target=_normalize_target(match.group(2)), line=lineno))

        for match in INLINE_CODE_RE.finditer(line):
            token = _normalize_target(match.group(1))
            if _is_probable_path(token):
                refs.append(Reference(kind="inline", target=token, line=lineno))

    return refs


def _split_target(target: str) -> tuple[str, str | None]:
    if target.startswith("#"):
        return "", target[1:]
    if "#" not in target:
        return target, None
    path_part, anchor = target.split("#", 1)
    return path_part, anchor


def _resolve_local_path(base_dir: Path, path_part: str) -> Path:
    decoded = unquote(path_part)
    if not decoded:
        return base_dir
    path = Path(decoded)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def validate_readme(root: Path, md_file: Path) -> int:
    markdown_path = (root / md_file).resolve() if not md_file.is_absolute() else md_file
    if not markdown_path.exists():
        print(f"ERROR: markdown file not found: {markdown_path}")
        return 1

    refs = _iter_references(markdown_path)
    errors: list[str] = []
    checked = 0
    skipped_external = 0
    anchor_cache: dict[Path, set[str]] = {}

    for ref in refs:
        target = ref.target
        if not target:
            continue
        if _is_external(target):
            skipped_external += 1
            continue

        path_part, anchor = _split_target(target)
        target_path = _resolve_local_path(markdown_path.parent, path_part)
        checked += 1

        if not target_path.exists():
            errors.append(
                f"line {ref.line}: missing target for {ref.kind} reference `{target}` -> `{target_path}`"
            )
            continue

        if anchor:
            if target_path.is_dir():
                errors.append(
                    f"line {ref.line}: anchor target is directory for `{target}` -> `{target_path}`"
                )
                continue
            if target_path.suffix.lower() != ".md":
                continue
            anchors = anchor_cache.setdefault(target_path, _anchors_for_markdown(target_path))
            if anchor not in anchors:
                errors.append(
                    f"line {ref.line}: missing anchor `#{anchor}` in `{target_path}` for `{target}`"
                )

    if errors:
        print("ERROR: README link/path validation failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(
        "OK: README link/path validation passed "
        f"(checked={checked}, external_skipped={skipped_external}, references={len(refs)})."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate markdown links and map-first path references in README-like markdown files."
    )
    parser.add_argument("--root", default=".", help="Repository root path (default: current directory)")
    parser.add_argument("--file", default="README.md", help="Markdown file to validate (default: README.md)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    md_file = Path(args.file)
    return validate_readme(root=root, md_file=md_file)


if __name__ == "__main__":
    raise SystemExit(main())
