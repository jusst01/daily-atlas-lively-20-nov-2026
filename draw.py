#!/usr/bin/env python3
"""THE DAILY ATLAS - a 1024x1024 newspaper front page for 20 November 2026.

Renders the whole page from the story data below with Pillow and saves
entry.png next to this file.  Flat colour fills, crisp text, no texture.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SIDE = 1024
OUT = os.path.join(HERE, "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (243, 245, 247)
CARD = (252, 253, 255)
INK = (20, 24, 34)
GREY = (96, 100, 110)
ACCENT = (30, 52, 110)
TEAL = (44, 96, 88)
NAVY = (38, 58, 92)
BORDER = (188, 194, 204)
RED = (172, 62, 44)            # DATE CHECK red
SEA = (44, 92, 140)
SLATE = (52, 58, 66)
PALE = (232, 236, 244)
SRC = (90, 88, 80)

CONT = {
    "Americas": (168, 62, 44),
    "Europe": (58, 84, 128),
    "Mideast": (186, 122, 38),
    "Africa": (122, 106, 52),
    "Asia": (116, 80, 148),
    "Oceania": (44, 124, 134),
}
CONT_ORDER = ["Americas", "Europe", "Mideast", "Africa", "Asia", "Oceania"]


def mute(col, k=0.52):
    """Blend a colour toward the paper colour."""
    return tuple(int(round(c + (p - c) * k)) for c, p in zip(col, PAPER))


# ---------------------------------------------------------------- fonts
_FCACHE = {}


def F(name, size):
    key = (name, size)
    if key not in _FCACHE:
        _FCACHE[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _FCACHE[key]


SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF = "DejaVuSerif.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"
_ITAL = os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf")
SERIF_I = "DejaVuSerif-Italic.ttf" if os.path.exists(_ITAL) else SERIF

# ---------------------------------------------------------------- state
_img = Image.new("RGB", (10, 10), PAPER)
_measure = ImageDraw.Draw(_img)
CLIPS = []
DRAWN_NUMS = set()
DRAWN_ART = set()
SOURCE_CHIPS = 0
GRID_SEP = {}


def textlen(t, font):
    return _measure.textlength(t, font=font)


def wrap(text, font, max_width):
    """Greedy word wrap using draw.textlength."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if textlen(trial, font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, w, text, font, line_height, max_y, fill=INK, align="la"):
    """Draw wrapped lines from y while the next line still fits below max_y."""
    lines = wrap(text, font, w)
    for ln in lines:
        if y + line_height > max_y + 0.01:
            CLIPS.append((text[:40], round(y + line_height, 1), max_y))
            break
        if align == "ma":
            d.text((x + w / 2.0, y), ln, font=font, fill=fill, anchor="ma")
        else:
            d.text((x, y), ln, font=font, fill=fill, anchor="la")
        y += line_height
    return y


def chip(d, cx, cy, r, n, fill):
    """Filled circle with the story number in white Sans-Bold."""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)
    d.text((cx, cy), str(n), font=F(SANS_B, r * 1.12), fill=(255, 255, 255),
           anchor="mm")


def pill(d, x0, y0, x1, y1, rad, fill):
    d.rounded_rectangle((x0, y0, x1, y1), radius=rad, fill=fill)


def fit_font(name, text, size, max_w, floor=6.0):
    """Largest font size (<= size) at which text fits max_w."""
    s = size
    while s > floor and textlen(text, F(name, s)) > max_w:
        s -= 0.2
    return F(name, s)


# ---------------------------------------------------------------- data
FEATURED = [
    dict(num=1, kick="KYIV · WAR", tag="THREE BRIDGES IN ONE NIGHT",
         tagcol=RED, chip="CONFIRMED · REUTERS",
         head="Kyiv's bridges hit in one night",
         summ="Russia's overnight barrage damages three Dnipro crossings — "
              "Podilskyi, Darnytskyi and Southern. Three water workers killed, "
              "about 15 injured.",
         art="bridges"),
    dict(num=2, kick="GOPALPUR · STORM", tag="LANDFALL AT DAWN",
         tagcol=SEA, chip="CONFIRMED · IMD",
         head="Cyclone Akvan comes ashore",
         summ="Akvan crosses the Odisha coast weakened to 70-80 km/h, below "
              "forecast. 300,000+ evacuated; no major damage reported.",
         art="cyclone"),
    dict(num=3, kick="ANTALYA · CLIMATE", tag="FINAL DAY · NO DEAL",
         tagcol=ACCENT, chip="CONFIRMED · REUTERS",
         head="COP31's last day, no deal",
         summ="The revised draft drops every mention of fossil fuels. 92,000 "
              "attendees — the largest COP ever; talks may run into the "
              "weekend.",
         art="cop31"),
]

