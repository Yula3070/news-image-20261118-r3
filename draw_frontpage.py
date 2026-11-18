#!/usr/bin/env python3
"""The Day in World News - evening edition front page, Wednesday 18 Nov 2026.

A single-page newspaper (1024x1024) rendered entirely with PIL. Every
picture on the page is a flat vector shape drawn in this file: no photos,
no borrowed art, no external images. Output is deterministic: entry.png.

Composition, top to bottom:
  deep-green masthead with gold kickers -> 3 large illustrated leads
  -> 10 illustrated stories in two rows of five -> BY THE NUMBERS strip
  -> flat world atlas with numbered pins + ALSO list of 32 short stories
  -> sources footer. 45 stories in total, six continents.
"""

import os
from PIL import Image, ImageDraw, ImageFont

CANVAS_W = 1024
CANVAS_H = 1024
EDGE = 22
INNER_W = CANVAS_W - 2 * EDGE

# ---- palette ------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (28, 28, 26)
PINE = (16, 54, 41)
PINE_DARK = (10, 38, 29)
CREAM = (247, 240, 222)
CREAM_DIM = (214, 204, 178)
GILT = (208, 170, 64)
GILT_SOFT = (226, 205, 140)
RUBY = (178, 34, 34)
TEAL = (14, 106, 106)
SLATE = (112, 108, 96)
RULEC = (196, 186, 158)
SKY = (205, 225, 233)
SEA = (172, 203, 218)
LAND = (224, 216, 192)
LAND_LINE = (168, 156, 122)
NIGHT = (18, 30, 52)

REGION_TINT = {
    "AMERICAS": (34, 120, 60),
    "EUROPE": (36, 84, 160),
    "AFRICA": (176, 110, 32),
    "MIDDLE EAST": (178, 34, 34),
    "ASIA": (176, 132, 20),
    "OCEANIA": (14, 106, 106),
    "GLOBAL": (110, 70, 150),
    "SPACE": (70, 70, 110),
}

TYPE_DIR = "/usr/share/fonts/truetype/dejavu"


def load_typeface(name, size):
    """Load a DejaVu face by file name; fail loudly if it is missing."""
    path = os.path.join(TYPE_DIR, name)
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return ImageFont.truetype(path, size)


def head_face(size):
    return load_typeface("DejaVuSerif-Bold.ttf", size)


def head_plain(size):
    return load_typeface("DejaVuSerif.ttf", size)


def head_italic(size):
    # No serif italic face ships on this box; fall back to the book face.
    return load_typeface("DejaVuSerif.ttf", size)


def body_face(size):
    return load_typeface("DejaVuSans.ttf", size)


def body_strong(size):
    return load_typeface("DejaVuSans-Bold.ttf", size)


# ---- text plumbing ------------------------------------------------------


def split_text(canvas, text, face, width, limit=None):
    """Greedy word wrap by pixel width. Cuts with an ellipsis past limit."""
    words = text.split()
    out = []
    current = ""
    for word in words:
        joined = word if not current else current + " " + word
        if canvas.textlength(joined, font=face) <= width:
            current = joined
            continue
        if current:
            out.append(current)
        current = word
        while canvas.textlength(current, font=face) > width and len(current) > 1:
            half = len(current) // 2
            while half > 1 and canvas.textlength(current[:half], font=face) > width:
                half -= 1
            out.append(current[:half])
            current = current[half:]
    if current:
        out.append(current)
    if limit is not None and len(out) > limit:
        out = out[:limit]
        tail = out[-1]
        while out and canvas.textlength(tail + " …", font=face) > width:
            tail = tail[:-1]
        out[-1] = (tail + " …") if tail else "…"
    return out


def place_lines(canvas, x, y, lines, face, color, gap):
    """Draw stacked lines; return the y just below the last one."""
    for line in lines:
        canvas.text((x, y), line, font=face, fill=color)
        y += gap
    return y


def tracked_text(canvas, x, y, text, face, color, track=2):
    """Draw uppercase text with manual letter tracking; return end x."""
    cx = x
    for ch in text:
        canvas.text((cx, y), ch, font=face, fill=color)
        cx += canvas.textlength(ch, font=face) + (track if ch != " " else 4)
    return cx


def number_disc(canvas, cx, cy, num, radius=10, fill=RUBY):
    """A filled disc with a white number, used for story numbering."""
    canvas.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius], fill=fill
    )
    face = body_strong(11 if radius <= 10 else 13)
    label = str(num)
    tw = canvas.textlength(label, font=face)
    th = face.getbbox(label)[3] - face.getbbox(label)[1]
    canvas.text((cx - tw / 2, cy - th / 2 - 1), label, font=face, fill=(255, 255, 255))

# ---- world atlas --------------------------------------------------------
# Rough hand-authored continent outlines in (lon, lat). They only need to
# read as a world map at ~330 px wide; no coastline is traced from data.

