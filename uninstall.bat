@echo off
REM FIB Tool - Uninstallation Script for Windows
REM Removes FIB Tool from KLayout SALT directory

echo ==========================================
echo FIB Tool - Uninstaller
echo ==========================================
echo.

REM Set KLayout SALT directory
set "KLAYOUT_SALT_DIR=%APPDATA%\KLayout\salt"
set "TARGET_DIR=%KLAYOUT_SALT_DIR%\fib-tool"

echo Target: %TARGET_DIR%
echo.

REM Check if installed
if not exist "%TARGET_DIR%" (
    echo FIB Tool is not installed.
    echo Nothing to uninstall.
    pause
    exit /b 0
)

REM Show what will be removed
if exist "%TARGET_DIR%\python\fib_tool" (
    echo Found: Installed files
) else (
    echo Found: Installation directory
)

echo.
set /p CONFIRM="Remove FIB Tool from KLayout? (y/n): "

if /i not "%CONFIRM%"=="y" (
    echo Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo Removing FIB Tool...

REM Remove directory
rmdir /s /q "%TARGET_DIR%"

if %ERRORLEVEL% equ 0 (
    echo [OK] FIB Tool removed successfully
    echo.
    echo To reinstall, run: install.bat
) else (
    echo [X] Error removing FIB Tool
    echo.
    echo Please check if:
    echo 1. KLayout is closed
    echo 2. You have permission to delete files
    pause
    exit /b 1
)

echo.
pause
