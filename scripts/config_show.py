#!/usr/bin/env python3
"""Print resolved unmachined config (alias for onboard.py --show)."""

from __future__ import absolute_import

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from onboard import main  # noqa: E402

if __name__ == "__main__":
    args = ["--show"]
    if "--json" in sys.argv:
        args.append("--json")
    sys.exit(main(args))
