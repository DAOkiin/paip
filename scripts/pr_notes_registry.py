#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

NOTES_REF = "refs/notes/commits"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class NoteEntry:
    commit: str
    note_object: str
    subject: str
    committer_date: str
    author_date: str
    branches: list[str]
    title: str
    body: str


def _run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def _run_lines(*args: str) -> list[str]:
    out = _run(*args)
    return [line for line in out.splitlines() if line.strip()]


def _note_title(note_text: str, fallback: str) -> str:
    for line in note_text.splitlines():
        text = line.strip()
        if not text:
            continue
        if text.startswith("#"):
            return text.lstrip("#").strip() or fallback
        return text
    return fallback


def _read_notes(notes_ref: str) -> list[NoteEntry]:
    raw = _run_lines("git", "notes", "--ref", notes_ref, "list")
    entries: list[NoteEntry] = []
    for line in raw:
        note_object, commit = line.split(maxsplit=1)
        commit = commit.strip()
        if not SHA_RE.match(commit):
            continue

        subject = _run("git", "show", "-s", "--format=%s", commit)
        committer_date = _run("git", "show", "-s", "--format=%cI", commit)
        author_date = _run("git", "show", "-s", "--format=%aI", commit)
        branches = sorted(_run_lines("git", "branch", "--format=%(refname:short)", "--contains", commit))

        note_body = _run("git", "notes", "--ref", notes_ref, "show", commit)
        title = _note_title(note_body, fallback=subject)

        entries.append(
            NoteEntry(
                commit=commit,
                note_object=note_object,
                subject=subject,
                committer_date=committer_date,
                author_date=author_date,
                branches=branches,
                title=title,
                body=note_body + ("\n" if not note_body.endswith("\n") else ""),
            )
        )

    entries.sort(key=lambda e: e.committer_date, reverse=True)
    return entries


def _sync(output_dir: Path, notes_ref: str) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    notes_dir = output_dir / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)

    entries = _read_notes(notes_ref)

    # Clean managed note files.
    for path in notes_dir.glob("*.md"):
        stem = path.stem
        if SHA_RE.match(stem):
            path.unlink()

    for entry in entries:
        (notes_dir / f"{entry.commit}.md").write_text(entry.body, encoding="utf-8")

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines: list[str] = []
    lines.append("# PR Notes Registry")
    lines.append("")
    lines.append("One-note-per-file markdown registry generated from `git notes`.")
    lines.append("")
    lines.append(f"- Source ref: `{notes_ref}`")
    lines.append(f"- Generated at (UTC): `{now}`")
    lines.append(f"- Total notes: `{len(entries)}`")
    lines.append("")
    lines.append("## Entries")
    lines.append("")
    lines.append("| Commit | Subject | Note Title | Committer Date | Branch Hints | Note File |")
    lines.append("|---|---|---|---|---|---|")

    for entry in entries:
        short = entry.commit[:8]
        branches = ", ".join(entry.branches) if entry.branches else "-"
        note_file = f"notes/{entry.commit}.md"
        subject = entry.subject.replace("|", "\\|")
        title = entry.title.replace("|", "\\|")
        lines.append(
            f"| `{short}` | {subject} | {title} | `{entry.committer_date}` | `{branches}` | [`{note_file}`]({note_file}) |"
        )

    (output_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def _lint(output_dir: Path, notes_ref: str) -> int:
    index_path = output_dir / "index.md"
    notes_dir = output_dir / "notes"

    if not index_path.exists():
        print(f"ERROR: missing registry index: {index_path}")
        return 1
    if not notes_dir.exists():
        print(f"ERROR: missing notes dir: {notes_dir}")
        return 1

    entries = _read_notes(notes_ref)
    expected = {e.commit for e in entries}
    actual = {p.stem for p in notes_dir.glob("*.md") if SHA_RE.match(p.stem)}

    missing = sorted(expected - actual)
    extra = sorted(actual - expected)

    if missing:
        print("ERROR: missing note files for commits:")
        for commit in missing:
            print(f"  - {commit}")
        return 1

    if extra:
        print("ERROR: unexpected note files not present in git notes:")
        for commit in extra:
            print(f"  - {commit}")
        return 1

    text = index_path.read_text(encoding="utf-8")
    for commit in sorted(expected):
        short = commit[:8]
        if short not in text or f"notes/{commit}.md" not in text:
            print(f"ERROR: commit {commit} missing from index table")
            return 1

    print("OK: PR notes registry is consistent with git notes.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync and lint markdown PR notes registry from git notes.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sync = sub.add_parser("sync")
    sync.add_argument("--output-dir", default="docs/_meta/pr-notes")
    sync.add_argument("--notes-ref", default=NOTES_REF)

    lint = sub.add_parser("lint")
    lint.add_argument("--output-dir", default="docs/_meta/pr-notes")
    lint.add_argument("--notes-ref", default=NOTES_REF)

    args = ap.parse_args()
    out = Path(args.output_dir)

    if args.cmd == "sync":
        return _sync(out, args.notes_ref)
    if args.cmd == "lint":
        return _lint(out, args.notes_ref)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
