@echo off
setlocal

set "URL=https://raw.githubusercontent.com/aceid-dev/AceManager/refs/heads/main/scripts/fix.ps1"
set "PS_BIN=powershell.exe"
where pwsh.exe >nul 2>&1 && set "PS_BIN=pwsh.exe"

:: Ejecutar script remoto usando PowerShell 5.1 o PowerShell 7
"%PS_BIN%" -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-RestMethod -Uri '%URL%' | Invoke-Expression"

endlocal
