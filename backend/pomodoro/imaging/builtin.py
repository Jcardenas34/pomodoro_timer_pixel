"""Procedurally generated built-in scenes (no binary art in the repo)."""

from __future__ import annotations

import math
import random

from PIL import Image

W, H = 320, 180

# Fixed 8-bit-style palette for the Fuji scene.
C = {
    "sky0": (29, 43, 83),
    "sky1": (68, 44, 110),
    "sky2": (126, 37, 83),
    "sky3": (190, 74, 110),
    "sky4": (255, 119, 120),
    "sky5": (255, 163, 90),
    "sky6": (255, 204, 140),
    "sun": (255, 236, 39),
    "sun2": (255, 190, 60),
    "cloud": (255, 214, 190),
    "cloud2": (230, 150, 160),
    "fuji_dark": (41, 54, 111),
    "fuji_lit": (65, 88, 138),
    "snow": (244, 244, 244),
    "snow_shadow": (194, 195, 210),
    "hill_far": (52, 70, 110),
    "hill_near": (30, 58, 74),
    "tree": (20, 44, 52),
    "lake": (41, 82, 140),
    "lake_hi": (95, 140, 200),
    "lake_sun": (255, 200, 90),
    "grass": (56, 128, 70),
    "grass_hi": (100, 170, 90),
    "grass_dark": (35, 90, 60),
    "path": (171, 120, 80),
    "path_hi": (205, 160, 110),
    "trunk": (82, 50, 40),
    "blossom": (255, 150, 190),
    "blossom_hi": (255, 205, 225),
    "blossom_dark": (210, 100, 150),
}

# Metadata the frontend needs to place sprites.
FUJI_META = {"groundTop": 158, "groundBottom": 176, "petals": True}

LAKE_TOP = 134
GRASS_TOP = 152


def _put(px, x: int, y: int, color) -> None:
    if 0 <= x < W and 0 <= y < H:
        px[x, y] = color


def _sky(px) -> None:
    bands = ["sky0", "sky1", "sky2", "sky3", "sky4", "sky5", "sky6"]
    band_h = LAKE_TOP / len(bands)
    for y in range(LAKE_TOP):
        pos = y / band_h
        i = min(int(pos), len(bands) - 1)
        frac = pos - i
        base, nxt = C[bands[i]], C[bands[min(i + 1, len(bands) - 1)]]
        for x in range(W):
            # Ordered dithering into the next band near each boundary.
            if frac > 0.9:
                px[x, y] = base if (x + y) % 4 == 0 else nxt
            elif frac > 0.7:
                px[x, y] = nxt if (x + y) % 2 == 0 else base
            else:
                px[x, y] = base


