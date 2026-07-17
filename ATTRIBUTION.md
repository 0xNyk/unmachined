# Attribution

unmachined is a distillation. The rules were merged, deduplicated, re-severitied, and in
places rewritten from a research pass across the anti-slop field. Where sources disagreed,
SKILL.md picks a winner and says so rather than averaging them.

This file credits the sources and records their licenses. Where a source is quoted rather
than distilled, the reference file carries an inline marker (for example `(humanizer)`,
`(jalaalrd)`, `(unslop)`).

unmachined itself is MIT. See `LICENSE`.

## Apache-2.0 sources

These two are acknowledged under the Apache License 2.0. Their rules informed
`references/design-system.md` (interface copy, empty states) and
`references/design-tells.md` (eyebrow and kicker discipline). The prose in this repo is
rewritten, not copied.

| Source | License |
|---|---|
| Anthropic, `frontend-design` skill | Apache-2.0 |
| `impeccable` skill | Apache-2.0 |

## MIT sources

| Source | Fed into | License |
|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer) | `text-tells.md`: vocabulary kill list, voice-and-soul rules | MIT (Copyright 2025 Siqi Chen) |
| [theclaymethod/unslop](https://github.com/theclaymethod/unslop) | `text-tells.md`: 313-phrase lexicon, deterministic scanning, the regenerate-against-directive loop | MIT |
| [jalaalrd/anti-ai-slop-writing](https://github.com/jalaalrd/anti-ai-slop-writing) | `text-tells.md`: punctuation budgets, specificity rules | MIT (asserted in README) |
| [nutlope/hallmark](https://github.com/nutlope/hallmark) | `design-system.md`, `design-tells.md` | MIT |
| [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill) | `design-tells.md`: decoration and metadata tells | MIT |
| Anthropic, frontend-aesthetics cookbook | `design-system.md`: the three dials | MIT (anthropics/claude-cookbooks) |
| [Vercel, web-interface-guidelines](https://github.com/vercel/web-interface-guidelines) | `stack-rules.md`, `design-system.md` | MIT (asserted in README) |
| [shadcn/ui](https://github.com/shadcn-ui/ui) official skill | `stack-rules.md`: shadcn de-genericization | MIT |
| ofershap/tailwind-best-practices | `stack-rules.md`: Tailwind v4 | MIT |

## CC BY-SA

**Wikipedia, "Signs of AI writing"** (WikiProject AI Cleanup), CC BY-SA 4.0. The taxonomy of
written tells traces back here, largely by way of blader/humanizer, which ports it.
unmachined's catalog is restructured and re-severitied rather than copied, but the debt is
direct and worth naming.

## Research

**Sun et al., "Idiosyncrasies in Large Language Models"**,
[arXiv:2502.12150](https://arxiv.org/abs/2502.12150) (ICML 2025). The empirical basis for
the claim that model idiosyncrasies live in word-level distributions and survive rewriting,
translation, and summarization. That finding is why unmachined fixes cadence and structure
instead of stopping at vocabulary.

## Style references

Mailchimp Content Style Guide (open-sourced), Atlassian Design System, Slack, Intuit, and
the GOV.UK Style Guide were consulted for `voice-and-copy.md`. Referenced, not reproduced.

---

Maintainers: if you want an attribution changed, or your material removed, open an issue.
