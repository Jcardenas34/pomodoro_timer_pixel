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

from .paint import GROUND_META, H, PATH_BOTTOM, PATH_TOP, W, Canvas, darken, swiss_flag


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
    # Chaparral texture and a sunlit crest on the hills.
    for x in range(W):
        top = int(96 + 9 * math.sin(x / 31 + 1) + 4 * math.sin(x / 11) - 20 * math.exp(-((x - 28) / 30) ** 2))
        c.put(x, top, (176, 104, 120))
        for y in range(top + 2, 142, 3):
            if c.rng.random() < 0.35:
                c.put(x, y, (112, 66, 98))
    # The sign: white letters on stilts across Mt Lee.
    c.text("HOLLYWOOD", 5, 91, (244, 238, 222))
    for x in range(6, 41, 4):
        c.put(x, 96, (150, 140, 150))
        c.put(x + 1, 97, (150, 140, 150))
    def near_ridge(x: float) -> float:
        return 120 + 5 * math.sin(x / 19) - 24 * math.exp(-((x - 284) / 34) ** 2)

    c.ridge(near_ridge, 142, near)
    # Griffith Observatory seated on the near ridge's crest.
    wall, shade, dome = (238, 226, 204), (196, 176, 160), (62, 86, 92)
    ox = 284
    b = int(near_ridge(ox)) + 2
    dome_hi = (104, 140, 140)
    c.rect(ox - 19, b - 8, ox + 19, b, wall)
    c.rect(ox - 19, b - 2, ox + 19, b, shade)
    for x in range(ox - 17, ox + 18, 3):  # colonnade
        c.rect(x, b - 7, x + 1, b - 2, shade)
    c.rect(ox - 19, b - 8, ox + 19, b - 7, (255, 246, 226))
    c.disc(ox, b - 9, 7, dome)
    for x in range(ox - 5, ox + 1):
        c.put(x, b - 14 + abs(x - ox + 3) // 2, dome_hi)
    c.rect(ox - 7, b - 9, ox + 8, b - 8, wall)
    for dx in (-16, 16):
        c.disc(ox + dx, b - 7, 3, dome)
        c.put(ox + dx - 1, b - 9, dome_hi)
    c.put(ox, b - 17, (255, 236, 150))
    c.rect(ox - 2, b - 6, ox + 3, b - 2, (255, 214, 130))  # lit entrance

    # Low city strip with evening lights.
    city, city_dark, lit = (70, 46, 80), (54, 36, 66), (255, 200, 110)
    for x0 in range(0, W, 9):
        top = 128 - c.rng.randint(0, 8)
        c.rect(x0, top, x0 + 8, 142, city)
        c.rect(x0 + 6, top, x0 + 8, 142, city_dark)
        c.windows(x0 + 1, top + 2, x0 + 6, 141, lit, city, 0.3, 2, 3, 1, 1)
        if c.rng.random() < 0.3:
            c.rect(x0 + 2, top - 3, x0 + 3, top, city_dark)  # rooftop antennas
            c.put(x0 + 2, top - 4, (255, 70, 60))
    # The 101 on an overpass: concrete deck and streaks of head/tail lights.
    c.rect(0, 136, W, 140, (124, 92, 104))
    c.rect(0, 139, W, 140, (90, 64, 84))
    for x in range(0, W, 5):
        c.put(x, 137, (255, 244, 210) if (x // 5) % 3 else (255, 80, 70))
        c.put(x + 2, 138, (255, 80, 70) if (x // 5) % 2 else (255, 244, 210))
    for x in range(10, W, 46):
        c.rect(x, 140, x + 3, 142, (90, 64, 84))

    c.ground(142, (96, 128, 64), (132, 160, 80), (62, 92, 52), (206, 184, 160), (228, 208, 182), "pavement")
    # Hedges and agave along the boulevard.
    for x in range(0, W, 22):
        c.bush(x + 8, 158, 4, (70, 108, 58), (104, 140, 72), (48, 80, 48))
    # Walk of Fame: charcoal squares with pink terrazzo stars and brass rims.
    star = ["..#..", "#####", ".###.", ".#.#."]
    for x0 in range(6, W, 24):
        c.rect(x0, 164, x0 + 9, 173, (84, 72, 84))
        for dy, row in enumerate(star):
            for dx, ch in enumerate(row):
                if ch == "#":
                    c.put(x0 + 2 + dx, 165 + dy, (232, 140, 160))
        c.rect(x0 + 2, 170, x0 + 7, 171, (226, 186, 90))  # brass name plate
    trunk, frond, frond2 = (52, 36, 62), (38, 30, 58), (70, 48, 84)
    for x, h in ((56, 72), (156, 92), (212, 76), (248, 84), (312, 90)):
        c.palm(x, 158, h, trunk, frond, frond2)
    for x in (24, 104, 184, 284):
        c.lamp(x, 158, 18, (44, 34, 54), (255, 220, 150))
    c.birds(6, 60, 200, 14, 40, (90, 50, 90))
    return c.img, _meta("jacaranda")


# --- Bologna: warm evening, Due Torri, terracotta roofs, porticoes ---------
def bologna() -> tuple[Image.Image, dict]:
    c = Canvas(40121)
    sky = [(44, 42, 96), (96, 60, 122), (172, 82, 112), (230, 122, 92), (255, 170, 104), (252, 210, 150)]
    c.sky(sky, 140)
    c.cloud(40, 30, 36, (255, 196, 160), (220, 130, 120))
    c.cloud(170, 30, 42, (255, 196, 160), (220, 130, 120))
    brick, brick_lit, brick_dark = (156, 72, 52), (196, 104, 66), (112, 50, 44)
    # Colle della Guardia with the Santuario di San Luca on its crest (left).
    hill = (150, 96, 112)
    c.ridge(lambda x: 104 + 10 * math.exp(-((x - 30) / 40) ** 2) * -1 + 0.08 * max(0, x - 60), 132, hill)
    c.haze(96, 132, (196, 120, 116), 4)
    sx = 30
    c.rect(sx - 10, 84, sx + 10, 94, (232, 170, 120))
    c.disc(sx, 84, 6, (214, 140, 100))
    c.rect(sx - 1, 74, sx + 1, 78, (214, 140, 100))
    c.rect(sx - 13, 86, sx - 10, 94, (214, 150, 110))
    c.rect(sx + 10, 86, sx + 13, 94, (214, 150, 110))
    for x in range(sx - 9, sx + 10, 3):
        c.put(x, 90, (150, 84, 70))
    # The 666-arch portico climbing the hill.
    for i in range(0, 46):
        x = sx + 12 + i
        y = 94 + i * 0.55
        c.put(x, y, (232, 170, 120))
        if i % 2 == 0:
            c.put(x, y + 1, (150, 84, 70))

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
    c.brick(ax - 6, 30, ax + 7, 132, brick_dark, course=4)
    for y in range(36, 124, 14):
        c.rect(ax - 1, y, ax + 1, y + 3, (60, 30, 30))
        c.put(ax - 2, y + 3, brick_lit)
    for x in range(ax - 7, ax + 8, 2):  # wooden gallery rail under the battlements
        c.put(x, 29, (80, 50, 40))
    # Torre Garisenda: shorter and visibly leaning.
    for y in range(68, 132):
        lean = (132 - y) // 9
        c.rect(ax + 13 + lean, y, ax + 19 + lean, y + 1, brick_dark)
        c.rect(ax + 19 + lean, y, ax + 25 + lean, y + 1, brick)
    c.rect(ax + 20, 68, ax + 32, 71, brick_dark)
    c.brick(ax + 14, 72, ax + 30, 132, brick_dark, course=4)

    # Terracotta roofs in two rows.
    roof, roof_dark = (206, 96, 62), (160, 70, 52)
    walls = [(226, 164, 96), (206, 124, 74), (232, 186, 120), (190, 100, 70)]
    for row, (base, h) in enumerate(((126, 14), (140, 12))):
        x = -6 + row * 9
        while x < W:
            w = c.rng.randint(18, 30)
            peak = base - h - c.rng.randint(0, 6)
            wall = c.rng.choice(walls)
            c.rect(x, peak + 5, x + w, 158, wall)
            c.rect(x + w - 2, peak + 5, x + w, 158, darken(wall, 0.86))
            c.poly([(x - 2, peak + 6), (x + w // 2, peak), (x + w + 1, peak + 6)], roof)
            for ty in range(peak + 2, peak + 6, 2):  # coppi tile courses
                for tx in range(x, x + w, 2):
                    if c.get(tx, ty) == roof:
                        c.put(tx, ty, roof_dark)
            c.line(x - 2, peak + 6, x + w + 1, peak + 6, roof_dark)
            if c.rng.random() < 0.6:  # chimney
                cx0 = x + c.rng.randint(3, max(4, w - 5))
                c.rect(cx0, peak - 1, cx0 + 2, peak + 4, darken(wall, 0.8))
                c.rect(cx0 - 1, peak - 2, cx0 + 3, peak - 1, roof_dark)
            # Windows with the green shutters Bologna is known for.
            for wy in range(peak + 10, 148, 8):
                for wx in range(x + 4, x + w - 4, 7):
                    glass = (255, 206, 120) if c.rng.random() < 0.35 else (120, 70, 50)
                    c.rect(wx, wy, wx + 2, wy + 3, glass)
                    c.rect(wx - 1, wy, wx, wy + 3, (70, 110, 70))
                    c.rect(wx + 2, wy, wx + 3, wy + 3, (70, 110, 70))
                    c.rect(wx - 1, wy + 3, wx + 3, wy + 4, darken(wall, 0.8))
            x += w + 1
    # Porticoes: a continuous arcade along the street, lamps glowing inside.
    arcade, pillar, glow = (86, 46, 40), (220, 150, 90), (255, 210, 120)
    c.rect(0, 140, W, 158, pillar)
    for x in range(2, W, 14):
        c.rect(x, 146, x + 10, 158, arcade)
        c.disc(x + 5, 146, 5, arcade)
        c.halo(x + 5, 150, 4, (150, 84, 60), 3)
        c.put(x + 5, 145, glow)
        c.rect(x + 4, 147, x + 7, 149, glow)
        c.rect(x + 1, 156, x + 9, 158, (120, 70, 56))  # warm floor inside
        c.rect(x - 2, 146, x, 147, (240, 176, 110))  # column capitals
    c.rect(0, 140, W, 142, (176, 108, 72))

    c.ground(156, (150, 110, 88), (176, 134, 104), (110, 80, 66), (140, 102, 84), (118, 84, 70), "cobble")
    # Cafe tables under parasols and a parked Vespa.
    for x in (18, 210, 300):
        c.rect(x, 152, x + 1, 160, (80, 60, 50))
        c.poly([(x - 7, 152), (x, 147), (x + 8, 152)], (236, 230, 214))
        c.line(x - 7, 152, x + 8, 152, (200, 70, 60))
        c.rect(x - 3, 158, x + 4, 159, (80, 60, 50))
    vx = 120
    vespa, vespa_hi = (120, 180, 170), (180, 222, 214)
    c.disc(vx, 158, 2, (30, 26, 30))
    c.disc(vx + 10, 158, 2, (30, 26, 30))
    c.poly([(vx - 2, 157), (vx + 1, 152), (vx + 7, 152), (vx + 12, 157)], vespa)
    c.rect(vx + 2, 151, vx + 7, 152, (60, 40, 40))  # seat
    c.line(vx + 10, 157, vx + 9, 148, vespa)
    c.rect(vx + 7, 148, vx + 12, 149, (40, 40, 40))  # handlebar
    c.put(vx + 11, 150, vespa_hi)
    c.birds(7, 20, 240, 10, 44, (110, 60, 80))
    return c.img, _meta("leaves")


# --- Paris: dusk, lit Eiffel Tower, Haussmann rooftops, the Seine -----------
def paris() -> tuple[Image.Image, dict]:
    c = Canvas(75007)
    sky = [(20, 24, 62), (40, 40, 102), (80, 60, 132), (150, 80, 142), (228, 120, 130), (255, 170, 132)]
    c.sky(sky, 140)
    c.stars(40, 40, [(240, 230, 255), (180, 180, 230)])
    c.moon(48, 26, 5, (250, 240, 210), (220, 205, 180))
    iron, gold = (48, 36, 72), (255, 204, 92)
    # Montmartre and the Sacre-Coeur, pale in the dusk haze on the left.
    c.ridge(lambda x: 104 - 8 * math.exp(-((x - 30) / 26) ** 2), 140, (120, 84, 130))
    sc, sc_dark = (226, 210, 222), (184, 166, 190)
    c.rect(18, 88, 44, 100, sc)
    c.rect(36, 88, 44, 100, sc_dark)
    c.disc(31, 87, 6, sc)
    c.rect(30, 76, 32, 81, sc)
    for dx in (-10, 10):
        c.disc(31 + dx, 89, 3, sc_dark)
    c.rect(44, 82, 48, 100, sc)  # campanile
    c.disc(46, 82, 2, sc)

    # Eiffel Tower: flared legs, two platforms, arch between the legs, lights on its edges.
    tx, top, base = 268, 12, 140

    def half(y: float) -> float:
        return 1 + 27 * ((y - top) / (base - top)) ** 2.3

    for y in range(top, base):
        h = half(y)
        c.rect(tx - h, y, tx + h + 1, y + 1, iron)
        # Lattice: open X-bracing inside each leg, sky showing through.
        if y > 30 and h > 3:
            inner = int(h) - 2
            for x in range(int(tx - inner), int(tx + inner) + 1):
                u = (x - tx) + inner
                if (u + y) % 6 not in (0, 1) and (u - y) % 6 not in (0, 1):
                    c.put(x, y, c.get(tx + 44, y))
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
            c.rect(x - 1, t - 6, x + 3, t - 5, stone)  # dormer hood
            c.rect(x, t - 5, x + 2, t - 1, (255, 214, 130))
            c.rect(x + 2, t - 11, x + 3, t - 7, stone_dark)  # chimney pots
            c.put(x + 2, t - 12, (180, 90, 70))
        c.rect(x0, t, x1, t + 1, (180, 166, 190))  # cornice
        c.window_grid(x0 + 3, t + 3, x1 - 2, 138, 2, 3, 5, 6, (255, 212, 124), (60, 58, 92), 0.55,
                      sill=(170, 156, 180))
        for by in (t + 11, t + 23):  # wrought-iron balconies on the 2nd and 5th floors
            c.rect(x0, by, x1, by + 1, (40, 36, 60))
            for x in range(x0, x1, 2):
                c.put(x, by - 1, (40, 36, 60))

    # The Seine with the tower's golden reflection.
    c.water(140, 150, (38, 46, 100), (80, 86, 150))
    c.reflect(140, 150, tx - 8, tx + 9, gold, taper=1)
    for x in range(10, 232, 23):
        c.reflect(140, 148, x, x + 3, (255, 212, 124))
    # A bateau-mouche gliding past with its deck lights on.
    c.boat(120, 149, 44, (232, 232, 240), (210, 200, 186), (40, 40, 60), (255, 222, 150))
    c.ground(150, (96, 90, 112), (122, 116, 138), (70, 66, 90), (130, 120, 132), (104, 96, 112), "cobble")
    # Bouquinistes: green book boxes on the quay wall.
    for x in range(4, W, 34):
        c.rect(x, 150, x + 16, 156, (52, 98, 74))
        c.rect(x, 150, x + 16, 151, (82, 132, 100))
        c.rect(x + 2, 152, x + 14, 155, (200, 180, 150))
        for bx in range(x + 2, x + 14, 2):
            c.put(bx, 153, c.rng.choice([(180, 60, 60), (60, 80, 140), (220, 200, 120)]))
    # Cafe with a red awning, and a green Morris column.
    c.rect(286, 128, 320, 156, (132, 118, 146))
    c.poly([(284, 134), (320, 134), (320, 140), (288, 140)], (190, 50, 60))
    for x in range(288, 320, 4):
        c.rect(x, 134, x + 2, 140, (236, 226, 214))
    c.rect(290, 142, 318, 156, (255, 212, 124))
    for x in (292, 302, 312):
        c.rect(x, 152, x + 5, 153, (40, 36, 50))
        c.rect(x + 2, 153, x + 3, 158, (40, 36, 50))
    mx = 252
    c.rect(mx - 3, 140, mx + 4, 158, (40, 96, 72))
    c.rect(mx - 2, 142, mx + 3, 154, (220, 200, 160))
    c.disc(mx + 0.5, 140, 3.5, (40, 96, 72))
    c.put(mx, 135, (40, 96, 72))
    # Quay lamps.
    for x in range(30, 270, 70):
        c.lamp(x, 158, 18, (30, 28, 44), gold, (190, 150, 120), double=True)
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
    # Rock faces showing through the snow on the shaded slopes.
    for x in range(W):
        top = int(alps(x))
        for y in range(top + 3, top + 14):
            if (x + y) % 5 == 0 and math.sin(x / 13) < 0:
                c.put(x, y, (120, 132, 176))
    c.haze(96, 118, (186, 208, 240), 4)
    c.ridge(lambda x: 104 + 6 * math.sin(x / 27 + 2) + 3 * math.sin(x / 8), 118, (84, 126, 118))
    for x in range(0, W, 2):  # vineyard rows / trees on the far shore
        top = int(104 + 6 * math.sin(x / 27 + 2) + 3 * math.sin(x / 8))
        for y in range(top + 2, 118, 3):
            c.put(x, y, (66, 106, 98))
    # Vieille Ville on its hill: St-Pierre cathedral with the green spire.
    c.ridge(lambda x: 108 - 10 * math.exp(-((x - 24) / 30) ** 2), 118, (110, 140, 120))
    town = [(236, 226, 206), (222, 204, 180), (240, 236, 222)]
    for x0 in range(0, 52, 7):
        top = 98 + abs(x0 - 24) // 4 + c.rng.randint(0, 3)
        c.rect(x0, top, x0 + 6, 118, c.rng.choice(town))
        c.rect(x0, top - 2, x0 + 6, top, (176, 92, 70))
        c.window_grid(x0 + 1, top + 2, x0 + 6, 116, 1, 2, 2, 4, (120, 130, 150), (160, 160, 170), 0.5)
    stone, copper = (196, 186, 166), (90, 160, 140)
    for tx in (16, 30):
        c.rect(tx, 80, tx + 7, 102, stone)
        c.rect(tx + 5, 80, tx + 7, 102, (160, 150, 134))
        c.rect(tx + 2, 84, tx + 4, 90, (90, 90, 100))
    c.rect(22, 78, 25, 86, copper)
    c.poly([(21, 78), (23, 62), (26, 78)], copper)
    # Lake with a bright shimmer.
    c.water(116, 148, (54, 108, 182), (132, 184, 236))
    c.reflect(116, 132, 10, 40, (196, 206, 220))
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
    for x, y in ((60, 136), (110, 128), (220, 138), (32, 142)):
        c.poly([(x, y), (x, y - 9), (x + 6, y)], (255, 255, 255))
        c.poly([(x - 1, y - 1), (x - 1, y - 7), (x - 5, y - 1)], (226, 232, 244))
        c.rect(x - 3, y, x + 8, y + 2, (120, 70, 50))
        c.rect(x - 3, y + 1, x + 8, y + 2, (90, 54, 40))
    # CGN Belle Epoque paddle steamer with a Swiss flag astern.
    px0, py0 = 120, 146
    c.poly([(px0, py0 - 4), (px0 + 56, py0 - 4), (px0 + 52, py0), (px0 + 4, py0)], (252, 252, 255))
    c.rect(px0 + 2, py0 - 2, px0 + 54, py0 - 1, (40, 60, 110))
    c.rect(px0 + 8, py0 - 9, px0 + 48, py0 - 4, (240, 236, 226))
    c.window_grid(px0 + 10, py0 - 8, px0 + 47, py0 - 5, 2, 2, 4, 4, (90, 120, 160), (90, 120, 160), 1.0)
    c.rect(px0 + 24, py0 - 9, px0 + 32, py0 - 4, (226, 196, 120))  # paddle box
    for fx in (px0 + 20, px0 + 34):
        c.rect(fx, py0 - 15, fx + 3, py0 - 9, (226, 190, 90))
        c.rect(fx, py0 - 15, fx + 3, py0 - 14, (60, 50, 50))
    c.flag(px0 + 2, py0 - 4, 9, 5, 5, swiss_flag(5), (90, 70, 60), (255, 220, 120), wave=0.6)
    for x in range(px0, px0 + 56, 3):  # wake
        c.put(x, py0 + 1, (132, 184, 236))
    # Lakeside promenade with flower beds.
    c.ground(148, (84, 158, 84), (122, 196, 104), (56, 118, 66), (214, 206, 190), (236, 230, 218), "pavement")
    for x in range(0, W, 3):
        for y in (150, 153, 156):
            if c.rng.random() < 0.5:
                c.put(x + c.rng.randint(0, 2), y, c.rng.choice([(236, 64, 80), (255, 210, 60), (255, 255, 255)]))
    # L'Horloge fleurie: the flower clock in the Jardin Anglais.
    fx, fy = 230, 154
    for y in range(fy - 5, fy + 6):
        for x in range(fx - 15, fx + 16):
            d = ((x - fx) / 15) ** 2 + ((y - fy) / 5) ** 2
            if d <= 1:
                ring = d > 0.7
                c.put(x, y, (236, 64, 80) if ring and (x + y) % 2 else (255, 210, 60) if ring else
                      (122, 196, 104) if (x * 3 + y) % 7 else (255, 255, 255))
    c.line(fx, fy, fx - 7, fy - 2, (40, 40, 50))
    c.line(fx, fy, fx + 4, fy - 3, (40, 40, 50))
    # Promenade lamps and a bench.
    for x in (70, 170, 300):
        c.lamp(x, 160, 14, (40, 60, 70), (255, 250, 220))
    c.bench(96, 157, (150, 100, 60), (50, 50, 60))
    # The big Swiss flag over the quay (left third, clear of the clock).
    c.rect(22, 158, 27, 160, (120, 120, 130))
    c.flag(24, 158, 52, 15, 15, swiss_flag(15), (200, 204, 214), (255, 214, 90), wave=1.2,
           dark=lambda col: darken(col, 0.82))
    # Gulls and swans.
    c.birds(8, 60, 250, 30, 60, (90, 110, 150))
    for x, y in ((150, 132), (196, 136), (90, 140)):
        c.rect(x, y, x + 4, y + 2, (255, 255, 255))
        c.put(x + 3, y - 1, (255, 255, 255))
        c.put(x + 4, y - 1, (240, 140, 60))
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
    pink, pink_dark = (206, 128, 132), (164, 98, 112)
    c.rect(22, 90, 80, 104, pink)
    c.rect(22, 102, 80, 104, pink_dark)
    c.disc(24, 92, 6, pink)
    c.disc(78, 92, 6, pink)
    c.rect(79, 86, 85, 104, pink_dark)
    c.poly([(18, 88), (24, 80), (30, 88)], (60, 50, 80))
    c.poly([(72, 88), (78, 80), (84, 88)], (60, 50, 80))
    for x0 in (18, 72):  # snow on the tower caps
        c.line(x0, 88, x0 + 6, 80, snow)
    c.rect(22, 89, 80, 90, snow)
    c.window_grid(30, 94, 72, 102, 2, 2, 5, 4, lit, (140, 80, 90), 0.5, sill=snow)

    # Cathedral: nave with gothic windows, twin west towers, tall slate spires.
    c.rect(180, 104, 262, 140, brick)
    c.brick(180, 104, 262, 140, brick_dark, course=3)
    c.poly([(178, 104), (221, 88), (264, 104)], (60, 50, 70))
    c.line(178, 104, 221, 88, snow)
    c.line(221, 88, 264, 104, snow)
    for x in range(188, 258, 10):
        c.rect(x - 2, 108, x, 140, brick_dark)  # buttresses
        c.rect(x, 112, x + 4, 128, lit)
        c.disc(x + 1.5, 112, 2, lit)
        c.rect(x + 1, 112, x + 2, 128, (200, 140, 90))  # tracery
    for tx in (262, 280):
        c.rect(tx, 70, tx + 14, 140, brick)
        c.brick(tx, 70, tx + 10, 140, brick_dark, course=3)
        c.rect(tx + 10, 70, tx + 14, 140, brick_dark)
        c.rect(tx + 5, 96, tx + 9, 108, lit)
        c.disc(tx + 6.5, 96, 2, lit)
        # Tower clocks and the green-gold band under the spires.
        c.disc(tx + 7, 80, 4, (240, 226, 180))
        c.put(tx + 7, 78, (40, 30, 30))
        c.put(tx + 8, 80, (40, 30, 30))
        c.rect(tx - 1, 69, tx + 15, 71, (210, 170, 70))
        c.poly([(tx - 1, 70), (tx + 7, 10), (tx + 15, 70)], spire)
        c.line(tx + 7, 10, tx + 15, 70, (70, 84, 104))
        for y in range(20, 70, 8):  # copper seams
            half = (y - 10) * 8 / 60
            c.rect(tx + 7 - half, y, tx + 7 + half, y + 1, (60, 72, 90))
        c.put(tx + 7, 8, (255, 214, 90))
        c.put(tx + 7, 9, (255, 214, 90))
    c.rect(274, 118, 280, 140, brick_dark)
    c.rect(272, 124, 282, 140, (80, 40, 40))  # west portal
    c.disc(277, 124, 5, (80, 40, 40))
    c.disc(277, 106, 4, (190, 120, 150))  # rose window
    c.disc(277, 106, 2, lit)

    # Snowy pines and houses along the Fyris.
    for x in range(300, W, 9):
        c.pine(x, 142, 14 + x % 7, (26, 44, 60), snow)
    for x in range(88, 132, 12):
        c.pine(x, 142, 12 + x % 5, (26, 44, 60), snow)
    # Ochre and falu-red houses along the Fyris, Advent stars in the windows.
    hx = 132
    for col in ((214, 168, 84), (150, 52, 44), (220, 200, 150), (180, 120, 70)):
        c.rect(hx, 118, hx + 12, 140, col)
        c.poly([(hx - 1, 118), (hx + 6, 111), (hx + 13, 118)], (70, 60, 80))
        c.line(hx - 1, 118, hx + 6, 111, snow)
        c.line(hx + 6, 111, hx + 13, 118, snow)
        for wx in (hx + 2, hx + 7):
            c.rect(wx, 124, wx + 3, 128, lit)
            c.put(wx + 1, 125, (255, 140, 60))
        hx += 12
    c.water(140, 150, (28, 36, 72), (64, 76, 128))
    c.reflect(140, 150, 188, 290, lit, taper=0)
    # Ice along the river's edge.
    for x in range(0, W, 7):
        c.rect(x, 140, x + c.rng.randint(2, 5), 141, (200, 210, 236))
    c.ground(150, (222, 230, 246), (255, 255, 255), (170, 184, 216), (190, 200, 228), (240, 244, 255), "snow")
    # Footprints in the snow along the path.
    for x in range(0, W, 6):
        c.put(x, 167 + (x // 6) % 2 * 3, (170, 184, 216))
    # Bike rack (it's a student town), snow-capped lamps and benches.
    for bxx in range(200, 250, 10):
        c.disc(bxx, 156, 2, (40, 44, 70))
        c.disc(bxx + 6, 156, 2, (40, 44, 70))
        c.line(bxx, 156, bxx + 3, 152, (190, 50, 60))
        c.line(bxx + 3, 152, bxx + 6, 156, (190, 50, 60))
        c.put(bxx + 3, 151, (40, 44, 70))
        c.put(bxx + 5, 151, snow)
    c.rect(198, 157, 252, 158, (90, 90, 110))
    for x in (20, 120, 300):
        c.lamp(x, 160, 16, (40, 44, 70), lit, (200, 170, 150))
        c.rect(x - 1, 160 - 20, x + 2, 160 - 19, snow)
    c.bench(64, 157, (120, 80, 60), (40, 44, 70))
    c.rect(64, 153, 73, 154, snow)
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
        col = c.rng.choice(colors)
        c.rect(x, top, x + w, 128, col)
        c.rect(x + w - 2, top, x + w, 128, darken(col, 0.85))
        if c.rng.random() < 0.5:
            # Stepped Dutch gable, snow on each step.
            for i, inset in enumerate((0, 2, 4)):
                if w - 2 * inset > 2:
                    c.rect(x + inset, top - 3 * (i + 1), x + w - inset, top - 3 * i, col)
                    c.rect(x + inset, top - 3 * (i + 1), x + w - inset, top - 3 * (i + 1) + 1, snow)
        else:
            c.poly([(x, top), (x + w // 2, top - 8), (x + w, top)], (60, 48, 70))
            c.line(x, top - 1, x + w // 2, top - 8, snow)
        c.window_grid(x + 2, top + 3, x + w - 1, 124, 2, 2, 4, 5, lit, (80, 60, 70), 0.5, sill=snow)
        c.rect(x + w // 2 - 1, 123, x + w // 2 + 2, 128, darken(col, 0.6))  # door
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
    c.brick(232, 99, 320, 128, brick_dark, course=3)
    c.rect(232, 96, 320, 99, brick_dark)
    for ax in range(236, 318, 8):
        c.rect(ax, 116, ax + 5, 128, (70, 34, 34))
        c.disc(ax + 2, 116, 2.5, (70, 34, 34))
    c.windows(236, 102, 318, 112, lit, (100, 40, 36), 0.45, 6, 5, 2, 3)
    c.rect(sx - 8, 34, sx + 8, 128, brick)
    c.brick(sx - 8, 34, sx + 3, 128, brick_dark, course=3)
    c.rect(sx + 3, 34, sx + 8, 128, brick_dark)
    for y in range(44, 96, 12):
        c.rect(sx - 2, y, sx + 1, y + 5, lit)
    c.rect(sx - 10, 40, sx + 10, 42, (70, 34, 34))  # gallery
    c.railing(sx - 10, sx + 10, 37, 40, (70, 34, 34), 2)
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
    # Drifting ice and an archipelago steamer moored at the quay.
    for _ in range(18):
        ix, iy = c.rng.randrange(W), c.rng.randrange(132, 148)
        c.rect(ix, iy, ix + c.rng.randint(3, 7), iy + 1, (210, 220, 240))
    sx0 = 168
    c.poly([(sx0, 142), (sx0 + 50, 142), (sx0 + 46, 148), (sx0 + 3, 148)], (240, 240, 244))
    c.rect(sx0 + 2, 146, sx0 + 48, 147, (30, 30, 50))
    c.rect(sx0 + 8, 136, sx0 + 40, 142, (240, 240, 244))
    c.window_grid(sx0 + 10, 138, sx0 + 39, 141, 2, 2, 4, 3, lit, lit, 1.0)
    c.rect(sx0 + 22, 128, sx0 + 26, 136, (30, 30, 50))
    c.rect(sx0 + 22, 131, sx0 + 26, 132, (220, 180, 60))
    c.ground(150, (214, 220, 240), (255, 255, 255), (160, 170, 206), (150, 150, 176), (220, 226, 244), "cobble")
    # Quay edge with mooring bollards, lamps with snow caps.
    c.rect(0, 150, W, 152, (120, 120, 150))
    for x in range(10, W, 26):
        c.rect(x, 152, x + 3, 157, (40, 40, 60))
        c.rect(x - 1, 151, x + 4, 152, snow)
    for x in range(20, W, 60):
        c.lamp(x, 158, 20, (30, 30, 50), lit, (190, 160, 170))
        c.rect(x - 1, 133, x + 2, 134, snow)
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
    c.brick(8, 112, 104, 146, (120, 64, 50), course=3)
    c.poly([(4, 112), (20, 94), (92, 94), (108, 112)], (130, 138, 160))
    c.line(4, 112, 108, 112, (96, 102, 128))
    for x in range(22, 92, 10):
        c.line(x, 95, x - 4, 111, (104, 110, 136))
    c.rect(20, 94, 92, 95, (180, 186, 206))
    # Tall brick arches along the facade, warm light inside.
    for x in range(12, 100, 10):
        c.rect(x, 120, x + 6, 146, (110, 60, 50))
        c.disc(x + 2.5, 120, 3, (110, 60, 50))
        c.rect(x + 1, 124, x + 5, 140, lit if (x // 10) % 3 else (255, 180, 100))
        c.disc(x + 2.5, 124, 2, lit)

    # AT&T Stadium: long silver dome, glass walls, twin arches over the roof.
    cx, cy, rx, ry = 236, 128, 88, 30
    for y in range(cy - ry, cy + 1):
        half = rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2))
        c.rect(cx - half, y, cx + half, y + 1, (156, 166, 196) if y < cy - 12 else (120, 130, 168))
    c.rect(cx - rx + 4, cy, cx + rx - 4, 146, (40, 52, 96))
    c.windows(cx - rx + 6, cy + 2, cx + rx - 5, 145, (120, 190, 240), (40, 52, 96), 0.4, 4, 4, 3, 2)
    for x in range(cx - rx + 4, cx + rx - 4, 8):  # glass curtain wall mullions
        c.rect(x, cy, x + 1, 146, (90, 104, 150))
    c.rect(cx - rx + 4, cy, cx + rx - 4, cy + 1, (220, 226, 240))
    for x in range(cx - rx + 8, cx + rx - 8, 6):  # roof panel seams
        c.put(x, cy - 3, (130, 140, 176))
    for off in (-10, 10):
        for x in range(cx - rx - 4, cx + rx + 5):
            t = (x - cx) / (rx + 4)
            y = cy - 6 - 40 * (1 - t * t)
            c.put(x, y + off * 0.2, (236, 238, 248))
            c.put(x, y + 1 + off * 0.2, (190, 196, 220))

    # Flat Texas grass, live oaks, flag.
    # Arch trusses: a lattice between the two curves.
    for x in range(cx - rx - 4, cx + rx + 5, 4):
        t = (x - cx) / (rx + 4)
        y = cy - 6 - 40 * (1 - t * t)
        c.line(x, y - 2, x + 2, y + 2, (190, 196, 220))
    c.ground(146, (84, 116, 54), (122, 150, 70), (58, 86, 44), (176, 164, 150), (204, 192, 176), "pavement")
    # Game-day parking: rows of cars between the stadiums and the path.
    c.rect(0, 147, W, 158, (88, 88, 96))
    for x in range(0, W, 12):
        c.rect(x, 147, x + 1, 158, (210, 210, 200))
    car_colors = [(200, 40, 50), (40, 80, 170), (230, 230, 236), (30, 30, 36), (120, 124, 136), (200, 160, 60)]
    for x in range(2, W - 8, 12):
        if c.rng.random() < 0.8:
            col = c.rng.choice(car_colors)
            c.rect(x + 1, 149, x + 10, 155, col)
            c.rect(x + 3, 150, x + 8, 152, (150, 190, 220))
            c.rect(x + 1, 155, x + 10, 156, darken(col, 0.6))
    # Power line with grackles.
    c.line(0, 108, W, 116, (40, 30, 50))
    for x in (140, 146, 151, 190, 196):
        c.rect(x, 108 + x * 8 // W - 2, x + 2, 108 + x * 8 // W, (30, 24, 40))
    for x in (116, 140, 312):
        c.round_tree(x, 150, 7, (60, 40, 30), (48, 78, 44), (74, 110, 56), (34, 58, 36), 5)
    # Texas flag on a tall pole.
    def texas(fx: int, fy: int) -> tuple[int, int, int]:
        if fx < 4:
            return (255, 255, 255) if (fx, fy) in ((1, 3), (2, 3), (2, 2), (2, 4)) else (30, 60, 140)
        return (240, 240, 240) if fy < 4 else (220, 40, 50)
    c.flag(128, 158, 44, 12, 8, texas, (200, 200, 210), (255, 214, 90), wave=0.8,
           dark=lambda col: darken(col, 0.85))
    for x in (40, 200, 290):
        c.lamp(x, 160, 16, (60, 50, 60), (255, 230, 150))
    c.birds(5, 150, 300, 70, 92, (80, 40, 70))
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
    c.haze(100, 130, (196, 202, 214), 4)
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

    # Palacio de Bellas Artes: white marble with the orange-and-gold domes (left).
    marble, marble_dark = (240, 234, 222), (204, 196, 184)
    dome_o, dome_g = (232, 128, 60), (255, 204, 64)
    c.rect(0, 112, 62, 140, marble)
    c.rect(0, 136, 62, 140, marble_dark)
    for x in range(2, 62, 5):
        c.rect(x, 116, x + 2, 134, marble_dark)  # columns
    c.rect(0, 112, 62, 114, marble_dark)
    c.disc(31, 108, 12, dome_o)
    c.rect(19, 108, 44, 112, marble)
    for x in range(22, 41, 3):  # ribbed dome
        c.line(31, 96, x, 108, dome_g)
    c.disc(31, 95, 3, dome_g)
    c.put(31, 90, dome_g)
    c.rect(30, 91, 32, 93, dome_g)
    for dx in (-24, 24):
        c.disc(31 + dx, 110, 5, dome_o)
        c.put(31 + dx, 104, dome_g)
    # Traffic on Reforma: a red Metrobus and pink-and-white taxis.
    c.rect(150, 138, 186, 146, (190, 40, 40))
    c.rect(152, 139, 184, 142, (180, 210, 230))
    for x in range(156, 184, 6):
        c.rect(x, 139, x + 1, 142, (190, 40, 40))
    for wx in (156, 180):
        c.disc(wx, 146, 1.5, (30, 30, 30))
    for tx0 in (110, 214, 250):
        c.rect(tx0, 141, tx0 + 12, 146, (240, 240, 244))
        c.rect(tx0, 143, tx0 + 12, 144, (232, 100, 150))
        c.rect(tx0 + 3, 139, tx0 + 9, 141, (232, 100, 150))
        c.put(tx0 + 5, 140, (180, 210, 230))
        c.disc(tx0 + 2, 146, 1.5, (30, 30, 30))
        c.disc(tx0 + 10, 146, 1.5, (30, 30, 30))
    # Papel picado strung across the top, clear of the clock.
    for string_y, x0, colors in ((22, 0, [(232, 60, 120), (255, 170, 40), (60, 170, 210), (120, 200, 90)]),
                                 (32, -8, [(160, 80, 200), (255, 90, 70), (255, 220, 60), (60, 170, 210)])):
        for x in range(0, W):
            sag = 4 * math.sin(math.pi * ((x - x0) % 80) / 80)
            c.put(x, string_y + sag, (90, 80, 90))
        for i, fx in enumerate(range(x0 + 3, W, 8)):
            sag = 4 * math.sin(math.pi * ((fx - x0) % 80) / 80)
            col = colors[i % len(colors)]
            c.rect(fx, string_y + sag + 1, fx + 5, string_y + sag + 7, col)
            c.put(fx + 2, string_y + sag + 3, c.get(fx + 7, string_y + 12))  # cut-out
            c.put(fx + 1, string_y + sag + 6, c.get(fx + 7, string_y + 12))
            c.put(fx + 3, string_y + sag + 6, c.get(fx + 7, string_y + 12))
    # Jacarandas in bloom on both sides of the avenue.
    trunk, bloom, bloom_hi, bloom_dark = (80, 60, 60), (150, 102, 204), (196, 156, 236), (110, 72, 164)
    for x, r in ((20, 16), (58, 12), (100, 10), (232, 12), (310, 12)):
        c.round_tree(x, 152, r, trunk, bloom, bloom_hi, bloom_dark, 10)
    c.ground(150, (92, 142, 72), (124, 172, 92), (64, 110, 58), (206, 186, 164), (226, 210, 190), "pavement")
    for _ in range(40):
        c.put(c.rng.randrange(W), c.rng.randrange(PATH_TOP + 1, 176), bloom_hi)
    # A street vendor's cart under a striped umbrella.
    vx = 140
    c.rect(vx, 152, vx + 14, 158, (200, 60, 50))
    c.rect(vx, 152, vx + 14, 153, (255, 220, 120))
    c.disc(vx + 3, 158, 2, (40, 40, 40))
    c.disc(vx + 11, 158, 2, (40, 40, 40))
    c.rect(vx + 7, 140, vx + 8, 152, (80, 70, 70))
    c.poly([(vx - 4, 142), (vx + 7, 136), (vx + 19, 142)], (255, 220, 60))
    for x in range(vx - 3, vx + 18, 4):
        c.line(vx + 7, 136, x, 142, (60, 160, 120))
    for x in (60, 200, 296):
        c.lamp(x, 160, 18, (60, 60, 70), (255, 240, 200))
    return c.img, _meta("jacaranda")


# --- London: rainy blue-hour dusk, Elizabeth Tower, Parliament, the Eye ------
def london() -> tuple[Image.Image, dict]:
    c = Canvas(1859)
    sky = [(22, 26, 48), (32, 38, 66), (46, 52, 86), (70, 68, 104), (106, 88, 116), (150, 112, 112)]
    c.sky(sky, 128)
    # Low rain clouds in long dithered banks.
    cloud, cloud_dark = (62, 64, 96), (44, 48, 78)
    for y0, x0, w in ((14, -10, 150), (22, 170, 170), (36, 40, 120), (8, 230, 100)):
        for y in range(y0, y0 + 5):
            for x in range(x0 + (y - y0) * 2, x0 + w - (y - y0) * 3):
                if 0 <= x < W and ((y - y0) < 3 or (x + y) % 2 == 0):
                    c.put(x, y, cloud if y - y0 < 2 else cloud_dark)

    gold, gold_shade, gold_dark = (214, 170, 96), (164, 120, 70), (112, 80, 58)
    lit, unlit = (255, 222, 140), (82, 62, 62)
    haze_c = (84, 80, 108)

    # The Shard: a glass shard above the clock, faint in the haze.
    glass, glass_hi = (78, 94, 132), (110, 130, 168)
    c.poly([(92, 128), (101, 20), (104, 24), (110, 128)], glass)
    c.line(101, 20, 98, 128, glass_hi)
    for y in range(34, 128, 6):
        c.put(102, y, (170, 190, 220))

    # County Hall on the South Bank, behind the Eye.
    hall, hall_dark = (118, 104, 112), (88, 78, 92)
    c.rect(0, 106, 78, 128, hall)
    c.poly([(0, 106), (6, 100), (72, 100), (78, 106)], (64, 62, 84))
    c.window_grid(3, 109, 76, 126, 2, 3, 5, 6, lit, hall_dark, 0.45)
    c.haze(100, 128, haze_c, 4)

    # London Eye: rim, spokes, lit capsules, A-frame legs.
    ex, ey, r = 34, 80, 30
    rim, spoke, pod = (206, 212, 232), (128, 134, 166), (150, 212, 255)
    for i in range(16):
        a = 2 * math.pi * i / 16
        c.line(ex, ey, ex + math.cos(a) * r, ey + math.sin(a) * r, spoke)
    for t in range(360):
        a = math.radians(t)
        c.put(ex + math.cos(a) * r, ey + math.sin(a) * r, rim)
        c.put(ex + math.cos(a) * (r - 2), ey + math.sin(a) * (r - 2), spoke)
    for i in range(16):
        a = 2 * math.pi * i / 16
        px, py = ex + math.cos(a) * (r + 1), ey + math.sin(a) * (r + 1)
        c.rect(px - 1, py - 1, px + 2, py + 1, pod)
    c.disc(ex, ey, 2, rim)
    c.line(ex, ey, ex - 14, 128, rim, 2)
    c.line(ex, ey, ex + 10, 128, spoke, 2)

    # Palace of Westminster: floodlit gothic river front with pinnacles.
    pal_top = 98
    c.rect(150, pal_top, W, 128, gold)
    for x in range(150, W, 4):
        c.rect(x, pal_top - 3, x + 1, pal_top, gold_shade)  # pinnacles
        c.rect(x + 2, pal_top + 2, x + 3, 126, gold_shade)  # buttresses
    c.window_grid(151, pal_top + 4, W, 126, 1, 4, 4, 6, lit, gold_dark, 0.6)
    c.rect(150, 126, W, 128, gold_dark)
    # Victoria Tower: its battlements peek above the clock.
    vx = 158
    c.rect(vx, 30, vx + 18, 128, gold)
    c.shade_side(vx + 12, 30, vx + 18, 128, gold_shade)
    for x in range(vx, vx + 19, 3):
        c.rect(x, 26, x + 1, 30, gold_shade)
    c.window_grid(vx + 3, 36, vx + 12, 120, 2, 5, 4, 9, lit, gold_dark, 0.7)
    c.flag(vx + 9, 26, 10, 7, 4, lambda fx, fy: (200, 40, 50) if fy in (1, 2) or fx in (3,) else (40, 60, 140),
           (60, 50, 50), gold)

    # Elizabeth Tower (Big Ben) on the right third.
    bx, bw = 282, 18
    c.rect(bx, 66, bx + bw, 128, gold)
    c.shade_side(bx + 12, 66, bx + bw, 128, gold_shade)
    for y in range(72, 124, 6):
        c.rect(bx + 3, y, bx + 5, y + 4, lit)
        c.rect(bx + 8, y, bx + 10, y + 4, lit)
        c.rect(bx, y + 5, bx + bw, y + 6, gold_dark)
    # Clock stage: wider, with the lit dial and hands near ten past ten.
    c.rect(bx - 2, 46, bx + bw + 2, 66, gold)
    c.shade_side(bx + 13, 46, bx + bw + 2, 66, gold_shade)
    c.rect(bx - 2, 46, bx + bw + 2, 47, gold_dark)
    c.rect(bx - 2, 65, bx + bw + 2, 66, gold_dark)
    cx, cy = bx + bw / 2 - 0.5, 56
    c.halo(cx, cy, 11, (230, 200, 130), 3)
    c.disc(cx, cy, 7, gold_dark)
    c.disc(cx, cy, 6, (252, 238, 186))
    for k in range(12):
        a = 2 * math.pi * k / 12
        c.put(cx + math.cos(a) * 5, cy + math.sin(a) * 5, (90, 70, 60))
    c.line(cx, cy, cx - 3, cy - 2, (40, 30, 30))
    c.line(cx, cy, cx + 2, cy - 4, (40, 30, 30))
    # Belfry, then the slate spire with gilded ribs.
    c.rect(bx - 1, 38, bx + bw + 1, 46, gold_shade)
    for x in range(bx + 1, bx + bw, 4):
        c.rect(x, 39, x + 2, 45, (60, 50, 60))
    slate = (46, 50, 70)
    c.poly([(bx - 1, 38), (bx + bw / 2 - 0.5, 14), (bx + bw, 38)], slate)
    c.line(bx + bw / 2 - 0.5, 14, bx + 3, 38, (232, 190, 90))
    c.line(bx + bw / 2 - 0.5, 14, bx + bw - 4, 38, (232, 190, 90))
    for y in (24, 31):
        c.rect(bx + bw / 2 - 3, y, bx + bw / 2 + 2, y + 1, (232, 190, 90))
    c.rect(bx + bw / 2 - 1, 8, bx + bw / 2, 14, (232, 190, 90))

    # The Thames, broken golden reflections of the palace and the tower's dial.
    water, water_hi = (24, 30, 54), (60, 66, 102)
    c.water(128, 146, water, water_hi)
    c.reflect(128, 146, 152, W, gold_shade)
    c.reflect(128, 144, bx + 4, bx + 14, lit, taper=1)
    c.reflect(128, 140, 10, 58, pod)

    # Westminster Bridge: green parapet and arches, between the banks.
    green, green_dark, pier = (52, 106, 86), (34, 72, 62), (110, 108, 118)
    c.rect(0, 118, W, 123, green)
    c.rect(0, 118, W, 119, (96, 150, 124))
    for x in range(0, W, 3):
        c.put(x, 120, green_dark)
    for x0 in range(-6, W, 30):
        c.rect(x0 + 24, 123, x0 + 30, 136, pier)
        for x in range(x0, x0 + 24):
            t = (x - x0 - 12) / 12
            yy = 125 + round(9 * t * t)  # arch soffit: shallow mid-span, deep at the piers
            c.rect(x, 123, x + 1, yy, green_dark)
            c.put(x, yy, green)
    for x in range(14, W, 30):  # bridge lamps
        c.lamp(x, 118, 7, (30, 34, 40), lit, (200, 170, 120))
    for x, col in ((20, (200, 40, 50)), (44, (40, 40, 60)), (276, (60, 90, 160))):
        c.person(x, 118, (40, 44, 60), (220, 180, 150), (30, 30, 40), umbrella=col)

    # Victoria Embankment: granite wall with dolphin lamps, then the road.
    granite, granite_dark = (94, 94, 112), (66, 66, 82)
    c.rect(0, 144, W, 150, granite)
    c.rect(0, 149, W, 150, granite_dark)
    c.brick(0, 144, W, 149, granite_dark, course=3)
    road, road_line = (40, 42, 54), (196, 184, 140)
    c.rect(0, 150, W, PATH_TOP, road)
    for x in range(4, W, 14):
        c.rect(x, 155, x + 7, 156, road_line)
    for x in range(30, W, 60):
        c.lamp(x, 145, 12, (28, 32, 40), lit, (200, 170, 120), double=True)

    # Wet pavement (the sprites' path) with stone joints and puddle reflections.
    pave, pave_hi, pave_dark = (74, 78, 98), (104, 110, 134), (52, 54, 70)
    c.rect(0, PATH_TOP, W, PATH_BOTTOM, pave)
    c.rect(0, PATH_TOP, W, PATH_TOP + 1, (150, 150, 160))  # kerb
    for y in range(PATH_TOP + 5, PATH_BOTTOM, 5):
        c.rect(0, y, W, y + 1, pave_dark)
    for y in range(PATH_TOP + 1, PATH_BOTTOM):
        off = 6 if ((y - PATH_TOP - 1) // 5) % 2 else 0
        for x in range(off, W, 12):
            c.put(x, y, pave_dark)
    for x in range(30, W, 60):  # lamp glow pooled on the wet stone
        c.reflect(PATH_TOP + 1, PATH_BOTTOM - 1, x - 3, x + 4, (150, 140, 120))
    for _ in range(14):
        px, py = c.rng.randrange(W), c.rng.randrange(PATH_TOP + 3, PATH_BOTTOM - 2)
        c.dither_rect(px, py, px + c.rng.randint(6, 12), py + 2, pave_hi, pave)
    c.rect(0, PATH_BOTTOM, W, H, (36, 36, 46))
    c.rect(0, PATH_BOTTOM, W, PATH_BOTTOM + 1, (120, 120, 130))

    # Routemaster bus and a black cab on the road.
    red, red_dark, tyre = (204, 32, 38), (140, 20, 28), (18, 18, 24)
    bx0 = 66
    c.rect(bx0, 135, bx0 + 36, 158, red)
    c.rect(bx0, 135, bx0 + 36, 136, red_dark)
    c.rect(bx0, 146, bx0 + 36, 148, red_dark)
    c.rect(bx0, 156, bx0 + 36, 158, red_dark)
    for wx in range(bx0 + 3, bx0 + 33, 6):
        c.rect(wx, 138, wx + 4, 144, lit)
        c.rect(wx, 149, wx + 4, 154, lit)
    c.rect(bx0 + 31, 149, bx0 + 35, 158, (60, 50, 50))  # open rear platform
    c.rect(bx0 + 3, 138, bx0 + 33, 139, red)  # window tops
    for wx in (bx0 + 6, bx0 + 28):
        c.disc(wx, 158, 2.5, tyre)
    c.rect(bx0 + 10, 147, bx0 + 26, 148, (240, 220, 160))  # route board
    c.reflect(PATH_TOP + 1, PATH_TOP + 9, bx0 + 2, bx0 + 34, red_dark)
    cab, cab_hi = (26, 26, 32), (70, 72, 90)
    tx0 = 206
    c.poly([(tx0, 158), (tx0, 150), (tx0 + 5, 150), (tx0 + 8, 145), (tx0 + 20, 145), (tx0 + 23, 150),
            (tx0 + 28, 150), (tx0 + 28, 158)], cab)
    c.rect(tx0 + 9, 146, tx0 + 14, 150, (110, 120, 150))
    c.rect(tx0 + 15, 146, tx0 + 20, 150, (110, 120, 150))
    c.line(tx0 + 1, 151, tx0 + 27, 151, cab_hi)
    c.rect(tx0 + 12, 144, tx0 + 17, 145, (255, 200, 60))  # TAXI light
    for wx in (tx0 + 5, tx0 + 22):
        c.disc(wx, 158, 2.5, tyre)
    c.put(tx0 + 27, 153, (255, 240, 200))

    # Phone box and pillar box at the back of the pavement.
    def phone_box(x: int) -> None:
        c.halo(x + 4.5, 150, 10, (150, 110, 100), 3)
        c.rect(x, 138, x + 9, 160, red)
        c.rect(x, 138, x + 9, 140, red_dark)
        c.rect(x + 1, 140, x + 8, 142, (20, 20, 24))
        c.rect(x + 2, 140, x + 7, 141, (240, 240, 230))  # TELEPHONE fascia
        c.rect(x + 2, 143, x + 7, 157, lit)
        for yy in range(145, 157, 3):
            c.rect(x + 2, yy, x + 7, yy + 1, red_dark)
        c.rect(x + 4, 143, x + 5, 157, red_dark)
        c.rect(x - 1, 137, x + 10, 138, red_dark)

    phone_box(8)
    phone_box(300)
    c.rect(150, 150, 156, 160, red)
    c.rect(149, 149, 157, 151, red_dark)
    c.rect(151, 153, 155, 154, (20, 20, 24))
    return c.img, _meta("rain")


CITIES = [
    ("builtin:london", "London, England", london),
    ("builtin:la", "Los Angeles, CA", los_angeles),
    ("builtin:bologna", "Bologna, Italy", bologna),
    ("builtin:paris", "Paris, France", paris),
    ("builtin:geneva", "Geneva, Switzerland", geneva),
    ("builtin:uppsala", "Uppsala, Sweden", uppsala),
    ("builtin:stockholm", "Stockholm, Sweden", stockholm),
    ("builtin:arlington", "Arlington, TX", arlington),
    ("builtin:cdmx", "Mexico City (CDMX)", cdmx),
]
