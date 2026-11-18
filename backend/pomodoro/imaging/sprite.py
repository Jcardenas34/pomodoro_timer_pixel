"""Render role-grid templates into colored sprite sheets."""

from __future__ import annotations

from PIL import Image

from .sprite_template import DEFAULT_HAIRSTYLE, FRAME_H, FRAME_W, build_frames, sheet_meta

RGB = tuple[int, int, int]

# Juan: warm brown skin, black hair and mustache, teal shirt, dark jeans,
# white sneakers. He comes in three hairstyles (sprite_template.HAIRSTYLES).
LATINO_DEMO: dict[str, RGB] = {
    "O": (24, 20, 32),
    "H": (44, 38, 44),
    "h": (92, 82, 96),
    "D": (28, 24, 30),
    "S": (196, 132, 88),
    "s": (156, 96, 64),
    "E": (24, 20, 32),
    "W": (255, 255, 255),
    "M": (132, 64, 52),
    "U": (36, 30, 36),
    "T": (40, 160, 152),
    "t": (24, 112, 112),
    "L": (80, 52, 36),
    "P": (52, 72, 128),
    "p": (36, 50, 92),
    "B": (244, 244, 244),
    "b": (176, 176, 190),
}


def shade(color: RGB, factor: float = 0.78) -> RGB:
    """Darker variant of a color, used to derive shadow roles."""
    return tuple(max(0, min(255, round(c * factor))) for c in color)  # type: ignore[return-value]


def palette_from_colors(hair: RGB, skin: RGB, shirt: RGB, pants: RGB, shoes: RGB,
                        mustache: bool = False) -> dict[str, RGB]:
    """Build a full role palette from the five base colors a photo gives us."""
    return {
        "O": (26, 16, 32),
        "H": hair,
        "h": shade(hair, 1.35) if sum(hair) < 200 else shade(hair, 1.15),
        "D": shade(hair, 0.7),
        "S": skin,
        "s": shade(skin),
        "E": (26, 16, 32),
        "W": (255, 255, 255),
        "M": shade(skin, 0.6),
        "U": shade(hair, 0.85) if mustache else skin,
        "T": shirt,
        "t": shade(shirt),
        "L": shade(pants, 0.6),
        "P": pants,
        "p": shade(pants),
        "B": shoes,
        "b": shade(shoes, 0.72),
    }


def render_sheet(palette: dict[str, RGB], hairstyle: str = DEFAULT_HAIRSTYLE) -> tuple[Image.Image, dict]:
    """Return (RGBA sheet with frames laid out horizontally, frontend metadata)."""
    frames = build_frames(hairstyle)
    sheet = Image.new("RGBA", (FRAME_W * len(frames), FRAME_H), (0, 0, 0, 0))
    px = sheet.load()
    for i, rows in enumerate(frames):
        for y, row in enumerate(rows):
            for x, role in enumerate(row):
                if role != ".":
                    px[i * FRAME_W + x, y] = (*palette[role], 255)
    return sheet, sheet_meta()
