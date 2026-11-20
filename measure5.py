import importlib.util
from PIL import ImageFont, ImageDraw, Image
spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
img = Image.new("RGB", (10, 10)); d = ImageDraw.Draw(img)
kb = m.F(m.SANS_B, 8); c7 = m.F(m.SANS_B, 7)
print("num  kick_w  chip_w  gap(kicker end x+24 .. chip start x+230-chipw)")
for st in m.GRID:
    kw = d.textlength(st["kick"], font=kb)
    cw = d.textlength(st["chip"], font=c7)
    kend = 24 + kw
    cstart = 230 - cw
    print(f'{st["num"]:3d} {kw:7.1f} {cw:7.1f}  {cstart-kend:7.1f}  {"OVERLAP" if cstart < kend+4 else ""}')
