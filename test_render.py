"""Layout smoke test: renders draw.py with placeholder art in a scratch dir."""
import os, sys, importlib.util
from PIL import Image, ImageDraw

ART = "/tmp/arttest/assets"
os.makedirs(ART, exist_ok=True)
cols = {"bridges": (40, 60, 90), "cyclone": (90, 110, 130), "cop31": (120, 90, 70)}
for k, c in cols.items():
    p = os.path.join(ART, k + ".jpg")
    if not os.path.exists(p):
        im = Image.new("RGB", (952, 700), c)
        d = ImageDraw.Draw(im)
        for i in range(0, 952, 60):
            d.line((i, 0, i - 300, 700), fill=(200, 200, 200), width=3)
        im.save(p, quality=80)

spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.HERE = "/tmp/arttest"
m.OUT = "/tmp/arttest/entry.png"
m.main()
