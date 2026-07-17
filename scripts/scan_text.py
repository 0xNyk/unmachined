#!/usr/bin/env python3
"""unmachined text scanner: deterministic AI-slop detection. Zero dependencies.

Usage:
    python3 scan_text.py FILE [FILE...] [--json] [--threshold 40]
    echo "text" | python3 scan_text.py - [--json]

Exit codes: 0 = pass, 1 = fail (score >= threshold), 2 = usage error.

Scores 0-100 (lower is better). Findings carry severity: critical (+20),
major (+10), minor (+3). The full rule catalog with rationale lives in
references/text-tells.md; this scanner ships the deterministic core.
"""
import argparse
import json
import math
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------- word lists

CRITICAL_PHRASES = [
    # empty transitions / signposting
    "delve into", "delve", "dive into", "let's dive in", "let's explore",
    "let's break it down", "let's take a closer look", "unpack", "embark on",
    "here's what you need to know",
    # ai conclusions / authority tropes
    "in conclusion", "at the end of the day", "the key takeaway",
    "the bottom line", "it's important to remember", "it's worth noting",
    "needless to say", "one thing is clear", "without a doubt",
    "this changes everything", "here's what people miss",
    "the real question is", "the real unlock", "at its core",
    "what really matters",
    # chatgpt-isms
    "in today's fast-paced world", "in today's digital landscape",
    "as technology continues to evolve", "now more than ever",
    "whether you're", "from beginners to experts",
    "no matter your experience",
    # motivational filler
    "unlock your potential", "become the best version", "dream big",
    "game changer", "game-changer", "game-changing", "next level",
    "next-level",
    # ai-flagship vocabulary
    "tapestry", "testament to", "a testament", "evolving landscape",
    "rich tapestry", "pivotal moment", "indelible mark",
    # chatbot artifacts
    "i hope this helps", "great question", "excellent point",
    "you're absolutely right",
]

MAJOR_PHRASES = [
    # marketing fluff
    "cutting-edge", "state-of-the-art", "world-class", "industry-leading",
    "best-in-class", "market-leading", "revolutionary", "groundbreaking",
    "disruptive", "innovative solution", "robust platform", "robust solution",
    "seamless experience", "seamlessly", "seamless", "supercharge",
    "blazing fast", "blazingly fast", "powerful capabilities",
    "comprehensive solution", "scalable solution", "next-generation",
    "mind-blowing",
    # corporate buzzwords
    "synergy", "paradigm", "holistic", "value proposition",
    "mission-critical", "leverage", "leveraging", "utilize", "utilizing",
    "pivotal", "crucial", "landscape", "ecosystem", "elevate", "empower",
    "harness", "unlock", "revolutionize", "redefine",
    # ai analysis verbs
    "underscores", "underscoring", "highlighting the", "showcasing",
    "showcases", "fostering", "boasts a", "boasts an", "serves as a",
    "stands as a",
    # weasel attributions
    "experts argue", "industry reports", "some critics argue",
    "studies show that",
    # bloat
    "in order to", "due to the fact that", "at this point in time",
    "for all intents and purposes", "it goes without saying",
    "the vast majority of", "has the ability to",
]

MINOR_WORDS = [
    "just", "really", "very", "actually", "basically", "literally",
    "simply", "obviously", "clearly", "somewhat", "arguably", "vibrant",
    "intricate", "interplay", "garner", "notably", "moreover",
    "furthermore", "additionally",
]

ECHO_OPENERS = [
    "exactly right", "this is exactly", "you're right", "that's exactly",
    "spot on", "100%", "couldn't agree", "well said", "great point",
    "so true", "this!",
]

BANNED_OPENERS = [
    "certainly", "moreover", "additionally", "furthermore", "indeed",
    "undoubtedly", "importantly", "interestingly", "notably", "ultimately",
    "in essence", "in summary", "overall",
]

