#!/usr/bin/env bash
# Install the debug APK on a USB-connected phone (USB debugging on).
# From WSL this uses Windows adb.exe ($WIN_ADB, set by setup-android-sdk.sh),
# because WSL cannot see USB devices; elsewhere it falls back to adb on PATH.
set -euo pipefail

apk="$(cd "$(dirname "$0")/.." && pwd)/frontend/android/app/build/outputs/apk/debug/app-debug.apk"
[ -f "$apk" ] || { echo "No APK at $apk; run: cd frontend && npm run android:build" >&2; exit 1; }

if [ -n "${WIN_ADB:-}" ]; then
  "$WIN_ADB" install -r "$(wslpath -w "$apk")"
else
  adb install -r "$apk"
fi