CONTINENTS = {
    "north_america": [
        (-168, 66), (-150, 70), (-140, 70), (-128, 71), (-115, 73), (-100, 73),
        (-95, 80), (-85, 76), (-80, 73), (-75, 72), (-68, 62), (-60, 55),
        (-55, 52), (-60, 47), (-66, 45), (-70, 43), (-75, 36), (-80, 26),
        (-84, 30), (-90, 21), (-95, 17), (-100, 16), (-105, 20), (-110, 24),
        (-117, 33), (-124, 40), (-124, 49), (-132, 57), (-145, 60), (-158, 58),
        (-165, 60),
    ],
    "greenland": [
        (-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-20, 74),
        (-25, 77), (-35, 77), (-45, 76), (-55, 74), (-58, 70), (-55, 64),
    ],
    "south_america": [
        (-80, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
        (-35, -8), (-38, -15), (-48, -25), (-57, -38), (-65, -41), (-70, -52),
        (-73, -50), (-73, -37), (-70, -20), (-77, -12), (-80, -4),
    ],
    "europe": [
        (-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
        (10, 59), (5, 60), (10, 62), (18, 69), (25, 71), (30, 70), (40, 68),
        (45, 66), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40), (19, 42),
        (12, 44), (8, 44), (3, 43), (-2, 37), (-9, 37),
    ],
    "africa": [
        (-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (35, 28),
        (37, 22), (40, 15), (43, 11), (48, 11), (51, 10), (41, 0), (40, -10),
        (36, -18), (32, -26), (26, -34), (20, -35), (16, -28), (12, -18),
        (9, -1), (9, 4), (-8, 4), (-13, 8), (-16, 12), (-17, 15), (-16, 20),
        (-15, 27), (-10, 31),
    ],
    "asia": [
        (40, 68), (45, 66), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
        (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
        (160, 69), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
        (150, 59), (142, 54), (140, 46), (135, 43), (130, 42), (127, 40),
        (122, 38), (120, 32), (122, 28), (118, 25), (110, 21), (108, 18),
        (105, 10), (100, 8), (97, 15), (94, 17), (91, 22), (88, 22), (86, 20),
        (80, 15), (77, 8), (74, 20), (70, 23), (66, 25), (62, 25), (58, 26),
        (56, 27), (52, 28), (50, 29), (48, 30), (44, 29), (40, 31), (38, 35),
        (36, 36), (33, 36), (30, 36), (27, 37), (26, 40), (30, 44), (35, 50),
        (40, 55),
    ],
    "oceania": [
        (113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32),
        (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
        (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
        (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
        (118, -20),
    ],
}

LAT_TOP, LAT_BOTTOM = 78.0, -58.0


def project(lon, lat, box):
    """Equirectangular projection of lon/lat into a map box (x, y, w, h)."""
    x0, y0, w, h = box
    px = x0 + (lon + 180.0) / 360.0 * w
    py = y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOTTOM) * h
    return px, py


def render_atlas(canvas, box, featured, briefs):
    """Flat world map: sea, land polygons, numbered pins, brief dots."""
    x0, y0, w, h = box
    canvas.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA)
    for poly in CONTINENTS.values():
        pts = [project(lon, lat, box) for lon, lat in poly]
        canvas.polygon(pts, fill=LAND, outline=LAND_LINE)
    # graticule hint
    for lon in (-120, -60, 0, 60, 120):
        gx, _ = project(lon, 0, box)
        canvas.line([(gx, y0), (gx, y0 + h)], fill=(190, 212, 222), width=1)
    # brief dots first (under the numbered pins)
    for place in briefs:
        lon, lat, region = place[2], place[3], place[4]
        px, py = project(lon, lat, box)
        tint = REGION_TINT.get(region, SLATE)
        canvas.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=tint)
    # numbered pins for the 13 illustrated stories
    for story in featured:
        num = story["num"]
        if story.get("lon") is None:
            continue
        px, py = project(story["lon"], story["lat"], box)
        tint = REGION_TINT.get(story["region"], SLATE)
        canvas.ellipse([px - 9, py - 9, px + 9, py + 9], fill=tint,
                       outline=(255, 255, 255), width=2)
        face = body_strong(10)
        label = str(num)
        tw = canvas.textlength(label, font=face)
        canvas.text((px - tw / 2, py - 7), label, font=face, fill=(255, 255, 255))
    # Voyager lives off the map: pin in the corner, arrow pointing out
    vx, vy = x0 + w - 16, y0 + 14
    canvas.ellipse([vx - 9, vy - 9, vx + 9, vy + 9], fill=REGION_TINT["SPACE"],
                   outline=(255, 255, 255), width=2)
    face = body_strong(10)
    canvas.text((vx - 3, vy - 7), "3", font=face, fill=(255, 255, 255))
    canvas.line([(vx + 10, vy), (x0 + w + 2, vy)], fill=INK, width=1)
    canvas.text((vx - 64, vy + 11), "to Voyager 1 →", font=body_face(8),
                fill=INK)


# ---- flat illustrations (one per featured story) ------------------------
# Each sketch draws inside its own box (x, y, w, h). All shapes are
# original PIL primitives; nothing is traced or copied.


def sketch_gulf(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx, sy in [(0.18, 0.22), (0.42, 0.14), (0.66, 0.26), (0.85, 0.15),
                   (0.30, 0.32), (0.55, 0.36)]:
        canvas.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                       fill=(255, 255, 255))
    canvas.arc([x + 0.08 * w, y + 0.42 * h, x + 0.38 * w, y + 1.05 * h],
               200, 340, fill=(150, 190, 220), width=3)
    canvas.pieslice([x + 0.08 * w, y + 0.42 * h, x + 0.38 * w, y + 1.05 * h],
                    300, 340, fill=(150, 190, 220))
    canvas.rectangle([x, y + 0.66 * h, x + w, y + h], fill=(24, 64, 96))
    canvas.polygon([(x + 0.62 * w, y + 0.66 * h), (x + 0.70 * w, y + 0.52 * h),
                    (x + 0.78 * w, y + 0.66 * h)], fill=(90, 90, 90))
    canvas.rectangle([x + 0.68 * w, y + 0.44 * h, x + 0.72 * w, y + 0.54 * h],
                     fill=(140, 140, 140))
    for bx, by in [(0.30, 0.30), (0.52, 0.44), (0.80, 0.34)]:
        px, py = x + bx * w, y + by * h
        canvas.line([(px - 7, py), (px + 7, py)], fill=(255, 120, 60), width=2)
        canvas.line([(px, py - 7), (px, py + 7)], fill=(255, 120, 60), width=2)
        canvas.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 200, 80))
    canvas.text((x + 6, y + h - 15), "BAHRAIN · KUWAIT · THE GULF",
                font=body_strong(9), fill=(220, 225, 235))


def sketch_summit(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    for i, bx in enumerate([0.06, 0.16, 0.26, 0.36, 0.46, 0.56, 0.66, 0.76, 0.86]):
        bh = [0.30, 0.42, 0.26, 0.50, 0.34, 0.46, 0.30, 0.40, 0.24][i]
        canvas.rectangle([x + bx * w, y + h - 0.42 * h - bh * h,
                          x + (bx + 0.07) * w, y + h - 0.42 * h],
                         fill=(120, 118, 110))
    canvas.rectangle([x, y + h - 0.42 * h, x + w, y + h], fill=(210, 198, 168))
    canvas.ellipse([x + 0.22 * w, y + 0.52 * h, x + 0.78 * w, y + 0.82 * h],
                   fill=(176, 132, 20))
    canvas.ellipse([x + 0.30 * w, y + 0.56 * h, x + 0.70 * w, y + 0.76 * h],
                   fill=(232, 222, 196))
    for fx, cols in [(0.34, [(200, 40, 40), (255, 220, 60)]),
                     (0.47, [(180, 30, 30), (255, 255, 255), (40, 60, 160)]),
                     (0.60, [(255, 255, 255), (40, 60, 160), (200, 40, 40)])]:
        px = x + fx * w
        canvas.line([(px, y + 0.30 * h), (px, y + 0.56 * h)], fill=INK, width=2)
        for j, col in enumerate(cols):
            canvas.rectangle([px, y + (0.30 + j * 0.07) * h,
                              px + 0.09 * w, y + (0.37 + j * 0.07) * h], fill=col)
    canvas.text((x + 6, y + h - 15), "SHENZHEN · THREE-WAY TALKS THU",
                font=body_strong(9), fill=(60, 50, 30))


def sketch_voyager(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(10, 12, 26))
    for sx, sy in [(0.12, 0.20), (0.28, 0.10), (0.48, 0.26), (0.64, 0.12),
                   (0.80, 0.30), (0.92, 0.18), (0.36, 0.40), (0.58, 0.44)]:
        canvas.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                       fill=(255, 255, 255))
    canvas.ellipse([x - 0.02 * w, y + 0.52 * h, x + 0.22 * w, y + 0.98 * h],
                   fill=(50, 110, 180))
    canvas.ellipse([x + 0.02 * w, y + 0.62 * h, x + 0.14 * w, y + 0.86 * h],
                   fill=(90, 160, 90))
    for i in range(9):
        dx = x + (0.24 + i * 0.065) * w
        dy = y + (0.60 - i * 0.045) * h
        canvas.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=GILT)
    px, py = x + 0.86 * w, y + 0.16 * h
    canvas.polygon([(px - 12, py - 4), (px + 12, py - 4), (px + 4, py + 8),
                    (px - 4, py + 8)], fill=(200, 200, 210))
    canvas.rectangle([px - 3, py + 8, px + 3, py + 20], fill=(150, 150, 160))
    canvas.line([(px - 14, py + 20), (px + 14, py + 20)], fill=GILT, width=2)
    canvas.text((x + 0.52 * w, y + 0.30 * h), "1 LIGHT-DAY",
                font=body_strong(11), fill=GILT)
    canvas.text((x + 0.52 * w, y + 0.44 * h), "25.9 billion km",
                font=body_face(10), fill=(220, 220, 230))
    canvas.text((x + 6, y + h - 15), "EARTH · INTERSTELLAR SPACE · NASA",
                font=body_strong(9), fill=(200, 205, 220))


