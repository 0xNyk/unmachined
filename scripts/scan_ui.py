#!/usr/bin/env python3
"""unmachined UI scanner: deterministic AI-design-tell detection. Zero dependencies.

Greps source files for the machine-checkable subset of references/design-tells.md
and references/stack-rules.md. Visual tells that need a rendered page (layout
rhythm, hierarchy) stay with the LLM audit; this catches the grep-able core.

Usage:
    python3 scan_ui.py PATH [PATH...] [--json] [--threshold 40]
                       [--tailwind-version auto|3|4]

PATH may be files or directories (searched recursively for web source files).
Exit codes: 0 = pass, 1 = fail (score >= threshold), 2 = usage error.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EXTENSIONS = {".tsx", ".jsx", ".ts", ".js", ".html", ".css", ".vue", ".svelte", ".astro", ".mdx"}
SKIP_DIRS = {"node_modules", ".next", "dist", "build", ".git", "coverage", ".turbo", "out"}

CENTERED_HERO_PATTERN = (
    r"(?:(?:h-screen|min-h-screen|100vh)[^\n]*(?:items-center|justify-center)"
    r"|(?:items-center|justify-center)[^\n]*(?:h-screen|min-h-screen|100vh))"
    r"|(?:className|class)=[\"'][^\"']{0,500}"
    r"(?=[^\"']*(?:h-screen|min-h-screen|100vh))"
    r"(?=[^\"']*(?:items-center|justify-center))[^\"']*[\"']"
)
ICON_CIRCLE_PATTERN = (
    r"rounded-full[^\n]*bg-(?:blue|purple|indigo|green|pink|orange)-1?0?0[^\n]*p-[23]"
    r"|(?:className|class)=[\"'][^\"']{0,400}(?=[^\"']*rounded-full)"
    r"(?=[^\"']*bg-(?:blue|purple|indigo|green|pink|orange)-1?0?0)"
    r"(?=[^\"']*p-[23])[^\"']*[\"']"
)

# (severity, rule, regex, hint)
CHECKS = [
    # critical design tells
    ("critical", "AI purple gradient",
     r"(from|via|to)-(purple|violet|indigo|fuchsia)-\d|linear-gradient\([^)]*(purple|violet|indigo|#7c3aed|#8b5cf6|#a855f7|#6366f1)",
     "the single most recognized AI aesthetic; pick one deliberate accent instead"),
    ("critical", "default display font",
     r"font-family:\s*['\"]?(Inter|Roboto|Open Sans|Poppins|Lato)\b|fontFamily.*['\"](Inter|Roboto|Open Sans|Poppins|Lato)['\"]",
     "pair a deliberate display face with a body face; see design-system.md"),
    ("critical", "gradient headline text",
     r"bg-clip-text|background-clip:\s*text",
     "gradient-filled headings are a first-order tell"),
    ("critical", "emoji as feature icon",
     r"[✨\U0001F680⚡\U0001F525\U0001F3AF✅\U0001F4A1\U0001F31F]",
     "replace with a drawn icon set or none"),
    ("critical", "invented metric",
     r"\b(10|20|50|100)x (faster|better|more)|trusted by [\d,]+\+|\+\d+% (conversion|productivity)",
     "real numbers, a labelled placeholder, or nothing"),
    ("critical", "italic heading",
     r"<h[1-6][^>]*(italic|font-style:\s*italic)|(className|class)=[\"'][^\"']*\b(text-[0-9]?xl|heading)[^\"']*\bitalic",
     "headings stay roman; italics in display type is a reliable tell"),
    # major
    ("major", "centered 100vh hero",
     CENTERED_HERO_PATTERN,
     "full-viewport centered hero is the template answer; consider asymmetry or content-led height"),
    ("major", "section-number eyebrow",
     r">\s*0\d\s*[/·.]\s*[A-Z]",
     "eyebrows off by default; numbering only for true sequences"),
    ("major", "icon-in-colored-circle tile",
     ICON_CIRCLE_PATTERN,
     "SaaS-starter look; let icons sit unboxed or use a drawn treatment"),
    ("major", "transition-all",
     r"transition-all|transition:\s*all",
     "animate transform/opacity only, with named easings"),
    ("major", "universal hover scale",
     r"hover:scale-10[2-9]",
     "one orchestrated moment beats scattered hover effects"),
    ("major", "pure black or white surface",
     r"(background(-color)?:\s*#(000|000000|fff|ffffff)\b)|bg-(black|white)(?![\w/-])",
     "micro-tint surfaces; pure #000/#fff reads unconsidered"),
    ("major", "startup cliche name",
     r"\b(Acme|Nexus|SmartFlow)\b",
     "placeholder brand names are a tell; name the real thing"),
    # stack slop (tailwind v3 in a v4 world; verify version first per stack-rules.md)
    ("major", "tailwind v3 directive",
     r"@tailwind (base|components|utilities)",
     "v4 uses @import \"tailwindcss\"; confirm project version first"),
    ("major", "raw palette color in component",
     r"(bg|text|border)-(blue|indigo|purple|red|green)-[3-7]00",
     "use semantic tokens (bg-primary, text-muted-foreground), not raw palette stops"),
    ("major", "space-* utility",
     r"space-[xy]-\d",
     "prefer flex/grid + gap-*"),
    # minor
    ("minor", "placeholder person", r"\bJane Doe|John Doe\b", "use realistic, varied names"),
    ("minor", "z-index 9999", r"z-\[?9999\]?|z-index:\s*9999", "fix stacking context instead"),
    ("minor", "100vw", r"\b100vw\b", "causes horizontal scroll with scrollbars; use 100% or clip"),
    ("minor", "scroll cue", r"scroll (down|to explore)|↓ scroll", "content should invite scrolling on its own"),
]

WEIGHTS = {"critical": 20, "major": 10, "minor": 3}
TAILWIND_V4_ONLY_RULES = {"tailwind v3 directive"}


def iter_files(paths):
    for p in paths:
        path = Path(p)
        if path.is_file():
            yield path
        elif path.is_dir():
            for f in sorted(path.rglob("*")):
                if f.suffix in EXTENSIONS and not any(part in SKIP_DIRS for part in f.parts):
                    yield f


def detect_tailwind_version(path):
    """Return 3, 4, or None from the nearest package.json."""
    root = path if path.is_dir() else path.parent
    for directory in (root, *root.parents):
        package = directory / "package.json"
        if not package.is_file():
            continue
        try:
            payload = json.loads(package.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            continue
        dependencies = {}
        dependencies.update(payload.get("dependencies") or {})
        dependencies.update(payload.get("devDependencies") or {})
        version = dependencies.get("tailwindcss")
        if not isinstance(version, str):
            continue
        match = re.search(r"(?:^|[^0-9])([34])(?:\.|$)", version)
        if match:
            return int(match.group(1))
    return None


def scan_file(path, tailwind_version=None):
    findings = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    for severity, rule, pattern, hint in CHECKS:
        if rule in TAILWIND_V4_ONLY_RULES and tailwind_version != 4:
            continue
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            lineno = text.count("\n", 0, match.start()) + 1
            excerpt = re.sub(r"\s+", " ", match.group(0)).strip()[:110]
            findings.append({
                "severity": severity, "rule": rule, "hint": hint,
                "file": str(path), "line": lineno, "excerpt": excerpt,
            })
    return findings


def main():
    ap = argparse.ArgumentParser(description="unmachined deterministic UI scanner")
    ap.add_argument("paths", nargs="+", help="source files or directories")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--threshold", type=int, default=40)
    ap.add_argument(
        "--tailwind-version",
        choices=("auto", "3", "4"),
        default="auto",
        help="Tailwind context for version-specific checks (default: auto)",
    )
    args = ap.parse_args()

    if not 1 <= args.threshold <= 100:
        print("threshold must be between 1 and 100", file=sys.stderr)
        sys.exit(2)

    findings = []
    seen_rules_per_file = set()
    files = list(iter_files(args.paths))
    tailwind_versions = {}
    for f in files:
        version = (
            detect_tailwind_version(f)
            if args.tailwind_version == "auto"
            else int(args.tailwind_version)
        )
        tailwind_versions[str(f)] = version
        for finding in scan_file(f, tailwind_version=version):
            # score each (file, rule) pair once to avoid one repeated utility
            # class maxing the score, but report every location
            finding["scored"] = (finding["file"], finding["rule"]) not in seen_rules_per_file
            seen_rules_per_file.add((finding["file"], finding["rule"]))
            findings.append(finding)

    if not files:
        print("no scannable source files found", file=sys.stderr)
        sys.exit(2)

    total = min(100, sum(WEIGHTS[f["severity"]] for f in findings if f["scored"]))
    passed = total < args.threshold

    if args.json:
        print(json.dumps({"score": total, "threshold": args.threshold,
                          "pass": passed, "tailwind_versions": tailwind_versions,
                          "findings": findings}, indent=2))
    else:
        order = {"critical": 0, "major": 1, "minor": 2}
        for f in sorted(findings, key=lambda x: (order[x["severity"]], x["file"], x["line"])):
            print(f"[{f['severity'].upper():8}] {f['file']}:{f['line']} {f['rule']}")
            print(f"           {f['excerpt']}")
            print(f"           fix: {f['hint']}")
        versions = sorted({v for v in tailwind_versions.values() if v is not None})
        context = ",".join("v{0}".format(v) for v in versions) if versions else "unknown"
        print("\ntailwind context: {0}".format(context))
        print(f"design slop score: {total}/100 (threshold {args.threshold}) -> {'PASS' if passed else 'FAIL'}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
