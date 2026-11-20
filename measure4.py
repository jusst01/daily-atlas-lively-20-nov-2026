from PIL import ImageFont, ImageDraw, Image
F = "/usr/share/fonts/truetype/dejavu/"
img = Image.new("RGB", (10, 10)); d = ImageDraw.Draw(img)
def font(n, s): return ImageFont.truetype(F + n, s)
f12 = font("DejaVuSans-Bold.ttf", 12)
hw = d.textlength("ALSO ON FRIDAY 20 NOVEMBER", font=f12)
print("briefs heading 340 ->", 340 + hw)
print("map heading 24 ->", 24 + d.textlength("WHERE IT HAPPENED", font=f12))
f = font("DejaVuSans.ttf", 8.5)
names = ["Americas","Europe","Mideast","Africa","Asia","Oceania"]
total = sum(7+4+d.textlength(n, font=f) for n in names) + 14*(len(names)-1)
print("legend width", round(total,1), "spans", round(512-total/2,1), "->", round(512+total/2,1))