def sketch_kerch(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=SKY)
    canvas.rectangle([x, y + 0.62 * h, x + w, y + h], fill=(36, 90, 130))
    canvas.polygon([(x + 0.10 * w, y + 0.30 * h), (x + 0.50 * w, y + 0.12 * h),
                    (x + 0.90 * w, y + 0.30 * h), (x + 0.90 * w, y + 0.36 * h),
                    (x + 0.50 * w, y + 0.20 * h), (x + 0.10 * w, y + 0.36 * h)],
                   fill=(200, 200, 200))
    canvas.rectangle([x + 0.10 * w, y + 0.34 * h, x + 0.90 * w, y + 0.40 * h],
                     fill=(120, 120, 120))
    canvas.line([(x + 0.50 * w, y + 0.12 * h), (x + 0.50 * w, y + 0.40 * h)],
                fill=(90, 90, 90), width=2)
    canvas.polygon([(x + 0.56 * w, y + 0.40 * h), (x + 0.68 * w, y + 0.40 * h),
                    (x + 0.74 * w, y + 0.62 * h), (x + 0.62 * w, y + 0.62 * h)],
                   fill=(150, 150, 150))
    canvas.polygon([(x + 0.56 * w, y + 0.40 * h), (x + 0.62 * w, y + 0.40 * h),
                    (x + 0.60 * w, y + 0.52 * h)], fill=(90, 90, 90))
    for sx in (0.60, 0.66, 0.72, 0.78):
        canvas.arc([x + sx * w - 8, y + 0.60 * h, x + sx * w + 8, y + 0.74 * h],
                   180, 360, fill=(255, 255, 255), width=2)
    canvas.text((x + 6, y + h - 15), "KERCH STRAIT · 19 KM CROSSING",
                font=body_strong(9), fill=(20, 40, 60))


def sketch_alaska(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(226, 232, 226))
    pts = [(0.14, 0.30), (0.30, 0.18), (0.52, 0.16), (0.72, 0.22), (0.88, 0.34),
           (0.82, 0.52), (0.66, 0.60), (0.48, 0.72), (0.30, 0.66), (0.16, 0.52)]
    canvas.polygon([(x + px * w, y + py * h) for px, py in pts],
                   fill=(120, 160, 120), outline=(40, 90, 50))
    sx, sy = x + 0.44 * w, y + 0.40 * h
    canvas.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=RUBY)
    canvas.text((sx - 3, sy - 7), "★", font=body_strong(11), fill=(255, 255, 255))
    canvas.rectangle([x + 0.68 * w, y + 0.62 * h, x + 0.92 * w, y + 0.92 * h],
                     fill=(90, 70, 50))
    canvas.rectangle([x + 0.70 * w, y + 0.56 * h, x + 0.90 * w, y + 0.64 * h],
                     fill=(60, 45, 30))
    canvas.text((x + 0.70 * w, y + 0.68 * h), "✓", font=body_strong(20),
                fill=(255, 255, 255))
    canvas.rectangle([x + 0.06 * w, y + 0.10 * h, x + 0.42 * w, y + 0.22 * h],
                     fill=(36, 84, 160))
    canvas.rectangle([x + 0.06 * w, y + 0.24 * h, x + 0.34 * w, y + 0.36 * h],
                     fill=(178, 34, 34))
    canvas.text((x + 0.46 * w, y + 0.12 * h), "56 DEM", font=body_strong(11),
                fill=(36, 84, 160))
    canvas.text((x + 0.46 * w, y + 0.26 * h), "44 REP", font=body_strong(11),
                fill=(178, 34, 34))


