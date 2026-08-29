@echo off
setlocal enabledelayedexpansion

set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Programs\Thonny\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Thonny\python.exe"
)

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

if not defined PYTHON_EXE (
    python -c "import sys; print(sys.version)" >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        set "PYTHON_EXE=python"
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] No working Python installation was found.
    pause
    exit /b 1
)

"!PYTHON_EXE!" main.py
