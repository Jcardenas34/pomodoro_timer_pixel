from pomodoro.imaging.builtin import H, W, mt_fuji
from pomodoro.imaging.sprite import LATINO_DEMO, render_sheet
from pomodoro.imaging.sprite_template import FRAME_H, FRAME_W, ROLES, build_frames


def test_fuji_is_320x180_with_limited_palette():
    img = mt_fuji()
    assert img.size == (W, H) == (320, 180)
    assert len(img.getcolors(maxcolors=256)) <= 32


def test_fuji_is_deterministic():
    assert mt_fuji().tobytes() == mt_fuji().tobytes()


def test_template_frames_are_uniform_and_use_known_roles():
    frames = build_frames()
    assert len(frames) == 9  # down, up, right x (stand, step A, step B)
    for rows in frames:
        assert len(rows) == FRAME_H
        assert all(len(r) == FRAME_W for r in rows)
        assert set("".join(rows)) <= ROLES


def test_every_direction_has_distinct_step_frames():
    frames = ["".join(f) for f in build_frames()]
    for d in range(3):
        stand, a, b = frames[d * 3 : d * 3 + 3]
        assert len({stand, a, b}) == 3


def test_sheet_dimensions_and_meta():
    sheet, meta = render_sheet(LATINO_DEMO)
    assert sheet.size == (9 * 32, 32)
    assert sheet.mode == "RGBA"
    assert sheet.getpixel((0, 0))[3] == 0
    assert meta["walk"]["down"] == [0, 1, 0, 2]
    assert meta["idle"] == {"down": 0, "up": 3, "right": 6}