def sketch_eu(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    canvas.rectangle([x, y, x + w, y + 0.52 * h], fill=(30, 60, 130))
    import math
    cx, cy, r = x + 0.26 * w, y + 0.26 * h, 0.17 * h
    for i in range(12):
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        canvas.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 80))
    canvas.rectangle([x + 0.58 * w, y + 0.08 * h, x + 0.92 * w, y + 0.24 * h],
                     fill=(40, 90, 170))
    canvas.rectangle([x + 0.58 * w, y + 0.24 * h, x + 0.92 * w, y + 0.40 * h],
                     fill=(240, 200, 60))
    canvas.text((x + 0.60 * w, y + 0.42 * h), "€45bn", font=head_face(20),
                fill=INK)
    canvas.text((x + 0.06 * w, y + 0.60 * h), "FOR 2027", font=body_strong(11),
                fill=SLATE)
    for i, bx in enumerate([0.08, 0.30, 0.52, 0.74]):
        canvas.ellipse([x + bx * w, y + 0.76 * h, x + (bx + 0.14) * w, y + 0.94 * h],
                       fill=GILT, outline=(150, 110, 20))
        canvas.text((x + (bx + 0.045) * w, y + 0.78 * h), "€",
                    font=body_strong(12), fill=(120, 85, 10))


def sketch_cyclone(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(206, 226, 232))
    canvas.polygon([(x + 0.55 * w, y), (x + w, y), (x + w, y + h),
                    (x + 0.72 * w, y + h), (x + 0.62 * w, y + 0.55 * h),
                    (x + 0.70 * w, y + 0.30 * h)], fill=(222, 214, 190))
    import math
    cx, cy = x + 0.38 * w, y + 0.52 * h
    for k in range(5):
        r0, r1 = 6 + k * 7, 12 + k * 7
        canvas.arc([cx - r1, cy - r1, cx + r1, cy + r1], 20 + k * 40,
                   200 + k * 40, fill=(20, 60, 110), width=3)
    canvas.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(20, 60, 110))
    canvas.line([(x + 0.60 * w, y + 0.30 * h), (x + 0.46 * w, y + 0.44 * h)],
                fill=RUBY, width=2)
    canvas.polygon([(x + 0.46 * w, y + 0.44 * h), (x + 0.42 * w, y + 0.40 * h),
                    (x + 0.42 * w, y + 0.48 * h)], fill=RUBY)
    canvas.text((x + 0.50 * w, y + 0.08 * h), "BAY OF BENGAL",
                font=body_strong(9), fill=(20, 60, 110))
    canvas.text((x + 0.50 * w, y + 0.20 * h), "LANDFALL 20 NOV",
                font=body_strong(9), fill=RUBY)


def sketch_gta(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(28, 20, 48))
    for sx, sy in [(0.15, 0.20), (0.35, 0.12), (0.60, 0.18), (0.82, 0.14),
                   (0.25, 0.34), (0.72, 0.32)]:
        canvas.ellipse([x + sx * w - 1, y + sy * h - 1, x + sx * w + 1, y + sy * h + 1],
                       fill=(255, 220, 120))
    canvas.ellipse([x + 0.62 * w, y + 0.08 * h, x + 0.98 * w, y + 0.44 * h],
                   fill=(255, 190, 90))
    canvas.ellipse([x + 0.66 * w, y + 0.12 * h, x + 0.94 * w, y + 0.40 * h],
                   fill=(255, 210, 130))
    canvas.rounded_rectangle([x + 0.14 * w, y + 0.46 * h, x + 0.58 * w, y + 0.82 * h],
                             radius=12, fill=(60, 45, 95), outline=(180, 160, 220))
    canvas.ellipse([x + 0.20 * w, y + 0.56 * h, x + 0.28 * w, y + 0.68 * h],
                   fill=(30, 20, 50))
    canvas.ellipse([x + 0.44 * w, y + 0.56 * h, x + 0.52 * w, y + 0.68 * h],
                   fill=(30, 20, 50))
    canvas.line([(x + 0.20 * w, y + 0.62 * h), (x + 0.28 * w, y + 0.62 * h)],
                fill=(220, 220, 230), width=2)
    canvas.line([(x + 0.24 * w, y + 0.56 * h), (x + 0.24 * w, y + 0.68 * h)],
                fill=(220, 220, 230), width=2)
    canvas.text((x + 0.62 * w, y + 0.52 * h), "VI", font=head_face(34),
                fill=(255, 220, 120))
    canvas.text((x + 6, y + h - 15), "MIDNIGHT LAUNCH",
                font=body_strong(9), fill=(220, 200, 240))


def sketch_sudan(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(238, 228, 205))
    pts = [(0.30, 0.10), (0.62, 0.08), (0.86, 0.22), (0.80, 0.48), (0.66, 0.70),
           (0.44, 0.86), (0.26, 0.66), (0.18, 0.38)]
    canvas.polygon([(x + px * w, y + py * h) for px, py in pts],
                   fill=(214, 190, 150), outline=(120, 90, 50))
    dx, dy = x + 0.52 * w, y + 0.42 * h
    canvas.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=RUBY)
    canvas.ellipse([x + 0.60 * w, y + 0.08 * h, x + 0.92 * w, y + 0.40 * h],
                   outline=INK, width=3)
    canvas.line([(x + 0.88 * w, y + 0.36 * h), (x + 0.98 * w, y + 0.50 * h)],
                fill=INK, width=3)
    canvas.rectangle([x + 0.06 * w, y + 0.62 * h, x + 0.38 * w, y + 0.92 * h],
                     fill=(255, 255, 255), outline=SLATE)
    for i in range(3):
        canvas.line([(x + 0.10 * w, y + (0.70 + i * 0.08) * h),
                     (x + 0.34 * w, y + (0.70 + i * 0.08) * h)],
                    fill=SLATE, width=2)
    canvas.text((x + 0.44 * w, y + 0.86 * h), "EL OBEID",
                font=body_strong(9), fill=RUBY)


