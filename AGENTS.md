# Agent operating rules

These rules apply to every coding agent working in this repository.

## Scope

- Read `SKILL.md` before changing skill behavior.
- Preserve user changes and unrelated working-tree edits.
- Keep the root `SKILL.md` focused on routing. Put detailed rules in
  `references/` and deterministic checks in `scripts/`.
- Maintain Python 3.8 compatibility and zero runtime dependencies.
- Always-on policy lives in `references/always-on.md` plus
  `scripts/config_lib.py` / `scripts/onboard.py`. Do not scatter config paths.
- When editing this skill's own docs, keep unmachined text rules (no em-dashes
  as decoration in new prose; concrete findings).

## Verification

Before presenting a change as complete:

```sh
python3 scripts/validate_skill.py
python3 scripts/scan_text.py README.md
python3 scripts/scan_text.py SKILL.md
git diff --check
```

Run `python3 scripts/scan_ui.py <path>` when changing UI examples or frontend
rules. Never claim a check, render, or test passed unless it ran successfully.

## Git contract

- Inspection commands such as `git status`, `git diff`, and `git log` are
  always allowed.
- Work on a topic branch named `agent/<short-task>` unless the user explicitly
  requests another branch or the host provides an isolated worktree.
- Stage only files or hunks belonging to the current task. Use `git add -p`
  when a touched file also contains unrelated edits.
- Review `git diff --cached` and run `git diff --cached --check` before every
  commit.
- Commits must be cohesive, verified, and described by a short imperative
  message. Do not use `git commit -a` or stage the whole repository by default.
- Commit only when the user asks, or when the task explicitly includes creating
  a commit. Pushing, opening a pull request, merging, tagging, releasing, and
  posting external comments always require explicit user authorization.
- Push only the current topic branch. Never push directly to `main` unless the
  user explicitly requests it and repository policy permits it.
- Never amend, rebase, reset, delete branches, or force-push without a specific
  request. If a force-push is unavoidable, explain why and use
  `--force-with-lease`; plain `--force` is prohibited.
- After committing or pushing, report the branch, commit SHA, checks run, and
  any remaining local changes.

## Pull requests

- Prefer a pull request for changes to `SKILL.md`, scanners, CI, security or
  governance files, and release metadata.
- Base the PR summary on the actual diff. List commands that ran and disclose
  checks that could not run.
- Do not approve or merge the agent's own pull request.
