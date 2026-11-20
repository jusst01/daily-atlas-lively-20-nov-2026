import importlib.util, io, contextlib
spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.HERE = "/tmp/arttest"; m.OUT = "/tmp/arttest/entry.png"

from PIL import Image, ImageDraw
img = Image.new("RGB", (1024, 1024), m.PAPER); d = ImageDraw.Draw(img)
sy = m.draw_masthead(d)
rb = sy + 15; st = rb + 27; fy = st + 50; gy = fy + 162 + 16
by = gy + 3*84 + 2*8 + 12
hy = by + 8; my = hy + 30
print(f"sy={sy} rb={rb}-{rb+21} st={st}-{st+42} fy={fy}-{fy+162} gy={gy}")
print(f"grid rows {gy}-{gy+2*92+84}  by={by} hy={hy} my={my}")
print(f"grid last card bottom = {gy+2*92+84}, rule at {by} -> gap {by-(gy+2*92+84)}")
print(f"featured bottom {fy+162}, grid rule {gy-8} -> gap {gy-8-(fy+162)}")
