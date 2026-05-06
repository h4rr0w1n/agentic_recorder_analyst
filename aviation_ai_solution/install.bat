@echo off
REM ==============================================================================
REM Aviation AI Solution - Automated Installation Script (Windows)
REM Designed for ATC Operators and Team Leaders (No IT Knowledge Required)
REM ==============================================================================

echo ==========================================
echo   Aviation AI Solution Installer
echo   Version 1.0.0
echo ==========================================
echo.

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Error: Python 3 is not installed.
    echo    Please install Python 3.8 or higher first from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found: 
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [PKG] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo X Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [i]  Virtual environment already exists.
)

REM Activate virtual environment
echo [ACT] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [UPD] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo [INS] Installing required packages (this may take a few minutes)...
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo X Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed successfully.
) else (
    echo [!] requirements.txt not found. Skipping dependency installation.
)

REM Create necessary directories
echo [DIR] Creating data directories...
if not exist "data_lake" mkdir data_lake
if not exist "models" mkdir models
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo [OK] Directories ready.

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo Next Steps:
echo   1. To start the User Interface (Recommended):
echo      Double-click: run_ui.bat
echo.
echo   2. Or run via Command Line:
echo      run_cli.bat --help
echo.
echo   3. For detailed instructions, read: USER_MANUAL.md
echo.
echo ==========================================
pause
