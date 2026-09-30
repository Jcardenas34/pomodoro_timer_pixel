"""Shared pixel-painting helpers for the procedural city scenes (cities.py).

Same conventions as builtin.py: 320x180, hard-edged shapes, ordered dithering
between color bands, and a sprite path along the bottom of every scene.
"""

from __future__ import annotations

import math
import random
from typing import Callable, Sequence

from PIL import Image, ImageDraw

W, H = 320, 180
RGB = tuple[int, int, int]

# Every scene keeps the sprites' walkable band in the same place as Mt Fuji.
GROUND_META = {"groundTop": 158, "groundBottom": 176}
PATH_TOP, PATH_BOTTOM = 160, 176

# 3x5 pixel font, enough for signs.
FONT = {
    "H": ["101", "101", "111", "101", "101"],
    "O": ["111", "101", "101", "101", "111"],
    "L": ["100", "100", "100", "100", "111"],
    "Y": ["101", "101", "010", "010", "010"],
    "W": ["101", "101", "101", "111", "101"],
    "D": ["110", "101", "101", "101", "110"],
}


class Canvas:
    def __init__(self, seed: int) -> None:
        self.img = Image.new("RGB", (W, H))
        self.px = self.img.load()
        self.draw = ImageDraw.Draw(self.img)
        self.rng = random.Random(seed)

    # --- primitives --------------------------------------------------------
    def put(self, x: float, y: float, c: RGB) -> None:
        x, y = int(x), int(y)
        if 0 <= x < W and 0 <= y < H:
            self.px[x, y] = c

    def get(self, x: int, y: int) -> RGB:
        return self.px[max(0, min(W - 1, x)), max(0, min(H - 1, y))]

    def rect(self, x0: float, y0: float, x1: float, y1: float, c: RGB) -> None:
        """Filled rectangle, x1/y1 exclusive."""
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        if x1 > x0 and y1 > y0:
            self.draw.rectangle((x0, y0, x1 - 1, y1 - 1), fill=c)

    def poly(self, pts: Sequence[tuple[float, float]], c: RGB) -> None:
        self.draw.polygon([(round(x), round(y)) for x, y in pts], fill=c)

    def line(self, x0: float, y0: float, x1: float, y1: float, c: RGB, width: int = 1) -> None:
        self.draw.line((round(x0), round(y0), round(x1), round(y1)), fill=c, width=width)

    def disc(self, cx: float, cy: float, r: float, c: RGB) -> None:
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.put(x, y, c)

    def text(self, s: str, x: int, y: int, c: RGB, gap: int = 1) -> None:
        for ch in s:
            for dy, row in enumerate(FONT[ch]):
                for dx, bit in enumerate(row):
                    if bit == "1":
                        self.put(x + dx, y + dy, c)
            x += 3 + gap

    def dither_rect(self, x0: int, y0: int, x1: int, y1: int, a: RGB, b: RGB) -> None:
        """50% checkerboard of a and b (8-bit stand-in for a blend)."""
        for y in range(max(0, y0), min(H, y1)):
            for x in range(max(0, x0), min(W, x1)):
                self.px[x, y] = a if (x + y) % 2 == 0 else b

    # --- scenery ------------------------------------------------------------
    def sky(self, bands: Sequence[RGB], bottom: int, top: int = 0) -> None:
        """Horizontal color bands with ordered dithering at each boundary (as in builtin.py)."""
        band_h = (bottom - top) / len(bands)
        for y in range(top, bottom):
            pos = (y - top) / band_h
            i = min(int(pos), len(bands) - 1)
            frac = pos - i
            base, nxt = bands[i], bands[min(i + 1, len(bands) - 1)]
            for x in range(W):
                if frac > 0.9:
                    self.px[x, y] = base if (x + y) % 4 == 0 else nxt
                elif frac > 0.7:
                    self.px[x, y] = nxt if (x + y) % 2 == 0 else base
                else:
                    self.px[x, y] = base

    def sun(self, cx: int, cy: int, r: int, c: RGB, c2: RGB, stripes: bool = True) -> None:
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    dy = y - cy
                    if stripes and dy > 2 and (dy // 2) % 3 == 0:
                        continue
                    self.put(x, y, c if dy < r // 3 else c2)

    def moon(self, cx: int, cy: int, r: int, c: RGB, shade: RGB) -> None:
        self.disc(cx, cy, r, c)
        for x, y in ((cx - 2, cy - 1), (cx + 1, cy + 2), (cx + 2, cy - 2)):
            self.put(x, y, shade)

    def stars(self, n: int, y_max: int, colors: Sequence[RGB], avoid: Callable[[int, int], bool] | None = None) -> None:
        for _ in range(n):
            x, y = self.rng.randrange(W), self.rng.randrange(y_max)
            if avoid and avoid(x, y):
                continue
            self.put(x, y, self.rng.choice(colors))

    def cloud(self, x0: int, y0: int, w: int, c: RGB, c2: RGB) -> None:
        rng = self.rng
        puffs = [(x0 + i * 6, y0 - rng.randint(0, 4), rng.randint(4, 7)) for i in range(w // 6)]
        for cx, cy, r in puffs:
            for y in range(cy - r, y0 + 1):
                for x in range(cx - r, cx + r + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r or (y >= y0 - 1 and x0 <= x <= x0 + w):
                        self.put(x, y, c2 if y >= y0 - 1 else c)

    def ridge(self, profile: Callable[[int], float], bottom: int, c: RGB) -> None:
        for x in range(W):
            for y in range(max(0, int(profile(x))), bottom):
                self.px[x, y] = c

    def water(self, top: int, bottom: int, c: RGB, hi: RGB) -> None:
        self.rect(0, top, W, bottom, c)
        for y in range(top + 2, bottom, 3):
            for x in range(self.rng.randrange(6), W, self.rng.randint(14, 22)):
                self.rect(x, y, x + self.rng.randint(3, 8), y + 1, hi)

    def reflect(self, top: int, bottom: int, x0: int, x1: int, c: RGB, taper: int = 0) -> None:
        """Broken-line reflection column (sun, lights, towers) on water."""
        for y in range(top + 1, bottom, 2):
            d = (y - top) * taper // 4
            for x in range(x0 + d, x1 - d):
                if (x // 2 + y) % 3 != 0:
                    self.put(x, y, c)

    def ground(self, top: int, base: RGB, hi: RGB, dark: RGB, path: RGB, path_hi: RGB,
               style: str = "dirt") -> None:
        """Grass/snow/pavement from `top` down with the sprite path at PATH_TOP..PATH_BOTTOM."""
        rng = self.rng
        self.rect(0, top, W, H, base)
        for x in range(0, W, 2):
            self.put(x, top, hi)
        for _ in range(110):
            x = rng.randrange(W)
            y = rng.choice([rng.randrange(top + 2, PATH_TOP - 1), rng.randrange(PATH_BOTTOM + 1, H)])
            self.put(x, y, hi)
            self.put(x - 1, y + 1, hi)
            self.put(x + 1, y + 1, dark)
        for y in range(PATH_TOP, PATH_BOTTOM):
            edge = y in (PATH_TOP, PATH_BOTTOM - 1)
            for x in range(W):
                if style == "dirt" and edge and (x + y) % 3 == 0:
                    continue
                self.px[x, y] = path
        if style == "dirt":
            for _ in range(140):
                self.put(rng.randrange(W), rng.randrange(PATH_TOP + 1, PATH_BOTTOM - 1), path_hi)
        elif style == "cobble":
            for y in range(PATH_TOP, PATH_BOTTOM):
                off = 2 if (y - PATH_TOP) // 3 % 2 else 0
                for x in range(W):
                    if (y - PATH_TOP) % 3 == 2 or (x + off) % 5 == 0:
                        self.px[x, y] = path_hi
        elif style == "pavement":
            for x in range(W):
                self.px[x, PATH_TOP] = path_hi
                self.px[x, PATH_BOTTOM - 1] = dark
            for x in range(0, W, 16):
                for y in range(PATH_TOP + 1, PATH_BOTTOM - 1):
                    self.px[x, y] = path_hi
        elif style == "snow":
            for _ in range(90):
                self.put(rng.randrange(W), rng.randrange(PATH_TOP + 1, PATH_BOTTOM - 1), path_hi)

    def windows(self, x0: int, y0: int, x1: int, y1: int, lit: RGB, dark: RGB,
                lit_ratio: float = 0.5, dx: int = 3, dy: int = 4, w: int = 1, h: int = 2) -> None:
        for y in range(y0, y1 - h + 1, dy):
            for x in range(x0, x1 - w + 1, dx):
                self.rect(x, y, x + w, y + h, lit if self.rng.random() < lit_ratio else dark)

    # --- trees --------------------------------------------------------------
    def pine(self, x: int, base: int, h: int, c: RGB, snow: RGB | None = None) -> None:
        for i in range(h):
            half = i // 2
            for xx in range(x - half, x + half + 1):
                color = snow if snow and i % 4 == 0 and abs(xx - x) >= half - 1 else c
                self.put(xx, base - h + i, color)

    def palm(self, x: int, base: int, h: int, trunk: RGB, frond: RGB, frond2: RGB) -> None:
        # Slightly curved trunk.
        for i in range(h):
            lean = round(3 * math.sin(i / h * math.pi / 2))
            self.put(x + lean, base - i, trunk)
            if i % 3 == 0:
                self.put(x + lean + 1, base - i, trunk)
        tx, ty = x + 3, base - h
        for ang, length in ((-160, 13), (-130, 11), (-100, 8), (-60, 11), (-25, 13), (0, 10), (180, 10)):
            a = math.radians(ang)
            for s in range(length):
                droop = (s / length) ** 2 * 5
                px = tx + math.cos(a) * s
                py = ty + math.sin(a) * s * 0.6 + droop
                self.put(px, py, frond if s < length - 3 else frond2)
                self.put(px, py + 1, frond2)
        self.disc(tx, ty, 1.5, frond2)

    def round_tree(self, cx: int, base: int, r: int, trunk: RGB, leaf: RGB, leaf_hi: RGB, leaf_dark: RGB,
                   trunk_h: int = 8) -> None:
        self.rect(cx - 1, base - trunk_h, cx + 1, base, trunk)
        cy = base - trunk_h - r + 2
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = math.hypot(x - cx, y - cy)
                if d <= r - self.rng.random() * 1.8:
                    if y > cy + r * 0.35:
                        c = leaf_dark
                    elif self.rng.random() < 0.18 or (y < cy - r * 0.3 and (x + y) % 3 == 0):
                        c = leaf_hi
                    else:
                        c = leaf
                    self.put(x, y, c)
