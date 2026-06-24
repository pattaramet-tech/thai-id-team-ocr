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
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
node --version
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
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
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
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo  Installed requirements.txt
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
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
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