GRID = [
    dict(num=4, kick="ASIA · MARKETS", head="Asia's AI rout deepens",
         summ="Nikkei −4.9% and KOSPI −5.5%; Hang Seng nears bear "
              "ground. SoftBank plunges 16%.",
         kind="markets", chip="CONFIRMED · EXCHANGES"),
    dict(num=5, kick="NEW YORK · TECH", head="Anthropic joins the big indexes",
         summ="A day after its record Nasdaq debut, ANT is added to the MSCI "
              "and FTSE indexes.",
         kind="ipo", chip="CONFIRMED · WIRES"),
    dict(num=6, kick="WORLDWIDE · GAMES", head="GTA VI's $2.36bn first day",
         summ="Sensor Tower estimates 24.58M copies sold on launch day — "
              "a record.",
         kind="games", chip="ESTIMATES · SENSOR TOWER"),
    dict(num=7, kick="RIYADH · ENERGY", head="Oil edges up on supply fears",
         summ="Brent +0.3% to $92.22; Saudi defences down four more Houthi "
              "missiles.",
         kind="oil", chip="CONFIRMED · REUTERS"),
    dict(num=8, kick="EUROPE · DIPLOMACY", head="Europe reaches for a seat",
         summ="Leaders say Europe is ready to join talks with Russia on "
              "ending the war.",
         kind="diplomacy", chip="CONFIRMED · BBC"),
    dict(num=9, kick="LONDON · DEFENCE", head="Britain's £260m drone pledge",
         summ="More than 1,000 drones for Ukraine in a new £260M package.",
         kind="drones", chip="CONFIRMED · WIRES"),
    dict(num=10, kick="SCIENCE · SPACE", head="Two hidden companions found",
         summ="Rubin Observatory preview data reveals two ultra-faint Milky "
              "Way satellites.",
         kind="space", chip="CONFIRMED · UW"),
    dict(num=11, kick="LONDON · EUROPE", head="UK and EU agree youth mobility",
         summ="London and Brussels are set to agree a youth mobility scheme.",
         kind="youth", chip="CONFIRMED · BBC"),
    dict(num=12, kick="MALAWI · CRISIS", head="Fuel crisis turns violent",
         summ="A deepening fuel shortage triggers violence and economic "
              "strain.",
         kind="fuel", chip="CONFIRMED · WIRES"),
    dict(num=13, kick="TOKYO · PROTEST", head="13,000 march in Tokyo",
         summ="Protesters rally against the Takaichi government's policies.",
         kind="protest", chip="CONFIRMED · WIRES"),
    dict(num=14, kick="SENEGAL · MIGRATION", head="Boat capsize kills four",
         summ="A boat capsizes off Senegal as the migration surge continues.",
         kind="boat", chip="CONFIRMED · WIRES"),
    dict(num=15, kick="WASHINGTON · PRESS", head="Bag your phones",
         summ="The White House orders journalists to bag their phones after "
              "the China trip.",
         kind="phones", chip="CONFIRMED · WIRES"),
]

BRIEFS = [
    (16, "Brussels: Coordinated European youth action day — living costs, "
         "housing and education; more planned for the weekend"),
    (17, "Genoa: The airport suspends flights after unidentified drones are "
         "detected"),
    (18, "France: One dead and 15 injured in a fire at an 18-storey apartment "
         "building"),
    (19, "New Caledonia: A 5.6-magnitude earthquake strikes near the islands"),
    (20, "Washington: The US sanctions the Comancheros biker network and an "
         "'Ndrangheta web, its Toronto faction included"),
    (21, "Washington: Trump announces a posthumous pardon for baseball legend "
         "Pete Rose"),
    (22, "San Salvador: Bukele formally registers to seek a third presidential "
         "term"),
    (23, "Warsaw: Poland prepares a $50bn nuclear-power deal with US firms"),
    (24, "Menlo Park: Meta revises its 2030 climate targets amid its AI "
         "infrastructure expansion"),
    (25, "New Delhi: India-Japan 2+2 — Japanese forces will train at Indian "
         "ranges; missile and maritime tech agreed"),
    (26, "Amsterdam: 'The Year of the Ghost' wins Best Film at the IDFA "
         "documentary festival"),
    (27, "Cincinnati: Fiona the hippo dies at the zoo, days after swallowing a "
         "visitor's hat"),
    (28, "Washington: The White House taps Kirsten Davies as national cyber "
         "director after widespread outages"),
    (29, "Washington: The Senate nears a vote on a permitting bill to speed "
         "power-plant and transmission reviews"),
    (30, "South Pacific: Cyclone Xavier — RSMC Nadi issues bulletin 39; "
         "island warning levels unchanged"),
    (31, "Paris: Macron backs Philippe Diallo's bid for the FIFA presidency"),
    (32, "Formula 1: Verstappen backs F1's plan to press ahead with its Middle "
         "East races despite the war"),
    (33, "Washington: The US war with Iran has cost over $48bn so far, "
         "officials say"),
]

PINS = {
    1: (30.5, 50.4, 6, -6), 2: (84.9, 19.3, 6, 4), 3: (30.7, 36.9, -8, -6),
    4: (139.7, 35.7, 0, -9), 5: (-74.0, 40.7, -4, -9), 6: (-80.2, 25.8, 0, -6),
    7: (46.7, 24.6, 4, 0), 8: (13.4, 52.5, 8, -6), 9: (-0.1, 51.5, -8, -8),
    10: (-70.7, -30.2, 0, -6), 11: (4.35, 50.85, -12, 6),
    12: (33.8, -13.97, 6, 4), 13: (139.7, 35.7, 13, 7),
    14: (-17.4, 14.7, -6, 0), 15: (-77.0, 38.9, -12, -8),
    16: (4.35, 50.85, 10, 10), 17: (8.9, 44.4, 6, 6),
    18: (2.35, 48.85, -10, -10), 19: (165.5, -21.5, 0, -6),
    20: (-77.0, 38.9, 13, 8), 21: (-77.0, 38.9, -14, 6),
    22: (-89.2, 13.7, 0, 6), 23: (21.0, 52.2, 10, -4),
    24: (-122.2, 37.5, -6, -6), 25: (77.2, 28.6, -8, -6),
    26: (4.9, 52.4, -14, -12), 27: (-84.5, 39.1, 6, 8),
    28: (-77.0, 38.9, 0, -14), 29: (-77.0, 38.9, 14, -6),
    30: (178.4, -18.1, 0, -6), 31: (2.35, 48.85, 12, 8),
    32: (54.4, 24.5, 8, 6), 33: (-77.0, 38.9, -6, 12),
}

