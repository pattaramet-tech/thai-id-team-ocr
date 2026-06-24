@echo off
REM Thai ID Team OCR - Windows Shutdown Script
REM ============================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Thai ID Team OCR - Shutdown
echo ========================================
echo.

REM Check if processes are running
echo Checking for running processes...

REM Kill backend (port 8000)
echo.
echo Stopping Backend API (port 8000)...
netstat -ano | findstr :8000 >nul 2>&1
if errorlevel 1 (
    echo  No process on port 8000
) else (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        echo  Found process PID: %%a
        taskkill /PID %%a /F /T >nul 2>&1
        if errorlevel 1 (
            echo  WARNING: Could not kill PID %%a
            echo  Try closing the "Thai ID Team OCR - Backend" window manually
        ) else (
            echo  Killed process %%a
        )
    )
)

REM Kill frontend (port 3000)
echo.
echo Stopping Frontend (port 3000)...
netstat -ano | findstr :3000 >nul 2>&1
if errorlevel 1 (
    echo  No process on port 3000
) else (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
        echo  Found process PID: %%a
        taskkill /PID %%a /F /T >nul 2>&1
        if errorlevel 1 (
            echo  WARNING: Could not kill PID %%a
            echo  Try closing the "Thai ID Team OCR - Frontend" window manually
        ) else (
            echo  Killed process %%a
        )
    )
)

echo.
echo ========================================
echo Shutdown complete
echo ========================================
echo.
echo Note: If you still see the application windows open, close them manually
echo.

pause
