# Builds dist\PixelPomodoro.exe. Run from the repo root in Windows PowerShell (not WSL):
#   powershell -ExecutionPolicy Bypass -File scripts\build-exe.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Push-Location frontend
npm install
if ($LASTEXITCODE) { throw "npm install failed" }
npm run build
if ($LASTEXITCODE) { throw "npm run build failed" }
Pop-Location

py -m pip install -e backend pyinstaller
if ($LASTEXITCODE) { throw "pip install failed" }

py -m pomodoro --export-icon build\PixelPomodoro.ico
if ($LASTEXITCODE) { throw "icon export failed" }

py -m PyInstaller --noconfirm PixelPomodoro.spec
if ($LASTEXITCODE) { throw "PyInstaller failed" }

Write-Host "Built $(Resolve-Path dist\PixelPomodoro.exe)"