PIN_CONT = {
    1: "Europe", 2: "Asia", 3: "Mideast", 4: "Asia", 5: "Americas",
    6: "Americas", 7: "Mideast", 8: "Europe", 9: "Europe", 10: "Americas",
    11: "Europe", 12: "Africa", 13: "Asia", 14: "Africa", 15: "Americas",
    16: "Europe", 17: "Europe", 18: "Europe", 19: "Oceania", 20: "Americas",
    21: "Americas", 22: "Americas", 23: "Europe", 24: "Americas", 25: "Asia",
    26: "Europe", 27: "Americas", 28: "Americas", 29: "Americas",
    30: "Oceania", 31: "Europe", 32: "Mideast", 33: "Mideast",
}

# Coarse landmass mask: 36 rows x 73 columns of (first, last) column spans.
MASK_ROWS = [
    [(8, 11), (27, 30), (48, 50), (59, 61)],
    [(1, 6), (9, 23), (26, 31), (44, 70)],
    [(1, 7), (8, 25), (27, 31), (38, 70)],
    [(2, 8), (9, 26), (28, 30), (37, 70)],
    [(3, 8), (10, 26), (31, 31), (37, 70)],
    [(5, 8), (11, 25), (32, 33), (34, 70)],
    [(10, 24), (32, 32), (33, 69)],
    [(10, 23), (32, 45), (46, 66)],
    [(10, 23), (33, 44), (45, 66)],
    [(10, 23), (33, 43), (44, 63)],
    [(10, 22), (32, 38), (39, 47), (48, 64)],
    [(11, 21), (33, 53), (55, 62)],
    [(11, 17), (33, 48), (49, 53), (54, 60)],
    [(13, 16), (33, 45), (49, 52), (55, 60)],
    [(11, 11), (34, 45), (50, 51), (56, 58)],
    [(34, 44), (46, 47), (56, 58), (60, 61)],
    [(34, 45), (56, 62)],
    [(35, 45), (58, 63)],
    [(17, 22), (35, 45), (58, 64)],
    [(17, 23), (37, 44), (60, 66)],
    [(18, 23), (38, 44), (64, 68)],
    [(18, 24), (38, 44), (60, 67)],
    [(18, 24), (39, 44), (46, 46), (60, 68)],
    [(18, 24), (39, 44), (46, 46), (59, 68)],
    [(18, 23), (39, 44), (46, 46), (59, 67)],
    [(18, 23), (40, 44), (60, 66)],
    [(18, 22), (40, 43), (61, 65)],
    [(18, 22), (40, 43), (61, 65), (71, 71)],
    [(19, 21), (40, 42), (62, 64)],
    [(19, 21), (40, 42), (62, 63), (71, 72)],
    [(19, 20), (63, 63)],
    [(19, 20), (70, 71)],
    [(19, 19)],
    [(19, 19)],
    [(19, 19)],
    [(19, 19)],
]
MASK_COLS = 73
MASK_ROWS_N = 36


def cell_lonlat(row, col):
    lon = -168 + (col + 0.5) * (360.0 / MASK_COLS)
    lat = 78 - (row + 0.5) * (134.0 / MASK_ROWS_N)
    return lon, lat


def continent_of(lon, lat):
    if lon < -30:
        return "Americas"
    if lon >= 112 and lat < -11:
        return "Oceania"
    if lon >= 52:
        return "Asia"
    if lat >= 42:
        return "Europe"
    if lon >= 20 and lat >= 12:
        return "Mideast"
    if lat >= 35:
        return "Europe"
    return "Africa"


def land_cells():
    """Yield (row, col, continent) for every land cell in the mask."""
    for r, spans in enumerate(MASK_ROWS):
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                lon, lat = cell_lonlat(r, c)
                yield r, c, continent_of(lon, lat)



# ---------------------------------------------------------------- banners
def _label(d, x, y, text, font, fill, anchor="la"):
    d.text((x, y), text, font=font, fill=fill, anchor=anchor)


