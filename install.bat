@echo off
REM FIB Tool - Installation Script for Windows
REM Installs FIB Tool as a KLayout SALT package

setlocal enabledelayedexpansion

echo ==========================================
echo FIB Tool - SALT Package Installer
echo ==========================================
echo.

REM Set KLayout SALT directory
set "KLAYOUT_SALT_DIR=%APPDATA%\KLayout\salt"
echo KLayout SALT directory: %KLAYOUT_SALT_DIR%
echo.

REM Check if source directories exist
if not exist "python\fib_tool" (
    echo Error: python\fib_tool\ directory not found
    echo.
    echo It looks like the project hasn't been migrated to SALT structure yet.
    echo Please run the migration scripts first.
    pause
    exit /b 1
)

if not exist "pymacros" (
    echo Error: pymacros\ directory not found
    echo.
    echo It looks like the project hasn't been migrated to SALT structure yet.
    echo Please run the migration scripts first.
    pause
    exit /b 1
)

REM Create SALT directory if it doesn't exist
if not exist "%KLAYOUT_SALT_DIR%" mkdir "%KLAYOUT_SALT_DIR%"

REM Target directory
set "TARGET_DIR=%KLAYOUT_SALT_DIR%\fib-tool"

echo Installation options:
echo 1) Symbolic link (requires admin privileges, recommended for development)
echo    - Changes to source code immediately reflected
echo    - Easy to update
echo.
echo 2) Copy files (recommended for production)
echo    - Stable installation
echo    - Won't change if source is modified
echo.
set /p choice="Choose installation method (1 or 2): "

if "%choice%"=="1" goto symlink
if "%choice%"=="2" goto copy
echo Invalid choice. Exiting.
pause
exit /b 1

:symlink
echo.
echo Installing via symbolic link...
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Error: Symbolic links require administrator privileges on Windows.
    echo.
    echo Please either:
    echo 1. Run this script as Administrator
    echo 2. Choose option 2 (Copy files) instead
    echo.
    pause
    exit /b 1
)

REM Remove existing installation
if exist "%TARGET_DIR%" (
    echo Removing existing installation...
    rmdir /s /q "%TARGET_DIR%"
)

REM Create symbolic link
set "SOURCE_DIR=%CD%"
mklink /D "%TARGET_DIR%" "%SOURCE_DIR%"

if %errorLevel% equ 0 (
    echo OK Symbolic link created: %TARGET_DIR% -^> %SOURCE_DIR%
) else (
    echo Error: Failed to create symbolic link
    pause
    exit /b 1
)

goto verify

:copy
echo.
echo Installing via copy...
echo.

REM Remove existing installation
if exist "%TARGET_DIR%" (
    echo Removing existing installation...
    rmdir /s /q "%TARGET_DIR%"
)

REM Create target directory
mkdir "%TARGET_DIR%"

REM Copy files
echo Copying files...
xcopy /E /I /Y "python" "%TARGET_DIR%\python"
xcopy /E /I /Y "pymacros" "%TARGET_DIR%\pymacros"
copy /Y "grain.xml" "%TARGET_DIR%\"
if exist "README.md" copy /Y "README.md" "%TARGET_DIR%\"
if exist "LICENSE" copy /Y "LICENSE" "%TARGET_DIR%\"

echo OK Files copied to: %TARGET_DIR%

:verify
echo.
echo ==========================================
echo Verifying installation...
echo ==========================================

REM Verify structure
if exist "%TARGET_DIR%\grain.xml" (
    echo OK grain.xml found
) else (
    echo X grain.xml not found
)

if exist "%TARGET_DIR%\python\fib_tool" (
    dir /b "%TARGET_DIR%\python\fib_tool\*.py" 2>nul | find /c ".py" > temp.txt
    set /p PY_COUNT=<temp.txt
    del temp.txt
    echo OK python\fib_tool\ found (!PY_COUNT! Python files^)
) else (
    echo X python\fib_tool\ not found
)

if exist "%TARGET_DIR%\pymacros" (
    dir /b "%TARGET_DIR%\pymacros\*.lym" 2>nul | find /c ".lym" > temp.txt
    set /p LYM_COUNT=<temp.txt
    del temp.txt
    echo OK pymacros\ found (!LYM_COUNT! macro files^)
) else (
    echo X pymacros\ not found
)

echo.
echo ==========================================
echo OK Installation Complete!
echo ==========================================
echo.
echo Installation location: %TARGET_DIR%
echo.
echo Next steps:
echo 1. Close KLayout completely (not just the window)
echo 2. Reopen KLayout
echo 3. Open a GDS file
echo 4. Press Ctrl+Shift+F to open FIB Tool Panel
echo    Or use menu: Tools -^> Toggle FIB Tool Panel
echo.
echo Troubleshooting:
echo - If panel doesn't appear, press F5 to check console for errors
echo - Make sure you completely closed and reopened KLayout
echo - Check that layers 337, 338, 339 are visible
echo.
echo For development/testing:
echo - Use load_fib_tool.py in Macro Development (F5)
echo.
pause
