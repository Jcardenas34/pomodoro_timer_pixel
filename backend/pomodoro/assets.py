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
from .storage import Storage

# Bump when a generator changes so installed copies are regenerated.
BUILTIN_VERSION = 3


def builtin_assets() -> list[tuple[str, str, str, Image.Image, dict]]:
    sheet, sprite_meta = render_sheet(LATINO_DEMO)
    return [
        ("builtin:fuji", "background", "Mt Fuji at sunset", mt_fuji(), FUJI_META),
        *((asset_id, "background", name, *make()) for asset_id, name, make in CITIES),
        ("builtin:mateo", "sprite", "Mateo", sheet, sprite_meta),
    ]


def ensure_builtin(storage: Storage) -> None:
    installed = {a["id"]: a for a in storage.list_assets()}
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