def banner(d, x, y, w, h, kind, small=False):
    """Flat procedural banner strip for a grid card."""
    s = h / 34.0 if small else 1.0
    k = min(s, 1.0)
    # For the 34px grid strips the label is shrunk to fit inside the card.
    lfit = fit_font(SANS_B, "X", 7.0 if small else 7.0, w - 14)

    def lab(txt, fill):
        d.text((x + 7, y + 4), txt, font=lfit, fill=fill, anchor="la")

    if kind == "markets":
        d.rectangle((x, y, x + w, y + h), fill=(24, 26, 34))
        pts = [(x + 10, y + h * 0.30), (x + w * 0.28, y + h * 0.22),
               (x + w * 0.42, y + h * 0.58), (x + w * 0.60, y + h * 0.44),
               (x + w * 0.74, y + h * 0.74), (x + w - 18, y + h * 0.66)]
        d.line(pts, fill=RED, width=max(1, int(round(2 * k))), joint="curve")
        ax, ay = pts[-1]
        d.polygon([(ax, ay + 3 * k), (ax - 7 * k, ay - 4 * k),
                   (ax + 1 * k, ay - 5 * k)], fill=RED)
        lab("ASIA ROUT", RED)

    elif kind == "ipo":
        d.rectangle((x, y, x + w, y + h), fill=PALE)
        base = y + h - 6
        bw = 13 * k
        for i in range(3):
            bx = x + 12 + i * (bw + 6 * k)
            bh = (10 + i * 7) * k
            d.rectangle((bx, base - bh, bx + bw, base), fill=ACCENT)
        tx = x + 12 + 2 * (bw + 6 * k) + bw * 0.5
        ty = base - (10 + 2 * 7) * k
        d.line((tx, ty, tx, ty - 9 * k), fill=INK, width=max(1, int(round(k))))
        d.polygon([(tx, ty - 9 * k), (tx + 7 * k, ty - 7 * k),
                   (tx, ty - 5 * k)], fill=ACCENT)
        lab("ANT · INDEXES", INK)

    elif kind == "games":
        bands = [(46, 26, 66), (74, 32, 70), (110, 40, 74), (156, 54, 74),
                 (200, 84, 66), (226, 150, 60)]
        bh = h / 6.0
        for i, col in enumerate(bands):
            d.rectangle((x, y + i * bh, x + w, y + (i + 1) * bh), fill=col)
        d.ellipse((x + w * 0.60, y + h * 0.52, x + w * 0.60 + 15 * k,
                   y + h * 0.52 + 15 * k), fill=(250, 244, 224))
        for px in (x + w * 0.22, x + w * 0.40):
            d.line((px, y + h - 1, px - 2 * k, y + h * 0.42),
                   fill=(12, 12, 16), width=max(1, int(round(2 * k))))
            for ang in (-1, 1):
                d.line((px - 2 * k, y + h * 0.42,
                        px - 2 * k + ang * 8 * k, y + h * 0.42 - 3 * k),
                       fill=(12, 12, 16), width=max(1, int(round(2 * k))))
        lab("$2.36BN DAY ONE", (255, 255, 255))

    elif kind == "oil":
        d.rectangle((x, y, x + w, y + h), fill=SEA)
        hy = y + h * 0.62
        d.polygon([(x + 10, hy), (x + w - 12, hy), (x + w - 20, y + h - 3),
                   (x + 18, y + h - 3)], fill=(22, 32, 48))
        dx = x + w * 0.56
        d.rectangle((dx, hy - 12 * k, dx + 10 * k, hy), fill=(22, 32, 48))
        d.line((dx + 5 * k, hy - 12 * k, dx + 5 * k, hy - 20 * k),
               fill=(240, 244, 250), width=max(1, int(round(k))))
        lab("BRENT $92.22", (255, 255, 255))

    elif kind == "diplomacy":
        d.rectangle((x, y, x + w, y + h), fill=PALE)
        ty = y + h * 0.66
        d.line((x + 14, ty, x + w - 14, ty), fill=INK,
               width=max(1, int(round(2 * k))))
        for i in range(3):
            cx = x + w * (0.30 + i * 0.20)
            d.rectangle((cx - 5 * k, ty - 5 * k, cx + 5 * k, ty),
                        fill=ACCENT)
        for fx in (x + w * 0.16, x + w * 0.84):
            d.line((fx, ty, fx, ty - 12 * k), fill=GREY,
                   width=max(1, int(round(k))))
            d.polygon([(fx, ty - 12 * k), (fx + 8 * k, ty - 9 * k),
                       (fx, ty - 6 * k)], fill=ACCENT)
        lab("EUROPE · TALKS", INK)

    elif kind == "drones":
        d.rectangle((x, y, x + w, y + h), fill=SLATE)
        for i in range(3):
            cx = x + w * (0.24 + i * 0.26)
            cy = y + h * 0.62
            r = 3.0 * k
            d.line((cx - 6 * k, cy - 4 * k, cx + 6 * k, cy + 4 * k),
                   fill=(214, 222, 232), width=max(1, int(round(k))))
            d.line((cx - 6 * k, cy + 4 * k, cx + 6 * k, cy - 4 * k),
                   fill=(214, 222, 232), width=max(1, int(round(k))))
            for ox, oy in ((-6, -4), (6, -4), (-6, 4), (6, 4)):
                d.ellipse((cx + ox * k - r, cy + oy * k - r,
                           cx + ox * k + r, cy + oy * k + r),
                          outline=(214, 222, 232),
                          width=max(1, int(round(k))))
        lab("1,000+ DRONES", (255, 255, 255))

    elif kind == "space":
        d.rectangle((x, y, x + w, y + h), fill=(16, 20, 38))
        rng = np.random.RandomState(7)
        for _ in range(26):
            sx = x + 6 + rng.rand() * (w - 12)
            sy = y + 5 + rng.rand() * (h - 10)
            rr = 0.8 if rng.rand() < 0.6 else 1.3
            d.ellipse((sx - rr, sy - rr, sx + rr, sy + rr),
                      fill=(226, 230, 242))
        for gx in (x + w * 0.30, x + w * 0.74):
            gy = y + h * 0.62
            d.ellipse((gx - 1.6 * k, gy - 1.6 * k, gx + 1.6 * k, gy + 1.6 * k),
                      fill=(240, 238, 220))
            for ang, rx in ((0.35, 9), (2.4, 6)):
                bb = (gx - rx * k, gy - rx * 0.42 * k,
                      gx + rx * k, gy + rx * 0.42 * k)
                d.arc(bb, int(ang * 57.3) + 10, int(ang * 57.3) + 180,
                      fill=(196, 202, 226), width=max(1, int(round(k))))
        lab("MILKY WAY", (255, 255, 255))

    elif kind == "youth":
        d.rectangle((x, y, x + w, y + h), fill=PALE)
        base = y + h - 6
        for i, col in enumerate((NAVY, ACCENT)):
            fx = x + w * (0.34 + i * 0.24)
            d.line((fx, base, fx, base - 18 * k), fill=GREY,
                   width=max(1, int(round(k))))
            d.polygon([(fx, base - 18 * k), (fx + 11 * k, base - 15 * k),
                       (fx, base - 11 * k)], fill=col)
        lab("YOUTH MOBILITY", INK)

    elif kind == "fuel":
        d.rectangle((x, y, x + w, y + h), fill=(30, 30, 30))
        bx, by = x + w * 0.62, y + h * 0.42
        d.rounded_rectangle((bx, by, bx + 15 * k, by + 20 * k), radius=2 * k,
                            fill=(224, 166, 42))
        d.rectangle((bx + 3 * k, by + 3 * k, bx + 12 * k, by + 8 * k),
                    fill=(30, 30, 30))
        d.line((bx + 15 * k, by + 6 * k, bx + 21 * k, by + 9 * k),
               fill=(224, 166, 42), width=max(1, int(round(2 * k))))
        d.line((bx + 21 * k, by + 9 * k, bx + 21 * k, by + 19 * k),
               fill=(224, 166, 42), width=max(1, int(round(2 * k))))
        lab("MALAWI · FUEL", (224, 166, 42))

    elif kind == "protest":
        d.rectangle((x, y, x + w, y + h), fill=PALE)
        base = y + h - 5
        for i in range(4):
            cx = x + w * (0.20 + i * 0.13)
            d.ellipse((cx - 2.2 * k, base - 15 * k, cx + 2.2 * k,
                       base - 10.6 * k), fill=INK)
            d.line((cx, base - 10 * k, cx, base), fill=INK,
                   width=max(1, int(round(2 * k))))
        for i, sx in enumerate((x + w * 0.30, x + w * 0.58)):
            top = base - (20 if i == 0 else 17) * k
            d.line((sx, top, sx, base - 2 * k), fill=GREY,
                   width=max(1, int(round(k))))
            d.rectangle((sx - 9 * k, top - 9 * k, sx + 9 * k, top),
                        outline=INK, width=max(1, int(round(k))))
        lab("TOKYO · 13,000", INK)

    elif kind == "boat":
        d.rectangle((x, y, x + w, y + h), fill=SEA)
        wy = y + h * 0.72
        d.line((x + 6, wy, x + w - 6, wy + 3 * k), fill=(255, 255, 255),
               width=max(1, int(round(2 * k))))
        bx = x + w * 0.40
        d.polygon([(bx, wy - 2 * k), (bx + 26 * k, wy - 2 * k),
                   (bx + 21 * k, wy + 7 * k), (bx + 4 * k, wy + 7 * k)],
                  fill=(20, 30, 44))
        d.line((bx + 13 * k, wy - 2 * k, bx + 13 * k, wy - 17 * k),
               fill=(236, 240, 246), width=max(1, int(round(k))))
        d.polygon([(bx + 13 * k, wy - 17 * k), (bx + 13 * k, wy - 4 * k),
                   (bx + 24 * k, wy - 6 * k)], fill=(236, 240, 246))
        lab("SENEGAL · BOAT", (255, 255, 255))

    elif kind == "phones":
        d.rectangle((x, y, x + w, y + h), fill=SLATE)
        bx0, by0 = x + w * 0.34, y + h * 0.34
        bx1, by1 = x + w * 0.66, y + h - 4
        d.polygon([(bx0 + 5 * k, by0), (bx1 - 5 * k, by0), (bx1, by1),
                   (bx0, by1)], outline=(226, 232, 240),
                  width=max(1, int(round(k))))
        d.line((bx0 + 5 * k, by0 + 3 * k, bx1 - 5 * k, by0 + 3 * k),
               fill=(226, 232, 240), width=max(1, int(round(k))))
        px, py = (bx0 + bx1) / 2, (by0 + by1) / 2 + 2
        d.rounded_rectangle((px - 4 * k, py - 7 * k, px + 4 * k, py + 7 * k),
                            radius=1.5 * k, outline=(255, 255, 255),
                            width=max(1, int(round(k))))
        lab("BAG YOUR PHONES", (255, 255, 255))


