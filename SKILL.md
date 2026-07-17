---
name: unmachined
description: >-
  Finds and removes AI slop from prose, UX copy, and web interfaces. Use when
  writing, auditing, or revising articles, posts, READMEs, marketing copy, UI
  copy, layouts, or frontend code that must not feel AI-generated; when the
  user says unmachined, de-slop, AI slop, anti-slop, humanize, make this
  human, sounds like AI or ChatGPT, looks AI-generated, feels generic, or
  design/copy audits; and when always-on is enabled in unmachined config (any
  user-facing text in the CLI must pass anti-slop rules and scan_text before
  ship). Quality layer, not the author: it edits what authoring skills
  produce. Not for greenfield brand or aesthetic invention, pure logic without
  user-facing strings, or evading AI detectors. Supports onboard,
  always-on/off, status, learn (personal voice profile), audit, fix, text,
  ui, and diff workflows.
license: MIT
metadata:
  version: "0.5.1"
---

# unmachined

Make it read written and look made, not generated.

AI output converges on the statistical center: the same vocabulary, the same
cadence, the same purple gradient on the same centered hero. This skill holds
two lines of defense. First, catalogs of known tells with severity tiers.
Second, a variety requirement, because the fix becomes a new tell when every
output converges on the same alternative. Never swap one monoculture for
another.

**Priorities:** text first, design and layout equal second, branding last.

## Always-on (native enforcement)

Once installed, the skill can stay **on for the whole CLI session** so agents
do not write AI-text slop unless the user opts out.

| Mode | Behavior |
|---|---|
| **always_on: true** | Every user-facing text (and optional UI) is drafted under anti-slop rules and scanned before ship. No need to type `/unmachined` each time. |
| **always_on: false** | Opt-in only: run `/unmachined …` when you want enforcement. |
| **not onboarded** | Ask once (see onboard). Until answered, treat as off. |

Full contract: `references/always-on.md`.

### Onboarding (required once)

On first use, or when `onboarded_at` is missing, **ask**:

> Turn unmachined **always-on** for this CLI so all user-facing writing is
> anti-slop by default? Or leave **off** (only when you invoke the skill)?

Then save via:

```bash
python3 scripts/onboard.py                 # interactive
python3 scripts/onboard.py --always-on     # native on, text+ui
python3 scripts/onboard.py --always-on --text-only
python3 scripts/onboard.py --always-off
python3 scripts/onboard.py --show          # status
```

Config: project `.unmachined.json` overrides `~/.config/unmachined/config.json`.
Env `UNMACHINED_ALWAYS_ON=1|0` overrides the boolean for a single session.

### Agent duties when always_on is true

1. Resolve config (`scripts/onboard.py --show` or read the JSON files).
2. Load `references/text-tells.md` before drafting user-facing prose.
3. Write clean; do not draft slop intending to clean later.
4. Run `scripts/scan_text.py` on the deliverable; score >= threshold **blocks ship**.
5. If `ui` is in surfaces and the task is UI, also load design refs and
   `scan_ui.py` when editing UI source.
6. First content write of the session: one short line that always-on is active.

Out of scope: pure logic without user-facing strings; this skill's ban-list
docs; raw logs and data dumps. See always-on.md.

## Verbs

| Invocation | Behavior |
|---|---|
| `/unmachined <task>` (default) | Build or write with all applicable rules active from the start |
| `/unmachined onboard` | Ask always-on preference; write config |
| `/unmachined always-on` | Enable always-on and save |
| `/unmachined always-off` | Disable always-on and save |
| `/unmachined status` | Print resolved config |
| `/unmachined learn` | Build the personal voice profile from the user's own writing (`scripts/learn.py`) |
| `/unmachined learn status` | Print the saved voice-profile summary |
| `/unmachined learn off` / `learn on` | Toggle personal mode without deleting the profile |
| `/unmachined audit <target>` | Score and report findings by severity. Never edit |
| `/unmachined fix <target>` | Audit, repair, verify, and summarize the changes |
| `/unmachined text <target>` | Run only the prose and copy pipeline |
| `/unmachined ui <target>` | Run only the interface and frontend pipeline |
| `/unmachined diff [base]` | Audit only changed lines and their necessary context |

Hosts without slash commands use the same words in natural language.

## Dispatch contract

1. Parse an explicit verb first. If none is present, use the default build
   workflow. A file named `audit` or `fix` remains a target when supplied as a
   path.
2. If verb is `onboard` / `always-on` / `always-off` / `status`, handle config
   only (shell `scripts/onboard.py` …). If verb is `learn` (or `learn
   status|on|off`), shell `scripts/learn.py` and load
   `references/personal-voice.md`.
3. If no config `onboarded_at` and the task will write user-facing text, run
   onboarding **once** before continuing (or instruct the user to run the script).
4. If always_on is true, apply the always-on agent duties even when the user
   did not type `/unmachined`.
5. Resolve the smallest target that satisfies the request. For `diff`, use the
   working-tree diff by default.
