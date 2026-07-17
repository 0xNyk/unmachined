# Host support

The portable artifact is the skill directory itself. Keep behavioral logic in
`SKILL.md`, references, and scripts. Host adapters should only handle discovery
or packaging.

## Invocation

Use one command namespace everywhere:

```text
/unmachined <task>
/unmachined onboard
/unmachined always-on
/unmachined always-off
/unmachined status
/unmachined audit <target>
/unmachined fix <target>
/unmachined text <target>
/unmachined ui <target>
/unmachined diff [base]
```

Subcommands are ordinary arguments. This works on hosts that expose skills as
slash commands and remains understandable on hosts that invoke skills through
natural language. Separate `unmachined-audit` and `unmachined-fix` skills would
duplicate the shared rules, increase discovery noise, and let the workflows
drift.

## Always-on after install

After linking the skill directory, run onboarding once so the user chooses
native enforcement:

```bash
python3 /path/to/unmachined/scripts/onboard.py
```

If `always_on` is true in `~/.config/unmachined/config.json` or project
`.unmachined.json`, agents that have the skill installed must treat anti-slop
as the default for user-facing text (see `references/always-on.md`). Optional
session start: `python3 scripts/onboard.py --show` and note the policy in the
session brief.

## Discovery and installation

| Host | User scope | Project scope | Slash behavior |
|---|---|---|---|
| Claude Code | `~/.claude/skills/unmachined/` | `.claude/skills/unmachined/` | Skills are directly invocable as `/unmachined` |
| Codex | `$CODEX_HOME/skills/unmachined/` | Use the current Codex project skill location when project scoping is needed | Invoke the discovered skill by name; do not rely on legacy prompt files |
| Cursor | `~/.cursor/skills/unmachined/` | `.cursor/skills/unmachined/` | Current Agent Skills appear in the slash menu |
| Hermes | `~/.hermes/skills/unmachined/` or a category below `skills/` | Install through the Hermes skill manager when distribution is preferred | Every installed skill becomes `/unmachined` |

Symlink the whole directory for local development. Copy or install it for a
stable release. Restart or begin a new session after installation when the host
caches skill metadata.

## Portability rules

- Keep `name` and `description` within the Agent Skills specification. Put
  version data under `metadata`.
- Make the description say both what the skill does and when it should load.
- Keep `SKILL.md` as a routing document. Load focused references only when the
  selected pipeline needs them.
- Avoid host-specific tool names in the core workflow. Describe capabilities,
  then use whichever read, shell, browser, image, or edit tool the host offers.
- Treat automatic invocation as config-driven: when always-on is false,
  explicit `/unmachined` is required; when always-on is true, writing policy
  is automatic for user-facing text. Every workflow must also work when a
  user explicitly invokes `/unmachined`.
- Do not use pre-approved tool frontmatter for portability. Tool permission
  support varies by client, and this skill does not need silent side effects
  beyond reading/writing the user's unmachined config on onboard.

## Source basis

Checked July 2026 against the Agent Skills specification and the official
documentation for Claude Code, Codex, Cursor, and Hermes Agent. Recheck host
paths before publishing a new major release; discovery conventions can change.

- [Agent Skills specification](https://agentskills.io/specification)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Codex customization](https://developers.openai.com/codex/concepts/customization/#skills)
- [Cursor Agent Skills announcement](https://cursor.com/changelog/2-4)
- [Hermes: Working with Skills](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/guides/work-with-skills.md)
