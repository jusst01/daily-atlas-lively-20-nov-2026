#!/usr/bin/env python3
"""Flat-editorial fallback artwork for the three featured cards.

Only used if the Recraft route is unavailable. Draws real scenes (places,
people, the story readable in the picture) in flat colour fields with no
text. Renders at 2x and downsamples for clean edges.

Writes assets/bridges.jpg, assets/cyclone.jpg, assets/cop31.jpg at 952 wide.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
W, H = 952, 700
S = 2  # supersample factor


def canvas(w=W, h=H, col=(20, 26, 42)):
    return Image.new("RGB", (w * S, h * S), col)


def fin(im):
    return im.resize((W, H), Image.LANCZOS)


def glow(im, box, col, radius=26, alpha=70):
    """Soft flat glow blob (drawn on a separate layer, blurred once)."""
    lay = Image.new("RGB", im.size, (0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.ellipse([v * S for v in box], fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(radius * S / 2))
    return Image.blend(im, Image.blend(im, lay, 1.0), 0)  # placeholder


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = np.random.RandomState(20261120)

    # ---------------------------------------------------------- BRIDGES
    im = canvas(col=(14, 20, 36))
    d = ImageDraw.Draw(im)
    # land masses either side of a wide diagonal river
    land = (26, 34, 46)
    d.polygon([(0, 0), (W * S, 0), (W * S, H * 0.30 * S),
               (0, H * 0.40 * S)], fill=land)
    d.polygon([(0, H * 0.66 * S), (W * S, H * 0.56 * S), (W * S, H * S),
               (0, H * S)], fill=land)
    # river
    d.polygon([(0, H * 0.40 * S), (W * S, H * 0.30 * S),
               (W * S, H * 0.56 * S), (0, H * 0.66 * S)],
              fill=(16, 34, 56))
    # river sheen bands
    for i, t in enumerate((0.43, 0.48, 0.54, 0.60)):
        y0 = H * t * S
        d.line([(0, y0), (W * S, y0 - H * 0.10 * S)],
               fill=(22, 46, 72), width=int(2 * S))
    # city light dots on both banks
    for _ in range(320):
        x = rng.rand() * W
        bank = rng.rand()
        if bank < 0.5:
            y = rng.rand() * H * 0.34
        else:
            y = H * 0.62 + rng.rand() * H * 0.34
        r = (0.7 + rng.rand() * 1.5) * S
        c = (196, 176, 132) if rng.rand() < 0.75 else (232, 210, 160)
        d.ellipse([x * S - r, y * S - r, x * S + r, y * S + r], fill=c)
    # fires on both banks
    for fx, fy, fr in ((0.17, 0.30, 26), (0.30, 0.63, 20), (0.72, 0.60, 30),
                       (0.86, 0.28, 18)):
        for k in range(4):
            rr = (fr - k * 5) * S
            col = [(120, 54, 32), (186, 84, 40), (226, 132, 56),
                   (244, 190, 96)][k]
            d.ellipse([fx * W * S - rr, fy * H * S - rr,
                       fx * W * S + rr, fy * H * S + rr], fill=col)
    # three bridges across the river
    deck = (92, 104, 122)
    for bi, bx in enumerate((0.20, 0.50, 0.80)):
        x0 = bx * W * S
        ytop = (0.44 - bx * 0.02) * H * S
        ybot = (0.62 - bx * 0.02) * H * S
        if bi == 1:  # the broken bridge
            seg = (ybot - ytop)
            d.polygon([(x0 - 6 * S, ytop), (x0 + 6 * S, ytop),
                       (x0 + 6 * S, ytop + seg * 0.38),
                       (x0 - 6 * S, ytop + seg * 0.38)], fill=deck)
            d.polygon([(x0 - 6 * S, ytop + seg * 0.60), (x0 + 6 * S,
                       ytop + seg * 0.60), (x0 + 6 * S, ybot),
                       (x0 - 6 * S, ybot)], fill=deck)
            # broken stubs hanging into the gap
            d.line([(x0 - 6 * S, ytop + seg * 0.38), (x0 - 12 * S,
                   ytop + seg * 0.50)], fill=deck, width=int(3 * S))
            d.line([(x0 + 6 * S, ytop + seg * 0.60), (x0 + 13 * S,
                   ytop + seg * 0.48)], fill=deck, width=int(3 * S))
            # debris in the water
            for _ in range(9):
                dx = x0 + (rng.rand() - 0.5) * 40 * S
                dy = ytop + seg * 0.5 + (rng.rand() - 0.5) * 20 * S
                d.rectangle([dx, dy, dx + 4 * S, dy + 2 * S], fill=deck)
        else:
            d.polygon([(x0 - 6 * S, ytop), (x0 + 6 * S, ytop),
                       (x0 + 6 * S, ybot), (x0 - 6 * S, ybot)], fill=deck)
            for t in np.linspace(0.15, 0.85, 4):
                py = ytop + (ybot - ytop) * t
                d.rectangle([x0 - 9 * S, py, x0 + 9 * S, py + 4 * S],
                            fill=(72, 84, 100))
    # thin red missile trails arcing through the sky
    for t0, t1 in ((0.05, 0.42), (0.30, 0.62), (0.62, 0.92)):
        pts = []
        for t in np.linspace(0, 1, 60):
            x = (t0 + (t1 - t0) * t) * W * S
            y = (0.24 - 0.13 * np.sin(np.pi * t)) * H * S
            pts.append((x, y))
        d.line(pts, fill=(186, 62, 44), width=int(1.6 * S), joint="curve")
    im = fin(im)
    im.save(os.path.join(OUT, "bridges.jpg"), quality=88)

    # ---------------------------------------------------------- CYCLONE
    im = canvas(col=(52, 62, 78))
    d = ImageDraw.Draw(im)
    # flat sky bands, darker at the top
    for i in range(10):
        t = i / 10.0
        c = (int(52 + 40 * t), int(62 + 44 * t), int(78 + 40 * t))
        d.rectangle([0, i * H * 0.09 * S, W * S, (i + 1) * H * 0.09 * S],
                    fill=c)
    # the cyclone spiral, huge, filling the sky
    cx, cy = W * 0.5 * S, H * 0.40 * S
    for k in range(9):
        rad = (58 + k * 26) * S
        start = k * 34
        d.arc([cx - rad, cy - rad * 0.86, cx + rad, cy + rad * 0.86],
              start, start + 268, fill=(236, 240, 244),
              width=int((9 - k * 0.55) * S))
    d.ellipse([cx - 26 * S, cy - 22 * S, cx + 26 * S, cy + 22 * S],
              fill=(246, 248, 250))
    # sea
    d.rectangle([0, H * 0.62 * S, W * S, H * S], fill=(34, 74, 104))
    for i in range(7):
        t = i / 7.0
        y = (0.64 + t * 0.34) * H
        col = (44 + int(24 * t), 92 + int(26 * t), 124 + int(24 * t))
        d.rectangle([0, y * S, W * S, (y + 0.05 * H) * S], fill=col)
    # white crests rolling in
    for i in range(6):
        y = (0.66 + i * 0.055) * H
        pts = []
        for t in np.linspace(0, 1, 50):
            x = t * W * S
            yy = y * S + np.sin(t * 7 + i) * 4 * S
            pts.append((x, yy))
        d.line(pts, fill=(226, 234, 240), width=int((1.2 + i * 0.5) * S))
    # sand
    d.polygon([(0, H * 0.94 * S), (W * S, H * 0.90 * S), (W * S, H * S),
               (0, H * S)], fill=(196, 178, 146))
    # village huts
    for hx in np.linspace(0.08, 0.92, 6):
        bx = hx * W * S
        by = H * 0.895 * S
        d.rectangle([bx - 15 * S, by - 16 * S, bx + 15 * S, by],
                    fill=(158, 132, 106))
        d.polygon([(bx - 19 * S, by - 16 * S), (bx, by - 30 * S),
                   (bx + 19 * S, by - 16 * S)], fill=(122, 96, 78))
    # bent palms
    for px in (0.14, 0.30, 0.66, 0.84):
        bx = px * W * S
        by = H * 0.93 * S
        tipx = bx - 30 * S
        tipy = by - 78 * S
        d.line([(bx, by), (bx - 12 * S, by - 40 * S), (tipx, tipy)],
               fill=(74, 60, 46), width=int(4 * S), joint="curve")
        for ang in (-2.6, -2.1, -1.5, -0.9, -0.3):
            ex = tipx + np.cos(ang) * 26 * S
            ey = tipy + np.sin(ang) * 16 * S
            d.line([(tipx, tipy), (ex, ey)], fill=(46, 84, 62),
                   width=int(3 * S))
    # fishing boats hauled up on the sand
    for bx in (0.40, 0.55):
        x = bx * W * S
        y = H * 0.965 * S
        d.polygon([(x - 26 * S, y), (x + 26 * S, y), (x + 18 * S, y + 12 * S),
                   (x - 18 * S, y + 12 * S)], fill=(122, 96, 74))
        d.line([(x, y), (x, y - 22 * S)], fill=(96, 78, 60),
               width=int(2 * S))
    im = fin(im)
    im.save(os.path.join(OUT, "cyclone.jpg"), quality=88)

    # ---------------------------------------------------------- COP31
    im = canvas(col=(72, 88, 116))
    d = ImageDraw.Draw(im)
    # dusk sky: flat bands, warm at the horizon
    bands = [(58, 74, 104), (70, 86, 116), (88, 100, 126), (116, 116, 132),
             (152, 134, 130), (186, 152, 130), (210, 172, 138)]
    bh = H * 0.52 / len(bands)
    for i, c in enumerate(bands):
        d.rectangle([0, i * bh * S, W * S, (i + 1) * bh * S + 1], fill=c)
    # mountains behind
    d.polygon([(0, H * 0.52 * S), (W * 0.16 * S, H * 0.30 * S),
               (W * 0.32 * S, H * 0.50 * S), (W * 0.50 * S, H * 0.33 * S),
               (W * 0.70 * S, H * 0.50 * S), (W * 0.86 * S, H * 0.34 * S),
               (W * S, H * 0.50 * S), (W * S, H * 0.56 * S),
               (0, H * 0.56 * S)], fill=(84, 92, 112))
    d.polygon([(0, H * 0.56 * S), (W * 0.22 * S, H * 0.44 * S),
               (W * 0.44 * S, H * 0.57 * S), (W * 0.64 * S, H * 0.45 * S),
               (W * 0.84 * S, H * 0.57 * S), (W * S, H * 0.48 * S),
               (W * S, H * 0.62 * S), (0, H * 0.62 * S)],
              fill=(64, 74, 96))
    # ground
    d.rectangle([0, H * 0.60 * S, W * S, H * S], fill=(44, 48, 62))
    # glass conference centre: wide slab, lit window grid
    bx0, bx1 = W * 0.16, W * 0.84
    by0, by1 = H * 0.50, H * 0.80
    d.polygon([(bx0 * S, by1 * S), (bx1 * S, by1 * S),
               (bx1 * S, by0 * S), (bx0 * S, by0 * S)], fill=(38, 52, 76))
    cols, rows = 18, 4
    for cxi in range(cols):
        for ryi in range(rows):
            wx = bx0 + (cxi + 0.18) * (bx1 - bx0) / cols
            wy = by0 + (ryi + 0.22) * (by1 - by0) / rows
            ww = (bx1 - bx0) / cols * 0.62
            wh = (by1 - by0) / rows * 0.52
            lit = (cxi * 7 + ryi * 3) % 5 != 0
            d.rectangle([wx * S, wy * S, (wx + ww) * S, (wy + wh) * S],
                        fill=(228, 206, 156) if lit else (58, 74, 96))
    # roof line and entrance canopy
    d.rectangle([bx0 * S, (by0 - 5) * S, bx1 * S, by0 * S],
                fill=(28, 36, 54))
    d.polygon([(W * 0.42 * S, H * 0.80 * S), (W * 0.58 * S, H * 0.80 * S),
               (W * 0.62 * S, H * 0.86 * S), (W * 0.38 * S, H * 0.86 * S)],
              fill=(24, 30, 44))
    # row of national flags on tall poles in front
    for i in range(9):
        fx = (0.20 + i * 0.075) * W * S
        top = H * 0.40 * S
        base = H * 0.92 * S
        d.line([(fx, base), (fx, top)], fill=(150, 156, 168),
               width=int(2 * S))
        cols_flags = [(186, 62, 44), (222, 226, 232), (38, 58, 92),
                      (44, 96, 88), (186, 122, 38), (116, 80, 148),
                      (44, 124, 134), (168, 62, 44), (58, 84, 128)]
        d.polygon([(fx, top), (fx + 26 * S, top + 7 * S),
                   (fx, top + 15 * S)], fill=cols_flags[i])
    # delegates as small silhouettes arriving with briefcases
    for i in range(11):
        dx = (0.24 + i * 0.048 + (rng.rand() - 0.5) * 0.01) * W * S
        dy = (0.90 + rng.rand() * 0.05) * H * S
        hh = (26 + rng.rand() * 8) * S
        d.ellipse([dx - 3.4 * S, dy - hh, dx + 3.4 * S, dy - hh + 7 * S],
                  fill=(16, 18, 26))
        d.polygon([(dx - 5 * S, dy), (dx + 5 * S, dy),
                   (dx + 3.6 * S, dy - hh + 5 * S),
                   (dx - 3.6 * S, dy - hh + 5 * S)], fill=(16, 18, 26))
        # briefcase
        d.rectangle([dx + 5 * S, dy - 11 * S, dx + 11 * S, dy - 5 * S],
                    fill=(52, 40, 34))
    im = fin(im)
    im.save(os.path.join(OUT, "cop31.jpg"), quality=88)

    for n in ("bridges", "cyclone", "cop31"):
        p = os.path.join(OUT, n + ".jpg")
        with Image.open(p) as chk:
            print(n, chk.size, chk.format, os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
