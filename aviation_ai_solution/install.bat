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

REM Remove broken virtual environment if it exists
if exist "venv\Scripts\activate.bat" goto venv_exists
if exist "venv" (
    echo [FIX] Removing broken virtual environment...
    rmdir /s /q venv
)

:venv_exists

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [PKG] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo X Failed to create virtual environment.
        echo    Try running: python -m venv venv
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

if errorlevel 1 (
    echo X Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Upgrade pip using python -m pip
echo [UPD] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install only essential packages for basic functionality
echo [INS] Installing core packages (this may take a few minutes)...
pip install streamlit numpy pandas scikit-learn networkx pyyaml loguru tqdm python-dateutil pytz requests matplotlib plotly pytest --quiet

if errorlevel 1 (
    echo [!] Warning: Some packages failed to install.
    echo     You can still use basic features.
)

REM Check if requirements.txt exists
if exist "requirements.txt" (
    echo [i]  Note: Full requirements include advanced features.
    echo     For production use with all features, contact IT support.
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
echo Tip: The application will open in your web browser.
echo      Access it at: http://localhost:8501
echo ==========================================
pause

