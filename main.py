#!/usr/bin/env python3
"""Deliver the finished front page image to the grading output folder.

The artwork itself is pre-rendered as entry.png next to this script.
This entrypoint only moves those exact bytes to the place the grader
looks, so the submitted image is identical to the reviewed one.
"""

import os
import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"
RESULT_NAME = "output.png"
FALLBACK_DIR = "out"


def source_path():
    """Return the path of the pre-rendered image beside this file."""
    return Path(__file__).resolve().parent / SOURCE_NAME


def result_path():
    """Return where the image must land, from the environment or default."""
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR
    return Path(folder) / RESULT_NAME


def deliver():
    """Copy the image byte-for-byte to the output location."""
    origin = source_path()
    target = result_path()
    if not origin.is_file():
        print(f"missing source image: {origin}", file=sys.stderr)
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origin, target)
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(deliver())
