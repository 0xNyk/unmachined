#!/usr/bin/env python3
"""Resolve unmachined always-on config (stdlib only, Python 3.8+)."""

from __future__ import absolute_import, print_function

import json
import os
from datetime import datetime, timezone
from pathlib import Path


CONFIG_VERSION = 1
DEFAULT_THRESHOLD = 40
DEFAULT_SURFACES = ["text", "ui"]
VOICE_SOURCE_KEYS = ("voice_corpus", "voice_dir")


def user_config_path():
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "unmachined" / "config.json"
    return Path.home() / ".config" / "unmachined" / "config.json"


def project_config_path(cwd=None, discover=True):
    root = Path(cwd or os.getcwd()).resolve()
    if not discover:
        return root / ".unmachined.json"
    # walk up a few levels for monorepos
    for _ in range(6):
        candidate = root / ".unmachined.json"
        if candidate.is_file():
            return candidate
        if root.parent == root:
            break
        root = root.parent
    return Path(cwd or os.getcwd()).resolve() / ".unmachined.json"


def _read_json(path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError, TypeError):
        return None


def _bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("1", "true", "yes", "on"):
            return True
        if normalized in ("0", "false", "no", "off"):
            return False
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    return default


def _path_value(value):
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _normalize(data, source):
    if not isinstance(data, dict):
        return None
    surfaces = data.get("surfaces", list(DEFAULT_SURFACES))
    if isinstance(surfaces, str):
        surfaces = [s.strip() for s in surfaces.split(",") if s.strip()]
    if not isinstance(surfaces, list):
        surfaces = list(DEFAULT_SURFACES)
    surfaces = [s for s in surfaces if s in ("text", "ui")]
    if not surfaces:
        surfaces = list(DEFAULT_SURFACES)
    try:
        threshold = int(data.get("threshold", DEFAULT_THRESHOLD))
    except (TypeError, ValueError):
        threshold = DEFAULT_THRESHOLD
    try:
        version = int(data.get("version") or CONFIG_VERSION)
    except (TypeError, ValueError):
        version = CONFIG_VERSION
    return {
        "version": version,
        "always_on": _bool(data.get("always_on")),
        "surfaces": surfaces,
        "threshold": max(1, min(100, threshold)),
        "scan_before_ship": _bool(data.get("scan_before_ship", True), default=True),
        "onboarded_at": data.get("onboarded_at"),
        "notes": data.get("notes") or "",
        "voice_corpus": _path_value(data.get("voice_corpus")),
        "voice_dir": _path_value(data.get("voice_dir")),
        "source": source,
        "path": None,
    }


def resolve_config(cwd=None):
    """Return effective config. always_on defaults False until onboarded."""
    env = os.environ.get("UNMACHINED_ALWAYS_ON")
    project = project_config_path(cwd)
    user = user_config_path()

    base = {
        "version": CONFIG_VERSION,
        "always_on": False,
        "surfaces": list(DEFAULT_SURFACES),
        "threshold": DEFAULT_THRESHOLD,
        "scan_before_ship": True,
        "onboarded_at": None,
        "notes": "",
        "voice_corpus": None,
        "voice_dir": None,
        "source": "default",
        "path": None,
    }

    user_data = None
    if user.is_file():
        user_data = _normalize(_read_json(user), "user")
        if user_data:
            user_data["path"] = str(user)
            base = user_data

    if project.is_file():
        data = _normalize(_read_json(project), "project")
        if data:
            data["path"] = str(project)
            base = data
            # voice sources resolve per key: project first, then user
            if user_data:
                for key in VOICE_SOURCE_KEYS:
                    if base[key] is None:
                        base[key] = user_data[key]

    if env is not None:
        val = env.strip().lower()
        if val in ("1", "true", "yes", "on"):
            base["always_on"] = True
            base["source"] = base["source"] + "+env"
        elif val in ("0", "false", "no", "off"):
            base["always_on"] = False
            base["source"] = base["source"] + "+env"

    base["needs_onboarding"] = not bool(base.get("onboarded_at")) and env is None
    return base


def save_config(
    always_on,
    surfaces=None,
    threshold=DEFAULT_THRESHOLD,
    scan_before_ship=True,
    scope="user",
    cwd=None,
    notes="",
):
    if surfaces is None:
        surfaces = list(DEFAULT_SURFACES)
    surfaces = [surface for surface in surfaces if surface in ("text", "ui")]
    if not surfaces:
        raise ValueError("surfaces must include text, ui, or both")
    threshold = max(1, min(100, int(threshold)))
    path = user_config_path() if scope == "user" else project_config_path(cwd, discover=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": CONFIG_VERSION,
        "always_on": bool(always_on),
        "surfaces": list(surfaces),
        "threshold": threshold,
        "scan_before_ship": bool(scan_before_ship),
        "onboarded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": notes or "",
    }
    # optional voice-source keys (used by learn.py) survive re-onboarding
    existing = _read_json(path) if path.is_file() else None
    if isinstance(existing, dict):
        for key in VOICE_SOURCE_KEYS:
            value = _path_value(existing.get(key))
            if value:
                payload[key] = value
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return path, payload


def format_status(cfg):
    lines = [
        "unmachined config",
        "  always_on:        {0}".format(cfg["always_on"]),
        "  surfaces:         {0}".format(",".join(cfg["surfaces"])),
        "  threshold:        {0}".format(cfg["threshold"]),
        "  scan_before_ship: {0}".format(cfg["scan_before_ship"]),
        "  source:           {0}".format(cfg["source"]),
        "  path:             {0}".format(cfg["path"] or "(none)"),
        "  onboarded_at:     {0}".format(cfg["onboarded_at"] or "(not onboarded)"),
        "  needs_onboarding: {0}".format(cfg.get("needs_onboarding", False)),
    ]
    if cfg["always_on"]:
        lines.append(
            "  policy:           enforce anti-slop on all user-facing text in this CLI"
        )
    else:
        lines.append("  policy:           opt-in only (/unmachined …)")
    return "\n".join(lines)
