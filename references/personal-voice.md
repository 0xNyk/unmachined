# Personal voice layer

Contents: what the profile is, where it lives, how scans use it, how fix and
rewrite workflows use it, and what never personalizes.

The global scanner judges text against population-level thresholds: one
exclamation mark, two questions, no dominant sentence-length cadence. A real
writer has a measurable baseline that can sit away from those defaults
without being AI slop. The personal voice layer learns that baseline from the
user's own writing and (a) relaxes a small documented set of stylistic
budgets toward it, (b) gives fix and rewrite flows verbatim exemplars to
target, so a repaired draft sounds like the user, not like generic-human.

Everything is deterministic and local: computed statistics plus exemplars,
no LLM calls, no network.

## The profile

Built by `scripts/learn.py`, stored as JSON at
`~/.config/unmachined/voice-profile.json` (respects `XDG_CONFIG_HOME`),
next to the always-on config. Fields:

| Field | Meaning |
|---|---|
| `corpus` | sample/word/sentence counts, per-source counts, reference size |
| `sentence_length` | S/M/L shares (scanner buckets: S <=8 words, M <=20, L >20), mean words, top cadence trigram and its share |
| `contractions` | contractions per 100 words |
| `punctuation` | em-dash, exclamation, ellipsis, question rates per 1000 words |
| `casing` | lowercase sentence-start rate |
| `vocabulary.distinctive` | top words vs a reference corpus (rate ratio) |
| `openers` | top sentence openers, opener bigrams, and `favorites` |
| `paragraphs` | mean sentences and words per paragraph |
| `exemplars` | 10-20 verbatim samples, length-capped, flagged by source |
| `enabled` | personal mode toggle (`learn on` / `learn off`) |

Sources are pluggable ingesters, each optional. The corpus and voice-pack
locations are machine-local, never hardcoded: `--x-corpus`/`--voice-dir`
flags win, then the env vars `UNMACHINED_VOICE_CORPUS`/`UNMACHINED_VOICE_DIR`,
then the `voice_corpus`/`voice_dir` keys in the unmachined config (project
`.unmachined.json`, then `~/.config/unmachined/config.json`). Unconfigured
sources are skipped with a hint.

1. **X posts corpus** (`voice_corpus`) - the user's own posts as a JSON list
   of post strings. Any `comp-*.json` and `ref-*.json` files in the same
   directory are other authors; they become the reference distribution for
   distinctive vocabulary, never voice samples.
2. **Voice few-shot files** (`voice_dir`) - blockquotes under the user's
   own-voice label in the voice pack's `few-shot/*.md`; GENERIC
   counterexamples are excluded.
3. **Claude Code transcripts** - user-role messages the human typed
   (`promptSource: typed`; sidechains, tool results, sdk/system prompts, and
   CLI wrapper messages are rejected). Code fences, inline code, URLs, paths, and
   shell-looking lines are stripped so the profile learns prose, not shell.
   Compaction duplicates are removed by hash.
4. **`--path` globs** - arbitrary future sample files.

## Commands

```bash
python3 scripts/learn.py                  # build from all default sources
python3 scripts/learn.py status           # summary of the saved profile
python3 scripts/learn.py off              # keep the profile, stop applying it
python3 scripts/learn.py on               # re-enable
python3 scripts/learn.py --path 'drafts/*.md' --no-transcripts --days 30
```

## Scan consumption (personal mode)

```bash
python3 scripts/scan_text.py FILE --personal        # uses the enabled profile
python3 scripts/scan_text.py FILE --profile p.json  # explicit profile file
```

Module API: `scan(text, mode="prose", profile=None)`. The parameter is
additive; `profile=None` preserves exact global behavior, which is what
external gates that import the scanner keep getting.

Personalization is **relax-only**: a profile can loosen a stylistic budget
toward the measured baseline, never tighten one, so personal-mode findings
are always a subset of global findings. The full list of checks a profile
can touch:

| Check | Global | Personal |
|---|---|---|
| exclamation budget (minor) | 1 | expected count at the personal rate x1.5, capped at 4 |
| rhetorical questions (minor) | 2 | expected count at the personal rate x1.5, capped at 6 |
| rhythm monotony (major) | >50% trigram dominance | personal top-trigram share +0.1, capped at 75% |
| repetitive sentence opener (major) | 3 repeats | 4 repeats, only for openers in `openers.favorites` |

**Never personalized:** honesty rules (unsupported claims, invented metrics),
`CRITICAL_PHRASES`, `MAJOR_PHRASES`, `MINOR_WORDS`, em-dash, echo and banned
openers, negation-redefinition, template artifacts, sweeping claims, emoji
decoration. Slop is slop in anyone's voice.

## Fix and rewrite consumption

When personal mode is enabled and the task is `fix` (or any rewrite of the
user's own prose), rewrite **toward the exemplars**, not toward neutral
prose:

1. Load 3-5 `exemplars` (prefer ones matching the target surface: posts for
   posts, replies for replies) and keep them visible while editing.
2. Match the measured shape: sentence-length mix near the profile's S/M/L
   shares, contraction rate as measured, the user's openers and distinctive
   vocabulary where they fit naturally.
3. Respect casing habits: if `lowercase_sentence_start_rate` is high, do not
   capitalize every repaired sentence.
4. Fix findings without sanding voice: repair the flagged phrase, keep the
   cadence. If a repair would make the text read less like the exemplars,
   pick a different repair.
5. Exemplars are style targets, never content: do not copy their claims,
   numbers, or anecdotes into the draft.

## Failure modes

- No profile, or `enabled: false`: everything behaves exactly as before.
- Small corpus: `learn` refuses to save when no prose sentences were found.
- Stale profile: `generated_at` is in the JSON; re-run `learn` after the
  corpus grows. The profile never updates itself.
