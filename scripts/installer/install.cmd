@echo off
setlocal

set "SCRIPT=%~dp0install.py"

where python >nul 2>&1
if %errorlevel%==0 (
    python "%SCRIPT%"
    endlocal
    exit /b %errorlevel%
)

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 "%SCRIPT%"
    endlocal
    exit /b %errorlevel%
)

echo Error: no se encontro Python para ejecutar install.py
endlocal
exit /b 1
