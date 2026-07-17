#!/usr/bin/env python3
"""Validate the portable Agent Skills package without third-party modules."""

import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message):
    print("skill validation failed: {0}".format(message), file=sys.stderr)
    return 1


def scalar(frontmatter, key):
    match = re.search(r"(?m)^{0}:\s*(.+)$".format(re.escape(key)), frontmatter)
    return match.group(1).strip().strip('"\'') if match else None


def folded_description(frontmatter):
    match = re.search(
        r"(?ms)^description:\s*>-?\s*\n(?P<body>(?:^[ \t]+.*\n?)+)",
        frontmatter,
    )
    if not match:
        return scalar(frontmatter, "description")
    return " ".join(line.strip() for line in match.group("body").splitlines())


def main():
    root = Path(__file__).resolve().parent.parent
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return fail("SKILL.md is missing")

    text = skill_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        return fail("SKILL.md needs YAML frontmatter bounded by ---")

    frontmatter = parts[1]
    name = scalar(frontmatter, "name")
    description = folded_description(frontmatter)
    if not name or not NAME_RE.fullmatch(name):
        return fail("name must contain lowercase letters, numbers, and single hyphens")
    if name != root.name:
        return fail("name must match the skill directory")
    if len(name) > 64:
        return fail("name exceeds 64 characters")
    if not description or len(description) > 1024:
        return fail("description must contain 1 to 1024 characters")
    if len(text.splitlines()) >= 500:
        return fail("SKILL.md must stay below 500 lines")

    for directory in ("references", "scripts", "assets"):
        if not (root / directory).is_dir():
            return fail("{0}/ is missing".format(directory))

    # cross-reference freshness: every reference ships indexed, and every
    # indexed reference exists. Stale paths break progressive disclosure.
    mentioned = set(re.findall(r"references/[a-z0-9-]+\.md", text))
    for path in sorted((root / "references").glob("*.md")):
        relative = "references/{0}".format(path.name)
        if relative not in mentioned:
            return fail("{0} is not indexed in SKILL.md".format(relative))
    for relative in sorted(mentioned):
        if not (root / relative).is_file():
            return fail("SKILL.md references a missing file: {0}".format(relative))

    print("skill validation passed: {0}".format(name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
