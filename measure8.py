import importlib.util
from PIL import Image, ImageDraw
spec = importlib.util.spec_from_file_location(
    "drawmod", "/home/hermes/lively-news20-run/repo/draw.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
img = Image.new("RGB", (1024, 1024), m.PAPER); d = ImageDraw.Draw(img)
hb = m.F(m.SERIF_B, 17); sb = m.F(m.SERIF, 9.5)
for st in m.FEATURED:
    hl = m.wrap(st["head"], hb, 297)
    sl = m.wrap(st["summ"], sb, 297)
    h_end = 96 + len(hl) * 18
    s_end = h_end + len(sl) * 11.5
    print(f'{st["num"]}: head {len(hl)}L -> y{h_end} (limit 133) | summ {len(sl)}L -> y{s_end} (limit 160)'
          f'  {"OK" if h_end <= 133 and s_end <= 160 else "OVERFLOW"}')
    if s_end > 160:
        print("   lines:", sl)
