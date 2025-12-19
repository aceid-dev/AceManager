
@echo off
setlocal

set URL="https://raw.githubusercontent.com/aceid-dev/AceManager/refs/heads/main/scripts/installer/install.ps1"

:: Ejecutar PowerShell usando las variables
powershell -NoLogo -NoProfile -Command "irm '%URL%' | iex"

endlocal
