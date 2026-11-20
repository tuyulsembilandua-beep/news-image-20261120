#!/usr/bin/env python3
"""news-image-20261120 entry: copy the built front-page image to /output/entry.png.

The image (entry.png beside this file) is the finished 1024x1024 front page
for Friday 20 November 2026, composed at build time. This program only copies
its bytes, so both grader runs produce identical output. Standard library only.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # Fail loudly instead of shipping a truncated copy.
    if os.path.getsize(dst) != os.path.getsize(src):
        raise SystemExit("entry.png copy size mismatch")


if __name__ == "__main__":
    main()