# ---------------------------------------------------------------- masthead
def draw_masthead(d):
    d.text((24, 3), "THE WORLD'S NEWS IN ONE PICTURE",
           font=F(SANS_B, 12.5), fill=ACCENT, anchor="la")
    d.text((1000, 3), "33 STORIES · ONE PAGE",
           font=F(SANS_B, 12.5), fill=INK, anchor="ra")

    ts = 54
    while ts > 40 and textlen("THE DAILY ATLAS", F(SERIF_B, ts)) > 900:
        ts -= 2
    d.text((512, 13), "THE DAILY ATLAS", font=F(SERIF_B, ts), fill=INK,
           anchor="ma")

    r1 = 13 + ts + 6
    d.rectangle((24, r1, 1000, r1 + 2), fill=ACCENT)
    d.line((24, r1 + 5, 1000, r1 + 5), fill=ACCENT, width=1)

    dy = r1 + 9
    d.text((512, dy), "Friday 20 November 2026", font=F(SERIF_B, 21),
           fill=ACCENT, anchor="ma")

    sy = dy + 27
    d.text((24, sy), "EVERY STORY REPORTED ON THE DAY", font=F(SANS, 10.5),
           fill=GREY, anchor="la")
    d.text((1000, sy), "FRIDAY EDITION · NO. 20", font=F(SANS_B, 11),
           fill=INK, anchor="ra")
    return sy