def sketch_gaza(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(214, 224, 232))
    for i in range(6):
        lx = x + (0.08 + i * 0.15) * w
        canvas.line([(lx, y + 0.06 * h), (lx - 3, y + 0.22 * h)],
                    fill=(120, 150, 180), width=2)
    canvas.rectangle([x, y + 0.58 * h, x + w, y + h], fill=(70, 120, 160))
    for tx, tw, col in [(0.08, 0.24, (240, 235, 220)), (0.38, 0.28, (225, 220, 205)),
                        (0.70, 0.22, (240, 235, 220))]:
        canvas.polygon([(x + tx * w, y + 0.58 * h),
                        (x + (tx + tw / 2) * w, y + 0.30 * h),
                        (x + (tx + tw) * w, y + 0.58 * h)], fill=col,
                       outline=(140, 130, 110))
    canvas.rectangle([x + 0.42 * w, y + 0.68 * h, x + 0.60 * w, y + 0.88 * h],
                     fill=(255, 255, 255), outline=RUBY, width=2)
    canvas.line([(x + 0.51 * w, y + 0.72 * h), (x + 0.51 * w, y + 0.84 * h)],
                fill=RUBY, width=3)
    canvas.line([(x + 0.45 * w, y + 0.78 * h), (x + 0.57 * w, y + 0.78 * h)],
                fill=RUBY, width=3)
    canvas.text((x + 0.06 * w, y + 0.06 * h), "FOURTH WINTER OF WAR",
                font=body_strong(9), fill=(30, 60, 90))


def sketch_nvidia(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(18, 26, 18))
    cx, cy = x + 0.30 * w, y + 0.50 * h
    for dx in (-26, -14, 0, 14, 26):
        canvas.line([(cx + dx, cy - 26), (cx + dx, cy - 34)], fill=(120, 200, 90),
                    width=2)
        canvas.line([(cx + dx, cy + 26), (cx + dx, cy + 34)], fill=(120, 200, 90),
                    width=2)
    for dy in (-20, 0, 20):
        canvas.line([(cx - 26, cy + dy), (cx - 34, cy + dy)], fill=(120, 200, 90),
                    width=2)
        canvas.line([(cx + 26, cy + dy), (cx + 34, cy + dy)], fill=(120, 200, 90),
                    width=2)
    canvas.rectangle([cx - 26, cy - 26, cx + 26, cy + 26], fill=(30, 60, 30),
                     outline=(120, 200, 90), width=2)
    canvas.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], fill=(120, 200, 90))
    canvas.line([(x + 0.58 * w, y + 0.78 * h), (x + 0.68 * w, y + 0.60 * h),
                 (x + 0.76 * w, y + 0.66 * h), (x + 0.92 * w, y + 0.34 * h)],
                fill=(90, 220, 120), width=3)
    canvas.polygon([(x + 0.92 * w, y + 0.34 * h), (x + 0.86 * w, y + 0.34 * h),
                    (x + 0.92 * w, y + 0.44 * h)], fill=(90, 220, 120))
    canvas.text((x + 0.52 * w, y + 0.10 * h), "$115.8bn", font=head_face(16),
                fill=(140, 230, 140))
    canvas.text((x + 0.60 * w, y + 0.82 * h), "+103% YoY",
                font=body_strong(11), fill=(200, 220, 200))


def sketch_inflation(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(240, 234, 220))
    cx, cy = x + 0.26 * w, y + 0.50 * h
    canvas.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=GILT,
                   outline=(150, 110, 20), width=2)
    canvas.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=(150, 110, 20))
    canvas.text((cx - 11, cy - 17), "£", font=head_face(30), fill=(120, 85, 10))
    bars = [(0.52, 0.30, (150, 150, 150)), (0.64, 0.42, (150, 150, 150)),
            (0.76, 0.55, RUBY), (0.88, 0.68, RUBY)]
    for bx, bh, col in bars:
        canvas.rectangle([x + bx * w, y + h - 0.18 * h - bh * h,
                          x + (bx + 0.08) * w, y + h - 0.18 * h], fill=col)
    canvas.line([(x + 0.50 * w, y + 0.55 * h), (x + 0.96 * w, y + 0.14 * h)],
                fill=RUBY, width=3)
    canvas.polygon([(x + 0.96 * w, y + 0.14 * h), (x + 0.88 * w, y + 0.14 * h),
                    (x + 0.96 * w, y + 0.24 * h)], fill=RUBY)
    canvas.text((x + 0.52 * w, y + 0.06 * h), "3.5% → 3.6%",
                font=body_strong(11), fill=INK)


def sketch_gold(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(24, 22, 32))
    for bx, by in [(0.10, 0.62), (0.30, 0.62), (0.50, 0.62), (0.20, 0.38),
                   (0.40, 0.38), (0.30, 0.14)]:
        px, py = x + bx * w, y + by * h
        canvas.polygon([(px, py), (px + 0.16 * w, py),
                        (px + 0.13 * w, py + 0.20 * h),
                        (px + 0.03 * w, py + 0.20 * h)], fill=GILT,
                       outline=(150, 110, 20))
    canvas.line([(x + 0.68 * w, y + 0.30 * h), (x + 0.76 * w, y + 0.48 * h),
                 (x + 0.84 * w, y + 0.42 * h), (x + 0.94 * w, y + 0.66 * h)],
                fill=(230, 80, 80), width=3)
    canvas.polygon([(x + 0.94 * w, y + 0.66 * h), (x + 0.94 * w, y + 0.56 * h),
                    (x + 0.86 * w, y + 0.66 * h)], fill=(230, 80, 80))
    canvas.text((x + 0.60 * w, y + 0.06 * h), "$3,792", font=head_face(15),
                fill=(255, 220, 130))
    canvas.text((x + 0.66 * w, y + 0.74 * h), "AN OUNCE",
                font=body_strong(9), fill=(200, 200, 210))


SKETCHES = {
    "gulf": sketch_gulf,
    "summit": sketch_summit,
    "voyager": sketch_voyager,
    "kerch": sketch_kerch,
    "alaska": sketch_alaska,
    "eu": sketch_eu,
    "cyclone": sketch_cyclone,
    "gta": sketch_gta,
    "sudan": sketch_sudan,
    "gaza": sketch_gaza,
    "nvidia": sketch_nvidia,
    "inflation": sketch_inflation,
    "gold": sketch_gold,
}

