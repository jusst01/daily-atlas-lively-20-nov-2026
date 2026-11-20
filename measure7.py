import importlib.util, numpy as np
from PIL import Image
spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

# continent assignment sanity across the mask
from collections import Counter
c = Counter()
for r, cc, cont in m.land_cells():
    c[cont] += 1
print("land cells per continent:", dict(c), "total", sum(c.values()))

# how many land cells exist per row (should be contiguous-ish, no gaps)
gaps = 0
for r, spans in enumerate(m.MASK_ROWS):
    prev = None
    for a, b in spans:
        if prev is not None and a > prev + 1:
            gaps += 1
        prev = b
print("span gaps (fine, these are real sea lanes):", gaps)

# map box height and cell size
band_h = 217.0
print("map cell size", round(300/73.0, 2), "x", round(band_h/36.0, 2))