TEMPLATE_ARTIFACTS = [
    (r"\{[a-z_]+\}", "unfilled {placeholder}"),
    (r"\b(TODO|TBD|FIXME)\b", "TODO/TBD/FIXME left in text"),
    (r"(?i)lorem ipsum", "lorem ipsum"),
    (r"\b(suggested|generated|placeholder|draft)_[a-z_]+\b", "raw template field name"),
    # negative lookahead spares markdown links: [Label](url) is not a scaffold
    (r"\[[A-Z][^\]]{3,40}\](?!\()", "bracket scaffold line like [Hook - sharp claim]"),
    (r"(?m)^_{4,}\s*$", "____ separator"),
    (r"(?m)(…|\.\.\.)\s*$\n?\s*$", "dangling ellipsis line"),
]

# ------------------------------------------------------------------ scanning


def sentences(text):
    # drop markdown and html structure (headings, bullets, numbered lists, tables,
    # code fences, raw tags) before cadence analysis. A list item is not a sentence
    # and <details> is not an opener; counting them produces phantom repetition.
    prose_lines, in_fence = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or s.startswith(("#", "-", "*", "|", ">", "<")):
            continue
        if re.match(r"\d+[.)]\s", s):  # 1. ordered list item
            continue
        prose_lines.append(line)
    parts = re.split(r"(?<=[.!?])\s+", "\n".join(prose_lines).strip())
    return [p for p in parts if p]


def mask_code(text):
    # mentions are not uses: strip fenced blocks and inline code spans before
    # matching so rule catalogs and docs can quote tells as `code`
    text = re.sub(
        r"```.*?```",
        lambda match: "\n" * match.group(0).count("\n"),
        text,
        flags=re.DOTALL,
    )
    # an inline span may wrap across a line, so allow one newline inside it
    text = re.sub(
        r"`[^`]{1,200}`",
        lambda match: "\n" * match.group(0).count("\n") or " ",
        text,
    )
    # markdown images and links reduce to their alt/label text: the "!" in
    # ![alt](src) is syntax, not an exclamation, and a URL is not prose
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)


# ------------------------------------------------- personal voice (additive)
#
# A voice profile (scripts/voice_profile.py, references/personal-voice.md)
# relaxes ONLY these stylistic budgets toward the user's measured baseline:
#   - exclamation budget (minor)
#   - rhetorical-question budget (minor)
#   - rhythm-monotony dominance threshold (major)
#   - repetitive-sentence-opener count for the user's favorite openers (major)
# Relax-only invariant: findings with a profile are a subset of findings
# without one. Honesty rules, CRITICAL/MAJOR/MINOR vocabulary, em-dash,
# template artifacts, and unsupported-claim checks NEVER personalize.


def _profile_rate(profile, section, key):
    try:
        value = profile[section][key]
    except (KeyError, TypeError):
        return None
    return value if isinstance(value, (int, float)) else None


def _personal_budget(rate_per_1000, word_count, floor, cap):
    """Expected occurrences at the personal rate, with headroom, clamped so
    a profile can only relax the global budget, never tighten it."""
    expected = rate_per_1000 * word_count / 1000.0
    return max(floor, min(cap, int(math.ceil(expected * 1.5))))


def default_profile_path():
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = xdg if xdg else os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "unmachined", "voice-profile.json")


