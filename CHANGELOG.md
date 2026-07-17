# Changelog

This file records user-visible changes. Versions follow semantic versioning:
major for incompatible workflow changes, minor for new behavior, and patch for
compatible fixes.

## 0.5.0 - 2026-07-17

- **Personal voice layer (`learn` verb):** `scripts/learn.py` builds a
  deterministic voice profile (sentence-length mix, contraction and
  punctuation rates, casing, distinctive vocabulary, favorite openers,
  paragraph shape, verbatim exemplars) from pluggable local sources: the
  user's own X-posts corpus, voice few-shot files, human-typed Claude Code
  transcript messages (code/URLs/shell stripped), and `--path` globs. No LLM
  calls. Profile JSON lives next to the always-on config. Corpus and
  voice-pack locations are machine-local: `voice_corpus`/`voice_dir` keys in
  the unmachined config or `UNMACHINED_VOICE_CORPUS`/`UNMACHINED_VOICE_DIR`
  env vars, never hardcoded paths.
- `scan_text.py` gains an additive `profile=` parameter plus `--personal` /
  `--profile` flags. Personalization is relax-only and limited to four
  stylistic budgets (exclamations, questions, rhythm monotony, favorite
  repeated openers); honesty rules and all vocabulary lists never
  personalize. `profile=None` (the default) is byte-identical to 0.4.0
  behavior, so external gates importing `scan`/`score` are unaffected.
- Add `references/personal-voice.md`: profile contract and exemplar-targeting
  guidance for fix/rewrite ("rewrite toward the exemplars, not neutral
  prose").
- Verbs: `learn`, `learn status`, `learn on`, `learn off`.

## 0.4.0 - 2026-07-17

- **Scanner-catalog sync test:** every phrase list in `scripts/scan_text.py`
  (`CRITICAL_PHRASES`, `MAJOR_PHRASES`, `MINOR_WORDS`, `ECHO_OPENERS`,
  `BANNED_OPENERS`) must now appear in `references/text-tells.md`; the test
  fails on drift. Downstream consumers import the scanner directly, so its
  public names stay stable.
- Document 48 scanner phrases that were missing from the catalog, and align
  the S/M/L rhythm bucket threshold (S is <=8 words, matching the scanner).
- **Load budget** section in SKILL.md: one reference hop per pipeline, no
  bulk-loading `references/`, execute scanners instead of reading them.
- Description: add humanize/anti-slop/feels-generic synonyms and negative
  triggers (quality layer, not the author; no greenfield brand work; no
  detector evasion).
- `validate_skill.py` now checks that every shipped reference is indexed in
  SKILL.md and every indexed reference exists.
- Add short contents lines to the four largest references.
- Add `references/technical-founder-correspondence.md` (truth approval before
  voice editing in founder and sales-engineering replies).

## 0.3.0 - 2026-07-15

- **Always-on mode:** optional native enforcement so user-facing CLI text is
  drafted and scanned under anti-slop rules without typing `/unmachined` each
  time. Onboarding asks once; config at `~/.config/unmachined/config.json` or
  project `.unmachined.json`. Env `UNMACHINED_ALWAYS_ON=1|0`.
- Add `scripts/onboard.py`, `scripts/config_lib.py`, `scripts/config_show.py`,
  and `references/always-on.md`.
- Verbs: `onboard`, `always-on`, `always-off`, `status`.
- Bump skill metadata to 0.3.0.

## 0.2.x notes

- Add pipeline and install blueprint infographics.
- Add brand assets (logo mark, lockup, social card, infographics) and
  `docs/brand.md`.
- Add repository governance, contributor intake, agent Git rules, and portable
  skill validation.

## 0.2.0 - 2026-07-12

- Add the README banner.
- Add `ui` and `diff` workflows.
- Document Claude Code, Codex, Cursor, and Hermes installation and invocation.
- Align frontmatter with the Agent Skills specification.

## 0.1.0 - 2026-07-09

- Publish the initial text and UI tell catalogs.
- Add zero-dependency text and UI scanners.
