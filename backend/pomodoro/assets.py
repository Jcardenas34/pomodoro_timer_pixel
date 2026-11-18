"""Built-in asset installation and export for the frontend."""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path

from PIL import Image

from .imaging.builtin import FUJI_META, mt_fuji
from .imaging.cities import CITIES
from .imaging.sprite import LATINO_DEMO, render_sheet
from .imaging.sprite_template import HAIRSTYLE_NAMES, HAIRSTYLES
from .storage import Storage

# Bump when a generator changes so installed copies are regenerated.
BUILTIN_VERSION = 7


def juan_sprites() -> list[tuple[str, str, str, Image.Image, dict]]:
    """Juan in each hairstyle, with his mustache and clean-shaven.

    The picker lists the mustache versions; each "-shaven" sheet names it as its
    `base`, and the frontend swaps to it when the Mustache setting is off. The
    original Juan never had a mustache, so he has no variant.
    """
    shaven = {**LATINO_DEMO, "U": LATINO_DEMO["S"]}
    sprites = []
    for style, label in HAIRSTYLE_NAMES.items():
        base_id = f"builtin:juan-{style}"
        has_mustache = any("U" in "".join(grid) for grid in HAIRSTYLES[style].values())
        sheet, meta = render_sheet(LATINO_DEMO, style)
        sprites.append((base_id, "sprite", f"Juan · {label}", sheet,
                        {**meta, "hairstyle": style, "mustache": has_mustache}))
        if not has_mustache:
            continue
        sheet, meta = render_sheet(shaven, style)
        sprites.append((f"{base_id}-shaven", "sprite", f"Juan · {label} (clean-shaven)", sheet,
                        {**meta, "hairstyle": style, "mustache": False, "base": base_id}))
    return sprites


def builtin_assets() -> list[tuple[str, str, str, Image.Image, dict]]:
    return [
        ("builtin:fuji", "background", "Mt Fuji at sunset", mt_fuji(), FUJI_META),
        *((asset_id, "background", name, *make()) for asset_id, name, make in CITIES),
        *juan_sprites(),
    ]


def ensure_builtin(storage: Storage) -> None:
    installed = {a["id"]: a for a in storage.list_assets()}
    current_ids = {a[0] for a in builtin_assets()}
    # Drop built-ins that were renamed or retired (e.g. builtin:mateo -> builtin:juan),
    # otherwise the old copy would keep walking around next to the new one.
    for asset_id in installed:
        if asset_id.startswith("builtin:") and asset_id not in current_ids:
            storage.delete_asset(asset_id)
    for asset_id, kind, name, image, meta in builtin_assets():
        current = installed.get(asset_id)
        if current and current["meta"].get("version") == BUILTIN_VERSION and Path(current["path"]).exists():
            continue
        storage.put_asset(asset_id, kind, name, image, {**meta, "version": BUILTIN_VERSION})


def data_url(path: str | Path) -> str:
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


def to_frontend(asset: dict) -> dict:
    return {"id": asset["id"], "kind": asset["kind"], "name": asset["name"], "meta": asset["meta"],
            "active": asset["active"], "src": data_url(asset["path"])}


def export_demo(out_dir: Path) -> None:
    """Write built-in assets as plain files for browser-only frontend development."""
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for asset_id, kind, name, image, meta in builtin_assets():
        filename = asset_id.split(":")[1] + ".png"
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        (out_dir / filename).write_bytes(buf.getvalue())
        manifest.append({"id": asset_id, "kind": kind, "name": name, "meta": meta, "active": True,
                         "src": f"demo/{filename}"})
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    # Remove art for built-ins that no longer exist (e.g. mateo.png after the rename to Juan).
    keep = {m["src"].split("/")[-1] for m in manifest}
    for stale in out_dir.glob("*.png"):
        if stale.name not in keep:
            stale.unlink()