def load_voice_profile(path=None, require_enabled=False):
    """Read a voice profile JSON; returns None when absent or disabled."""
    target = path or default_profile_path()
    try:
        with open(target, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    if require_enabled and not data.get("enabled", False):
        return None
    return data


def scan(text, mode="prose", profile=None):
    findings = []
    text = mask_code(text)
    low = text.lower()

    # personal budgets (identical to globals when profile is None)
    word_count = len(text.split())
    excl_budget, question_budget = 1, 2
    monotony_share, favorite_openers = 0.5, ()
    if isinstance(profile, dict):
        rate = _profile_rate(profile, "punctuation", "exclamation_per_1000_words")
        if rate:
            excl_budget = _personal_budget(rate, word_count, floor=1, cap=4)
        rate = _profile_rate(profile, "punctuation", "question_per_1000_words")
        if rate:
            question_budget = _personal_budget(rate, word_count, floor=2, cap=6)
        share = _profile_rate(profile, "sentence_length", "top_trigram_share")
        if share:
            monotony_share = max(0.5, min(0.75, share + 0.1))
        favorites = (profile.get("openers") or {}).get("favorites")
        if isinstance(favorites, list):
            favorite_openers = tuple(f for f in favorites if isinstance(f, str))

    def hit(severity, rule, detail, match=None):
        finding = {"severity": severity, "rule": rule, "detail": detail}
        if match is not None:
            line = text.count("\n", 0, match.start()) + 1
            source_line = text.splitlines()[line - 1].strip()
            finding.update({"line": line, "excerpt": source_line[:110]})
        findings.append(finding)

    # phrase lists (word-boundary match)
    for phrase, sev, label in (
        [(p, "critical", "critical phrase") for p in CRITICAL_PHRASES]
        + [(p, "major", "major phrase") for p in MAJOR_PHRASES]
    ):
        match = re.search(r"(?<![\w-])" + re.escape(phrase) + r"(?:s|d|es)?(?![\w-])", low)
        if match:
            hit(sev, label, phrase, match)

    minor_hits = []
    for word in MINOR_WORDS:
        match = re.search(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", low)
        if match:
            minor_hits.append((word, match))
    for word, match in minor_hits[:8]:
        hit("minor", "hedge/filler word", word, match)

    # punctuation tells
    n_em = text.count("—") + text.count("–") + len(re.findall(r"(?<=\w)--(?=\w)", text))
    if n_em:
        hit("critical", "em/en dash", f"{n_em} occurrence(s); use a single hyphen or restructure")
    if text.count("!") > excl_budget:
        hit("minor", "exclamation budget", f"{text.count('!')} exclamation marks (budget: {excl_budget})")
    if "“" in text or "‘" in text:
        hit("minor", "curly quotes", "typographic quotes in plain-text surface")

    # structural patterns
    if re.search(r"\bnot (just|only|merely|simply)\b[^.!?\n]{3,80}[,;]?\s*(but|it'?s|it is|rather)\b", low):
        hit("critical", "negation-redefinition", "'not just X, it's Y' construction")
    if re.search(r"\bit'?s not about\b[^.!?\n]{3,60}\bit'?s about\b", low):
        hit("critical", "negation-redefinition", "'it's not about X, it's about Y'")
    if re.search(r"\bfrom \w+([ -]\w+)? to \w+([ -]\w+)?\b", low):
        hit("minor", "possible false range", "'from X to Y' - verify it is a real scale")
    if re.search(r"\b(every single (team|developer|company|person)|100% of|nobody is|no one is)\b", low):
        hit("major", "sweeping categorical claim", "absolute claim; qualify or cite")
    if re.search(r"\b(the market|the industry|the data|technology) (doesn'?t|does not|won'?t) (care|lie|wait)\b", low):
        hit("major", "personified abstraction", "abstraction given agency")

    # echo / sycophancy openers (first 40 chars)
    head = low.lstrip()[:40]
    for opener in ECHO_OPENERS:
        if head.startswith(opener):
            hit("critical", "echo opener", opener)

    # sentence-level cadence
    sents = sentences(text)
    if len(sents) >= 4:
        firsts = [s.split()[0].lower().strip(",.;:") for s in sents if s.split()]
        for word in set(firsts):
            needed = 4 if word in favorite_openers else 3
            if firsts.count(word) >= needed and word not in ("the", "a", "i", "it"):
                hit("major", "repetitive sentence opener", f"'{word}' opens {firsts.count(word)} sentences")
        for s in sents:
            first = s.split()[0].lower().strip(",.;:") if s.split() else ""
            if first in BANNED_OPENERS:
                hit("minor", "banned sentence opener", first)
        # rhythm monotony: S/M/L trigrams
        buckets = "".join(
            "S" if len(s.split()) <= 8 else "M" if len(s.split()) <= 20 else "L"
            for s in sents
        )
        trigrams = [buckets[i:i + 3] for i in range(len(buckets) - 2)]
        if trigrams:
            top = max(set(trigrams), key=trigrams.count)
            if trigrams.count(top) / len(trigrams) > monotony_share and len(trigrams) >= 4:
                hit("major", "rhythm monotony", f"trigram '{top}' dominates sentence-length cadence")

    if low.count("?") > question_budget and mode != "chat":
        hit("minor", "rhetorical questions", f"{low.count('?')} questions (budget: {question_budget})")

    # template artifacts. Case-sensitive by default: a leftover marker is written
    # TODO, while "todo" lowercase is an ordinary noun (a kanban column, a todo
    # list). Patterns that want case-insensitivity say so themselves.
    for pattern, label in TEMPLATE_ARTIFACTS:
        if re.search(pattern, text):
            hit("critical", "template artifact", label)

    # unsupported superiority claims
    if re.search(r"\b(fastest|lowest latency|#1|number one|guaranteed|unbeatable)\b", low):
        if not re.search(r"\d+\s?(ms|µs|us|%|x)\b|p\d{2}|benchmark|measured|methodology", low):
            hit("critical", "unsupported claim", "superiority claim without a cited measurement")

    # emoji in headings / bullets
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("#", "-", "*")) and any(
            unicodedata.category(ch) == "So" for ch in stripped
        ):
            hit("major", "emoji decoration", f"emoji in heading/bullet: {stripped[:50]}")
            break

    return findings


def score(findings):
    weights = {"critical": 20, "major": 10, "minor": 3}
    return min(100, sum(weights[f["severity"]] for f in findings))


def main():
    ap = argparse.ArgumentParser(description="unmachined deterministic text scanner")
    ap.add_argument("files", nargs="+", help="text files, or - for stdin")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--threshold", type=int, default=40, help="fail at score >= N (default 40)")
    ap.add_argument("--mode", choices=["prose", "chat", "ui"], default="prose")
    ap.add_argument("--personal", action="store_true",
                    help="judge against the learned voice profile when one is enabled")
    ap.add_argument("--profile", metavar="PATH", default=None,
                    help="explicit voice-profile JSON (implies personal mode)")
    args = ap.parse_args()

    profile = None
    if args.profile:
        profile = load_voice_profile(args.profile)
        if profile is None:
            print("cannot read profile: {0}".format(args.profile), file=sys.stderr)
            sys.exit(2)
    elif args.personal:
        profile = load_voice_profile(require_enabled=True)

    if not 1 <= args.threshold <= 100:
        print("threshold must be between 1 and 100", file=sys.stderr)
        sys.exit(2)
    if "-" in args.files and len(args.files) != 1:
        print("stdin (-) cannot be combined with file paths", file=sys.stderr)
        sys.exit(2)

    findings = []
    for path in args.files:
        try:
            text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        except (OSError, UnicodeError) as exc:
            print("cannot read {0}: {1}".format(path, exc), file=sys.stderr)
            sys.exit(2)
        if not text.strip():
            print("empty input: {0}".format("stdin" if path == "-" else path), file=sys.stderr)
            sys.exit(2)
        source = "<stdin>" if path == "-" else path
        for finding in scan(text, mode=args.mode, profile=profile):
            finding["file"] = source
            findings.append(finding)

    total = score(findings)
    passed = total < args.threshold

    if args.json:
        print(json.dumps({"score": total, "threshold": args.threshold,
                          "pass": passed, "personal": profile is not None,
                          "findings": findings}, indent=2))
    else:
        for f in sorted(findings, key=lambda x: ("critical", "major", "minor").index(x["severity"])):
            location = f["file"]
            if "line" in f:
                location += ":{0}".format(f["line"])
            print(f"[{f['severity'].upper():8}] {location} {f['rule']}: {f['detail']}")
            if f.get("excerpt"):
                print("           {0}".format(f["excerpt"]))
        personal_note = " [personal voice]" if profile is not None else ""
        print(f"\nslop score: {total}/100 (threshold {args.threshold}){personal_note} -> {'PASS' if passed else 'FAIL'}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
