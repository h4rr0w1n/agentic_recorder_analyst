@echo off
REM ==============================================================================
REM Quick Start Script - Launch User Interface (Windows)
REM Designed for ATC Operators (No IT Knowledge Required)
REM ==============================================================================

echo Starting Aviation AI Solution...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo X Virtual environment not found!
    echo    Please run install.bat first.
    echo    Or double-click install.bat to install.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Set PYTHONPATH to include the current directory
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Launch the UI with clear instructions
echo [i]  Opening web browser...
echo Tip: The application will be available at: http://localhost:8501
echo Wait while the application loads...
echo.

REM Run Streamlit
streamlit run ui\app.py --server.headless true --server.port 8501

pause

