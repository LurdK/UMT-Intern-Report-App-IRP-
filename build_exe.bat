@echo off
setlocal enabledelayedexpansion
title Build Intern Report App Executable
echo ========================================================
echo   Building Intern Report App (IRP) Single Portable .EXE
echo ========================================================
echo.

:: Detect valid Python executable
set "PYTHON_EXE="

:: 1. Check Thonny Python
if exist "%LOCALAPPDATA%\Programs\Thonny\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Thonny\python.exe"
)

:: 2. Check standard Python installations if Thonny not found
if not defined PYTHON_EXE (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
        if exist "%%i\python.exe" set "PYTHON_EXE=%%i\python.exe"
    )
)

if not defined PYTHON_EXE (
    for /d %%i in ("%PROGRAMFILES%\Python3*") do (
        if exist "%%i\python.exe" set "PYTHON_EXE=%%i\python.exe"
    )
)

:: 3. Test generic 'python' command only if not Windows Store stub
if not defined PYTHON_EXE (
    python -c "import sys; print(sys.version)" >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] No working Python installation was found.
    echo Please install Python 3 or ensure it is added to your PATH.
    pause
    exit /b 1
)

echo [Found Python] Using: !PYTHON_EXE!
echo.

echo [1/3] Verifying PyInstaller...
"!PYTHON_EXE!" -m pip install pyinstaller --quiet

echo [2/3] Building Single Portable .EXE with PyInstaller...
"!PYTHON_EXE!" -m PyInstaller --noconfirm --onefile --windowed ^
    --name "InternReportApp" ^
    --distpath "Intern Report App" ^
    --add-data "Report Format;Report Format" ^
    main.py

echo.
if exist "Intern Report App\InternReportApp.exe" (
    echo ========================================================
    echo   BUILD SUCCESSFUL!
    echo   Single Portable Executable generated at:
    echo   Intern Report App\InternReportApp.exe
    echo ========================================================
    echo.
    echo Opening folder...
    explorer "Intern Report App"
) else (
    echo [ERROR] Build failed. Please check the logs above.
)


pause
