#!/usr/bin/env python3
"""unmachined learn: build and manage the personal voice profile.

Usage:
    python3 learn.py                     # ingest all default sources, save
    python3 learn.py status              # print the saved profile summary
    python3 learn.py off | on            # disable/enable personal mode
    python3 learn.py --path 'notes/*.md' # extra sample globs
    python3 learn.py --no-transcripts --days 30 --json

Deterministic and local: computed statistics plus verbatim exemplars, no LLM
calls. Consumption contract: references/personal-voice.md.
"""
from __future__ import absolute_import, print_function

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config_lib  # noqa: E402
import voice_profile  # noqa: E402

# Default sample sources are machine-local, never hardcoded: an env var wins,
# then the unmachined config (project .unmachined.json, then user config).
SOURCE_DEFAULTS = (
    ("x_corpus", "UNMACHINED_VOICE_CORPUS", "voice_corpus"),
    ("voice_dir", "UNMACHINED_VOICE_DIR", "voice_dir"),
)


def resolve_default_sources(args):
    """Fill unset --x-corpus/--voice-dir from env vars or the local config.

    Returns hint lines for sources that stay unconfigured (skipped)."""
    config = None
    hints = []
    for attr, env_var, config_key in SOURCE_DEFAULTS:
        if getattr(args, attr) is not None:
            continue
        value = os.environ.get(env_var)
        if not value:
            if config is None:
                config = config_lib.resolve_config()
            value = config.get(config_key)
        if value:
            setattr(args, attr, value)
        else:
            hints.append(
                "{0}: not configured; set {1} in {2} (or {3}) to include it".format(
                    attr.replace("_", "-"), config_key,
                    config_lib.user_config_path(), env_var))
    return hints


def build(args, hints=()):
    for hint in hints:
        print(hint, file=sys.stderr)
    samples = []
    if args.x_corpus:
        samples += voice_profile.ingest_x_corpus(args.x_corpus)
    if args.voice_dir:
        samples += voice_profile.ingest_voice_dir(args.voice_dir)
    if args.transcripts:
        samples += voice_profile.ingest_transcripts(days=args.days)
    samples += voice_profile.ingest_paths(args.path)
    if not samples:
        print("no samples found; check source paths", file=sys.stderr)
        return 2

    reference = []
    if args.x_corpus:
        reference = voice_profile.load_reference_texts(Path(args.x_corpus).parent)

    try:
        profile = voice_profile.compute_profile(samples, reference_texts=reference)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    path = voice_profile.save_profile(profile, args.output)
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        print("saved {0}".format(path))
        print(voice_profile.format_summary(profile))
    return 0


def set_enabled(args, enabled):
    profile = voice_profile.load_profile(args.output)
    if profile is None:
        print("no profile found; run learn first", file=sys.stderr)
        return 2
    profile["enabled"] = enabled
    path = voice_profile.save_profile(profile, args.output)
    print("personal voice {0} ({1})".format("on" if enabled else "off", path))
    return 0


def status(args):
    profile = voice_profile.load_profile(args.output)
    if profile is None:
        print("no voice profile at {0}; run learn first".format(
            args.output or voice_profile.profile_path()))
        return 1
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        print(voice_profile.format_summary(profile))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Learn the user's personal voice profile (deterministic, local)"
    )
    parser.add_argument("verb", nargs="?", default="learn",
                        choices=["learn", "status", "on", "off"],
                        help="learn (default) | status | on | off")
    parser.add_argument("--x-corpus", default=None,
                        help="own-voice X posts JSON (list of strings); default"
                             " from $UNMACHINED_VOICE_CORPUS or config key"
                             " voice_corpus; '' to skip")
    parser.add_argument("--voice-dir", default=None,
                        help="voice pack dir with few-shot/*.md; default from"
                             " $UNMACHINED_VOICE_DIR or config key voice_dir;"
                             " '' to skip")
    parser.add_argument("--no-transcripts", dest="transcripts", action="store_false",
                        help="skip Claude Code transcript ingestion")
    parser.add_argument("--days", type=int, default=90,
                        help="transcript window in days (default 90)")
    parser.add_argument("--path", action="append", default=[],
                        help="extra sample glob (repeatable)")
    parser.add_argument("--output", default=None,
                        help="profile path (default: next to unmachined config)")
    parser.add_argument("--json", action="store_true", help="print the full profile JSON")
    args = parser.parse_args(argv)

    if args.verb == "status":
        return status(args)
    if args.verb == "on":
        return set_enabled(args, True)
    if args.verb == "off":
        return set_enabled(args, False)

    hints = resolve_default_sources(args)
    for attr in ("x_corpus", "voice_dir"):
        value = getattr(args, attr)
        if value in ("", "none"):
            setattr(args, attr, None)
        elif value:
            setattr(args, attr, os.path.expanduser(value))
    return build(args, hints)


if __name__ == "__main__":
    sys.exit(main())
