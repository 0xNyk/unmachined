# Always-on enforcement

When the user enables **always-on** (native) mode, unmachined is not only a
slash command. It is a **session writing policy** for every host that has the
skill installed.

## Config locations (first match wins for project scope)

| Scope | Path |
|---|---|
| Project | `.unmachined.json` in the current workspace root |
| User | `~/.config/unmachined/config.json` |
| Env override | `UNMACHINED_ALWAYS_ON=1` or `0` (wins over files for the boolean only) |

Create or update config with:

```bash
python3 scripts/onboard.py
# or non-interactive
python3 scripts/onboard.py --always-on --surfaces text,ui --threshold 40
python3 scripts/onboard.py --always-off
python3 scripts/config_show.py
```

## Schema

```json
{
  "version": 1,
  "always_on": true,
  "surfaces": ["text", "ui"],
  "threshold": 40,
  "scan_before_ship": true,
  "onboarded_at": "2026-07-14T00:00:00Z",
  "notes": "optional free text"
}
```

| Field | Meaning |
|---|---|
| `always_on` | If true, agents apply text (and optional UI) rules on **every** user-facing write without waiting for `/unmachined` |
| `surfaces` | `text` only, or `text` + `ui`. Default when on: `["text","ui"]` |
| `threshold` | `scan_text.py` score at or above this **blocks** ship. Default `40` |
| `scan_before_ship` | If true, run deterministic scanners on new/changed prose before presenting it as done |
| `onboarded_at` | Set by `onboard.py` when the user answers the install question |

Missing config = **not onboarded**. First explicit `/unmachined` run or first content write in a session **must** offer onboarding once (see below). Until then, always-on is treated as **off** (opt-in, not surprise enforcement).

## What always-on covers

**In scope (must pass text pipeline when always_on):**

- Marketing and product copy
- UI strings, empty states, button labels, error text
- READMEs, docs, blog MDX, changelogs, release notes
- Emails, X/social posts, commit messages that are user-facing prose
- Offer catalogs, FAQ answers, landing sections

**Out of scope (do not force full unmachined ceremony):**

- Pure logic code with no user-facing strings
- Ban-list / skill reference catalogs that name forbidden phrases
- Logs, stack traces, raw JSON data dumps
- Machine identifiers, URLs, file paths, code symbols

When a file mixes code and copy, enforce only on the copy (string literals,
markdown bodies, MDX prose). Prefer writing copy through the text pipeline
before embedding it.

## Agent contract (binding when always_on is true)

1. **Load** `references/text-tells.md` (and `voice-and-copy.md` for microcopy)
   before drafting user-facing text. Load design refs only if `ui` is in
   `surfaces` and the task is UI.
2. **Write under the rules** (em-dash ban, no critical vocabulary, concrete
   claims, honesty gate). Do not draft slop and clean later as the default path.
3. **Scan before ship** when `scan_before_ship` is true:
   - New or edited prose file:  
     `python3 scripts/scan_text.py <file> --mode prose|ui --threshold <threshold>`
   - Pasted or chat-only body: pipe through stdin.
   - Score **>= threshold** = **do not deliver** until fixed. Critical hits first.
4. **Self-critique once** after a clean scan: one pass for cadence and variety.
5. **State policy briefly** on the first content write of a session when always_on
   is on: `unmachined always-on (text[+ui], threshold N)`. No long lecture.
6. **Never claim** always-on is active unless `config_show` / file / env says so.

## Onboarding (must ask once)

Triggers (first of):

- `python3 scripts/onboard.py` or `/unmachined onboard`
- First `/unmachined` invocation with no config file
- Agent detects install and no `onboarded_at` while about to write user-facing text

Ask **one** clear question (or use the script interactively):

> unmachined can stay **always on** for this CLI: every user-facing text
> draft is written and scanned under anti-slop rules, not only when you type
> `/unmachined`. Turn always-on **on** or leave **off** (opt-in per command)?

Options:

| Choice | Result |
|---|---|
| **On** (recommended if the user hates AI tone) | `always_on: true`, surfaces text+ui, threshold 40 |
| **Off** | `always_on: false`, onboarded_at set so you do not re-ask every turn |
| **Text only** | `always_on: true`, `surfaces: ["text"]` |

Do not re-ask every session. Re-ask only if the user runs `onboard` again or
deletes the config. Honor `UNMACHINED_ALWAYS_ON` without overwriting the file
unless onboarding explicitly saves.

## Toggles

```text
/unmachined onboard          # full wizard
/unmachined always-on        # enable + save
/unmachined always-off       # disable + save
/unmachined status           # print resolved config
```

Shell equivalents: `scripts/onboard.py` with `--always-on` / `--always-off` /
`--show`.

## Project vs user

- Project `.unmachined.json` is for repos that must never ship slop (product sites).
- User config is the personal CLI default across repos.
- Resolution: env boolean override → project file → user file → default off.

## Host notes

Hosts cannot inject tools mid-generation. Always-on works because **agents
follow this skill contract** when the skill is installed and config says on.
Keep the skill linked in the host skill path (`ln -s` per README). Session
start hooks that run `python3 scripts/config_show.py --json` are optional and
recommended for Hermes/Claude session notes.