# ---- the day's stories --------------------------------------------------
# Headlines and decks are written here, in my own words, from the day's
# reporting (Reuters, AP, ONS, IMD, NASA, UN, Amnesty). Verified facts:
# Peltola 144,302–131,844, Senate 56–44 (Reuters/AP); UK CPI 3.6% Oct,
# up from 3.5% (ONS); Russia 141 drones overnight, 126 downed (Ukr. Air
# Force); Kerch road span down, 2 killed (Aksyonov); Nvidia $115.8bn
# +103% (company); Cyclone Akvan landfall 20 Nov, 204,070 to evacuate
# (IMD); Voyager 1 one light-day, 25.9bn km (NASA); Knesset Kahana 66–52;
# S&P 500 −1.03% to 7,340.53, fourth straight fall; EU €45bn loan plan.

FEATURED = [
    {
        "num": 1, "region": "MIDDLE EAST", "topic": "IRAN WAR",
        "headline": "Bahrain and Kuwait intercept Iran's drones",
        "deck": "Iran says it aimed at a US radar in Bahrain; US jets hit a "
                "missile site on Qeshm. No damage.",
        "sketch": "gulf", "lon": 50.5, "lat": 26.2,
    },
    {
        "num": 2, "region": "ASIA", "topic": "SUMMIT",
        "headline": "Xi welcomes Trump to Shenzhen",
        "deck": "Xi meets him at the airport; three-way talks with Putin "
                "on Thursday.",
        "sketch": "summit", "lon": 114.1, "lat": 22.5,
    },
    {
        "num": 3, "region": "SPACE", "topic": "SCIENCE",
        "headline": "Voyager 1 passes one light-day from Earth",
        "deck": "NASA's probe passes 25.9 billion km away, a record; a "
                "command sent today reaches it tomorrow.",
        "sketch": "voyager", "lon": None, "lat": None,
    },
    {
        "num": 4, "region": "EUROPE", "topic": "UKRAINE WAR",
        "headline": "Kerch bridge span falls into the sea",
        "deck": "Second strike in two days downs the road arch; rail arch stands.",
        "sketch": "kerch", "lon": 36.5, "lat": 45.3,
    },
    {
        "num": 5, "region": "AMERICAS", "topic": "US POLITICS",
        "headline": "Democrats take Alaska's Senate seat",
        "deck": "Peltola unseats Sullivan, 144,302 votes to 131,844.",
        "sketch": "alaska", "lon": -152.0, "lat": 64.0,
    },
    {
        "num": 6, "region": "EUROPE", "topic": "UKRAINE AID",
        "headline": "EU proposes €45bn loan for Ukraine",
        "deck": "Two-thirds of a €70bn gap, repaid if Russia pays reparations.",
        "sketch": "eu", "lon": 4.4, "lat": 50.8,
    },
    {
        "num": 7, "region": "ASIA", "topic": "WEATHER",
        "headline": "Cyclone Akvan veers toward Odisha",
        "deck": "Landfall due 20 Nov between Puri and Narsapur; evacuations begin.",
        "sketch": "cyclone", "lon": 86.0, "lat": 19.8,
    },
    {
        "num": 8, "region": "GLOBAL", "topic": "GAMES",
        "headline": "GTA VI on sale, New Zealand first",
        "deck": "Launches roll west by time zone; 14.9m digital pre-orders.",
        "sketch": "gta", "lon": -74.0, "lat": 40.7,
    },
    {
        "num": 9, "region": "AFRICA", "topic": "SUDAN WAR",
        "headline": "Amnesty: RSF drones killed 37 in El Obeid",
        "deck": "Amnesty urges a war-crimes inquiry; RSF blames Sudan's army.",
        "sketch": "sudan", "lon": 30.2, "lat": 13.2,
    },
    {
        "num": 10, "region": "MIDDLE EAST", "topic": "GAZA",
        "headline": "Floods swamp Gaza's tents; WHO urges aid",
        "deck": "WHO asks for open aid routes as a fourth winter brings cold.",
        "sketch": "gaza", "lon": 34.5, "lat": 31.5,
    },
    {
        "num": 11, "region": "UNITED STATES", "topic": "BUSINESS",
        "headline": "Nvidia revenue doubles to $115.8bn",
        "deck": "Sales rose 103% on data-centre demand; Huang will not return.",
        "sketch": "nvidia", "lon": -122.0, "lat": 37.4,
    },
    {
        "num": 12, "region": "EUROPE", "topic": "ECONOMY",
        "headline": "UK inflation up to 3.6%, one-year high",
        "deck": "Fuel and tobacco tax pushed October CPI up from 3.5%.",
        "sketch": "inflation", "lon": -0.1, "lat": 51.5,
    },
    {
        "num": 13, "region": "AMERICAS", "topic": "MARKETS",
        "headline": "Gold slides to a one-year low",
        "deck": "Fed officials signal more rate rises; minutes due 19:00 GMT.",
        "sketch": "gold", "lon": 8.5, "lat": 47.4,
    },
]

