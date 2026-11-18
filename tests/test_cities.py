import pytest

from pomodoro.assets import builtin_assets, export_demo
from pomodoro.imaging.cities import CITIES
from pomodoro.imaging.paint import GROUND_META, H, W

EFFECTS = {"petals", "jacaranda", "leaves", "snow", "mist", "fireflies", "rain"}


@pytest.mark.parametrize("asset_id,name,make", CITIES, ids=[c[0] for c in CITIES])
def test_city_scene_is_8bit_and_walkable(asset_id, name, make):
    img, meta = make()
    assert img.size == (W, H) == (320, 180)
    # Still a limited, hand-picked palette (Mt Fuji uses 30); the detailed city
    # scenes stay at or under 72 flat colors -- London's night lights are the busiest.
    assert len(img.getcolors(maxcolors=256)) <= 72
    assert meta["groundTop"] == GROUND_META["groundTop"] and meta["groundBottom"] == GROUND_META["groundBottom"]
    assert meta["effect"] in EFFECTS
    # Every pixel is painted: pure black only ever shows up as a gap between layers.
    assert (0, 0, 0) not in {color for _, color in img.getcolors(maxcolors=256)}
    # Deterministic, so installed copies only regenerate when BUILTIN_VERSION changes.
    assert make()[0].tobytes() == img.tobytes()


def test_geneva_mist_starts_at_the_fountain():
    _, meta = dict((i, m) for i, _, m in CITIES)["builtin:geneva"]()
    x, y = meta["effectOrigin"]
    assert 0 <= x < W and 0 <= y < H


def test_all_cities_are_builtin_backgrounds_and_exported(tmp_path):
    ids = [a[0] for a in builtin_assets() if a[1] == "background"]
    assert ids[0] == "builtin:fuji"
    assert ids[1:] == [c[0] for c in CITIES]
    export_demo(tmp_path)
    for asset_id in ids:
        assert (tmp_path / f"{asset_id.split(':')[1]}.png").exists()


def test_london_is_a_rainy_scene():
    _, meta = dict((i, m) for i, _, m in CITIES)["builtin:london"]()
    assert meta["effect"] == "rain"


def test_geneva_flies_the_swiss_flag():
    img, _ = dict((i, m) for i, _, m in CITIES)["builtin:geneva"]()
    px = img.load()
    # The big quay flag: red field with a white cross, on the left third clear of the clock.
    region = [(x, y) for x in range(0, 60) for y in range(90, 130)]
    reds = [p for p in region if px[p] == (218, 41, 28)]
    xs = [x for x, _ in reds]
    ys = [y for _, y in reds]
    cross = [(x, y) for x, y in region
             if min(xs) <= x <= max(xs) and min(ys) <= y <= max(ys) and px[x, y] == (255, 255, 255)]
    assert len(reds) > 80 and len(cross) > 15


def test_fuji_is_unchanged_by_the_city_rework():
    import hashlib

    from pomodoro.imaging.builtin import mt_fuji

    assert hashlib.sha256(mt_fuji().tobytes()).hexdigest() == "d0972283ad797ad93f2a6c88f35748d8ef5bb732b6303a3121dc7f0859cdecba"
