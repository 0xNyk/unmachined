# Contributing

The useful contribution is a new tell, or evidence that an existing one is wrong.

**To propose a tell**, open an issue or PR with three things:

1. **The evidence.** Where you saw it, and roughly how often. "Every model does this" is not
   evidence. A link, a sample, or a generation count is.
2. **A severity.** Critical (a phrase that damns the whole draft), major (a strong signal),
   or minor (a smell). Scoring runs 20 / 10 / 3 and blocks at 40, so calling something
   critical is a claim that four of them should never coexist in a passing draft.
3. **The alternative.** A tell without a fix is a complaint. And because the fix becomes the
   next tell once everyone converges on it, give a range rather than one replacement.

**Machine-checkable rules go in the scanner** (`scripts/scan_text.py` or
`scripts/scan_ui.py`). Both are zero-dependency Python and deliberately blunt. Anything that
needs judgment (rhythm, hierarchy, whether a joke lands) belongs in `references/`, not in a
regex.

**Removals are welcome too.** A rule that fires on good human writing is worse than no rule
at all, so a demonstrated false positive is a bug and will be treated as one.

Run the scanners on your own changes before opening the PR:

```
python3 scripts/scan_text.py README.md
python3 scripts/scan_ui.py path/to/ui/src
```

Sources get credited in [ATTRIBUTION.md](ATTRIBUTION.md). Lift a rule from someone, say so.

## Workflow

Open an issue before changing scoring, severity, supported hosts, or the core
philosophy. Small fixes can go straight to a pull request.

1. Fork the repository if you are an outside contributor. Regular collaborators
   should create a topic branch in this repository.
2. Keep each commit to one meaningful change. Stage explicit paths or use
   `git add -p`; do not sweep unrelated working-tree changes into the commit.
3. Run the checks below and record the results in the pull request template.
4. Open a pull request against `main`. Do not force-push after review unless a
   maintainer asks for it; a new push may invalidate an existing approval.

```sh
python3 scripts/validate_skill.py
python3 scripts/scan_text.py README.md
python3 scripts/scan_text.py SKILL.md
git diff --check
```

By contributing, you agree that your contribution is licensed under the MIT
license in [LICENSE](LICENSE). See [GOVERNANCE.md](GOVERNANCE.md) for how project
decisions are made and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for participation
expectations.