# ---------------------------------------------------------------- region bar
def draw_region_bar(d, rb_y):
    segs = [("ASIA 4", CONT["Asia"], 4), ("MIDDLE EAST 4", CONT["Mideast"], 4),
            ("EUROPE 10", CONT["Europe"], 10), ("AFRICA 2", CONT["Africa"], 2),
            ("AMERICAS 10", CONT["Americas"], 10),
            ("OCEANIA 2", CONT["Oceania"], 2), ("GLOBAL 1", SRC, 1)]
    total_w = 1000 - 24
    total_n = sum(s[2] for s in segs)
    MINW = 52.0
    widths = [total_w * s[2] / total_n for s in segs]
    # Raise every segment to the 52px floor, taking the shortfall from the
    # widest segments proportionally to their headroom above the floor.
    short = sum(max(0.0, MINW - w) for w in widths)
    if short > 0:
        widths = [max(MINW, w) for w in widths]
        while short > 0.01:
            head = [max(0.0, w - MINW) for w in widths]
            tot_head = sum(head)
            if tot_head <= 0.01:
                break
            for i in range(len(widths)):
                if head[i] > 0:
                    take = min(head[i], short * head[i] / tot_head)
                    widths[i] -= take
                    short -= take
    # correct any residual rounding drift on the widest segment
    drift = sum(widths) - total_w
    widths[widths.index(max(widths))] -= drift
    assert abs(sum(widths) - total_w) < 0.01
    assert min(widths) >= MINW - 0.01, widths
    f = F(SANS_B, 10)
    x = 24.0
    n_seg = 0
    for (label, col, _), w in zip(segs, widths):
        d.rectangle((round(x), rb_y, round(x + w), rb_y + 21), fill=col)
        lf = fit_font(SANS_B, label, 10, w - 6)
        d.text((x + w / 2.0, rb_y + 10.5), label, font=lf,
               fill=(255, 255, 255), anchor="mm")
        x += w
        n_seg += 1
    return n_seg


# ---------------------------------------------------------------- stats
STATS = [
    ("3", "Kyiv bridges damaged in one night"),
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("−4.9%", "the Nikkei 225 on Friday"),
    ("$2.36bn", "GTA VI estimated first-day sales"),
    ("0", "fossil-fuel mentions in COP31's draft"),
    ("£260m", "Britain's drone package for Ukraine"),
]


def draw_stats(d, st_y):
    d.rectangle((24, st_y, 1000, st_y + 42), fill=CARD, outline=BORDER,
                width=1)
    cw = (1000 - 24) / 6.0
    fv = F(SERIF_B, 19)
    fc = F(SANS, 8)
    for i, (val, cap) in enumerate(STATS):
        x0 = 24 + i * cw
        cx = x0 + cw / 2.0
        if i:
            d.line((round(x0), st_y + 1, round(x0), st_y + 41),
                   fill=BORDER, width=1)
        d.text((cx, st_y + 3), val, font=fv, fill=ACCENT, anchor="ma")
        y = st_y + 27
        for ln in wrap(cap, fc, cw - 10):
            assert y + 9.5 <= st_y + 42 + 0.01, "stat caption overflows"
            d.text((cx, y), ln, font=fc, fill=INK, anchor="ma")
            y += 9.5
    return 6


# ---------------------------------------------------------------- featured
def _load_art(kind, w, h):
    path = os.path.join(HERE, "assets", kind + ".jpg")
    im = Image.open(path).convert("RGB")
    aw, ah = im.size
    target = w / float(h)
    if aw / float(ah) > target:
        nw = int(round(ah * target))
        left = (aw - nw) // 2
        im = im.crop((left, 0, left + nw, ah))
    else:
        nh = int(round(aw / target))
        top = (ah - nh) // 2
        im = im.crop((0, top, aw, top + nh))
    return im.resize((w, h), Image.LANCZOS)


def draw_featured(d, img, fy):
    w, h = 317, 162
    for i, st in enumerate(FEATURED):
        x = 24 + i * 329
        d.rectangle((x, fy, x + w, fy + h), fill=CARD, outline=BORDER,
                    width=1)
        art = _load_art(st["art"], w, 74)
        img.paste(art, (x, fy))
        DRAWN_ART.add(st["art"])

        # tag bar with left strip
        d.rectangle((x, fy + 48, x + w, fy + 74), fill=st["tagcol"])
        strip = INK if st["tagcol"] == ACCENT else ACCENT
        d.rectangle((x, fy + 48, x + 5, fy + 74), fill=strip)
        tagf = fit_font(SANS_B, st["tag"], 12, w - 22)
        d.text((x + 14, fy + 61), st["tag"], font=tagf, fill=(255, 255, 255),
               anchor="lm")

        chip(d, x + 18, fy + 86, 9.5, st["num"], ACCENT)
        kickf = fit_font(SANS_B, st["kick"], 10.5, 150)
        d.text((x + 34, fy + 86), st["kick"], font=kickf, fill=ACCENT,
               anchor="lm")

        # source chip, right side
        cf = F(SANS_B, 8)
        pw = textlen(st["chip"], cf) + 14
        pill(d, x + 309 - pw, fy + 78, x + 309, fy + 94, 7, SRC)
        d.text((x + 309 - pw / 2.0, fy + 86), st["chip"], font=cf,
               fill=(255, 255, 255), anchor="mm")
        global SOURCE_CHIPS
        SOURCE_CHIPS += 1

        DRAWN_NUMS.add(st["num"])
        y = block(d, x + 10, fy + 96, 297, st["head"], F(SERIF_B, 17), 18,
                  fy + 133, fill=INK)
        block(d, x + 10, y, 297, st["summ"], F(SERIF, 9.5), 11.5, fy + 160,
              fill=INK)


