"""Launcher icons and splash screens for the Android build, drawn from the built-in art.

    python -m pomodoro --export-android-art frontend/android/app/src/main/res
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from .imaging.builtin import mt_fuji
from .imaging.sprite import LATINO_DEMO, render_sheet

# Density buckets: legacy icon px, adaptive layer px (108 dp).
DENSITIES = {"mdpi": (48, 108), "hdpi": (72, 162), "xhdpi": (96, 216), "xxhdpi": (144, 324), "xxxhdpi": (192, 432)}
# Square around Mt Fuji's peak down to the grass the sprite stands on (scene is 320x180).
ICON_CROP = (88, 32, 232, 176)


def _sprite() -> Image.Image:
    sheet, meta = render_sheet(LATINO_DEMO)
    w, h = meta["frameWidth"], meta["frameHeight"]
    i = meta["idle"]["down"]
    return sheet.crop((i * w, 0, (i + 1) * w, h))


def _scaled(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    return im.resize(size, Image.NEAREST)


def _cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Scale to fill `size`, cropping the overflow evenly (like CSS object-fit: cover)."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    big = im.resize((max(tw, round(im.width * scale)), max(th, round(im.height * scale))), Image.NEAREST)
    left, top = (big.width - tw) // 2, (big.height - th) // 2
    return big.crop((left, top, left + tw, top + th))


def icon_layers(px: int) -> tuple[Image.Image, Image.Image]:
    """(background, foreground) adaptive-icon layers of px x px."""
    background = _scaled(mt_fuji().crop(ICON_CROP).convert("RGBA"), (px, px))
    foreground = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    # Keep the sprite inside the 66 dp safe zone that every launcher mask shows.
    sprite = _scaled(_sprite(), (px // 2, px // 2))
    foreground.alpha_composite(sprite, ((px - sprite.width) // 2, px * 58 // 108 - sprite.height // 2))
    return background, foreground


def legacy_icon(px: int) -> Image.Image:
    # Pre-Android-8 icons are not masked: render the 108 dp layers and trim to the visible 72 dp.
    layer = px * 108 // 72
    bg, fg = icon_layers(layer)
    bg.alpha_composite(fg)
    inset = (layer - px) // 2
    return bg.crop((inset, inset, inset + px, inset + px))


def export_android_art(res_dir: Path) -> None:
    for density, (legacy_px, layer_px) in DENSITIES.items():
        out = res_dir / f"mipmap-{density}"
        out.mkdir(parents=True, exist_ok=True)
        bg, fg = icon_layers(layer_px)
        bg.save(out / "ic_launcher_background.png")
        fg.save(out / "ic_launcher_foreground.png")
        icon = legacy_icon(legacy_px)
        icon.save(out / "ic_launcher.png")
        icon.save(out / "ic_launcher_round.png")

    adaptive = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@mipmap/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
"""
    anydpi = res_dir / "mipmap-anydpi-v26"
    anydpi.mkdir(parents=True, exist_ok=True)
    for name in ("ic_launcher.xml", "ic_launcher_round.xml"):
        (anydpi / name).write_text(adaptive)

    # Splash: the Fuji scene, replacing Capacitor's placeholder in every existing size.
    scene = mt_fuji().convert("RGB")
    for splash in res_dir.glob("drawable*/splash.png"):
        with Image.open(splash) as old:
            size = old.size
        _cover(scene, size).save(splash)
