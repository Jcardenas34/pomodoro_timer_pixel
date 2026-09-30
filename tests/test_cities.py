import pytest

from pomodoro.assets import builtin_assets, export_demo
from pomodoro.imaging.cities import CITIES
from pomodoro.imaging.paint import GROUND_META, H, W

EFFECTS = {"petals", "jacaranda", "leaves", "snow", "mist", "fireflies"}


@pytest.mark.parametrize("asset_id,name,make", CITIES, ids=[c[0] for c in CITIES])
def test_city_scene_is_8bit_and_walkable(asset_id, name, make):
    img, meta = make()
    assert img.size == (W, H) == (320, 180)
    # Limited palette like Mt Fuji (30 colors); Arlington's sunset + stadium is the busiest.
    assert len(img.getcolors(maxcolors=256)) <= 40
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