# ---------------------------------------------------------------- grid
def draw_grid(d, gy):
    w, h = 238, 84
    d.line((24, gy - 8, 1000, gy - 8), fill=INK, width=1)
    for i, st in enumerate(GRID):
        col, row = i % 4, i // 4
        x = 24 + col * 246
        y0 = gy + row * 92
        d.rectangle((x, y0, x + w, y0 + h), fill=CARD, outline=BORDER,
                    width=1)
        banner(d, x, y0, w, 34, st["kind"], small=True)

        chip(d, x + 13, y0 + 41, 6, st["num"], ACCENT)
        cf = F(SANS_B, 7)
        ccol = RED if st["chip"].startswith("CLAIM") else GREY
        chip_x0 = x + 230 - textlen(st["chip"], cf)
        # keep the kicker clear of the right-anchored source chip
        kf = fit_font(SANS_B, st["kick"], 8, chip_x0 - (x + 24) - 5)
        d.text((x + 24, y0 + 41), st["kick"], font=kf, fill=ACCENT,
               anchor="lm")

        d.text((x + 230, y0 + 41), st["chip"], font=cf, fill=ccol,
               anchor="rm")
        global SOURCE_CHIPS
        SOURCE_CHIPS += 1

        DRAWN_NUMS.add(st["num"])
        hfont = F(SERIF_B, 12)
        hlines = wrap(st["head"], hfont, 222)
        h_asc, h_desc = hfont.getmetrics()
        head_bottom = y0 + 47 + (len(hlines) - 1) * 12.5 + h_asc + h_desc
        block(d, x + 8, y0 + 47, 222, st["head"], hfont, 12.5,
              y0 + 72, fill=INK)
        # the summary must begin below the headline's real last line
        summ_top = max(y0 + 60, head_bottom + 2)
        ssize = 8.5
        while True:
            sfont = F(SERIF, ssize)
            slh = ssize + 1.0
            nsl = len(wrap(st["summ"], sfont, 222))
            if summ_top + nsl * slh <= y0 + 83 + 0.01 or ssize <= 7.5:
                break
            ssize -= 0.5
        block(d, x + 8, summ_top, 222, st["summ"], sfont, slh, y0 + 83,
              fill=INK)
        GRID_SEP[st["num"]] = (round(head_bottom, 1), round(summ_top, 1))


# ---------------------------------------------------------------- map
def draw_map(d, mx, my, mw, mh):
    d.rectangle((mx, my, mx + mw, my + mh), fill=(240, 238, 230),
                outline=INK, width=1)
    cw = mw / float(MASK_COLS)
    ch = mh / float(MASK_ROWS_N)
    for r, c, cont in land_cells():
        x0 = mx + c * cw
        y0 = my + r * ch
        d.rectangle((round(x0), round(y0), round(x0 + cw + 0.6),
                     round(y0 + ch + 0.6)), fill=mute(CONT[cont]))
    for num, (lon, lat, dx, dy) in PINS.items():
        px = mx + (lon + 168) / 360.0 * mw + dx
        py = my + (78 - lat) / 134.0 * mh + dy
        cont = PIN_CONT[num]
        d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=CONT[cont])
        d.text((px, py), str(num), font=F(SANS_B, 7.8),
               fill=(255, 255, 255), anchor="mm")


# ---------------------------------------------------------------- briefs
def layout_briefs(size):
    """Pick contiguous column breaks balancing heights; return layout."""
    f = F(SANS, size)
    lh = size + 2
    heights = []
    lines_all = []
    for _, txt in BRIEFS:
        ls = wrap(txt, f, 145)
        lines_all.append(ls)
        heights.append(len(ls) * lh + 2)
    n = len(BRIEFS)
    best = None
    for a in range(3, 8):
        for b in range(3, 8):
            for c in range(3, 8):
                dd = n - a - b - c
                if not (3 <= dd <= 7):
                    continue
                bounds = [(0, a), (a, a + b), (a + b, a + b + c),
                          (a + b + c, n)]
                cols = [sum(heights[s:e]) for s, e in bounds]
                m = max(cols)
                if best is None or m < best[0]:
                    best = (m, bounds, cols)
    return f, lh, lines_all, heights, best


def draw_briefs(d, bx0, by0, max_y=930.0):
    chosen = None
    for size in (9.5, 9.25, 9.0, 8.75, 8.5, 8.25, 8.0):
        f, lh, lines_all, heights, best = layout_briefs(size)
        if best is None:
            continue
        tallest = best[0]
        chosen = (size, f, lh, lines_all, heights, best)
        if by0 + tallest <= max_y:
            break
    size, f, lh, lines_all, heights, (tallest, bounds, cols) = chosen
    assert by0 + tallest <= max_y, "briefs do not fit in the band"

    # Stretch the band toward a minimum of about 215px: add the same pad to
    # every inter-brief gap in every column.
    largest_count = max(e - s for s, e in bounds)
    pad = max(0.0, 215.0 - tallest) / float(largest_count)
    gap = 2.0 + pad

    final_cols = []
    for s, e in bounds:
        final_cols.append(sum(heights[s:e]) + pad * (e - s - 1))
    band_h = max(final_cols)

    for ci, (s, e) in enumerate(bounds):
        x = bx0 + ci * 165
        y = by0
        for bi in range(s, e):
            num, txt = BRIEFS[bi]
            chip(d, x + 7, y + 6, 6.5, num, ACCENT)
            DRAWN_NUMS.add(num)
            yy = y
            for ln in lines_all[bi]:
                d.text((x + 18, yy), ln, font=f, fill=INK, anchor="la")
                yy += lh
            y = yy
            if bi < e - 1:
                sep = y + gap / 2.0
                for px in range(int(x + 2), int(x + 145), 5):
                    d.point((px, sep), fill=BORDER)
                y += gap
        assert y - by0 <= band_h + 0.01, "column %d overflows band" % ci
    return band_h, size, bounds


# ---------------------------------------------------------------- bottom band
def draw_legend(d, cy):
    """Legend centred on x=512 in the bottom band's header row."""
    f = F(SANS, 8.5)
    gaps = 14.0
    total = sum(7 + 4 + textlen(n, f) for n in CONT_ORDER) \
        + gaps * (len(CONT_ORDER) - 1)
    x = 512 - total / 2.0
    for name in CONT_ORDER:
        d.ellipse((x, cy - 3.5, x + 7, cy + 3.5), fill=CONT[name])
        x += 11
        d.text((x, cy), name, font=f, fill=INK, anchor="lm")
        x += textlen(name, f) + gaps


