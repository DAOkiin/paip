# PR Notes

`git notes` are used to persist PR descriptions in markdown, bound to commit SHAs.

## Source of truth

- Git notes ref: `refs/notes/commits`
- Markdown registry index: `docs/_meta/pr-notes/index.md`
- One note per commit file: `docs/_meta/pr-notes/notes/<commit-sha>.md`

## Read notes

```bash
git notes show <sha>
git log --show-notes=commits --oneline -n 5
```

## Refresh markdown registry

```bash
just notes-registry-refresh
just notes-registry-lint
```

## Add/update a note

```bash
git notes add -f -F /tmp/pr_body.md <sha>
just notes-registry-refresh
```

## Push notes

```bash
git push <remote> refs/notes/commits:refs/notes/commits
```

When hooks are installed (`just hooks-install`), `pre-push` auto-syncs `refs/notes/commits` and blocks branch push if sync fails.

## Notes format

- Note body is free-form markdown.
- Registry keeps metadata and a file copy per commit for easy browsing.