# (place, brief, lon, lat, region) — 32 short stories, numbered 14–45.
BRIEFS = [
    ("Manila", "Trump hails 'biggest' Philippine trade deal", 121.0, 14.6, "ASIA"),
    ("Manila", "Quad leaders meet, first in two years", 121.3, 14.4, "ASIA"),
    ("Tokyo", "Takaichi makes first China visit as PM", 139.7, 35.7, "ASIA"),
    ("Ottawa", "Carney and Xi agree tariff relief", -75.7, 45.4, "AMERICAS"),
    ("Ulaanbaatar", "MPs to vote on president's offer to quit", 106.9, 47.9, "ASIA"),
    ("Colombo", "Sri Lanka all out for 98 against Pakistan", 79.9, 6.9, "ASIA"),
    ("Canberra", "Sanctions settler leader Daniella Weiss", 149.1, -35.3, "OCEANIA"),
    ("Berlin", "Germany pledges air defences, F-16 arms to Kyiv", 13.4, 52.5, "EUROPE"),
    ("Pristina", "Ex-president Thaçi gets 17 months", 21.0, 42.7, "EUROPE"),
    ("Belgrade", "A MiG-29 crashes near Belgrade", 20.5, 44.8, "EUROPE"),
    ("Kemerovo", "19 die in plane crash, media say", 86.1, 55.4, "EUROPE"),
    ("London", "UK hands US Army spy suspect to US custody", -0.1, 51.5, "EUROPE"),
    ("Paris", "Court suspends Paris school-protest ban", 2.35, 48.85, "EUROPE"),
    ("Maputo", "Opposition leader Mondlane on trial", 32.6, -25.9, "AFRICA"),
    ("Conakry", "Guinea jails 224 over illegal gold mining", -13.7, 9.6, "AFRICA"),
    ("Port Louis", "Mauritius sets UK Chagos deadline", 57.5, -20.2, "AFRICA"),
    ("Badme", "Ethiopia-Eritrea: artillery fire near Badme", 37.8, 14.7, "AFRICA"),
    ("Pretoria", "South Africa reprimands Nigeria's new envoy", 28.2, -25.7, "AFRICA"),
    ("Kinshasa", "Ebola adds 400–500 cases weekly", 15.3, -4.3, "AFRICA"),
    ("San Francisco", "Anthropic prices IPO; trades Thursday", -122.4, 37.8, "AMERICAS"),
    ("Washington", "No sign of cyberattack in outages", -77.0, 38.9, "AMERICAS"),
    ("Caracas", "Unions call 24-hour strike over pay", -66.9, 10.5, "AMERICAS"),
    ("Bogotá", "Economy shrinks 0.8% in Q3", -74.1, 4.7, "AMERICAS"),
    ("Asunción", "Attorney general quits before impeachment", -57.6, -25.3, "AMERICAS"),
    ("Lima", "Tumbles River passes red alert", -77.0, -12.0, "AMERICAS"),
    ("Antalya", "Ministers weigh divided draft in Antalya", 30.7, 36.9, "EUROPE"),
    ("Zurich", "FIFA: France's Diallo to challenge Infantino", 8.5, 47.4, "EUROPE"),
    ("Jerusalem", "Knesset elects Kahana as speaker, 66–52", 35.2, 31.8, "MIDDLE EAST"),
    ("New York", "S&P 500 slides for a fourth straight day", -74.0, 40.7, "AMERICAS"),
    ("Shenzhen", "APEC opens in Shenzhen with Xi's keynote", 114.1, 22.5, "ASIA"),
    ("Washington", "Measles status lost; PAHO ends 26-year run", -77.3, 38.7, "AMERICAS"),
    ("Dongola", "Archaeologists reach Old Dongola church floor", 30.5, 19.2, "AFRICA"),
]

# BY THE NUMBERS strip: (big figure, caption)
FIGURES = [
    ("141", "Russian drones fired at Ukraine overnight; 126 downed"),
    ("25.9bn km", "Voyager 1 from Earth: one light-day"),
    ("14.9m", "GTA VI digital pre-orders, Sensor Tower estimate"),
    ("56–44", "Senate split after Peltola win"),
]

# ---- page composition ---------------------------------------------------

LEAD_X = [EDGE, 353, 684]
LEAD_W = 318
LEAD_Y = 150
LEAD_ILL_H = 124

MID_X = [EDGE, 220, 419, 617, 816]
MID_W = 186
MID_Y1 = 400
MID_Y2 = 560
MID_H = 152
MID_ILL_H = 68

STATS_Y = 720
BOTTOM_Y = 778
FOOTER_Y = 1002


def tracked_width(canvas, text, face, track=2):
    total = 0.0
    for ch in text:
        total += canvas.textlength(ch, font=face) + (track if ch != " " else 4)
    return total


def compose_masthead(canvas):
    canvas.rectangle([0, 0, CANVAS_W, 138], fill=PINE)
    canvas.rectangle([0, 138, CANVAS_W, 141], fill=GILT)
    kicker = body_strong(13)
    tracked_text(canvas, EDGE, 16, "THE DAY IN WORLD NEWS", kicker, GILT, 2)
    right = "45 STORIES · 6 CONTINENTS · ONE DAY"
    rw = tracked_width(canvas, right, kicker, 2)
    tracked_text(canvas, CANVAS_W - EDGE - rw, 16, right, kicker, GILT, 2)
    title = head_face(54)
    canvas.text((EDGE, 42), "Wednesday 18 November 2026", font=title, fill=CREAM)
    canvas.text((EDGE, 108),
                "Every story on this page happened, or was first reported, on this day.",
                font=head_italic(14), fill=CREAM_DIM)


def compose_tag(canvas, x, y, story, small=False):
    number_disc(canvas, x + 10, y + 10, story["num"], 10 if small else 11)
    tint = REGION_TINT.get(story["region"], SLATE)
    label = story["region"] + " · " + story["topic"]
    canvas.text((x + 24, y + 1), label, font=body_strong(10 if small else 11),
                fill=tint)


def compose_lead(canvas, story, x):
    SKETCHES[story["sketch"]](canvas, x, LEAD_Y, LEAD_W, LEAD_ILL_H)
    canvas.rectangle([x, LEAD_Y, x + LEAD_W, LEAD_Y + LEAD_ILL_H],
                     outline=RULEC)
    ty = LEAD_Y + LEAD_ILL_H + 6
    compose_tag(canvas, x, ty, story)
    hy = ty + 24
    lines = split_text(canvas, story["headline"], head_face(24), LEAD_W, 2)
    place_lines(canvas, x, hy, lines, head_face(24), INK, 28)
    dy = hy + 28 * len(lines) + 4
    dlines = split_text(canvas, story["deck"], body_face(12), LEAD_W, 2)
    place_lines(canvas, x, dy, dlines, body_face(12), (60, 58, 50), 15)


def compose_card(canvas, story, x, y0):
    SKETCHES[story["sketch"]](canvas, x, y0, MID_W, MID_ILL_H)
    canvas.rectangle([x, y0, x + MID_W, y0 + MID_ILL_H], outline=RULEC)
    ty = y0 + MID_ILL_H + 4
    compose_tag(canvas, x, ty, story, small=True)
    hy = ty + 22
    lines = split_text(canvas, story["headline"], head_face(14), MID_W, 2)
    place_lines(canvas, x, hy, lines, head_face(14), INK, 17)
    dy = hy + 17 * len(lines) + 2
    dlines = split_text(canvas, story["deck"], body_face(10.5), MID_W, 2)
    place_lines(canvas, x, dy, dlines, body_face(10.5), (60, 58, 50), 12.5)


