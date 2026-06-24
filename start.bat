@echo off
REM Thai ID Team OCR - Windows Startup Script
REM =========================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Thai ID Team OCR - Startup
echo ========================================
echo.

REM Check if we're in project root
if not exist "apps\api" (
    echo ERROR: Run this script from project root directory
    echo        Expected: thai-id-team-ocr\start.bat
    pause
    exit /b 1
)

REM Run dependency check
echo Checking dependencies...
python scripts/check_deps.py
if errorlevel 1 (
    echo.
    echo ERROR: Dependencies missing!
    echo Please run: setup-windows.bat
    pause
    exit /b 1
)

echo.
echo Creating required folders...
if not exist uploads mkdir uploads
if not exist exports mkdir exports
if not exist temp mkdir temp
if not exist backups mkdir backups

echo.
echo ========================================
echo Starting Backend API (Port 8000)
echo ========================================
echo.

REM Start backend in separate window
start "Thai ID Team OCR - Backend" cmd /k ^
    cd apps\api ^& ^
    .venv\Scripts\activate.bat ^& ^
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak

REM Check if backend is responding
set "max_attempts=30"
set "attempt=0"
:check_backend
set /a attempt+=1
if %attempt% gtr %max_attempts% (
    echo.
    echo ERROR: Backend did not start (timeout after 30 seconds)
    echo Please check backend logs in the separate window
    pause
    exit /b 1
)

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak
    goto check_backend
)

echo Backend is running!

echo.
echo ========================================
echo Starting Frontend (Port 3000)
echo ========================================
echo.

REM Start frontend in separate window
start "Thai ID Team OCR - Frontend" cmd /k ^
    cd apps\web ^& ^
    npm run dev

REM Wait for frontend to start
echo Waiting for frontend to start...
timeout /t 8 /nobreak

echo.
echo ========================================
echo Opening Application
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo           API Docs: http://localhost:8000/docs
echo.
echo Frontend: http://localhost:3000
echo.

REM Open browser
start http://localhost:3000

echo.
echo ========================================
echo System is running!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo To stop the application:
echo   - Close both "Thai ID Team OCR" windows, OR
echo   - Run: stop.bat
echo.
pause