6. State detected surfaces in one short line when both text and UI apply.
7. `audit` and `diff` are read-only unless the user asks to fix.
8. Load only the references named by the chosen pipeline.

## Load budget

One hop per level: description -> this file -> the reference the pipeline
names. Bulk-loading `references/` is a defect, not thoroughness.

- Text (default): `text-tells.md` only. Add `voice-and-copy.md` for microcopy,
  `technical-founder-correspondence.md` for founder or sales replies.
- UI: `design-tells.md`. Add `design-system.md` only when building or
  restyling, `audit-playbook.md` only for audit/fix on existing UI, and
  `stack-rules.md` only when package.json shows Next.js, Tailwind, or shadcn.
- Config verbs (`onboard`, `always-on`, `always-off`, `status`): scripts only,
  no references.
- Personal voice (`learn` verb, or fix/rewrite of the user's own prose when a
  profile is enabled): `personal-voice.md` only.
- Execute the scanners, never read their source. `scan_text.py` and
  `scan_ui.py` are run targets, not reading material.

## Text pipeline (main priority)

1. Read `references/text-tells.md`. Microcopy also needs
   `references/voice-and-copy.md`.
2. Draft or edit under the rules (em-dash ban; no critical vocabulary; concrete
   claims; honesty gate).
3. Run the deterministic scanner before self-judgment:
   `python3 scripts/scan_text.py <file> [file...] [--json] [--threshold 40] [--mode prose|chat|ui]`
   Stdin works for pasted content. Score >= threshold blocks `fix` / build /
   always-on delivery. Fix criticals first. For JSX/TSX or other source files,
   do not treat a whole-file `scan_text.py` score as a copy verdict: operators,
   comments, template expressions, and placeholders can produce false positives.
   Run `scan_ui.py` on the source, then scan extracted user-facing strings or
   changed copy separately with `scan_text.py`. When a personal voice profile
   is enabled and the text is the user's own writing, add `--personal` and
   follow `references/personal-voice.md` for fix/rewrite exemplar targeting.
4. Self-critique once, naming what still reads as AI-generated. Revise for
   cadence and variety. Do not sand every sentence to the same length.
5. Honesty gate: every number is real or a labelled placeholder. No invented
   metrics, quotes, or anecdotes.
6. For technical founder DMs, prospect chats, or sales-engineering replies, load
   `references/technical-founder-correspondence.md`. Separate truth approval from
   voice editing: the domain owner confirms the substance first, then improve the
   wording without changing claims. For outreach batches, scan every message
   individually and scan the concatenated bodies as a batch; repeated openers,
   questions, founder lines, CTAs, or sentence rhythms block shipment even when
   each message passes alone. Deleted or retracted messages remain history, but
   their claims and CTAs are inactive until a corrected replacement is sent.

## Design pipeline

1. Read `references/design-tells.md` and `references/design-system.md`. Audits
   also need `references/audit-playbook.md`.
   `python3 scripts/scan_ui.py <src-dir> [--json] [--threshold 40] [--tailwind-version auto|3|4]`
2. For Next.js/Tailwind/shadcn, read `references/stack-rules.md` and match the
   project pin.
3. Structure before color; one justified aesthetic risk; WCAG 2.2 AA; reduced
   motion; focus visible; 320-768px layouts.

## Cross-output variety

Consecutive outputs must not share the same layout skeleton, display font, or
accent hue unless the project design system requires it.

## Resolved rule conflicts

- Em-dash: banned in generated text. Hyphen, comma, or restructure.
- Serif type: only with justification; not a lazy default.
- Metrics: real, cited, or labelled placeholder.
- Eyebrows / section numbers: only when they encode a true sequence.

## Reference index

| File | Load when |
|---|---|
| `references/always-on.md` | Onboard, always-on, or session writing policy |
| `references/text-tells.md` | Any text work |
| `references/technical-founder-correspondence.md` | Technical founder DMs, prospect chats, sales-engineering replies, or corrections after domain-owner review |
| `references/voice-and-copy.md` | Microcopy, UX writing |
| `references/personal-voice.md` | `learn` verb, personal-mode scans, fix/rewrite of the user's own prose |
| `references/design-tells.md` | Any UI work |
| `references/design-system.md` | Building or restyling UI |
| `references/audit-playbook.md` | audit or fix on existing UI |
| `references/stack-rules.md` | Next.js / Tailwind / shadcn |
| `references/host-support.md` | Install paths and host notes |
| `scripts/onboard.py` | Onboarding and always-on toggles |
| `scripts/learn.py` | Build/inspect/toggle the personal voice profile |
| `scripts/config_show.py` | Status |
| `scripts/scan_text.py` | Every text deliverable before shipping |
| `scripts/scan_ui.py` | UI source audits |

## Output discipline

This skill's own reports must pass its own rules. Findings are concrete: quote
the line, name the rule, show the fix. No praise padding. Never claim a scan,
render, or test that did not run.