def compose_figures(canvas):
    canvas.line([(EDGE, STATS_Y), (CANVAS_W - EDGE, STATS_Y)], fill=RULEC, width=1)
    canvas.line([(EDGE, STATS_Y + 50), (CANVAS_W - EDGE, STATS_Y + 50)],
                fill=RULEC, width=1)
    canvas.text((EDGE, STATS_Y + 6), "BY THE", font=body_strong(12), fill=RUBY)
    canvas.text((EDGE, STATS_Y + 22), "NUMBERS", font=body_strong(12), fill=RUBY)
    sx = 150
    sw = 205
    for big, cap in FIGURES:
        canvas.text((sx, STATS_Y + 2), big, font=head_face(19), fill=INK)
        clines = split_text(canvas, cap, body_face(10), sw - 8, 2)
        place_lines(canvas, sx, STATS_Y + 26, clines, body_face(10),
                    (60, 58, 50), 11)
        sx += sw
    canvas.line([(sx, STATS_Y + 4), (sx, STATS_Y + 46)], fill=RULEC, width=1)


def compose_bottom(canvas):
    canvas.text((EDGE, BOTTOM_Y), "WHERE IT HAPPENED",
                font=body_strong(11), fill=INK)
    map_box = (EDGE, BOTTOM_Y + 18, 326, 158)
    render_atlas(canvas, map_box, FEATURED, BRIEFS)
    canvas.rectangle([map_box[0], map_box[1],
                      map_box[0] + map_box[2], map_box[1] + map_box[3]],
                     outline=RULEC)
    legend_rows = [[("Americas", (34, 120, 60)), ("Europe", (36, 84, 160)),
                    ("Africa", (176, 110, 32)), ("Middle East", (178, 34, 34))],
                   [("Asia", (176, 132, 20)), ("Oceania", (14, 106, 106)),
                    ("Global", (110, 70, 150))]]
    for ri, row in enumerate(legend_rows):
        ly = BOTTOM_Y + 182 + ri * 12
        lx = EDGE
        for name, tint in row:
            canvas.ellipse([lx, ly + 2, lx + 7, ly + 9], fill=tint)
            canvas.text((lx + 10, ly), name, font=body_face(9), fill=INK)
            lx += 10 + canvas.textlength(name, font=body_face(9)) + 8
    canvas.text((EDGE, BOTTOM_Y + 208),
                "Numbered pins: stories 1–13 · dots: briefs 14–45.",
                font=body_face(9), fill=SLATE)
    ax = 362
    canvas.text((ax, BOTTOM_Y), "ALSO ON WEDNESDAY 18 NOVEMBER — 32 MORE STORIES",
                font=body_strong(11), fill=INK)
    col_w = 312
    col_x = [ax, ax + 328]
    face = body_face(10)
    num_face = body_strong(10)
    place_face = body_strong(10)
    for i, item in enumerate(BRIEFS):
        col = 0 if i < 16 else 1
        row = i % 16
        x = col_x[col]
        y = BOTTOM_Y + 20 + row * 12.5
        place, text = item[0], item[1]
        num = str(14 + i)
        canvas.text((x, y), num, font=num_face, fill=RUBY)
        nx = x + canvas.textlength(num + " ", font=num_face)
        canvas.text((nx, y), place + ": ", font=place_face, fill=INK)
        tx = nx + canvas.textlength(place + ": ", font=place_face)
        canvas.text((tx, y), text, font=face, fill=(60, 58, 50))


def compose_footer(canvas):
    canvas.text((EDGE, FOOTER_Y),
                "Every story on this page was reported on Wednesday 18 November 2026; "
                "disputed claims are attributed.",
                font=body_face(9.5), fill=SLATE)
    canvas.text((EDGE, FOOTER_Y + 12),
                "Sources: Reuters, AP, AFP, BBC, Al Jazeera, ONS, IMD, NASA, UN, "
                "Amnesty. Original drawings.",
                font=body_face(9.5), fill=SLATE)


def render_frontpage():
    page = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
    canvas = ImageDraw.Draw(page)
    compose_masthead(canvas)
    for story, x in zip(FEATURED[:3], LEAD_X):
        compose_lead(canvas, story, x)
    canvas.line([(EDGE, 392), (CANVAS_W - EDGE, 392)], fill=RULEC, width=1)
    for story, x in zip(FEATURED[3:8], MID_X):
        compose_card(canvas, story, x, MID_Y1)
    for story, x in zip(FEATURED[8:13], MID_X):
        compose_card(canvas, story, x, MID_Y2)
    compose_figures(canvas)
    compose_bottom(canvas)
    compose_footer(canvas)
    return page


def check_fits():
    """Measure every wrapped block; warn about anything that overflows."""
    meter = Image.new("RGB", (4, 4))
    canvas = ImageDraw.Draw(meter)
    bad = False
    for story in FEATURED[:3]:
        n = len(split_text(canvas, story["headline"], head_face(24), LEAD_W, 99))
        if n > 2:
            print(f"OVERFLOW lead headline #{story['num']}: {n} lines")
            bad = True
        n = len(split_text(canvas, story["deck"], body_face(12), LEAD_W, 99))
        if n > 2:
            print(f"OVERFLOW lead deck #{story['num']}: {n} lines")
            bad = True
    for story in FEATURED[3:]:
        n = len(split_text(canvas, story["headline"], head_face(14), MID_W, 99))
        if n > 2:
            print(f"OVERFLOW card headline #{story['num']}: {n} lines")
            bad = True
        n = len(split_text(canvas, story["deck"], body_face(10.5), MID_W, 99))
        if n > 2:
            print(f"OVERFLOW card deck #{story['num']}: {n} lines")
            bad = True
    for i, item in enumerate(BRIEFS):
        total = (
            canvas.textlength(str(14 + i) + " ", font=body_strong(10))
            + canvas.textlength(item[0] + ": ", font=body_strong(10))
            + canvas.textlength(item[1], font=body_face(10))
        )
        if total > 312:
            print(f"OVERFLOW also #{14 + i}: {total:.0f}px > 312px")
            bad = True
    title_w = canvas.textlength("Wednesday 18 November 2026", font=head_face(54))
    if title_w > INNER_W:
        print(f"OVERFLOW masthead title: {title_w:.0f}px")
        bad = True
    if not bad:
        print("fits: all blocks within their boxes")
    return not bad


if __name__ == "__main__":
    import hashlib

    ok = check_fits()
    page = render_frontpage()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    page.save(out)
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote {out} sha256={digest} fits_ok={ok}")
