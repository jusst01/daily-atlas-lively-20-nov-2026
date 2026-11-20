from PIL import ImageFont, ImageDraw, Image
F = "/usr/share/fonts/truetype/dejavu/"
img = Image.new("RGB", (10, 10)); d = ImageDraw.Draw(img)
def font(n, s): return ImageFont.truetype(F + n, s)
def wrap(text, f, mw):
    words = text.split(); lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= mw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

print("== title ==")
for s in range(54, 38, -2):
    f = font("DejaVuSerif-Bold.ttf", s)
    w = d.textlength("THE DAILY ATLAS", font=f)
    print(s, round(w,1), "fits" if w <= 900 else "")
    if w <= 900: break

print("== featured ==")
feat = [
 ("Kyiv's bridges hit in one night", "Russia's overnight barrage damages three Dnipro crossings - Podilskyi, Darnytskyi and Southern. Three water workers killed, about 15 injured."),
 ("Cyclone Akvan comes ashore", "Akvan crosses the Odisha coast weakened to 70-80 km/h, below forecast. 300,000+ evacuated; no major damage reported."),
 ("COP31's last day, no deal", "The revised draft drops every mention of fossil fuels. 92,000 attendees - the largest COP ever; talks may run into the weekend."),
]
hb = font("DejaVuSerif-Bold.ttf", 17)
sm = font("DejaVuSerif.ttf", 9.5)
for h, s in feat:
    hl = wrap(h, hb, 297); sl = wrap(s, sm, 297)
    print(f"head {len(hl)}L ({len(hl)*18}px) | summ {len(sl)}L ({len(sl)*11.5}px) :: {h}")
    if len(hl) > 2: print("  !! HEAD TOO LONG", hl)
    if len(sl) > 2: print("  !! SUMM TOO LONG", sl)
    if len(hl) == 2 and len(sl) > 1: print("  !! 2L head + multi summ", hl, sl)

print("== stat captions (cell 162.67, wrap 152.67) ==")
f8 = font("DejaVuSans.ttf", 8)
for c in ["Kyiv bridges damaged in one night", "evacuated ahead of Cyclone Akvan",
          "the Nikkei 225 on Friday", "GTA VI estimated first-day sales",
          "fossil-fuel mentions in COP31's draft", "Britain's drone package for Ukraine"]:
    ls = wrap(c, f8, 152.67)
    print(len(ls), [round(d.textlength(l, font=f8),1) for l in ls], c)
    if len(ls) > 1: print("   ", ls)

print("== date check (Sans 9, 896 wide, 2 lines) ==")
f9 = font("DejaVuSans.ttf", 9)
dc = "Left out on purpose - they broke on other days: the Houthi strike on Riyadh's PIF Tower (Thu 19 Nov) - the Tbilisi gas blast, six dead (Thu 19 Nov) - the ICJ genocide ruling on Myanmar (Thu 19 Nov) - the Shenzhen three-way summit (Thu 19 Nov) - GTA VI's launch day itself (Thu 19 Nov) - Nvidia's record quarter (Tue 17 Nov) - the Siberia An-12 crash, 19 killed (Tue 17 Nov)."
ls = wrap(dc, f9, 896)
print(len(ls), "lines"); [print("  ", round(d.textlength(l, font=f9),1), l) for l in ls]

print("== footer line 2 (Sans 8.5, centred on 512 -> max ~976) ==")
f85 = font("DejaVuSans.ttf", 8.5)
ft = "Every story happened or was first reported on Friday 20 November 2026 - Disputed claims are attributed - Sources: Reuters - AP - BBC - IMD - CNBC - Sensor Tower - UN News"
print(round(d.textlength(ft, font=f85),1))
print("== footer 1 (Serif 9.5) ==")
print(round(d.textlength("CLAIM = one side's account, not independently confirmed.", font=font("DejaVuSerif.ttf", 9.5)),1))
print("== region labels (Sans-Bold 10) ==")
f10 = font("DejaVuSans-Bold.ttf", 10)
for l in ["ASIA 4","MIDDLE EAST 4","EUROPE 10","AFRICA 2","AMERICAS 10","OCEANIA 2","GLOBAL 1"]:
    print(l, round(d.textlength(l, font=f10),1))
print("== kickers Serif? no: featured kick Sans-Bold 10.5 ==")
fk = font("DejaVuSans-Bold.ttf", 10.5)
for l in ["KYIV · WAR","GOPALPUR · STORM","ANTALYA · CLIMATE"]:
    print(l, round(d.textlength(l, font=fk),1))
print("== grid kickers Sans-Bold 8 ==")
gk = font("DejaVuSans-Bold.ttf", 8)
for l in ["ASIA · MARKETS","WORLDWIDE · GAMES","SENEGAL · MIGRATION","SCIENCE · SPACE"]:
    print(l, round(d.textlength(l, font=gk),1))
print("== source chips Sans-Bold 7 (grid) ==")
c7 = font("DejaVuSans-Bold.ttf", 7)
for l in ["CONFIRMED · EXCHANGES","ESTIMATES · SENSOR TOWER","CONFIRMED · REUTERS"]:
    print(l, round(d.textlength(l, font=c7),1))
