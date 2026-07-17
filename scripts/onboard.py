#!/usr/bin/env python3
"""Interactive and non-interactive onboarding for unmachined always-on mode."""

from __future__ import absolute_import, print_function

import argparse
import sys
from pathlib import Path

# allow running as script
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_lib import (  # noqa: E402
    DEFAULT_SURFACES,
    DEFAULT_THRESHOLD,
    format_status,
    resolve_config,
    save_config,
)


def prompt_yes_no(question, default_yes=True):
    hint = "Y/n" if default_yes else "y/N"
    try:
        raw = input("{0} [{1}]: ".format(question, hint)).strip().lower()
    except EOFError:
        return default_yes
    if not raw:
        return default_yes
    return raw in ("y", "yes", "on", "1", "true")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Configure unmachined always-on anti-slop for this CLI"
    )
    parser.add_argument(
        "--always-on",
        action="store_true",
        help="Enable always-on and save (non-interactive)",
    )
    parser.add_argument(
        "--always-off",
        action="store_true",
        help="Disable always-on and save (non-interactive)",
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="With --always-on: only text surface (no UI pipeline)",
    )
    parser.add_argument(
        "--surfaces",
        help="Comma-separated surfaces to enforce: text,ui (with --always-on)",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=DEFAULT_THRESHOLD,
        help="Scan fail threshold (default 40)",
    )
    parser.add_argument(
        "--project",
        action="store_true",
        help="Write .unmachined.json in the current project instead of user config",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print resolved config and exit",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="With --show: print JSON",
    )
    args = parser.parse_args(argv)

    if args.show:
        cfg = resolve_config()
        if args.json:
            import json

            print(json.dumps(cfg, indent=2, sort_keys=True))
        else:
            print(format_status(cfg))
        return 0

    if args.always_on and args.always_off:
        print("choose only one of --always-on / --always-off", file=sys.stderr)
        return 2
    if args.text_only and args.surfaces:
        print("choose only one of --text-only / --surfaces", file=sys.stderr)
        return 2
    if (args.text_only or args.surfaces) and not args.always_on:
        print("--text-only and --surfaces require --always-on", file=sys.stderr)
        return 2

    scope = "project" if args.project else "user"
    if args.surfaces:
        surfaces = [item.strip() for item in args.surfaces.split(",") if item.strip()]
        invalid = [item for item in surfaces if item not in DEFAULT_SURFACES]
        if invalid or not surfaces:
            print("--surfaces accepts text, ui, or text,ui", file=sys.stderr)
            return 2
        surfaces = list(dict.fromkeys(surfaces))
    else:
        surfaces = ["text"] if args.text_only else list(DEFAULT_SURFACES)

    if args.always_on or args.always_off:
        always_on = bool(args.always_on)
        path, payload = save_config(
            always_on=always_on,
            surfaces=surfaces if always_on else list(DEFAULT_SURFACES),
            threshold=args.threshold,
            scope=scope,
        )
        print("saved {0}".format(path))
        print(format_status(resolve_config()))
        return 0

    # Interactive wizard
    print("")
    print("unmachined onboarding")
    print("---------------------")
    print(
        "Always-on means every user-facing text (and optional UI copy) written"
    )
    print(
        "in this CLI is drafted and scanned under anti-slop rules, not only when"
    )
    print("you run /unmachined.")
    print("")

    current = resolve_config()
    if current.get("onboarded_at"):
        print("Current: always_on={0} ({1})".format(
            current["always_on"], current["source"]
        ))
        print("")

    always_on = prompt_yes_no(
        "Turn always-on ON for this CLI?",
        default_yes=True,
    )
    text_only = False
    if always_on:
        text_only = not prompt_yes_no(
            "Also enforce UI/design anti-slop when building interfaces?",
            default_yes=True,
        )
    surfaces = ["text"] if text_only else list(DEFAULT_SURFACES)

    path, payload = save_config(
        always_on=always_on,
        surfaces=surfaces,
        threshold=args.threshold,
        scope=scope,
    )
    print("")
    print("Saved to {0}".format(path))
    print(format_status(resolve_config()))
    print("")
    if always_on:
        print("Agents with this skill installed will enforce anti-slop on")
        print("user-facing text until you run: python3 scripts/onboard.py --always-off")
    else:
        print("Opt-in mode: invoke /unmachined when you want a scan or rewrite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
