"""Assembles docs/screenshots/.frames (written by frontend/scripts/capture-screenshots.mjs)
into docs/screenshots/hero.gif, then deletes the frames.

Each frame gets its own palette, undithered, so the pixel art stays crisp when a scene
change brings in a whole new set of colors."""

import json
import shutil
import sys
from pathlib import Path

from PIL import Image

SHOTS = Path(__file__).resolve().parents[1] / "docs" / "screenshots"
FRAMES = SHOTS / ".frames"
WIDTH = int(sys.argv[1]) if len(sys.argv) > 1 else 960


def main() -> None:
    meta = json.loads((FRAMES / "frames.json").read_text())
    images, durations = [], []
    for f in meta:
        im = Image.open(FRAMES / f["file"]).convert("RGB")
        if im.width != WIDTH:
            im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.Resampling.LANCZOS)
        images.append(im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
        durations.append(max(20, round(f["ms"] / 10) * 10))  # GIF delays are in centiseconds
    out = SHOTS / "hero.gif"
    images[0].save(out, save_all=True, append_images=images[1:], duration=durations, loop=0,
                   optimize=True, disposal=1)
    shutil.rmtree(FRAMES)
    print(f"wrote {out} ({len(images)} frames, {out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
