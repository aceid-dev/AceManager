@echo off
setlocal

set URL="https://raw.githubusercontent.com/aceid-dev/AceManager/refs/heads/main/scripts/fix.ps1"

:: Ejecutar PowerShell usando las variables
powershell -NoLogo -NoProfile -Command "irm '%URL%' | iex"

endlocal