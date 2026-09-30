#!/usr/bin/env bash
# One-time Android SDK setup for building the APK from WSL (no sudo).
#
#   conda activate pixel-pomodoro          # provides JDK 21
#   bash scripts/setup-android-sdk.sh
#
# Installs the Linux command-line SDK into $ANDROID_HOME (default ~/Android/Sdk),
# and Windows platform-tools (adb.exe) into $WIN_ADB_DIR, because WSL cannot see
# USB devices but Windows adb can.
set -euo pipefail

ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
WIN_ADB_DIR="${WIN_ADB_DIR:-/mnt/c/Users/$(cmd.exe /c 'echo %USERNAME%' 2>/dev/null | tr -d '\r')/AppData/Local/Android/platform-tools}"
CMDLINE_TOOLS_ZIP="commandlinetools-linux-13114758_latest.zip"

# Versions required by the Capacitor 8 Android template (android/variables.gradle, AGP 8.13).
PACKAGES=("platform-tools" "platforms;android-36" "build-tools;35.0.0")

if ! java -version 2>&1 | grep -qE 'version "(1[7-9]|2[0-9])'; then
  echo "JDK 17+ required on PATH. Run: conda activate pixel-pomodoro (environment.yml ships openjdk=21)" >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if [ ! -x "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]; then
  echo "Downloading Android command-line tools -> $ANDROID_HOME"
  curl -fsSL -o "$tmp/tools.zip" "https://dl.google.com/android/repository/$CMDLINE_TOOLS_ZIP"
  unzip -q "$tmp/tools.zip" -d "$tmp"
  mkdir -p "$ANDROID_HOME/cmdline-tools"
  rm -rf "$ANDROID_HOME/cmdline-tools/latest"
  mv "$tmp/cmdline-tools" "$ANDROID_HOME/cmdline-tools/latest"
fi

sdkmanager="$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager"
yes | "$sdkmanager" --sdk_root="$ANDROID_HOME" --licenses > /dev/null || true  # yes exits on SIGPIPE
"$sdkmanager" --sdk_root="$ANDROID_HOME" "${PACKAGES[@]}"

if [ ! -f "$WIN_ADB_DIR/adb.exe" ]; then
  echo "Downloading Windows platform-tools (adb.exe) -> $WIN_ADB_DIR"
  curl -fsSL -o "$tmp/pt-win.zip" "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
  unzip -q "$tmp/pt-win.zip" -d "$tmp/win"
  mkdir -p "$(dirname "$WIN_ADB_DIR")"
  rm -rf "$WIN_ADB_DIR"
  mv "$tmp/win/platform-tools" "$WIN_ADB_DIR"
fi

cat <<EOF

Android SDK ready. Add these to ~/.bashrc (or run them in this shell):

  export ANDROID_HOME="$ANDROID_HOME"
  export WIN_ADB="$WIN_ADB_DIR/adb.exe"
EOF
