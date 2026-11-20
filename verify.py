"""Verify the built entry.png against the spec's numeric requirements."""
import hashlib
import os
import sys

from PIL import Image

P = sys.argv[1] if len(sys.argv) > 1 else "/home/hermes/lively-news20-run/repo/entry.png"
raw = open(P, "rb").read()
print("path      ", P)
print("magic     ", raw[:8].hex(" "), "PNG" if raw[:4] == b"\x89PNG" else "NOT PNG")
print("bytes     ", len(raw), "(limit 1048576)", "OK" if len(raw) <= 1048576 else "TOO BIG")
print("sha256    ", hashlib.sha256(raw).hexdigest())
im = Image.open(P)
print("format    ", im.format, "mode", im.mode, "size", im.size,
      "OK" if im.size == (1024, 1024) and im.format == "PNG" else "BAD")
print("KiB       ", round(len(raw) / 1024.0, 1))
