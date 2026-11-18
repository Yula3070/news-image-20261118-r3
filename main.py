"""Entrypoint for the news-image-20261118 round 3 entry.

The front page image (entry.png) is already rendered by draw_frontpage.py.
This script has a single, fully deterministic job: place an exact copy of
that image into the grader's output directory so the result can be
collected.

Standard library only. No network requests, no randomness, no writes
anywhere except the output directory. Running it twice always produces
the same bytes.

The output directory comes from the MAKEFUN_OUTPUT_DIR environment
variable and falls back to /output when that variable is not set.
"""

import os
import shutil
import sys
from pathlib import Path

ENTRY_FILENAME = "entry.png"
FALLBACK_DIR = "/output"


def run() -> int:
    here = Path(__file__).resolve().parent
    origin = here / ENTRY_FILENAME
    if not origin.is_file():
        print(f"missing entry image: {origin}", file=sys.stderr)
        return 1

    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)

    target = target_dir / ENTRY_FILENAME
    shutil.copyfile(origin, target)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
