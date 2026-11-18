"""PyInstaller entry point. It runs this file as a plain script, so `pomodoro/__main__.py`'s
relative imports would fail if it were the entry; importing the package keeps them working."""

from pomodoro.__main__ import main

main()
