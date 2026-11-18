"""SQLite persistence and on-disk asset store."""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

DEFAULT_SETTINGS = {
    "frameColor": "#000000",
    "frameWidth": 6,
    "workMinutes": 25,
    "shortMinutes": 5,
    "longMinutes": 15,
    "longEvery": 4,
    "autoStartBreaks": True,
    "autoStartWork": False,
    "sound": True,
    "background": "builtin:fuji",
    "sprite": "builtin:juan-sidepart",
    "mustache": True,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, created_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY, task_id INTEGER REFERENCES tasks(id), phase TEXT NOT NULL,
    started_at REAL NOT NULL, ended_at REAL, seconds INTEGER DEFAULT 0, completed INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY, kind TEXT NOT NULL, name TEXT NOT NULL, path TEXT NOT NULL,
    meta_json TEXT NOT NULL, active INTEGER DEFAULT 1, created_at REAL NOT NULL);
"""


def default_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "PixelPomodoro"


class Storage:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = Path(data_dir or default_data_dir())
        self.asset_dir = self.data_dir / "assets"
        self.asset_dir.mkdir(parents=True, exist_ok=True)
        # pywebview calls the API from worker threads.
        self.db = sqlite3.connect(self.data_dir / "pomodoro.db", check_same_thread=False)
        self.db.executescript(SCHEMA)
        self.db.commit()

    # --- settings -------------------------------------------------------
    def get_settings(self) -> dict:
        stored = {k: json.loads(v) for k, v in self.db.execute("SELECT key, value_json FROM settings")}
        return {**DEFAULT_SETTINGS, **stored}

    def save_settings(self, values: dict) -> dict:
        for key, value in values.items():
            if key in DEFAULT_SETTINGS:
                self.db.execute(
                    "INSERT OR REPLACE INTO settings (key, value_json) VALUES (?, ?)", (key, json.dumps(value))
                )
        self.db.commit()
        return self.get_settings()

    # --- sessions -------------------------------------------------------
    def _task_id(self, name: str | None) -> int | None:
        name = (name or "").strip()
        if not name:
            return None
        self.db.execute("INSERT OR IGNORE INTO tasks (name, created_at) VALUES (?, ?)", (name, time.time()))
        return self.db.execute("SELECT id FROM tasks WHERE name = ?", (name,)).fetchone()[0]

    def start_session(self, task: str | None, phase: str) -> int:
        cur = self.db.execute(
            "INSERT INTO sessions (task_id, phase, started_at) VALUES (?, ?, ?)",
            (self._task_id(task), phase, time.time()),
        )
        self.db.commit()
        return cur.lastrowid

    def end_session(self, session_id: int, seconds: int, completed: bool) -> None:
        self.db.execute(
            "UPDATE sessions SET ended_at = ?, seconds = ?, completed = ? WHERE id = ?",
            (time.time(), int(seconds), int(completed), session_id),
        )
        self.db.commit()

    def stats(self, since: float) -> list[dict]:
        rows = self.db.execute(
            """SELECT COALESCE(t.name, '(no task)'), SUM(s.seconds), SUM(s.completed)
               FROM sessions s LEFT JOIN tasks t ON t.id = s.task_id
               WHERE s.phase = 'work' AND s.started_at >= ?
               GROUP BY s.task_id ORDER BY SUM(s.seconds) DESC""",
            (since,),
        )
        return [{"task": name, "seconds": secs or 0, "pomodoros": done or 0} for name, secs, done in rows]

    # --- assets ---------------------------------------------------------
    def put_asset(self, asset_id: str, kind: str, name: str, image, meta: dict) -> Path:
        path = self.asset_dir / f"{asset_id.replace(':', '_')}.png"
        image.save(path)
        self.db.execute(
            "INSERT OR REPLACE INTO assets (id, kind, name, path, meta_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (asset_id, kind, name, str(path), json.dumps(meta), time.time()),
        )
        self.db.commit()
        return path

    def delete_asset(self, asset_id: str) -> None:
        row = self.db.execute("SELECT path FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if row:
            Path(row[0]).unlink(missing_ok=True)
            self.db.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
            self.db.commit()

    def list_assets(self, kind: str | None = None) -> list[dict]:
        sql = "SELECT id, kind, name, path, meta_json, active FROM assets"
        args: tuple = ()
        if kind:
            sql += " WHERE kind = ?"
            args = (kind,)
        return [
            {"id": i, "kind": k, "name": n, "path": p, "meta": json.loads(m), "active": bool(a)}
            for i, k, n, p, m, a in self.db.execute(sql + " ORDER BY created_at", args)
        ]
