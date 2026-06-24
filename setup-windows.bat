@echo off
REM Thai ID Team OCR - Windows Setup Script
REM ========================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Thai ID Team OCR - Windows Setup
echo ========================================
echo.

REM Check if we're in project root
if not exist "apps\api" (
    echo ERROR: Run this script from project root directory
    echo        Expected: thai-id-team-ocr\setup-windows.bat
    pause
    exit /b 1
)

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Python not found!
    echo ========================================
    echo.
    echo Please install Python 3.8+ from:
    echo   https://www.python.org/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo Then restart this script.
    echo.
    pause
    exit /b 1
)
echo Python version:
python --version
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Node.js not found!
    echo ========================================
    echo.
    echo Please install Node.js from:
    echo   https://nodejs.org/
    echo.
    echo Install the LTS version and add to PATH.
    echo Then restart this script.
    echo.
    pause
    exit /b 1
)
echo Node.js version:
node --version
echo npm version:
npm --version
echo.

REM Create folders
echo Creating required folders...
if not exist uploads mkdir uploads
if not exist exports mkdir exports
if not exist temp mkdir temp
if not exist backups mkdir backups
if not exist scripts mkdir scripts
echo  Created: uploads/, exports/, temp/, backups/
echo.

REM Setup Python backend
echo ========================================
echo Setting up Backend (Python)
echo ========================================
echo.

cd apps\api

REM Check if venv exists
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo.
        echo ========================================
        echo ERROR: Failed to create virtual environment
        echo ========================================
        echo.
        echo Please check:
        echo   1. Python is installed correctly
        echo   2. Run "python --version" in Command Prompt
        echo   3. Check disk space in apps/api folder
        echo.
        pause
        exit /b 1
    )
    echo Virtual environment created
    echo.
)

REM Activate venv
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo.

REM Install Python dependencies
echo Installing Python dependencies...
echo (This may take 2-5 minutes)
pip install -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to install Python dependencies
    echo ========================================
    echo.
    echo Trying to upgrade pip first...
    python -m pip install --upgrade pip
    echo.
    echo Retrying pip install...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo Installation failed again. Please:
        echo   1. Check internet connection
        echo   2. Run: python -m pip install --upgrade pip
        echo   3. Run: pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
)
echo Python dependencies installed
echo.

REM Deactivate venv (we'll activate it during startup)
call .venv\Scripts\deactivate.bat
cd ..\..

REM Setup frontend
echo ========================================
echo Setting up Frontend (Node.js)
echo ========================================
echo.

cd apps\web

echo Installing Node.js dependencies...
echo (This may take 2-5 minutes)
call npm install
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Failed to install Node.js dependencies
    echo ========================================
    echo.
    echo Please check:
    echo   1. Internet connection is working
    echo   2. Node.js is properly installed
    echo   3. Run: npm cache clean --force
    echo   4. Run: npm install again
    echo.
    pause
    exit /b 1
)
echo Node.js dependencies installed
echo.

cd ..\..

REM Check OCR dependencies
echo ========================================
echo Checking Optional Dependencies
echo ========================================
echo.

python scripts/check_deps.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.

echo Next steps:
echo   1. Install OCR dependencies (if needed):
echo      - Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
echo      - Poppler: https://github.com/oschwartz10612/poppler-windows/releases
echo.
echo   2. Create first Admin user:
echo      - Run: start.bat
echo      - Go to: http://localhost:3000/auth/bootstrap-admin
echo.
echo   3. Start the application:
echo      - Run: start.bat
echo.

pause
