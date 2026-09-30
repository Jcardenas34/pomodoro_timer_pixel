"""Procedural 8-bit city scenes in the Mt Fuji style (320x180, limited palettes).

Composition: the flip clock covers roughly x 50..270, y 45..135 of the scene,
so each landmark stands on a side third (or rises above the clock) instead of
sitting dead center.

Each generator returns (image, meta). meta carries the sprite ground band
(shared with Fuji) and the frontend particle `effect` for that city.
"""

from __future__ import annotations

import math

from PIL import Image

from .paint import GROUND_META, PATH_TOP, W, Canvas


def _meta(effect: str) -> dict:
    return {**GROUND_META, "effect": effect}


# --- Los Angeles: golden hour, Hollywood sign, Griffith Observatory, palms ----
def los_angeles() -> tuple[Image.Image, dict]:
    c = Canvas(90028)
    sky = [(58, 48, 110), (122, 58, 118), (200, 86, 104), (244, 130, 90), (255, 178, 96), (255, 216, 140)]
    c.sky(sky, 130)
    c.sun(232, 34, 16, (255, 240, 170), (255, 196, 90))
    c.cloud(30, 40, 42, (255, 190, 150), (230, 130, 120))
    c.cloud(110, 20, 30, (255, 190, 150), (230, 130, 120))

    far, near = (132, 78, 108), (96, 58, 90)
    # Santa Monica Mountains / Hollywood Hills, Mt Lee higher on the left.
    c.ridge(lambda x: 96 + 9 * math.sin(x / 31 + 1) + 4 * math.sin(x / 11) - 20 * math.exp(-((x - 28) / 30) ** 2),
            142, far)
    c.text("HOLLYWOOD", 5, 91, (244, 238, 222))
    def near_ridge(x: float) -> float:
        return 120 + 5 * math.sin(x / 19) - 24 * math.exp(-((x - 284) / 34) ** 2)

    c.ridge(near_ridge, 142, near)
    # Griffith Observatory seated on the near ridge's crest.
    wall, shade, dome = (238, 226, 204), (196, 176, 160), (62, 86, 92)
    ox = 284
    b = int(near_ridge(ox)) + 2
    c.rect(ox - 19, b - 8, ox + 19, b, wall)
    c.rect(ox - 19, b - 2, ox + 19, b, shade)
    for x in range(ox - 17, ox + 17, 4):
        c.put(x, b - 5, shade)
    c.disc(ox, b - 9, 7, dome)
    c.rect(ox - 7, b - 9, ox + 8, b - 8, wall)
    c.disc(ox - 16, b - 7, 3, dome)
    c.disc(ox + 16, b - 7, 3, dome)
    c.put(ox, b - 17, (255, 236, 150))

    # Low city strip with evening lights.
    city, lit = (70, 46, 80), (255, 200, 110)
    for x0 in range(0, W, 9):
        top = 128 - c.rng.randint(0, 8)
        c.rect(x0, top, x0 + 8, 142, city)
        c.windows(x0 + 1, top + 2, x0 + 7, 141, lit, city, 0.3, 2, 3, 1, 1)

    c.ground(142, (96, 128, 64), (132, 160, 80), (62, 92, 52), (206, 184, 160), (228, 208, 182), "pavement")
    trunk, frond, frond2 = (52, 36, 62), (38, 30, 58), (70, 48, 84)
    for x, h in ((56, 72), (156, 92), (212, 76), (248, 84), (312, 90)):
        c.palm(x, 158, h, trunk, frond, frond2)
    return c.img, _meta("jacaranda")


