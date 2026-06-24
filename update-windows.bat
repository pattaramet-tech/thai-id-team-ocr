@echo off
REM Thai ID Team OCR - Windows Update Script
REM =========================================

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Thai ID Team OCR - Update
echo ========================================
echo.

REM Check if we're in project root
if not exist "apps\api" (
    echo ERROR: Run this script from project root directory
    echo        Expected: thai-id-team-ocr\update-windows.bat
    pause
    exit /b 1
)

REM Check git
echo Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not found!
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)
echo.

REM Check current branch
echo Checking current branch...
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set "CURRENT_BRANCH=%%i"
echo Current branch: %CURRENT_BRANCH%

if not "%CURRENT_BRANCH%"=="main" (
    echo WARNING: You are on branch '%CURRENT_BRANCH%', not 'main'
    echo Update will pull from main branch
    echo.
)
echo.

REM Check working tree
echo Checking working tree status...
git status --porcelain >nul 2>&1
if not errorlevel 0 (
    echo ERROR: Git status check failed
    pause
    exit /b 1
)

REM Count uncommitted changes
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set "CHANGES=%%i"

if not "%CHANGES%"=="0" (
    echo ERROR: Working directory has uncommitted changes:
    echo.
    git status
    echo.
    echo To update safely, please commit or stash your changes:
    echo   git add .
    echo   git commit -m "Your message"
    echo OR
    echo   git stash
    echo.
    pause
    exit /b 1
)
echo Working tree is clean - OK
echo.

REM Check current version
echo ========================================
echo Checking Versions
echo ========================================
echo.
python scripts/check_version.py
echo.

REM Ask for confirmation
echo ========================================
echo BACKUP BEFORE UPDATE
echo ========================================
echo.
echo We will now create a backup of your database.
echo This backup can be restored if something goes wrong.
echo.

set /p CONFIRM="Continue with backup and update? (yes/no): "
if /i not "%CONFIRM%"=="yes" (
    echo Update cancelled.
    pause
    exit /b 0
)
echo.

REM Create backup
echo ========================================
echo Creating Backup
echo ========================================
echo.
python scripts/backup_before_update.py
if errorlevel 1 (
    echo.
    echo ERROR: Backup failed! Aborting update.
    pause
    exit /b 1
)
echo.

REM Update from git
echo ========================================
echo Updating from GitHub
echo ========================================
echo.
echo Running: git pull origin main
git pull origin main
if errorlevel 1 (
    echo.
    echo ERROR: Git pull failed!
    echo Your code has NOT been updated.
    echo Your backup is still available in: backups/
    pause
    exit /b 1
)
echo.

REM Update Python dependencies
echo ========================================
echo Installing Backend Dependencies
echo ========================================
echo.
cd apps\api
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    cd ..\..
    pause
    exit /b 1
)
echo Python dependencies installed
cd ..\..
echo.

REM Update Node dependencies
echo ========================================
echo Installing Frontend Dependencies
echo ========================================
echo.
cd apps\web
call npm install >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    cd ..\..
    pause
    exit /b 1
)
echo Node.js dependencies installed
cd ..\..
echo.

REM Run backend tests
echo ========================================
echo Running Backend Tests
echo ========================================
echo.
cd apps\api
python -m pytest tests/ -q
if errorlevel 1 (
    echo.
    echo WARNING: Some tests failed!
    echo Please check the errors above.
    cd ..\..
    pause
    exit /b 1
)
echo Backend tests passed
cd ..\..
echo.

REM Build frontend
echo ========================================
echo Building Frontend
echo ========================================
echo.
cd apps\web
call npm run build >nul 2>&1
if errorlevel 1 (
    echo ERROR: Frontend build failed
    cd ..\..
    pause
    exit /b 1
)
echo Frontend build successful
cd ..\..
echo.

REM Success!
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Your backup is saved at: backups/
echo.
echo Next steps:
echo   1. Run: start.bat
echo   2. Login and verify everything works
echo   3. Keep your backup for a few days in case issues arise
echo.
echo If something goes wrong:
echo   1. Run: start.bat
echo   2. Go to: Admin -> สำรองข้อมูล (Restore)
echo   3. Select the backup and restore
echo.
pause
