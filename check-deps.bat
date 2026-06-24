@echo off
REM Thai ID Team OCR - Dependency Checker
REM ====================================

echo.
echo ========================================
echo Dependency Checker
echo ========================================
echo.

python scripts/check_deps.py
if errorlevel 1 (
    echo.
    echo Some dependencies are missing.
    echo Please run: setup-windows.bat
)

echo.
pause