def draw_bottom(d, img, gy):
    by = gy + 3 * 84 + 2 * 8 + 12
    d.line((24, by, 1000, by), fill=INK, width=1)
    hy = by + 8
    d.text((24, hy), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=ACCENT,
           anchor="la")
    d.text((340, hy), "ALSO ON FRIDAY 20 NOVEMBER", font=F(SANS_B, 12),
           fill=INK, anchor="la")
    draw_legend(d, hy + 22)

    my = hy + 30
    band_h, bsize, bounds = draw_briefs(d, 340, my)
    draw_map(d, 24, my, 300, band_h)
    return my, band_h, bsize, bounds


# ---------------------------------------------------------------- date check
DC_TEXT = ("Left out on purpose — they broke on other days: the Houthi "
           "strike on Riyadh's PIF Tower (Thu 19 Nov) — the Tbilisi gas "
           "blast, six dead (Thu 19 Nov) — the ICJ genocide ruling on "
           "Myanmar (Thu 19 Nov) — the Shenzhen three-way summit "
           "(Thu 19 Nov) — GTA VI's launch day itself (Thu 19 Nov) "
           "— Nvidia's record quarter (Tue 17 Nov) — the Siberia "
           "An-12 crash, 19 killed (Tue 17 Nov).")


def draw_date_check(d, dc_y):
    d.rectangle((24, dc_y, 1000, dc_y + 36), fill=CARD, outline=RED, width=2)
    d.rectangle((24, dc_y, 86, dc_y + 36), fill=RED)
    d.text((55, dc_y + 6), "DATE", font=F(SANS_B, 10.5), fill=(255, 255, 255),
           anchor="ma")
    d.text((55, dc_y + 19), "CHECK", font=F(SANS_B, 10.5),
           fill=(255, 255, 255), anchor="ma")
    f = F(SANS, 9)
    lines = wrap(DC_TEXT, f, 896)
    assert len(lines) <= 2, "DATE CHECK text exceeds 2 lines: %d" % len(lines)
    y = dc_y + 5
    for ln in lines:
        assert y + 12 <= dc_y + 36 + 0.01, "DATE CHECK line overflows box"
        d.text((96, y), ln, font=f, fill=INK, anchor="la")
        y += 12
    return len(lines)


# ---------------------------------------------------------------- footer
def draw_footer(d, dc_y):
    fy2 = dc_y + 42
    d.line((24, fy2, 1000, fy2), fill=INK, width=1)
    d.text((512, fy2 + 5), "CLAIM = one side's account, not independently "
           "confirmed.", font=F(SERIF_I, 9.5), fill=INK, anchor="ma")
    d.text((512, fy2 + 21), "Every story happened or was first reported on "
           "Friday 20 November 2026 · Disputed claims are attributed "
           "· Sources: Reuters · AP · BBC · IMD · "
           "CNBC · Sensor Tower · UN News",
           font=F(SANS, 8.5), fill=GREY, anchor="ma")


# ---------------------------------------------------------------- main
def main():
    global SOURCE_CHIPS
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    d = ImageDraw.Draw(img)

    sy = draw_masthead(d)
    rb_y = sy + 15
    n_seg = draw_region_bar(d, rb_y)
    st_y = rb_y + 27
    n_cells = draw_stats(d, st_y)

    fy = st_y + 50
    draw_featured(d, img, fy)
    gy = fy + 162 + 16
    draw_grid(d, gy)

    my, band_h, bsize, bounds = draw_bottom(d, img, gy)
    dc_y = my + band_h + 8
    n_dc = draw_date_check(d, dc_y)
    draw_footer(d, dc_y)

    # ------------------------------------------------------------ asserts
    assert not CLIPS, "CLIP failures: %r" % (CLIPS,)
    assert len(DRAWN_NUMS) == 33, "drawn story numbers: %d" % len(DRAWN_NUMS)
    assert DRAWN_NUMS == set(range(1, 34)), sorted(set(range(1, 34)) - DRAWN_NUMS)
    assert DRAWN_ART == {"bridges", "cyclone", "cop31"}, DRAWN_ART
    assert n_seg == 7, "region segments: %d" % n_seg
    assert n_cells == 6, "stat cells: %d" % n_cells
    assert n_dc <= 2
    assert SOURCE_CHIPS == 15, "source chips: %d" % SOURCE_CHIPS
    assert len(GRID_SEP) == 12, "grid separation records: %d" % len(GRID_SEP)
    bad = {n: v for n, v in GRID_SEP.items() if not v[0] < v[1]}
    assert not bad, "headline/summary collision on grid cards: %r" % (bad,)

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    assert size <= 1048576, "entry.png too big: %d" % size

    with Image.open(OUT) as chk:
        assert chk.size == (1024, 1024), chk.size
        assert chk.format == "PNG", chk.format
    with open(OUT, "rb") as fh:
        assert fh.read(4) == b"\x89PNG", "not a PNG"

    print("briefs font %.2f, columns %r" % (bsize, bounds))
    print("band_h %.1f, dc_y %.1f, footer bottom %.1f"
          % (band_h, dc_y, dc_y + 42))
    print("wrote %s  %d bytes  (%.1f KiB)" % (OUT, size, size / 1024.0))
    print("Assertion summary: no CLIP failures; all 33 story numbers drawn; three featured artworks (bridges, cyclone, cop31) loaded and pasted; region bar's 7 segments drawn; stat strip's 6 cells drawn; DATE CHECK text drawn in at most 2 lines (%d lines); source chip drawn for each of the 15 card stories (%d chips); headline/summary separation assertion passed for all %d grid cards." % (n_dc, SOURCE_CHIPS, len(GRID_SEP)))


if __name__ == "__main__":
    main()
