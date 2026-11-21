import os
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import hashlib

def main():
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    assets_dir = os.path.join(base_dir, "assets")

    # Fonts
    font_dir = "/usr/share/fonts/truetype/dejavu/"
    sans_path = os.path.join(font_dir, "DejaVuSans.ttf")
    sans_bold_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    serif_path = os.path.join(font_dir, "DejaVuSerif.ttf")
    serif_bold_path = os.path.join(font_dir, "DejaVuSerif-Bold.ttf")

    def get_font(path, size):
        return ImageFont.truetype(path, size)

    # Colors
    PAPER = (243, 244, 241)
    CREAM = (250, 250, 247)
    INK = (19, 28, 43)
    NAVY = (30, 58, 95)
    NAVY_DARK = (16, 32, 54)
    MUTED_RED = (178, 58, 46)
    LAND = (217, 220, 214)
    MUTED_GREY = (104, 112, 122)
    WHITE = (255, 255, 255)
    BORDER_COLOR = (210, 212, 208)

    # Canvas
    W, H = 1024, 1024
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Band Stack check (Sum = 1024)
    bands = [
        ("top_margin", 20),
        ("eyebrow", 15),
        ("masthead", 46),
        ("gap1", 5),
        ("region_bar", 22),
        ("gap2", 6),
        ("stat_strip", 46),
        ("gap3", 8),
        ("featured_row", 196),
        ("gap4", 8),
        ("grid_block", 206),
        ("gap5", 8),
        ("bottom_band", 258),
        ("gap6", 6),
        ("how_sure", 16),
        ("gap7", 6),
        ("date_check", 152),
    ]
    total_height = sum(h for _, h in bands)
    assert total_height == 1024, f"Band stack sum is {total_height}, expected 1024"

    current_y = 20

    # 1. Eyebrow (height 15)
    eb_y = current_y
    eb_font = get_font(sans_bold_path, 11)
    draw.text((28, eb_y), "THE DAILY ATLAS", fill=INK, font=eb_font)
    right_text = "33 STORIES - ONE PAGE"
    bbox = eb_font.getbbox(right_text)
    rw = bbox[2] - bbox[0]
    draw.text((996 - rw, eb_y), right_text, fill=INK, font=eb_font)
    current_y += 15

    # 2. Masthead (height 46)
    mh_y = current_y
    mh_date = "FRIDAY 20 NOVEMBER 2026"
    # Find font size to fit 968 width, start 38, never below 30
    mh_font_size = 38
    mh_font = get_font(serif_bold_path, mh_font_size)
    while mh_font_size > 30:
        bbox = mh_font.getbbox(mh_date)
        tw = bbox[2] - bbox[0]
        if tw <= 968:
            break
        mh_font_size -= 1
        mh_font = get_font(serif_bold_path, mh_font_size)
    bbox = mh_font.getbbox(mh_date)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    mh_x = 28 + (968 - tw) // 2
    draw.text((mh_x, mh_y + (46 - th) // 2 - 4), mh_date, fill=NAVY, font=mh_font)
    # Double rule: 2px navy over 1px ink at bottom of masthead
    draw.line([(28, mh_y + 42), (996, mh_y + 42)], fill=NAVY, width=2)
    draw.line([(28, mh_y + 44), (996, mh_y + 44)], fill=INK, width=1)
    current_y += 46

    current_y += 5 # gap

    # 3. Region bar (height 22)
    rb_y = current_y
    regions = [
        ("ASIA 4", 4, (116, 80, 148)),
        ("MIDDLE EAST 4", 4, (186, 122, 38)),
        ("EUROPE 10", 10, (58, 84, 128)),
        ("AFRICA 2", 2, (122, 106, 52)),
        ("AMERICAS 10", 10, (168, 62, 44)),
        ("OCEANIA 2", 2, (44, 124, 134)),
        ("GLOBAL 1", 1, (90, 88, 80)),
    ]
    # Mute toward paper (243,244,241) by ~0.45
    def mute_color(c):
        return (
            int(c[0] * 0.55 + 243 * 0.45),
            int(c[1] * 0.55 + 244 * 0.45),
            int(c[2] * 0.55 + 241 * 0.45)
        )

    rx = 28
    total_w = 968
    rb_font = get_font(sans_bold_path, 10)
    for i, (rname, count, col) in enumerate(regions):
        mcol = mute_color(col)
        w_seg = int(total_w * count / 33)
        if i == len(regions) - 1:
            w_seg = 996 - rx # remainder
        draw.rectangle([rx, rb_y, rx + w_seg, rb_y + 22], fill=mcol)
        # label
        bbox = rb_font.getbbox(rname)
        lw = bbox[2] - bbox[0]
        lh = bbox[3] - bbox[1]
        if lw + 6 > w_seg:
            # stack name and count
            parts = rname.split()
            name_part = " ".join(parts[:-1])
            count_part = parts[-1]
            draw.text((rx + (w_seg - rb_font.getbbox(name_part)[2])/2, rb_y + 2), name_part, fill=WHITE, font=rb_font)
            draw.text((rx + (w_seg - rb_font.getbbox(count_part)[2])/2, rb_y + 11), count_part, fill=WHITE, font=rb_font)
        else:
            draw.text((rx + (w_seg - lw)/2, rb_y + (22 - lh)/2 - 2), rname, fill=WHITE, font=rb_font)
        rx += w_seg
    draw.line([(28, rb_y + 22), (996, rb_y + 22)], fill=BORDER_COLOR, width=1)
    current_y += 22

    current_y += 6 # gap

    # 4. Stat strip (height 46)
    ss_y = current_y
    draw.rectangle([28, ss_y, 996, ss_y + 46], fill=CREAM, outline=BORDER_COLOR, width=1)
    stats = [
        ("3", "Kyiv bridges damaged in one night"),
        ("372,000", "people evacuated ahead of Cyclone Akvan"),
        ("−4.9%", "the Nikkei 225 on Friday"),
        ("$2.36bn", "GTA VI's estimated first-day sales"),
        ("0", "mentions of fossil fuels in COP31's draft deal"),
        ("£260m", "Britain's drone package for Ukraine"),
    ]
    cell_w = 968 / 6.0
    val_font = get_font(serif_bold_path, 21)
    cap_font = get_font(sans_path, 9) # 11px wrapped, or 9-10 to fit 2 lines in 46h
    for i, (val, cap) in enumerate(stats):
        cx = 28 + i * cell_w
        if i > 0:
            draw.line([(cx, ss_y), (cx, ss_y + 46)], fill=BORDER_COLOR, width=1)
        # draw value centred around y+14
        vbox = val_font.getbbox(val)
        vw = vbox[2] - vbox[0]
        vh = vbox[3] - vbox[1]
        draw.text((cx + (cell_w - vw)/2, ss_y + 3), val, fill=INK, font=val_font)
        # draw caption wrapped to 2 lines
        # simple wrap helper for stat caption
        words = cap.split()
        line1, line2 = "", ""
        overflow = False
        for w in words:
            if not overflow:
                test_line = (line1 + " " + w).strip()
                if cap_font.getbbox(test_line)[2] <= cell_w - 8:
                    line1 = test_line
                    continue
                else:
                    overflow = True
            line2 = (line2 + " " + w).strip()
        draw.text((cx + (cell_w - cap_font.getbbox(line1)[2])/2, ss_y + 24), line1, fill=INK, font=cap_font)
        if line2:
            draw.text((cx + (cell_w - cap_font.getbbox(line2)[2])/2, ss_y + 34), line2, fill=INK, font=cap_font)
    current_y += 46

    current_y += 8 # gap

    # 5. Featured row (height 196)
    feat_y = current_y
    featured_stories = [
        {
            "num": "01.", "kicker": "KYIV · WAR", "chip": "CONFIRMED - REUTERS",
            "head": "Kyiv's bridges hit in one night",
            "dek": "Russia's barrage damages three Dnipro crossings. Three water workers killed, about 15 injured.",
            "image": "bridges.jpg"
        },
        {
            "num": "02.", "kicker": "GOPALPUR · STORM", "chip": "CONFIRMED - IMD",
            "head": "Cyclone Akvan comes ashore",
            "dek": "Akvan crosses the coast weakened to 70-80 km/h, below forecast. 372,000 evacuated; no major damage.",
            "image": "cyclone.jpg"
        },
        {
            "num": "03.", "kicker": "ANTALYA · CLIMATE", "chip": "CONFIRMED - REUTERS",
            "head": "COP31's last day, no deal",
            "dek": "The draft drops every mention of fossil fuels. 92,000 attendees; talks may run into the weekend.",
            "image": "cop31.jpg"
        },
    ]

    card_w = 314
    card_gap = 13
    feat_font_head = get_font(serif_bold_path, 16)
    feat_font_dek = get_font(serif_path, 11)
    feat_font_kicker = get_font(sans_bold_path, 10.5)
    feat_font_num = get_font(sans_bold_path, 12)
    feat_font_chip = get_font(sans_bold_path, 8)

    drawn_numbers = set()

    for i, fstory in enumerate(featured_stories):
        # Dek assertions
        if i == 0:
            assert fstory["dek"] == "Russia's barrage damages three Dnipro crossings. Three water workers killed, about 15 injured.", "Dek 1 corrupted"
        if i == 1:
            assert fstory["dek"] == "Akvan crosses the coast weakened to 70-80 km/h, below forecast. 372,000 evacuated; no major damage.", "Dek 2 corrupted"

        cx = 28 + i * (card_w + card_gap)
        draw.rectangle([cx, feat_y, cx + card_w, feat_y + 196], fill=CREAM, outline=BORDER_COLOR, width=1)

        # Artwork at top: 314x140, center crop
        img_path = os.path.join(assets_dir, fstory["image"])
        if os.path.exists(img_path):
            with Image.open(img_path) as im:
                im = im.convert("RGB")
                iw, ih = im.size
                target_w, target_h = 314, 140
                # center crop to 314:140 ratio
                target_aspect = target_w / target_h
                im_aspect = iw / ih
                if im_aspect > target_aspect:
                    new_w = int(ih * target_aspect)
                    left = (iw - new_w) // 2
                    im_crop = im.crop((left, 0, left + new_w, ih))
                else:
                    new_h = int(iw / target_aspect)
                    top = (ih - new_h) // 2
                    im_crop = im.crop((0, top, iw, top + new_h))
                im_thumb = im_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)
                img.paste(im_thumb, (cx, feat_y))

        # Caption block below (56px height): y from feat_y + 140 to feat_y + 196
        cy_text = feat_y + 142

        # Kicker row: number + kicker + source chip right anchored
        num_str = fstory["num"]
        kicker_str = fstory["kicker"]
        chip_str = fstory["chip"]

        draw.text((cx + 6, cy_text), num_str, fill=NAVY, font=feat_font_num)
        num_w = feat_font_num.getbbox(num_str)[2] - feat_font_num.getbbox(num_str)[0]

        draw.text((cx + 8 + num_w, cy_text + 1), kicker_str, fill=NAVY, font=feat_font_kicker)

        # chip right anchored
        chip_bbox = feat_font_chip.getbbox(chip_str)
        chip_w = chip_bbox[2] - chip_bbox[0] + 8
        chip_h = 12
        chip_x = cx + card_w - 6 - chip_w
        chip_y = cy_text + 1
        draw.rectangle([chip_x, chip_y, chip_x + chip_w, chip_y + chip_h], fill=(220, 222, 218))
        draw.text((chip_x + 4, chip_y + 1), chip_str, fill=INK, font=feat_font_chip)

        cy_text += 16

        # Headline (1 line)
        head_str = fstory["head"]
        draw.text((cx + 6, cy_text), head_str, fill=INK, font=feat_font_head)
        cy_text += 20

        # Dek (wrapped to 2 lines max)
        dek_str = fstory["dek"]
        words = dek_str.split()
        line1, line2 = "", ""
        overflow = False
        for w in words:
            if not overflow:
                test = (line1 + " " + w).strip()
                if feat_font_dek.getbbox(test)[2] <= card_w - 12:
                    line1 = test
                    continue
                else:
                    overflow = True
            line2 = (line2 + " " + w).strip()
        draw.text((cx + 6, cy_text), line1, fill=INK, font=feat_font_dek)
        if line2:
            draw.text((cx + 6, cy_text + 11), line2, fill=INK, font=feat_font_dek)

        drawn_numbers.add(i + 1)

    current_y += 196

    current_y += 8 # gap

    # 6. Grid block (height 222)
    grid_y = current_y
    grid_stories = [
        {
            "num": 4, "kicker": "ASIA · MARKETS", "head": "Asia's AI rout deepens",
            "summ": "Nikkei −4.9% and KOSPI −5.5%; Hang Seng nears bear ground. SoftBank −16%.",
            "chip": "CONFIRMED - EXCHANGES", "strip": "strip4.jpg"
        },
        {
            "num": 5, "kicker": "NEW YORK · TECH", "head": "Anthropic joins the big indexes",
            "summ": "A day after its record debut, ANT joins the MSCI and FTSE indexes.",
            "chip": "CONFIRMED - WIRES", "strip": "strip5.jpg"
        },
        {
            "num": 6, "kicker": "WORLDWIDE · GAMES", "head": "GTA VI's $2.36bn first day",
            "summ": "Sensor Tower estimates 24.58M copies sold on launch day - a record.",
            "chip": "ESTIMATES - SENSOR TOWER", "strip": "strip6.jpg"
        },
        {
            "num": 7, "kicker": "RIYADH · ENERGY", "head": "Oil edges up on supply fears",
            "summ": "Brent +0.3% to $92.22; Saudi defences down four more Houthi missiles.",
            "chip": "CONFIRMED - REUTERS", "strip": "strip7.jpg"
        },
        {
            "num": 8, "kicker": "EUROPE · DIPLOMACY", "head": "Europe reaches for a seat",
            "summ": "Leaders say Europe is ready to join talks with Russia on the war.",
            "chip": "CONFIRMED - BBC", "strip": "strip8.jpg"
        },
        {
            "num": 9,
            "kicker": "LONDON · DEFENCE",
            "head": "Britain's drone package",
            "summ": "More than 1,000 drones for Ukraine in a new £260m package.",
            "chip": "CONFIRMED - WIRES",
            "strip": "strip9.jpg"
        },
        {
            "num": 10, "kicker": "SCIENCE · SPACE", "head": "Two hidden companions found",
            "summ": "Rubin preview data reveals two ultra-faint Milky Way satellites.",
            "chip": "CONFIRMED - UW", "strip": "strip10.jpg"
        },
        {
            "num": 11, "kicker": "LONDON · EUROPE", "head": "UK and EU agree youth mobility",
            "summ": "London and Brussels are set to agree a youth mobility scheme.",
            "chip": "CONFIRMED - BBC", "strip": "strip11.jpg"
        },
        {
            "num": 12, "kicker": "MALAWI · CRISIS", "head": "Fuel crisis turns violent",
            "summ": "A deepening fuel shortage triggers violence and economic strain.",
            "chip": "CONFIRMED - WIRES", "strip": "strip12.jpg"
        },
        {
            "num": 13, "kicker": "TOKYO · PROTEST", "head": "13,000 march in Tokyo",
            "summ": "Protesters rally against the Takaichi government's policies.",
            "chip": "CONFIRMED - WIRES", "strip": "strip13.jpg"
        },
        {
            "num": 14, "kicker": "SENEGAL · MIGRATION",
            "head": "Boat capsize kills four",
            "summ": "A boat capsizes off Senegal as the migration surge continues.",
            "chip": "CONFIRMED - WIRES", "strip": "strip14.jpg"
        },
        {
            "num": 15, "kicker": "WASHINGTON · PRESS",
            "head": "Bag your phones",
            "summ": "The White House orders journalists to bag phones after the China trip.",
            "chip": "CONFIRMED - WIRES", "strip": "strip15.jpg"
        },
    ]

    g_card_w = 236
    g_card_h = 70
    g_cols = 4
    g_rows = 3
    g_x_gap = 8
    g_y_gap = 4 # row height 70 + 4 gap = 74 step

    grid_font_head = get_font(serif_bold_path, 12)
    grid_font_summ = get_font(serif_path, 11)
    grid_font_kicker = get_font(sans_bold_path, 8.5)
    grid_font_num = get_font(sans_bold_path, 11)
    grid_font_chip = get_font(sans_bold_path, 7.5)

    for idx, gstory in enumerate(grid_stories):
        col = idx % g_cols
        row = idx // g_cols
        gx = 28 + col * (g_card_w + g_x_gap)
        gy = grid_y + row * 74

        draw.rectangle([gx, gy, gx + g_card_w, gy + g_card_h], fill=CREAM, outline=BORDER_COLOR, width=1)

        # Scene strip at top: 236x22
        strip_path = os.path.join(assets_dir, gstory["strip"])
        if os.path.exists(strip_path):
            with Image.open(strip_path) as im:
                im = im.convert("RGB")
                iw, ih = im.size
                tw, th = 236, 22
                t_aspect = tw / th
                im_aspect = iw / ih
                if im_aspect > t_aspect:
                    new_w = int(ih * t_aspect)
                    left = (iw - new_w) // 2
                    im_crop = im.crop((left, 0, left + new_w, ih))
                else:
                    new_h = int(iw / t_aspect)
                    top = (ih - new_h) // 2
                    im_crop = im.crop((0, top, iw, top + new_h))
                im_thumb = im_crop.resize((tw, th), Image.Resampling.LANCZOS)
                img.paste(im_thumb, (gx, gy))
        else:
            # flat muted tint panel if missing
            draw.rectangle([gx, gy, gx + 236, gy + 22], fill=(217, 220, 214))

        # Text inside card below strip (y from gy + 23 to gy + 70)
        gt_y = gy + 23

        # Chip row: printed number + kicker + source chip
        num_str = f"{gstory['num']:02d}."
        kicker_str = gstory["kicker"]
        chip_str = gstory["chip"]

        draw.text((gx + 4, gt_y), num_str, fill=NAVY, font=grid_font_num)
        num_w = grid_font_num.getbbox(num_str)[2] - grid_font_num.getbbox(num_str)[0]

        draw.text((gx + 6 + num_w, gt_y + 1), kicker_str, fill=NAVY, font=grid_font_kicker)

        # Source chip right anchored
        chip_bbox = grid_font_chip.getbbox(chip_str)
        chip_w = chip_bbox[2] - chip_bbox[0] + 6
        chip_h = 10
        chip_x = gx + g_card_w - 4 - chip_w
        chip_y = gt_y + 1

        is_claim = chip_str.startswith("CLAIM") or chip_str.startswith("ESTIMATES")
        chip_bg = NAVY_DARK if is_claim else (220, 222, 218)
        chip_fg = WHITE if is_claim else INK
        draw.rectangle([chip_x, chip_y, chip_x + chip_w, chip_y + chip_h], fill=chip_bg)
        draw.text((chip_x + 3, chip_y), chip_str, fill=chip_fg, font=grid_font_chip)

        gt_y += 12

        # Headline (1 line)
        head_str = gstory["head"]
        draw.text((gx + 4, gt_y), head_str, fill=INK, font=grid_font_head)
        gt_y += 14

        # Summary (wrapped to 2 lines max)
        summ_str = gstory["summ"]
        words = summ_str.split()
        line1, line2 = "", ""
        overflow = False
        for w in words:
            if not overflow:
                test = (line1 + " " + w).strip()
                if grid_font_summ.getbbox(test)[2] <= g_card_w - 8:
                    line1 = test
                    continue
                else:
                    overflow = True
            line2 = (line2 + " " + w).strip()
        draw.text((gx + 4, gt_y), line1, fill=INK, font=grid_font_summ)
        if line2:
            draw.text((gx + 4, gy + g_card_h - 11), line2, fill=INK, font=grid_font_summ)

        drawn_numbers.add(gstory["num"])

    current_y += 206

    current_y += 8 # gap

    # 7. Bottom band (height 258)
    bb_y = current_y
    bb_height = 258

    section_head_font = get_font(sans_bold_path, 12)
    draw.text((28, bb_y), "WHERE IT HAPPENED", fill=NAVY, font=section_head_font)
    draw.text((392, bb_y), "ALSO ON FRIDAY 20 NOVEMBER", fill=INK, font=section_head_font)

    content_bb_y = bb_y + 18
    content_bb_h = bb_height - 18

    # Map LEFT: x 28..368 (width 340)
    map_x, map_y = 28, content_bb_y
    map_w, map_h = 340, content_bb_h
    draw.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=PAPER, outline=BORDER_COLOR, width=1)

    # Render land cells from mask
    land_mask_spans = {
        1: [(8,11), (27,30), (48,50), (59,61)],
        2: [(1,6), (9,23), (26,31), (44,70)],
        3: [(1,7), (8,25), (27,31), (38,70)],
        4: [(2,8), (9,26), (28,30), (37,70)],
        5: [(3,8), (10,26), (31,31), (37,70)],
        6: [(5,8), (11,25), (32,33), (34,70)],
        7: [(10,24), (32,32), (33,69)],
        8: [(10,23), (32,45), (46,66)],
        9: [(10,23), (33,44), (45,66)],
        10: [(10,23), (33,43), (44,63)],
        11: [(10,22), (32,38), (39,47), (48,64)],
        12: [(11,21), (33,53), (55,62)],
        13: [(11,17), (33,48), (49,53), (54,60)],
        14: [(13,16), (33,45), (49,52), (55,60)],
        15: [(11,11), (34,45), (50,51), (56,58)],
        16: [(34,44), (46,47), (56,58), (60,61)],
        17: [(34,45), (56,62)],
        18: [(35,45), (58,63)],
        19: [(17,22), (35,45), (58,64)],
        20: [(17,23), (37,44), (60,66)],
        21: [(18,23), (38,44), (64,68)],
        22: [(18,24), (38,44), (60,67)],
        23: [(18,24), (39,44), (46,46), (60,68)],
        24: [(18,24), (39,44), (46,46), (59,68)],
        25: [(18,23), (39,44), (46,46), (59,67)],
        26: [(18,23), (40,44), (60,66)],
        27: [(18,22), (40,43), (61,65)],
        28: [(18,22), (40,43), (61,65), (71,71)],
        29: [(19,21), (40,42), (62,64)],
        30: [(19,21), (40,42), (62,63), (71,72)],
        31: [(19,20), (63,63)],
        32: [(19,20), (70,71)],
        33: [(19,19)],
        34: [(19,19)],
        35: [(19,19)],
        36: [(19,19)],
    }

    cell_w_map = map_w / 73.0
    cell_h_map = map_h / 36.0

    for r in range(1, 37):
        spans = land_mask_spans.get(r, [])
        for (c_start, c_end) in spans:
            for c in range(c_start, c_end + 1):
                x1 = map_x + (c - 1) * cell_w_map
                y1 = map_y + (r - 1) * cell_h_map
                x2 = x1 + cell_w_map + 0.6
                y2 = y1 + cell_h_map + 0.6
                draw.rectangle([x1, y1, x2, y2], fill=LAND, outline=LAND)

    # Map Pins
    map_pins_data = {
        1: (30.5, 50.4, 6, -6),
        2: (84.9, 19.3, 6, 4),
        3: (30.7, 36.9, -8, -6),
        4: (139.7, 35.7, 0, -9),
        5: (-74.0, 40.7, -4, -9),
        6: (-80.2, 25.8, 0, -6),
        7: (46.7, 24.6, 4, 0),
        8: (13.4, 52.5, 8, -6),
        9: (-0.1, 51.5, -8, -8),
        10: (-70.7, -30.2, 0, -6),
        11: (4.35, 50.85, -12, 6),
        12: (33.8, -13.97, 6, 4),
        13: (139.7, 35.7, 13, 7),
        14: (-17.4, 14.7, -6, 0),
        15: (-77.0, 38.9, -12, -8),
        16: (4.35, 50.85, 10, 10),
        17: (8.9, 44.4, 6, 6),
        18: (2.35, 48.85, -10, -10),
        19: (165.5, -21.5, 0, -6),
        20: (-77.0, 38.9, 13, 8),
        21: (-77.0, 38.9, -14, 6),
        22: (-89.2, 13.7, 0, 6),
        23: (21.0, 52.2, 10, -4),
        24: (-122.2, 37.5, -6, -6),
        25: (77.2, 28.6, -8, -6),
        26: (4.9, 52.4, -14, -12),
        27: (-84.5, 39.1, 6, 8),
        28: (-77.0, 38.9, 0, -14),
        29: (-77.0, 38.9, 14, -6),
        30: (178.4, -18.1, 0, -6),
        31: (2.35, 48.85, 12, 8),
        32: (54.4, 24.5, 8, 6),
        33: (-77.0, 38.9, -6, 12),
    }

    scale_x = map_w / 300.0
    scale_y = map_h / 215.0

    pin_positions = []
    for num, (lon, lat, dx, dy) in map_pins_data.items():
        px = map_x + (lon + 168) / 360.0 * map_w + dx * scale_x
        py = map_y + (78 - lat) / 134.0 * map_h + dy * scale_y
        pin_positions.append((num, px, py))

    # Collision resolution for minimum 22px separation
    for _ in range(10):
        moved = False
        for i in range(len(pin_positions)):
            for j in range(i + 1, len(pin_positions)):
                num1, x1, y1 = pin_positions[i]
                num2, x2, y2 = pin_positions[j]
                dist = np.hypot(x1 - x2, y1 - y2)
                if dist < 22 and dist > 0:
                    angle = np.arctan2(y2 - y1, x2 - x1)
                    overlap = (22 - dist) / 2.0
                    x1 -= np.cos(angle) * overlap
                    y1 -= np.sin(angle) * overlap
                    x2 += np.cos(angle) * overlap
                    y2 += np.sin(angle) * overlap
                    pin_positions[i] = (num1, x1, y1)
                    pin_positions[j] = (num2, x2, y2)
                    moved = True
        if not moved:
            break

    pin_font = get_font(sans_bold_path, 11)
    for num, px, py in pin_positions:
        # Ensure inside map box
        px = max(map_x + 9, min(map_x + map_w - 9, px))
        py = max(map_y + 9, min(map_y + map_h - 9, py))
        draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=NAVY, outline=WHITE)
        num_str = str(num)
        bbox = pin_font.getbbox(num_str)
        nw = bbox[2] - bbox[0]
        nh = bbox[3] - bbox[1]
        draw.text((px - nw / 2, py - nh / 2 - 2), num_str, fill=WHITE, font=pin_font)
        drawn_numbers.add(num)

    # Briefs RIGHT: stories 16-33 in two columns inside x 392..996 (each 296 wide, 12px gutter)
    briefs_data = [
        (16, "Brussels", "Youth action day - living costs, housing, education"),
        (17, "Genoa", "Airport suspends flights after unidentified drones detected"),
        (18, "France", "One dead, 15 hurt in fire at 18-storey apartment block"),
        (19, "New Caledonia", "5.6-magnitude earthquake strikes near the islands"),
        (20, "Washington", "US sanctions Comancheros biker network and an 'Ndrangheta web"),
        (21, "Washington", "Trump announces posthumous pardon for baseball legend Pete Rose"),
        (22, "San Salvador", "Bukele registers to seek a third presidential term"),
        (23, "Warsaw", "Poland prepares a $50bn nuclear-power deal with US firms"),
        (24, "Menlo Park", "Meta revises 2030 climate targets amid AI expansion"),
        (25, "New Delhi", "India-Japan 2+2 - Japanese forces to train at Indian ranges"),
        (26, "Amsterdam", "'The Year of the Ghost' wins Best Film at IDFA festival"),
        (27, "Cincinnati", "Fiona the hippo dies at the zoo after swallowing a visitor's hat"),
        (28, "Washington", "White House taps Kirsten Davies as national cyber director"),
        (29, "Washington", "Senate nears vote on bill to speed power-plant reviews"),
        (30, "South Pacific", "Cyclone Xavier - bulletin 39 issued; warning levels unchanged"),
        (31, "Paris", "Macron backs Diallo's bid for the FIFA presidency"),
        (32, "Formula 1", "Verstappen backs F1 pressing on with Middle East races"),
        (33, "Washington", "US war with Iran has cost over $48bn so far, officials say"),
    ]

    # Verify no leading number pattern in brief text
    import re
    for num, place, summ in briefs_data:
        full_text = f"{place}: {summ}"
        assert not re.match(r"^\d+[\.\)]", full_text), f"Brief {num} contains leading number pattern"

    col_w = 296
    gutter = 12
    col1_x = 392
    col2_x = 392 + col_w + gutter

    brief_place_font = get_font(sans_bold_path, 10.5)
    brief_summ_font = get_font(sans_path, 10.5)
    badge_font = get_font(sans_bold_path, 9.5)

    # We have 18 briefs: 9 per column
    # Let's compute vertical positions dynamically or allocate evenly across content_bb_h
    col1_briefs = briefs_data[:9]
    col2_briefs = briefs_data[9:]

    def draw_brief_column(briefs_list, start_x, start_y, available_h):
        num_items = len(briefs_list)
        row_h = available_h / num_items
        for i, (num, place, summ) in enumerate(briefs_list):
            by = start_y + i * row_h + 2

            # Draw Badge: filled navy circle radius 8, white numeral
            bx = start_x + 8
            b_cy = by + 6
            draw.ellipse([bx - 8, b_cy - 8, bx + 8, b_cy + 8], fill=NAVY)
            num_str = str(num)
            bbox = badge_font.getbbox(num_str)
            nw = bbox[2] - bbox[0]
            nh = bbox[3] - bbox[1]
            draw.text((bx - nw / 2, b_cy - nh / 2 - 2), num_str, fill=WHITE, font=badge_font)

            # Text starting at bx + 14
            text_x = start_x + 22
            text_w = col_w - 22

            # Place lead + summary wrapped
            full_str = f"{place}: {summ}"
            # wrap lines manually or measure
            words = full_str.split()
            line1, line2 = "", ""
            overflow = False
            # bold the place part: we can draw place in bold, rest in normal sans
            # For simplicity, measure words
            for w in words:
                if not overflow:
                    test = (line1 + " " + w).strip()
                    if brief_summ_font.getbbox(test)[2] <= text_w:
                        line1 = test
                        continue
                    else:
                        overflow = True
                line2 = (line2 + " " + w).strip()

            draw.text((text_x, by), line1, fill=INK, font=brief_summ_font)
            if line2:
                draw.text((text_x, by + 11), line2, fill=INK, font=brief_summ_font)

            drawn_numbers.add(num)

    draw_brief_column(col1_briefs, col1_x, content_bb_y, content_bb_h)
    draw_brief_column(col2_briefs, col2_x, content_bb_y, content_bb_h)

    current_y += 306

    current_y += 6 # gap

    # 8. HOW SURE (height 16)
    hs_y = current_y
    hs_font = get_font(sans_path, 9.5)
    hs_bold_font = get_font(sans_bold_path, 9.5)

    # Draw chips and text
    hx = 28
    draw.text((hx, hs_y + 2), "HOW SURE -", fill=INK, font=hs_bold_font)
    hx += 70

    # CONFIRMED chip
    draw.rectangle([hx, hs_y + 2, hx + 58, hs_y + 13], fill=NAVY)
    draw.text((hx + 4, hs_y + 2), "CONFIRMED", fill=WHITE, font=hs_bold_font)
    hx += 62
    draw.text((hx, hs_y + 2), ": reported by wire services on the day -", fill=INK, font=hs_font)
    hx += 215

    # CLAIM chip (outline)
    draw.rectangle([hx, hs_y + 2, hx + 36, hs_y + 13], outline=NAVY, width=1)
    draw.text((hx + 4, hs_y + 2), "CLAIM", fill=NAVY, font=hs_bold_font)
    hx += 40
    draw.text((hx, hs_y + 2), ": one side's account or estimate -", fill=INK, font=hs_font)
    hx += 175

    # FORECAST chip (dashed outline / outline)
    draw.rectangle([hx, hs_y + 2, hx + 52, hs_y + 13], outline=NAVY, width=1)
    draw.text((hx + 3, hs_y + 2), "FORECAST", fill=NAVY, font=hs_bold_font)
    hx += 56
    draw.text((hx, hs_y + 2), ": scheduled or expected", fill=INK, font=hs_font)

    current_y += 16

    current_y += 6 # gap

    # 9. DATE CHECK box (height 136, drawn LAST)
    dc_y = current_y
    dc_h = 136
    draw.rectangle([28, dc_y, 996, dc_y + dc_h], fill=CREAM, outline=BORDER_COLOR, width=1)
    # 16px muted-red header bar
    draw.rectangle([28, dc_y, 996, dc_y + 16], fill=MUTED_RED)
    dc_head_font = get_font(sans_bold_path, 9)
    draw.text((36, dc_y + 2), "DATE CHECK - every story above is Friday 20 November 2026", fill=WHITE, font=dc_head_font)

    # Body: two groups in 4 columns x 5 rows of cells (19 cells total)
    left_out = [
        ("Riyadh", "PIF Tower strike", "Thu 19 Nov"),
        ("Hormuz", "tanker hit", "Thu 19 Nov"),
        ("ICJ", "Myanmar genocide", "Thu 19 Nov"),
        ("Shenzhen", "three-way summit", "Thu 19 Nov"),
        ("Tbilisi", "gas blast, 6 dead", "Thu 19 Nov"),
        ("GTA VI", "launch day itself", "Thu 19 Nov"),
        ("Anthropic", "Nasdaq debut", "Thu 19 Nov"),
        ("Wall St", "Thursday slide", "Thu 19 Nov"),
        ("Senate", "war-powers vote", "Thu 19 Nov"),
        ("ATP Finals", "semis line-up", "Thu 19 Nov"),
        ("Voyager 1", "one light-day", "Thu 19 Nov"),
        ("Bao", "star-merger paper", "Tue 18 Nov"),
        ("Nvidia", "record quarter", "Tue 17 Nov"),
        ("Siberia", "An-12 crash", "Tue 17 Nov"),
    ]
    not_yet = [
        ("COP31", "final deal", "into the weekend"),
        ("ATP Finals", "semis, Turin", "Sat 21 Nov"),
        ("BepiColombo", "at Mercury", "Sat 21 Nov"),
        ("Ebola trial", "first doses", "26 Nov"),
        ("OPEC+", "ministerials", "29 Nov"),
    ]

    dc_label_font = get_font(sans_bold_path, 9.5)
    dc_cell_font = get_font(sans_path, 9)
    dc_cell_bold_font = get_font(sans_bold_path, 9)

    body_y = dc_y + 18
    draw.text((36, body_y), "LEFT OUT - OTHER DAYS:", fill=NAVY, font=dc_label_font)
    body_y += 12

    # 4 columns for left out items
    col_width_dc = 230
    row_height_dc = 8
    for idx, (place, desc, date_str) in enumerate(left_out):
        c = idx % 4
        r = idx // 4
        cell_x = 36 + c * col_width_dc
        cell_y = body_y + r * row_height_dc
        item_text = f"{place} - {desc} - "
        draw.text((cell_x, cell_y), item_text, fill=INK, font=dc_cell_font)
        tw = dc_cell_font.getbbox(item_text)[2]
        draw.text((cell_x + tw, cell_y), date_str, fill=NAVY, font=dc_cell_bold_font)

        last_y = cell_y

    body_y += 4 * row_height_dc + 4
    draw.text((36, body_y), "NOT YET:", fill=NAVY, font=dc_label_font)
    body_y += 12

    for idx, (place, desc, date_str) in enumerate(not_yet):
        c = idx % 4
        r = idx // 4
        cell_x = 36 + c * col_width_dc
        cell_y = body_y + r * row_height_dc
        item_text = f"{place} - {desc} - "
        draw.text((cell_x, cell_y), item_text, fill=INK, font=dc_cell_font)
        tw = dc_cell_font.getbbox(item_text)[2]
        draw.text((cell_x + tw, cell_y), date_str, fill=NAVY, font=dc_cell_bold_font)

        last_y = cell_y

    # Assertions
    print(f"dc_y={dc_y}")
    print(f"body_y={body_y}")
    print(f"last_y={last_y}")
    assert len(left_out) == 14, f"Expected 14 left-out items, got {len(left_out)}"
    assert len(not_yet) == 5, f"Expected 5 not-yet items, got {len(not_yet)}"
    assert last_y + 9 <= 1018, f"Last item too low: {last_y + 9}"

    # Verify all 33 story numbers drawn
    assert drawn_numbers == set(range(1, 34)), f"Missing story numbers: {set(range(1, 34)) - drawn_numbers}"

    # Save output
    output_path = os.path.join(base_dir, "entry.png")
    img.save(output_path, "PNG")

    # Assertions on entry.png
    assert os.path.exists(output_path), "entry.png not created"
    assert img.size == (1024, 1024), f"Incorrect dimensions: {img.size}"
    file_size = os.path.getsize(output_path)
    assert file_size <= 1048576, f"File size too large: {file_size} bytes"

    with open(output_path, "rb") as fh:
        magic = fh.read(8)
    assert magic == b'\x89PNG\r\n\x1a\n', "Invalid PNG magic bytes"

    # Compute sha256
    sha256_hash = hashlib.sha256(open(output_path, "rb").read()).hexdigest()
    print(f"Successfully generated entry.png: size={file_size} bytes, sha256={sha256_hash}")

if __name__ == "__main__":
    main()
