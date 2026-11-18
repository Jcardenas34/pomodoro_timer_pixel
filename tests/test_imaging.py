from pomodoro.imaging.builtin import H, W, mt_fuji
from pomodoro.imaging.sprite import LATINO_DEMO, render_sheet
from pomodoro.imaging.sprite_template import FRAME_H, FRAME_W, ROLES, build_frames

# The pre-hairstyle Juan as committed in d6443d3..cecfb5d (rendered from git HEAD).
ORIGINAL_SHEET_SHA256 = "7fcd743d8052d098c6fed2d051f60b9cc8cb90f54d68dd16df3e6fcb4799034c"


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


def test_three_short_to_medium_hairstyles_plus_the_original():
    from pomodoro.imaging.sprite_template import HAIRSTYLES

    assert set(HAIRSTYLES) == {"original", "crew", "sidepart", "wavy"}
    for style, heads in HAIRSTYLES.items():
        assert set(heads) == {"down", "up", "right"}
        for direction, grid in heads.items():
            assert len(grid) == 16 and all(len(r) == 16 for r in grid), (style, direction)
            assert set("".join(grid)) <= ROLES
    # Each style really is a different haircut from the front.
    fronts = {"".join(h["down"]) for h in HAIRSTYLES.values()}
    assert len(fronts) == 4


def test_juan_has_a_mustache_facing_front_and_sideways_but_not_from_behind():
    from pomodoro.imaging.sprite_template import HAIRSTYLES

    for style, heads in HAIRSTYLES.items():
        if style == "original":
            assert "U" not in "".join(g for grid in heads.values() for g in grid)
            continue
        assert "U" in "".join(heads["down"]) and "U" in "".join(heads["right"])
        assert "U" not in "".join(heads["up"])
    assert LATINO_DEMO["U"] != LATINO_DEMO["S"]


def test_mustache_role_falls_back_to_skin_when_off():
    from pomodoro.imaging.sprite import palette_from_colors

    hair, skin = (40, 30, 30), (200, 150, 110)
    off = palette_from_colors(hair, skin, (1, 2, 3), (4, 5, 6), (7, 8, 9))
    on = palette_from_colors(hair, skin, (1, 2, 3), (4, 5, 6), (7, 8, 9), mustache=True)
    assert off["U"] == skin and on["U"] != skin


def test_every_hairstyle_renders_a_full_sheet():
    from pomodoro.imaging.sprite_template import HAIRSTYLES

    for style in HAIRSTYLES:
        sheet, meta = render_sheet(LATINO_DEMO, style)
        assert sheet.size == (9 * 32, 32)
        # Nothing may spill above the frame: the top row stays transparent.
        assert all(sheet.getpixel((x, 0))[3] == 0 for x in range(sheet.width))


def test_clean_shaven_sheet_has_no_mustache_pixels():
    shaven = {**LATINO_DEMO, "U": LATINO_DEMO["S"]}
    for style in ("crew", "sidepart", "wavy"):
        with_m, _ = render_sheet(LATINO_DEMO, style)
        without, _ = render_sheet(shaven, style)
        colors = {c for _, c in without.getcolors(maxcolors=256)}
        assert (*LATINO_DEMO["U"], 255) in {c for _, c in with_m.getcolors(maxcolors=256)}
        assert (*LATINO_DEMO["U"], 255) not in colors


def test_original_juan_is_kept_pixel_for_pixel():
    """The pre-hairstyle Juan (D-0008), exactly as first drawn: 9 frames of 32x32."""
    import hashlib

    sheet, _ = render_sheet(LATINO_DEMO, "original")
    assert hashlib.sha256(sheet.tobytes()).hexdigest() == ORIGINAL_SHEET_SHA256
