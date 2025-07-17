@echo off
echo Installing CATDAMS Session Bridge as Windows Service...
echo.

REM Check if NSSM is available (Non-Sucking Service Manager)
where nssm >nul 2>nul
if %errorlevel% neq 0 (
    echo NSSM not found. Please install NSSM first:
    echo Download from: https://nssm.cc/download
    echo Or use the manual startup scripts instead.
    pause
    exit /b 1
)

REM Get the current directory
set "CURRENT_DIR=%~dp0"
set "PYTHON_PATH=python"
set "SCRIPT_PATH=%CURRENT_DIR%session_bridge.py"

echo Installing service with:
echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo.

nssm install CATDAMS-SessionBridge "%PYTHON_PATH%" "%SCRIPT_PATH%"
nssm set CATDAMS-SessionBridge AppDirectory "%CURRENT_DIR%"
nssm set CATDAMS-SessionBridge Description "CATDAMS Session Bridge - Coordinates session IDs between desktop agent and browser extension"
nssm set CATDAMS-SessionBridge Start SERVICE_AUTO_START

echo.
echo Service installed successfully!
echo To start the service: net start CATDAMS-SessionBridge
echo To stop the service: net stop CATDAMS-SessionBridge
echo To remove the service: nssm remove CATDAMS-SessionBridge confirm
echo.
pause 