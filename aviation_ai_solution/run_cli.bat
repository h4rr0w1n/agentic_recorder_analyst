@echo off
REM ==============================================================================
REM Quick Start Script - Command Line Interface (Windows)
REM ==============================================================================

echo Starting Aviation AI Solution (CLI Mode)...
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

REM Launch the CLI with passed arguments
python -m aviation_ai_solution.main %*

pause
