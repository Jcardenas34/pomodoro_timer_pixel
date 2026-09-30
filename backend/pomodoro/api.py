"""Methods exposed to the frontend as window.pywebview.api.*"""

from __future__ import annotations

import time

from .assets import to_frontend
from .storage import Storage


class Api:
    def __init__(self, storage: Storage) -> None:
        # Underscored attributes are not exposed to JavaScript by pywebview.
        self._storage = storage
        self._window = None

    def get_state(self) -> dict:
        return {
            "settings": self._storage.get_settings(),
            "assets": [to_frontend(a) for a in self._storage.list_assets()],
        }

    def save_settings(self, values: dict) -> dict:
        return self._storage.save_settings(values)

    def start_session(self, task: str | None, phase: str) -> int:
        return self._storage.start_session(task, phase)

    def end_session(self, session_id: int, seconds: int, completed: bool) -> None:
        self._storage.end_session(session_id, seconds, completed)

    def get_stats(self, days: int = 7) -> list[dict]:
        return self._storage.stats(time.time() - days * 86400)

    def toggle_fullscreen(self) -> None:
        if self._window:
            self._window.toggle_fullscreen()

    def quit(self) -> None:
        if self._window:
            self._window.destroy()
