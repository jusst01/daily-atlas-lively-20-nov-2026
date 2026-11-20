import sys
from PIL import ImageFont, ImageDraw, Image

F = "/usr/share/fonts/truetype/dejavu/"
def font(n, s): return ImageFont.truetype(F + n, s)

img = Image.new("RGB", (10, 10)); d = ImageDraw.Draw(img)

def wrap(text, f, mw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= mw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

grid = [
 ("ASIA · MARKETS", "Asia's AI rout deepens", "Nikkei −4.9% and KOSPI −5.5%; Hang Seng nears bear ground. SoftBank plunges 16%."),
 ("NEW YORK · TECH", "Anthropic joins the big indexes", "A day after its record Nasdaq debut, ANT is added to the MSCI and FTSE indexes."),
 ("WORLDWIDE · GAMES", "GTA VI's $2.36bn first day", "Sensor Tower estimates 24.58M copies sold on launch day - a record."),
 ("RIYADH · ENERGY", "Oil edges up on supply fears", "Brent +0.3% to $92.22; Saudi defences down four more Houthi missiles."),
 ("EUROPE · DIPLOMACY", "Europe reaches for a seat", "Leaders say Europe is ready to join talks with Russia on ending the war."),
 ("LONDON · DEFENCE", "Britain's £260m drone pledge", "More than 1,000 drones for Ukraine in a new £260M package."),
 ("SCIENCE · SPACE", "Two hidden companions found", "Rubin Observatory preview data reveals two ultra-faint Milky Way satellites."),
 ("LONDON · EUROPE", "UK and EU agree youth mobility", "London and Brussels are set to agree a youth mobility scheme."),
 ("MALAWI · CRISIS", "Fuel crisis turns violent", "A deepening fuel shortage triggers violence and economic strain."),
 ("TOKYO · PROTEST", "13,000 march in Tokyo", "Protesters rally against the Takaichi government's policies."),
 ("SENEGAL · MIGRATION", "Boat capsize kills four", "A boat capsizes off Senegal as the migration surge continues."),
 ("WASHINGTON · PRESS", "Bag your phones", "The White House orders journalists to bag their phones after the China trip."),
]
hb = font("DejaVuSerif-Bold.ttf", 12)
sb = font("DejaVuSerif.ttf", 8.5)
for k, h, s in grid:
    hl = wrap(h, hb, 222); sl = wrap(s, sb, 222)
    print(f"{len(hl)}L head {d.textlength(h, font=hb):6.1f} | {len(sl)}L summ | {h[:30]}")
    if len(hl) > 1:
        # summary space = only 1 line
        print("   !! 2-line head, summary needs", len(sl), "lines")
    if len(sl) > (2 if len(hl) == 1 else 1):
        print("   !! SUMMARY TOO LONG")
