# Security

## What this code does

The two scanners in `scripts/` read files you point them at, match them against regex
catalogs, and print findings. No network calls, no file writes, no subprocess execution,
and no imports beyond the Python standard library (`argparse`, `json`, `re`, `sys`,
`unicodedata`, `pathlib`). Both are about 400 lines together and can be read in one
sitting.

`SKILL.md` and `references/` are plain Markdown loaded into an agent's context. Those files
instruct a model. Nothing in them runs.

## Reporting a vulnerability

Open a [security advisory](https://github.com/0xNyk/unmachined/security/advisories/new).
Please do not open a public issue for anything exploitable.

Expect a first response within a week.

## Scope

In scope: anything in `scripts/` that reads outside the paths it was given, crashes on
hostile input in a way that matters, or consumes unbounded resources on a crafted file.

Out of scope: the scanner disagreeing with you about whether a word is slop. That is a
[false positive](CONTRIBUTING.md), and it is a normal bug. File it as one.

A note on prompt injection: this skill is Markdown that an agent reads. A hostile file
handed to an agent alongside this skill can try to talk to the agent, as with any other
document. That is a property of the host, not of these rules.
