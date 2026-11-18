"""Entry point: `python -m pomodoro [--dev] [--screen N] [--windowed] [--gui qt]`."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .api import Api
from .assets import ensure_builtin, export_demo
from .android_art import export_android_art, export_windows_icon
from .audio import export_chimes
from .storage import Storage

# A PyInstaller build unpacks frontend/dist under sys._MEIPASS (see PixelPomodoro.spec).
ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[2]
DIST = ROOT / "frontend" / "dist" / "index.html"
DEV_URL = "http://localhost:5173"


def running_in_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text().lower()
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(prog="pixel-pomodoro")
    parser.add_argument("--dev", action="store_true", help="load the Vite dev server instead of frontend/dist")
    parser.add_argument("--screen", type=int, default=None, help="monitor index to open on (0 = primary)")
    parser.add_argument("--windowed", action="store_true", help="start windowed instead of full screen")
    parser.add_argument("--export-demo", type=Path, metavar="DIR",
                        help="write built-in art to DIR for browser-only frontend dev, then exit")
    parser.add_argument("--gui", default="qt" if sys.platform.startswith("linux") else None,
                        help="pywebview GUI backend (default: qt on Linux, native elsewhere)")
    parser.add_argument("--export-android", type=Path, metavar="RES_DIR",
                        help="write chimes, launcher icons and splash into an Android res/ dir, then exit")
    parser.add_argument("--export-icon", type=Path, metavar="ICO",
                        help="write the Windows .exe icon to ICO, then exit")
    args = parser.parse_args()

    if args.export_icon:
        export_windows_icon(args.export_icon)
        print(f"wrote Windows icon to {args.export_icon}")
        return

    if args.export_android:
        export_chimes(args.export_android / "raw")
        export_android_art(args.export_android)
        print(f"wrote Android chimes, icons and splash to {args.export_android}")
        return

    if args.export_demo:
        export_demo(args.export_demo)
        print(f"wrote demo assets to {args.export_demo}")
        return

    if args.gui:
        # Read by pywebview when it picks a backend, including for webview.screens.
        os.environ.setdefault("PYWEBVIEW_GUI", args.gui)
    if running_in_wsl():
        # Chromium's GPU path spews GL errors under WSLg. SwiftShader (Chromium's own software
        # GL) renders correctly and keeps GPU-style compositing: ~46 fps at 1080p versus ~23
        # with --disable-gpu, whose software compositor is slow at upscaling the scene canvas.
        os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--use-gl=swiftshader")

    import webview  # imported late so --export-demo works without a GUI toolkit

    storage = Storage()
    ensure_builtin(storage)
    api = Api(storage)

    if not args.dev and not DIST.exists():
        raise SystemExit(f"{DIST} not found: run `npm run build` in frontend/ first (or pass --dev)")

    screen = None
    if args.screen is not None:
        screens = webview.screens
        if not 0 <= args.screen < len(screens):
            raise SystemExit(f"--screen {args.screen} out of range (found {len(screens)} screens)")
        screen = screens[args.screen]

    window = webview.create_window(
        "Pixel Pomodoro",
        DEV_URL if args.dev else str(DIST),
        js_api=api,
        fullscreen=not args.windowed,
        screen=screen,
        background_color="#000000",
        min_size=(640, 360),
    )
    api._window = window
    webview.start(gui=args.gui, debug=args.dev, http_server=not args.dev)


if __name__ == "__main__":
    main()
