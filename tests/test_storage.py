import time

from pomodoro.assets import builtin_assets, ensure_builtin
from pomodoro.storage import DEFAULT_SETTINGS, Storage


def test_settings_merge_defaults_and_ignore_unknown(tmp_path):
    s = Storage(tmp_path)
    assert s.get_settings() == DEFAULT_SETTINGS
    s.save_settings({"frameColor": "#ff0000", "bogus": 1})
    got = s.get_settings()
    assert got["frameColor"] == "#ff0000"
    assert "bogus" not in got


def test_sessions_aggregate_per_task(tmp_path):
    s = Storage(tmp_path)
    a = s.start_session("Write", "work")
    s.end_session(a, 1500, True)
    b = s.start_session("Write", "work")
    s.end_session(b, 300, False)
    c = s.start_session(None, "work")
    s.end_session(c, 60, True)
    stats = {r["task"]: r for r in s.stats(time.time() - 3600)}
    assert stats["Write"] == {"task": "Write", "seconds": 1800, "pomodoros": 1}
    assert stats["(no task)"]["seconds"] == 60


def test_builtin_assets_install_once(tmp_path):
    s = Storage(tmp_path)
    ensure_builtin(s)
    ensure_builtin(s)
    ids = sorted(a["id"] for a in s.list_assets())
    assert ids == sorted(a[0] for a in builtin_assets())  # each built-in exactly once
    assert {"builtin:fuji", "builtin:paris", "builtin:london"} <= set(ids)
    assert {"builtin:juan-crew", "builtin:juan-sidepart", "builtin:juan-wavy"} <= set(ids)


def test_default_sprite_setting_names_an_installed_sprite(tmp_path):
    s = Storage(tmp_path)
    ensure_builtin(s)
    sprite_ids = {a["id"] for a in s.list_assets("sprite")}
    assert s.get_settings()["sprite"] in sprite_ids


def test_renamed_builtin_sprite_replaces_the_old_one(tmp_path):
    from PIL import Image

    s = Storage(tmp_path)
    s.put_asset("builtin:mateo", "sprite", "Mateo", Image.new("RGBA", (8, 8)), {"version": 3})
    old_path = tmp_path / "assets" / "builtin_mateo.png"
    assert old_path.exists()
    ensure_builtin(s)
    sprites = [a for a in s.list_assets("sprite")]
    assert {a["id"] for a in sprites} >= {"builtin:juan-original", "builtin:juan-crew", "builtin:juan-sidepart",
                                          "builtin:juan-wavy"}
    assert all(a["name"].startswith("Juan") for a in sprites)
    assert not old_path.exists()


def test_each_hairstyle_has_a_clean_shaven_variant(tmp_path):
    s = Storage(tmp_path)
    ensure_builtin(s)
    sprites = {a["id"]: a for a in s.list_assets("sprite")}
    for style in ("crew", "sidepart", "wavy"):
        base, shaven = sprites[f"builtin:juan-{style}"], sprites[f"builtin:juan-{style}-shaven"]
        assert base["meta"]["mustache"] is True and "base" not in base["meta"]
        assert shaven["meta"] == {**shaven["meta"], "mustache": False, "base": base["id"]}
    assert s.get_settings()["mustache"] is True
    # The original Juan never had a mustache, so there is nothing to shave.
    assert sprites["builtin:juan-original"]["meta"]["mustache"] is False
    assert "builtin:juan-original-shaven" not in sprites
