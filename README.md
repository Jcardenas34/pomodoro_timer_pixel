# Pixel Pomodoro

A full-screen pomodoro timer for a second monitor. It shows an 8-bit scene inside a picture-frame border, pixel people walking around, and a split-flap countdown like an old railway board.

- **Backend:** Python (pywebview window, SQLite, Pillow art generation)
- **Frontend:** TypeScript + Vite

## Run it with conda (WSL bash)

This runs Linux Python inside WSL. The window appears on your Windows desktop through WSLg, using Qt WebEngine from conda-forge, so no `sudo apt` is needed.

```bash
cd /mnt/c/Users/Carde/Desktop/git_projects/pomodoro_timer
conda env create -f environment.yml       # one time
conda activate pixel-pomodoro
(cd frontend && npm install && npm run build)
python -m pomodoro --windowed             # drag to monitor 2, then press F
```

Full screen from WSLg may open on your primary monitor. Starting with `--windowed`, dragging the window to the second monitor and pressing `F` is the reliable way.

Under WSL the app turns off Chromium GPU rendering (`--disable-gpu`) because it breaks under WSLg. Software rendering is fast enough here. Data lives in `~/.local/share/PixelPomodoro`.

After changing `environment.yml`, update the env with `conda env update -f environment.yml --prune`.

## Run it natively on Windows (PowerShell)

Use **Windows** Python, not WSL, so the app gets a native WebView2 window that can go full screen on your second monitor.

```powershell
cd frontend
npm install
npm run build
cd ..
py -m pip install -e backend
py -m pomodoro --screen 1      # 0 = primary monitor, 1 = second monitor
```

Options:
- `--windowed` starts windowed instead of full screen.
- `--dev` loads the Vite dev server (`npm run dev`) with devtools.

Data (settings, session history, generated art) lives in `%APPDATA%\PixelPomodoro`.

## Run it on Android (sideloaded APK)

The same frontend runs in a Capacitor shell (`frontend/android/`). There is no Python on the phone.

- **Art:** bundled as pre-rendered PNGs.
- **Settings and session history:** stored on the device.
- **Photo upload:** not included.

**One-time setup (WSL, no sudo):**

```bash
conda env update -f environment.yml --prune   # adds JDK 21
conda activate pixel-pomodoro
bash scripts/setup-android-sdk.sh             # Android SDK -> ~/Android/Sdk, Windows adb.exe
# then add the two exports it prints (ANDROID_HOME, WIN_ADB) to ~/.bashrc
```

**On the phone (once):**
1. Open Settings → About phone and tap *Build number* 7 times.
2. Open Settings → Developer options and turn on *USB debugging*.
3. Plug the phone into the PC and accept the "Allow USB debugging" prompt.

**Build and install:**

```bash
cd frontend
npm run android:build     # exports art + chimes, builds web app, syncs, gradle assembleDebug
npm run android:install   # adb install -r (via Windows adb.exe from WSL)
```

The APK is at `frontend/android/app/build/outputs/apk/debug/app-debug.apk`. Without USB, copy that file to the phone and tap it, then allow "install unknown apps" for your file manager. Rebuilding and reinstalling keeps your settings and history.

**On the phone:**
- The app is landscape and immersive full screen.
- Tap anywhere to show the controls: Start/Pause, Reset, Skip phase, Set task, Settings.
- Back closes a panel. When no panel is open, Back minimizes the app.
- The screen stays on while the timer runs.
- If you lock the phone or switch apps mid-phase, a notification plays the same 8-bit chime at the deadline. Allow notifications when asked on first launch. If the phone is on silent, the chime stays silent.

## Keys

| Key | Action |
|---|---|
| Space | start / pause |
| R | reset the current phase |
| N | skip to the next phase |
| T | set the task you're working on |
| S | settings (border color and width, durations, auto-start, chime) |
| F | toggle full screen |
| Esc | close a panel |

Move the mouse to show the control bar. It hides again after 3 seconds.

## Browser-only development (works from WSL)

```bash
cd backend && python3 -m pomodoro --export-demo ../frontend/public/demo
cd ../frontend && npm run dev        # http://localhost:5173
```

Without pywebview, the frontend falls back to an in-page backend (`src/local.ts`). It stores settings and sessions in localStorage and uses the exported demo art. The Android build uses the same backend.

## Tests

```bash
python3 -m pytest tests        # art generators, sprite template, storage
cd frontend && npm test        # timer state machine
```

## Layout

- `backend/pomodoro/imaging/builtin.py`: procedural Mt Fuji scene (320×180)
- `backend/pomodoro/imaging/sprite_template.py`: role-coded walk-cycle template (hair/skin/shirt/pants/shoes)
- `backend/pomodoro/imaging/sprite.py`: recolors the template into a sprite sheet
- `frontend/src/flipclock.ts`: split-flap digits
- `frontend/src/scene.ts`: canvas scene, wandering sprites, falling petals
- `frontend/src/timer.ts`: deadline-based pomodoro state machine
- `frontend/src/local.ts`: on-device backend (Android and browser), mirrors `storage.py`
- `frontend/src/android.ts`: keep-awake, phase-end chime notification, back button
- `frontend/android/`: Capacitor Android project (landscape, immersive `MainActivity`)
- `backend/pomodoro/audio.py`, `android_art.py`: chime WAVs, launcher icons, splash (`--export-android`)
- `docs/DECISIONS.md`: decision log

## Roadmap

1. ~~Demo: Fuji, walking sprite, flip clock, configurable frame~~
2. Stats panel (session logging is already in place)
3. Photo bank: upload photos → 8-bit backgrounds and likeness sprites
4. PyInstaller single `.exe`