# --- Bologna: warm evening, Due Torri, terracotta roofs, porticoes ---------
def bologna() -> tuple[Image.Image, dict]:
    c = Canvas(40121)
    sky = [(44, 42, 96), (96, 60, 122), (172, 82, 112), (230, 122, 92), (255, 170, 104), (252, 210, 150)]
    c.sky(sky, 140)
    c.cloud(40, 30, 36, (255, 196, 160), (220, 130, 120))
    c.cloud(170, 30, 42, (255, 196, 160), (220, 130, 120))
    brick, brick_lit, brick_dark = (156, 72, 52), (196, 104, 66), (112, 50, 44)

    # Torre degli Asinelli: tall, slim, battlemented, with a lantern.
    ax = 262
    for y in range(22, 132):
        half = 5 + (y - 22) // 40
        c.rect(ax - half, y, ax, y + 1, brick_dark)
        c.rect(ax, y, ax + half, y + 1, brick_lit)
    c.rect(ax - 7, 24, ax + 7, 28, brick)
    for x in range(ax - 7, ax + 7, 3):
        c.rect(x, 21, x + 2, 24, brick)
    c.rect(ax - 2, 12, ax + 2, 21, brick_dark)
    c.rect(ax - 1, 9, ax + 1, 12, brick)
    for y in range(36, 124, 14):
        c.rect(ax - 1, y, ax + 1, y + 3, (60, 30, 30))
    # Torre Garisenda: shorter and visibly leaning.
    for y in range(68, 132):
        lean = (132 - y) // 9
        c.rect(ax + 13 + lean, y, ax + 19 + lean, y + 1, brick_dark)
        c.rect(ax + 19 + lean, y, ax + 25 + lean, y + 1, brick)
    c.rect(ax + 20, 68, ax + 32, 71, brick_dark)

    # Terracotta roofs in two rows.
    roof, roof_dark = (206, 96, 62), (160, 70, 52)
    walls = [(226, 164, 96), (206, 124, 74), (232, 186, 120), (190, 100, 70)]
    for row, (base, h) in enumerate(((126, 14), (140, 12))):
        x = -6 + row * 9
        while x < W:
            w = c.rng.randint(18, 30)
            peak = base - h - c.rng.randint(0, 6)
            c.rect(x, peak + 5, x + w, 158, c.rng.choice(walls))
            c.poly([(x - 2, peak + 6), (x + w // 2, peak), (x + w + 1, peak + 6)], roof)
            c.line(x - 2, peak + 6, x + w + 1, peak + 6, roof_dark)
            c.windows(x + 3, peak + 9, x + w - 2, 150, (255, 206, 120), (120, 70, 50), 0.35, 5, 7, 2, 3)
            x += w + 1
    # Porticoes: a continuous arcade along the street, lamps glowing inside.
    arcade, pillar, glow = (86, 46, 40), (220, 150, 90), (255, 210, 120)
    c.rect(0, 140, W, 158, pillar)
    for x in range(2, W, 14):
        c.rect(x, 146, x + 10, 158, arcade)
        c.disc(x + 5, 146, 5, arcade)
        c.put(x + 5, 145, glow)
        c.rect(x + 4, 147, x + 7, 149, glow)
    c.rect(0, 140, W, 142, (176, 108, 72))

    c.ground(156, (150, 110, 88), (176, 134, 104), (110, 80, 66), (140, 102, 84), (118, 84, 70), "cobble")
    return c.img, _meta("leaves")


# --- Paris: dusk, lit Eiffel Tower, Haussmann rooftops, the Seine -----------
def paris() -> tuple[Image.Image, dict]:
    c = Canvas(75007)
    sky = [(20, 24, 62), (40, 40, 102), (80, 60, 132), (150, 80, 142), (228, 120, 130), (255, 170, 132)]
    c.sky(sky, 140)
    c.stars(40, 40, [(240, 230, 255), (180, 180, 230)])
    c.moon(48, 26, 5, (250, 240, 210), (220, 205, 180))
    iron, gold = (48, 36, 72), (255, 204, 92)

    # Eiffel Tower: flared legs, two platforms, arch between the legs, lights on its edges.
    tx, top, base = 268, 12, 140

    def half(y: float) -> float:
        return 1 + 27 * ((y - top) / (base - top)) ** 2.3

    for y in range(top, base):
        h = half(y)
        c.rect(tx - h, y, tx + h + 1, y + 1, iron)
        # Lattice: hollow out the middle of the upper and lower sections.
        if y > 40 and h > 3 and (y % 4 == 0):
            c.rect(tx - h + 2, y, tx + h - 1, y + 1, c.get(tx + 44, y))
        if y % 2 == 0:
            c.put(tx - h, y, gold)
            c.put(tx + h, y, gold)
    for py, extra in ((70, 3), (98, 4)):
        c.rect(tx - half(py) - extra, py, tx + half(py) + extra + 1, py + 2, iron)
        for x in range(int(tx - half(py) - extra), int(tx + half(py) + extra + 1), 2):
            c.put(x, py, gold)
    for y in range(110, base):
        r = 14
        for x in range(tx - r, tx + r + 1):
            if (x - tx) ** 2 + ((y - base) * 1.4) ** 2 <= r * r:
                c.put(x, y, c.get(tx + 44, y))
    c.rect(tx - 1, top - 5, tx + 1, top, iron)
    c.put(tx, top - 6, (255, 250, 220))

    # Haussmann blocks: stone fronts, blue-grey mansard roofs, warm windows.
    stone, stone_dark, mansard = (132, 118, 146), (100, 90, 122), (70, 72, 112)
    for x0, x1, h in ((0, 58, 34), (58, 112, 28), (112, 170, 36), (170, 234, 30)):
        t = 140 - h
        c.rect(x0, t, x1, 140, stone if x0 % 2 == 0 else stone_dark)
        c.poly([(x0, t), (x0 + 3, t - 7), (x1 - 3, t - 7), (x1, t)], mansard)
        for x in range(x0 + 5, x1 - 4, 9):
            c.rect(x, t - 5, x + 2, t - 1, (255, 214, 130))
            c.rect(x + 2, t - 11, x + 3, t - 7, stone_dark)  # chimney pots
        c.windows(x0 + 3, t + 3, x1 - 2, 138, (255, 212, 124), (60, 58, 92), 0.55, 5, 6, 2, 3)
        c.rect(x0, t + 11, x1, t + 12, stone_dark)  # wrought-iron balcony line

    # The Seine with the tower's golden reflection.
    c.water(140, 150, (38, 46, 100), (80, 86, 150))
    c.reflect(140, 150, tx - 8, tx + 9, gold, taper=1)
    for x in range(10, 232, 23):
        c.reflect(140, 148, x, x + 3, (255, 212, 124))
    c.ground(150, (96, 90, 112), (122, 116, 138), (70, 66, 90), (130, 120, 132), (104, 96, 112), "cobble")
    # Quay lamps.
    for x in range(30, W, 70):
        c.rect(x, 140, x + 1, 158, (30, 28, 44))
        c.rect(x - 1, 138, x + 2, 141, gold)
    return c.img, _meta("leaves")


# --- Geneva: bright morning, Jet d'Eau, Lac Leman, the Alps -----------------
def geneva() -> tuple[Image.Image, dict]:
    c = Canvas(1201)
    sky = [(84, 150, 226), (112, 176, 238), (150, 200, 244), (196, 224, 250)]
    c.sky(sky, 118)
    c.cloud(20, 30, 40, (255, 255, 255), (214, 228, 246))
    c.cloud(190, 18, 36, (255, 255, 255), (214, 228, 246))
    alp, snow, snow_shade = (150, 164, 206), (252, 252, 255), (206, 216, 240)

    def alps(x: int) -> float:
        # Jagged range with Mont Blanc's broad dome on the left.
        return (84 + 8 * abs(math.sin(x / 13)) + 5 * abs(math.sin(x / 5 + 1))
                - 30 * math.exp(-((x - 40) / 34) ** 2))

    for x in range(W):
        top = int(alps(x))
        for y in range(top, 118):
            c.put(x, y, snow if y < top + 8 + (x % 5) else alp)
            if y < top + 8 and (x // 3) % 2 and y > top + 2:
                c.put(x, y, snow_shade)
    c.ridge(lambda x: 104 + 6 * math.sin(x / 27 + 2) + 3 * math.sin(x / 8), 118, (84, 126, 118))
    # Lake with a bright shimmer.
    c.water(116, 148, (54, 108, 182), (132, 184, 236))
    # Jet d'Eau: jetty, plume, and wind-blown spray crown.
    jx = 276
    c.rect(jx - 30, 130, jx + 6, 133, (206, 198, 180))
    c.put(jx, 129, (255, 60, 60))  # the little lighthouse
    plume, plume_shade = (250, 252, 255), (196, 222, 246)
    for y in range(22, 130):
        w = 1 + (130 - y) // 40
        c.rect(jx - w, y, jx + w + 1, y + 1, plume)
        c.put(jx + w, y, plume_shade)
    for i in range(160):
        a = c.rng.random()
        x = jx + a * 34 + c.rng.randint(-4, 4)
        y = 24 + a * 80 + c.rng.randint(-6, 6) - 20 * (1 - a) ** 2
        c.put(x, y, plume if c.rng.random() < 0.5 else plume_shade)
    c.dither_rect(jx - 6, 118, jx + 12, 130, plume_shade, (54, 108, 182))
    # Sailboats.
    for x, y in ((60, 136), (110, 128), (220, 138)):
        c.poly([(x, y), (x, y - 9), (x + 6, y)], (255, 255, 255))
        c.rect(x - 3, y, x + 8, y + 2, (120, 70, 50))
    # Lakeside promenade with flower beds.
    c.ground(148, (84, 158, 84), (122, 196, 104), (56, 118, 66), (214, 206, 190), (236, 230, 218), "pavement")
    for x in range(0, W, 3):
        for y in (150, 153, 156):
            if c.rng.random() < 0.5:
                c.put(x + c.rng.randint(0, 2), y, c.rng.choice([(236, 64, 80), (255, 210, 60), (255, 255, 255)]))
    return c.img, {**_meta("mist"), "effectOrigin": [jx, 24]}


# --- Uppsala: blue winter twilight, the cathedral's twin spires, snow ---------
def uppsala() -> tuple[Image.Image, dict]:
    c = Canvas(75105)
    sky = [(12, 16, 42), (24, 32, 72), (40, 52, 104), (72, 80, 142), (140, 112, 172), (220, 152, 172)]
    c.sky(sky, 138)
    c.stars(70, 70, [(255, 255, 255), (170, 190, 240)])
    c.moon(32, 26, 6, (246, 244, 226), (210, 208, 196))
    brick, brick_dark, spire, snow = (150, 62, 52), (108, 42, 42), (44, 54, 70), (230, 236, 250)
    lit = (255, 204, 124)

    # Hill with Uppsala Castle on the left.
    c.ridge(lambda x: 116 - 16 * math.exp(-((x - 50) / 50) ** 2) + 2 * math.sin(x / 7), 140, (60, 64, 110))
    c.rect(22, 90, 80, 104, (206, 128, 132))
    c.disc(24, 92, 6, (206, 128, 132))
    c.disc(78, 92, 6, (206, 128, 132))
    c.poly([(18, 88), (24, 80), (30, 88)], (60, 50, 80))
    c.poly([(72, 88), (78, 80), (84, 88)], (60, 50, 80))
    c.windows(30, 94, 72, 102, lit, (140, 80, 90), 0.5, 5, 4, 2, 2)

    # Cathedral: nave with gothic windows, twin west towers, tall slate spires.
    c.rect(180, 104, 262, 140, brick)
    c.poly([(178, 104), (221, 88), (264, 104)], (60, 50, 70))
    c.line(178, 104, 221, 88, snow)
    c.line(221, 88, 264, 104, snow)
    for x in range(188, 258, 10):
        c.rect(x, 112, x + 4, 128, lit)
        c.disc(x + 1.5, 112, 2, lit)
    for tx in (262, 280):
        c.rect(tx, 70, tx + 14, 140, brick)
        c.rect(tx + 10, 70, tx + 14, 140, brick_dark)
        c.rect(tx + 5, 80, tx + 9, 92, lit)
        c.disc(tx + 6.5, 80, 2, lit)
        c.poly([(tx - 1, 70), (tx + 7, 10), (tx + 15, 70)], spire)
        c.line(tx + 7, 10, tx + 15, 70, (70, 84, 104))
        c.put(tx + 7, 8, (255, 214, 90))
        c.put(tx + 7, 9, (255, 214, 90))
    c.rect(274, 118, 280, 140, brick_dark)
    c.rect(272, 124, 282, 140, (80, 40, 40))  # west portal
    c.disc(277, 124, 5, (80, 40, 40))

    # Snowy pines and houses along the Fyris.
    for x in range(300, W, 9):
        c.pine(x, 142, 14 + x % 7, (26, 44, 60), snow)
    for x in range(88, 132, 12):
        c.pine(x, 142, 12 + x % 5, (26, 44, 60), snow)
    c.water(140, 150, (28, 36, 72), (64, 76, 128))
    c.reflect(140, 150, 188, 290, lit, taper=0)
    c.ground(150, (222, 230, 246), (255, 255, 255), (170, 184, 216), (190, 200, 228), (240, 244, 255), "snow")
    return c.img, _meta("snow")


# --- Stockholm: pink twilight, Stadshuset's three crowns, Gamla stan quay -----
def stockholm() -> tuple[Image.Image, dict]:
    c = Canvas(11129)
    sky = [(30, 30, 82), (62, 50, 112), (118, 70, 140), (196, 100, 142), (248, 148, 132), (255, 200, 152)]
    c.sky(sky, 128)
    c.stars(30, 34, [(255, 255, 255)])
    snow, lit, gold = (232, 236, 250), (255, 206, 120), (255, 208, 64)

    # Gamla stan: narrow colorful merchant houses and Riddarholmen's iron spire.
    colors = [(222, 160, 74), (220, 110, 62), (172, 62, 52), (240, 200, 104), (200, 140, 90)]
    x = 0
    while x < 160:
        w = c.rng.randint(10, 16)
        top = 96 + c.rng.randint(0, 12)
        c.rect(x, top, x + w, 128, c.rng.choice(colors))
        c.poly([(x, top), (x + w // 2, top - 8), (x + w, top)], (60, 48, 70))
        c.line(x, top - 1, x + w // 2, top - 8, snow)
        c.windows(x + 2, top + 3, x + w - 1, 126, lit, (80, 60, 70), 0.5, 4, 5, 2, 2)
        x += w
    rx = 34
    c.rect(rx - 5, 70, rx + 5, 104, (60, 50, 70))
    c.poly([(rx - 5, 70), (rx, 16), (rx + 5, 70)], (36, 34, 56))
    for y in range(24, 70, 4):
        c.put(rx, y, (120, 110, 150))  # openwork cast iron

    # Stadshuset: brick tower with copper lantern and three gold crowns.
    sx = 284
    brick, brick_dark, copper = (164, 62, 46), (122, 44, 38), (84, 146, 124)
    c.rect(232, 96, 320, 128, brick)
    c.rect(232, 96, 320, 99, brick_dark)
    for ax in range(236, 318, 8):
        c.rect(ax, 116, ax + 5, 128, (70, 34, 34))
        c.disc(ax + 2, 116, 2.5, (70, 34, 34))
    c.windows(236, 102, 318, 112, lit, (100, 40, 36), 0.45, 6, 5, 2, 3)
    c.rect(sx - 8, 34, sx + 8, 128, brick)
    c.rect(sx + 3, 34, sx + 8, 128, brick_dark)
    for y in range(44, 96, 12):
        c.rect(sx - 2, y, sx + 1, y + 5, lit)
    c.rect(sx - 10, 30, sx + 10, 34, brick_dark)
    c.rect(sx - 4, 18, sx + 4, 30, copper)
    c.poly([(sx - 5, 18), (sx, 8), (sx + 5, 18)], copper)
    for dx in (-3, 0, 3):
        c.rect(sx + dx - 1, 4, sx + dx + 1, 6, gold)
        c.put(sx + dx, 3, gold)
    c.rect(sx - 1, 6, sx + 1, 8, gold)

    # Riddarfjärden with reflections, then a snowy cobbled quay.
    c.water(128, 150, (40, 48, 100), (90, 96, 156))
    c.reflect(128, 150, sx - 6, sx + 6, lit, taper=1)
    for x0 in range(4, 160, 17):
        c.reflect(128, 144, x0, x0 + 3, lit)
    c.reflect(128, 140, sx - 2, sx + 3, gold)
    c.ground(150, (214, 220, 240), (255, 255, 255), (160, 170, 206), (150, 150, 176), (220, 226, 244), "cobble")
    for x in range(20, W, 60):
        c.rect(x, 138, x + 1, 158, (30, 30, 50))
        c.rect(x - 1, 136, x + 2, 139, lit)
    return c.img, _meta("snow")


# --- Arlington: Texas sunset, AT&T Stadium arches, Globe Life Field ----------
def arlington() -> tuple[Image.Image, dict]:
    c = Canvas(76011)
    sky = [(50, 40, 100), (118, 50, 112), (198, 70, 92), (240, 110, 72), (255, 160, 72), (255, 210, 112)]
    c.sky(sky, 140)
    c.sun(122, 100, 22, (255, 236, 140), (255, 180, 70))
    c.cloud(140, 30, 54, (255, 180, 140), (220, 110, 100))
    c.cloud(250, 50, 36, (255, 180, 140), (220, 110, 100))
    lit = (255, 214, 120)

    c.rect(0, 140, W, 146, (58, 86, 44))  # distant tree line at the horizon
    # Globe Life Field: brick box with a big angled retractable roof.
    c.rect(8, 112, 104, 146, (150, 84, 62))
    c.poly([(4, 112), (20, 94), (92, 94), (108, 112)], (130, 138, 160))
    c.line(4, 112, 108, 112, (96, 102, 128))
    for x in range(22, 92, 10):
        c.line(x, 95, x - 4, 111, (104, 110, 136))
    c.windows(12, 118, 102, 144, lit, (110, 60, 50), 0.35, 6, 6, 3, 2)

    # AT&T Stadium: long silver dome, glass walls, twin arches over the roof.
    cx, cy, rx, ry = 236, 128, 88, 30
    for y in range(cy - ry, cy + 1):
        half = rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2))
        c.rect(cx - half, y, cx + half, y + 1, (156, 166, 196) if y < cy - 12 else (120, 130, 168))
    c.rect(cx - rx + 4, cy, cx + rx - 4, 146, (40, 52, 96))
    c.windows(cx - rx + 6, cy + 2, cx + rx - 5, 145, (120, 190, 240), (40, 52, 96), 0.4, 4, 4, 3, 2)
    c.rect(cx - rx + 4, cy, cx + rx - 4, cy + 1, (220, 226, 240))
    for off in (-10, 10):
        for x in range(cx - rx - 4, cx + rx + 5):
            t = (x - cx) / (rx + 4)
            y = cy - 6 - 40 * (1 - t * t)
            c.put(x, y + off * 0.2, (236, 238, 248))
            c.put(x, y + 1 + off * 0.2, (190, 196, 220))

    # Flat Texas grass, live oaks, flag.
    c.ground(146, (84, 116, 54), (122, 150, 70), (58, 86, 44), (176, 164, 150), (204, 192, 176), "pavement")
    for x in (116, 140, 312):
        c.round_tree(x, 150, 7, (60, 40, 30), (48, 78, 44), (74, 110, 56), (34, 58, 36), 5)
    c.rect(128, 116, 129, 150, (200, 200, 210))
    c.rect(129, 116, 135, 120, (220, 40, 50))
    c.rect(129, 118, 135, 120, (240, 240, 240))
    c.rect(129, 116, 131, 120, (30, 60, 140))
    c.put(130, 117, (255, 255, 255))
    return c.img, _meta("fireflies")


# --- Mexico City: hazy afternoon, Angel de la Independencia, Popocatepetl ----
def cdmx() -> tuple[Image.Image, dict]:
    c = Canvas(6600)
    sky = [(78, 138, 210), (108, 164, 222), (148, 188, 226), (196, 206, 214)]
    c.sky(sky, 130)
    c.cloud(200, 30, 40, (255, 255, 255), (212, 222, 236))
    haze, snow = (150, 146, 176), (246, 246, 252)

    # Popocatepetl with its steam plume, faint in the haze.
    for x in range(W):
        top = 58 + abs(x - 44) * 0.62
        if abs(x - 44) < 6:
            top = 58 + 3  # crater lip
        for y in range(int(top), 130):
            c.put(x, y, snow if y < 72 + (x % 4) and y < top + 12 else haze)
    for i in range(70):
        a = c.rng.random()
        c.disc(44 + a * 50 + c.rng.randint(-3, 3), 52 - a * 26 + c.rng.randint(-2, 2), 2 + a * 3,
               (224, 226, 234) if c.rng.random() < 0.6 else (200, 204, 218))

    # Street level of the avenue between the sky and the park.
    c.rect(0, 130, W, 150, (120, 118, 132))
    c.rect(0, 146, W, 150, (96, 94, 108))
    # Paseo de la Reforma towers.
    glass, glass_dark, lit = (118, 138, 174), (88, 106, 150), (190, 214, 240)
    for x0, w, top in ((120, 16, 60), (138, 12, 78), (186, 20, 50), (210, 14, 72), (156, 18, 64), (300, 12, 88), (78, 14, 90)):
        c.rect(x0, top, x0 + w, 140, glass)
        c.rect(x0 + w - 4, top, x0 + w, 140, glass_dark)
        c.windows(x0 + 2, top + 3, x0 + w - 4, 138, lit, glass, 0.35, 3, 4, 1, 2)
    c.poly([(186, 50), (206, 42), (206, 50)], glass_dark)  # Torre Reforma's slanted crown

    # Angel de la Independencia: plinth, column, golden Victoria on top.
    ax = 276
    stone, stone_dark, gold, gold_dark = (232, 222, 196), (190, 178, 156), (255, 204, 64), (214, 150, 40)
    c.rect(ax - 18, 140, ax + 18, 150, stone_dark)
    c.rect(ax - 14, 128, ax + 14, 140, stone)
    c.rect(ax - 14, 138, ax + 14, 140, stone_dark)
    for dx in (-12, 12):
        c.rect(ax + dx - 2, 122, ax + dx + 2, 128, (60, 60, 60))  # bronze figures at the base
    # Kept below y~40 so the Victoria survives the sky crop on 20:9 phones.
    top = 60
    c.rect(ax - 3, top, ax + 3, 128, stone)
    c.rect(ax + 1, top, ax + 3, 128, stone_dark)
    for y in range(top + 12, 124, 14):
        c.rect(ax - 4, y, ax + 4, y + 2, gold_dark)
    c.rect(ax - 5, top - 4, ax + 5, top, stone_dark)
    # Victoria: body, raised wreath arm, spread wings.
    v = top - 14
    c.rect(ax - 1, v, ax + 1, v + 10, gold)
    c.put(ax, v - 2, gold)
    c.line(ax + 1, v + 2, ax + 5, v - 4, gold)
    c.disc(ax + 5, v - 5, 1.2, gold_dark)
    c.poly([(ax - 1, v + 3), (ax - 9, v - 3), (ax - 7, v + 5)], gold)
    c.poly([(ax + 1, v + 3), (ax + 8, v), (ax + 5, v + 7)], gold_dark)

    # Jacarandas in bloom on both sides of the avenue.
    trunk, bloom, bloom_hi, bloom_dark = (80, 60, 60), (150, 102, 204), (196, 156, 236), (110, 72, 164)
    for x, r in ((20, 16), (58, 12), (100, 10), (232, 12), (310, 12)):
        c.round_tree(x, 152, r, trunk, bloom, bloom_hi, bloom_dark, 10)
    c.ground(150, (92, 142, 72), (124, 172, 92), (64, 110, 58), (206, 186, 164), (226, 210, 190), "pavement")
    for _ in range(40):
        c.put(c.rng.randrange(W), c.rng.randrange(PATH_TOP + 1, 176), bloom_hi)
    return c.img, _meta("jacaranda")


CITIES = [
    ("builtin:la", "Los Angeles, CA", los_angeles),
    ("builtin:bologna", "Bologna, Italy", bologna),
    ("builtin:paris", "Paris, France", paris),
    ("builtin:geneva", "Geneva, Switzerland", geneva),
    ("builtin:uppsala", "Uppsala, Sweden", uppsala),
    ("builtin:stockholm", "Stockholm, Sweden", stockholm),
    ("builtin:arlington", "Arlington, TX", arlington),
    ("builtin:cdmx", "Mexico City (CDMX)", cdmx),
]
