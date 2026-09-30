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
    assert {"builtin:fuji", "builtin:paris", "builtin:mateo"} <= set(ids)
