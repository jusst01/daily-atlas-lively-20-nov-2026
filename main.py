#!/usr/bin/env python3
"""Deploy the bundled entry.png into $MAKEFUN_OUTPUT_DIR (default /output).

Standard library only. Resolves the bundled image relative to this file,
stages a copy in the destination directory, makes it world-readable, then
atomically renames it into place and verifies the byte size.
"""

import os
import shutil
import sys
import tempfile

NAME = "entry.png"


def fail(msg, code=1):
    print("main.py: ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, NAME)

    if not os.path.isfile(src):
        fail("bundled image not found: %s" % src)

    src_size = os.path.getsize(src)
    if src_size == 0:
        fail("bundled image is empty: %s" % src)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as e:
        fail("cannot create output directory %s: %s" % (out_dir, e))

    dest = os.path.join(out_dir, NAME)

    fd, staged = tempfile.mkstemp(prefix="." + NAME + ".", dir=out_dir)
    os.close(fd)
    try:
        shutil.copyfile(src, staged)
        staged_size = os.path.getsize(staged)
        if staged_size != src_size:
            fail("staged copy size %d != source size %d"
                 % (staged_size, src_size))
        # mkstemp creates 0600; the grader reads as another user.
        os.chmod(staged, 0o644)
        os.replace(staged, dest)
    except Exception as e:
        try:
            os.unlink(staged)
        except OSError:
            pass
        fail("copy to %s failed: %s: %s" % (dest, type(e).__name__, e))

    final_size = os.path.getsize(dest)
    if final_size != src_size:
        fail("deployed size %d != source size %d" % (final_size, src_size))

    print("main.py: deployed %s (%d bytes) to %s" % (NAME, final_size, dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
