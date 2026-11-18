# PyInstaller spec for the Windows desktop exe. Build with scripts/build-exe.ps1.
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["scripts/pyinstaller_entry.py"],
    pathex=["backend"],
    datas=[("frontend/dist", "frontend/dist")],  # found at runtime via sys._MEIPASS
    excludes=["PyQt5", "PyQt6", "PySide2", "PySide6", "qtpy"],  # Windows uses WebView2, not Qt
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name="PixelPomodoro",
    icon="build/PixelPomodoro.ico",
    console=False,  # no terminal window behind the app
    upx=False,
)
