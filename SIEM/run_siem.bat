@echo off
echo Starting SIEM System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Navigate to SIEM directory
cd /d "%~dp0\siem"

REM Install dependencies if needed
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
    
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
    
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
) else (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

REM Run the SIEM
echo Starting SIEM components...
echo.
echo NOTE: This application requires administrator privileges to listen on port 514
echo If you encounter permission errors, please run this script as Administrator
echo.
python main.py

pause 