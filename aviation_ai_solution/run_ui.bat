@echo off
REM ==============================================================================
REM Quick Start Script - Launch User Interface (Windows)
REM ==============================================================================

echo Starting Aviation AI Solution...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo X Virtual environment not found!
    echo    Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Launch the UI
python -m aviation_ai_solution.ui.app

pause
