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

Without pywebview, the frontend falls back to a mock backend (`src/bridge.ts`). It uses localStorage for settings and the exported demo art.

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
- `docs/DECISIONS.md`: decision log

## Roadmap

1. ~~Demo: Fuji, walking sprite, flip clock, configurable frame~~
2. Stats panel (session logging is already in place)
3. Photo bank: upload photos → 8-bit backgrounds and likeness sprites
4. PyInstaller single `.exe`