def _sun(px, cx: int, cy: int, r: int) -> None:
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                dy = y - cy
                # Retro stripes cut through the lower half.
                if dy > 2 and (dy // 2) % 3 == 0:
                    continue
                _put(px, x, y, C["sun"] if dy < r // 3 else C["sun2"])


def _cloud(px, x0: int, y0: int, w: int, rng: random.Random) -> None:
    puffs = [(x0 + i * 6, y0 - rng.randint(0, 4), rng.randint(4, 7)) for i in range(w // 6)]
    for cx, cy, r in puffs:
        for y in range(cy - r, y0 + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r or (y >= y0 - 1 and x0 <= x <= x0 + w):
                    _put(px, x, y, C["cloud2"] if y >= y0 - 1 else C["cloud"])


def _fuji_top(x: int) -> float:
    """Height profile: flat crater, steep near the top, flattening toward the base."""
    peak_y, base_y, crater, half_w = 34, 132, 9, 130
    d = max(0.0, abs(x - 160) - crater)
    return peak_y + (base_y - peak_y) * (d / half_w) ** 0.72


def _fuji(px, rng: random.Random) -> None:
    jag = [rng.randint(-3, 4) for _ in range(W // 3 + 2)]
    for x in range(W):
        top = int(_fuji_top(x))
        lit = x >= 160
        # Snowline dips lower along gullies.
        snow_line = 58 + jag[x // 3] + (6 if (x // 7) % 3 == 0 else 0) + abs(x - 160) // 10
        for y in range(max(top, 0), LAKE_TOP):
            if y < snow_line:
                color = C["snow"] if lit else C["snow_shadow"]
            else:
                color = C["fuji_lit"] if lit else C["fuji_dark"]
                # Faint ridge lines.
                if (x - 160) % 23 == 0 and y < snow_line + 20:
                    color = C["fuji_dark"] if lit else C["hill_far"]
            px[x, y] = color
        # Crater notch.
        if abs(x - 160) <= 5 and top <= 35:
            _put(px, x, top, C["snow_shadow"])


def _hills(px) -> None:
    for x in range(W):
        far = 118 + 5 * math.sin(x / 23) + 3 * math.sin(x / 9 + 1)
        near = 126 + 4 * math.sin(x / 17 + 2) + 2 * math.sin(x / 5)
        for y in range(int(far), LAKE_TOP):
            px[x, y] = C["hill_far"]
        for y in range(int(near), LAKE_TOP):
            px[x, y] = C["hill_near"]
    # Pine-tree silhouettes along the near hills.
    for tx in range(4, W, 11):
        base = int(126 + 4 * math.sin(tx / 17 + 2) + 2 * math.sin(tx / 5)) + 2
        h = 6 + (tx * 7) % 5
        for i in range(h):
            half = i // 2
            for x in range(tx - half, tx + half + 1):
                _put(px, x, base - h + i, C["tree"])


def _lake(px) -> None:
    for y in range(LAKE_TOP, GRASS_TOP):
        for x in range(W):
            px[x, y] = C["lake"]
    # Broken-line reflection of the snow cap and the sun.
    for y in range(LAKE_TOP + 1, GRASS_TOP, 2):
        depth = y - LAKE_TOP
        mirrored = 34 + depth * 4  # compressed mirror of the mountain
        for x in range(W):
            if _fuji_top(x) < mirrored and (x + y) % 5 != 0 and depth < 12:
                px[x, y] = C["lake_hi"]
        for x in range(236 - 12 + depth, 236 + 12 - depth):
            if (x // 3 + y) % 2 == 0:
                _put(px, x, y, C["lake_sun"])


def _ground(px, rng: random.Random) -> None:
    for y in range(GRASS_TOP, H):
        for x in range(W):
            px[x, y] = C["grass"]
    # Dirt path where the sprites walk.
    for y in range(160, 176):
        edge = 1 if y in (160, 175) else 0
        for x in range(W):
            if edge and (x + y) % 3 == 0:
                continue
            px[x, y] = C["path"]
    for _ in range(140):
        x, y = rng.randrange(W), rng.randrange(161, 175)
        _put(px, x, y, C["path_hi"])
    # Grass tufts.
    for _ in range(110):
        x = rng.randrange(W)
        y = rng.choice([rng.randrange(GRASS_TOP + 2, 159), rng.randrange(177, H)])
        _put(px, x, y, C["grass_hi"])
        _put(px, x - 1, y + 1, C["grass_hi"])
        _put(px, x + 1, y + 1, C["grass_dark"])
    for x in range(W):
        if x % 2 == 0:
            _put(px, x, GRASS_TOP, C["grass_hi"])


def _blossom_tree(px, rng: random.Random) -> None:
    tx, ty = 34, 160
    # Trunk and two branches.
    for y in range(96, ty):
        lean = (ty - y) // 14
        for x in range(tx - 2 + lean, tx + 2 + lean):
            _put(px, x, y, C["trunk"])
    for i in range(22):
        _put(px, tx + 3 + i, 108 - i // 2, C["trunk"])
        _put(px, tx + 3 + i, 109 - i // 2, C["trunk"])
        _put(px, tx + 2 - i, 104 - i // 3, C["trunk"])
    clusters = [(tx + 6, 86, 16), (tx + 26, 94, 12), (tx - 14, 94, 13), (tx + 4, 104, 11), (tx - 20, 106, 8)]
    for cx, cy, r in clusters:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if d <= r - rng.random() * 2.5:
                    if y > cy + r * 0.35:
                        color = C["blossom_dark"]
                    elif rng.random() < 0.18 or (y < cy - r * 0.3 and (x + y) % 3 == 0):
                        color = C["blossom_hi"]
                    else:
                        color = C["blossom"]
                    _put(px, x, y, color)
    # Fallen petals on the grass.
    for _ in range(25):
        _put(px, tx + rng.randint(-30, 40), rng.randint(153, 159), C["blossom_hi"])


def mt_fuji() -> Image.Image:
    rng = random.Random(1707)
    img = Image.new("RGB", (W, H))
    px = img.load()
    _sky(px)
    _sun(px, 236, 76, 20)
    _cloud(px, 40, 44, 48, rng)
    _cloud(px, 250, 30, 40, rng)
    _cloud(px, 196, 58, 24, rng)
    _fuji(px, rng)
    _hills(px)
    _lake(px)
    _ground(px, rng)
    _blossom_tree(px, rng)
    return img
