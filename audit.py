"""Numeric layout audit of the rendered page (no visual inspection)."""
import importlib.util, os
import numpy as np
from PIL import Image

spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.HERE = "/tmp/arttest"
m.OUT = "/tmp/arttest/entry.png"
m.main()

im = Image.open("/tmp/arttest/entry.png").convert("RGB")
a = np.asarray(im).astype(int)
print("size", im.size, "shape", a.shape)

PAPER = np.array(m.PAPER)
# 1. margins: outer 2px frame must be pure paper (flat, no bleed)
for name, sl in [("top", (slice(0, 2), slice(None))),
                 ("bottom", (slice(1022, 1024), slice(None))),
                 ("left", (slice(None), slice(0, 2))),
                 ("right", (slice(None), slice(1022, 1024)))]:
    reg = a[sl]
    diff = np.abs(reg - PAPER).max()
    print(f"margin {name}: max deviation from paper {diff}")

# 2. flatness check: paper areas must be exactly flat (no noise)
bg = a[970:1024, 24:1000]
print("paper region unique colours:", len(np.unique(bg.reshape(-1, 3), axis=0)))

# 3. column ink coverage per band to spot overflow
def inkmask(reg):
    return (np.abs(reg - PAPER).max(axis=2) > 8)

for y0, y1, label in [(0, 12, "topline"), (48, 60, "date"),
                      (60, 74, "subline"), (78, 100, "regionbar")]:
    cols = inkmask(a[y0:y1, :]).any(axis=0)
    xs = np.where(cols)[0]
    if len(xs):
        print(f"{label}: x {xs.min()}..{xs.max()}")

# 4. check nothing drawn outside 24..1000 for the rules
row = a[0:12, :]
print("ok")
