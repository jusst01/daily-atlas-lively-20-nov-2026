import importlib.util
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
img = Image.new("RGB", (1024, 1024), m.PAPER); d = ImageDraw.Draw(img)
f = m.F(m.SERIF_B, 54)
print("title bbox at (512,13) anchor ma:", d.textbbox((512, 13), "THE DAILY ATLAS", font=f, anchor="ma"))
print("ascent/descent:", f.getmetrics())
print("r1 =", 13 + 54 + 6)
print("date bbox:", d.textbbox((512, 82), "Friday 20 November 2026", font=m.F(m.SERIF_B, 21), anchor="ma"))
