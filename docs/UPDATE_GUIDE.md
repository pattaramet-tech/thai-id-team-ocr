# Update Guide - Thai ID Team OCR

**How to safely update the application from GitHub**

## 🔄 One-Click Update

The easiest way to update on Windows:

```batch
update-windows.bat
```

This script will:
1. ✅ Check that you have no uncommitted changes
2. ✅ Create a backup of your database
3. ✅ Pull the latest code from GitHub
4. ✅ Install any new dependencies
5. ✅ Run tests to verify everything works

## 📋 What Gets Updated

### Code Updates
- ✅ Backend Python code
- ✅ Frontend React code
- ✅ Configuration files
- ✅ Documentation

### Dependencies
- ✅ Python packages (from requirements.txt)
- ✅ Node.js packages (npm install)
- ✅ May require Tesseract or Poppler reinstall (see troubleshooting)

### NOT Updated (Your Data)
- ✅ Database (thai_id_ocr.db)
- ✅ Uploaded images
- ✅ Exported files
- ✅ Backups
- ✅ User accounts and settings

## 🛡️ Backup Before Update

### Automatic Backup

When you run `update-windows.bat`, it automatically creates a backup:

1. Shows current version
2. Asks for confirmation
3. Creates backup in `backups/` folder
4. Shows backup filename

**Example backup file:**
```
backups/thai-id-team-ocr-backup-20260625-143022.zip
backups/backup-20260625-143022.json
```

### Manual Backup

If you want to backup before updating:

```batch
1. Run: start.bat
2. Login as admin
3. Go to: Admin → สำรองข้อมูล
4. Click: "สร้างไฟล์สำรอง"
5. Keep the backup file safe
```

## 🚀 Update Steps

### Step 1: Prepare

Make sure:
- ✅ All changes are committed to git
  ```batch
  git status
  ```
  Should show "working tree clean"

- ✅ Application is stopped
  ```batch
  stop.bat
  ```

### Step 2: Update

```batch
update-windows.bat
```

The script will:
- Ask for confirmation
- Create backup
- Pull from GitHub
- Install dependencies
- Run tests

### Step 3: Verify

```batch
1. Run: start.bat
2. Go to: http://localhost:3000
3. Login with your credentials
4. Check that everything works:
   - Can create teams
   - Can upload images
   - Can see players
   - Can export XLSX
   - Admin pages work (System Health, Backup, Help)
```

### Step 4: Cleanup (Optional)

If everything works fine after a few days:

```batch
1. Go to: Admin → สำรองข้อมูล
2. Delete old backups to save space
```

## 🔙 Rollback (Restore from Backup)

If something goes wrong after updating:

### Option 1: Use Admin UI (Recommended)

```
1. Run: start.bat
2. Go to: http://localhost:3000
3. Login as admin
4. Go to: Admin → สำรองข้อมูล
5. Find your backup (usually most recent)
6. Click: "ฟื้นฟู"
7. Type: RESTORE_CONFIRM
8. Click: "ฟื้นฟู" again
9. Wait for "Backup restored" message
10. Restart Backend (close and re-run start.bat)
```

### Option 2: Using Command Line

If Admin UI doesn't work:

```batch
REM This is more advanced, use Option 1 if possible

REM 1. Stop the application
stop.bat

REM 2. Find your backup file
dir backups\

REM 3. Restore using Python
python -c "from apps.api.app.services.backup import BackupService; BackupService.restore_backup('thai-id-team-ocr-backup-XXXXXXXX-XXXXXX.zip')"

REM 4. Start again
start.bat
```

### Option 3: Manual Database Restore

If scripts don't work:

```batch
REM 1. Find your backup file
dir backups\

REM 2. Extract the ZIP file
REM   Use Windows Explorer: right-click → Extract All

REM 3. Restore the database file
REM   Copy: thai_id_ocr.db from backup
REM   To: project root folder
REM   (Overwrite existing file)

REM 4. Start application
start.bat
```

## ✔️ Checking Your Version

To see what version you're running:

```batch
python scripts/check_version.py
```

Shows:
- Current local version (from code)
- Latest git tag (from GitHub)
- Latest commit info
- Whether update is available

## 🔧 Troubleshooting Updates

### "Git not found" Error

Install Git from: https://git-scm.com/

### "Working tree has uncommitted changes"

You have unsaved changes. Either:

**Option A: Commit your changes**
```batch
git add .
git commit -m "My changes"
```

**Option B: Discard your changes**
```batch
git checkout .
```

**Option C: Save for later**
```batch
git stash
```

### "Git pull failed"

Your backup is safe! Try:

1. Check GitHub is accessible
2. Check your internet connection
3. Try again later
4. If stuck, restore from backup

### Backend Won't Start After Update

1. Check logs in backend window
2. Try running tests manually:
   ```batch
   cd apps\api
   python -m pytest tests\ -v
   ```
3. If tests fail, restore from backup

### Frontend Won't Load

```batch
cd apps\web
npm install
npm run build
start.bat
```

### Database Issues After Update

**Option 1: Restore from backup (recommended)**
- Use Admin UI → Restore

**Option 2: Fresh start (if backup doesn't work)**
```batch
1. Delete: thai_id_ocr.db
2. Run: start.bat
3. System creates new empty database
4. Create first admin at bootstrap-admin page
```

⚠️ Warning: This loses all data!

### Python/Node.js Version Issues

Update Python and Node.js to latest LTS:

- Python: https://www.python.org/
- Node.js: https://nodejs.org/

Then run:
```batch
setup-windows.bat
update-windows.bat
```

## 📊 Data Safety

### What's Protected During Update

- ✅ Database (backed up before update)
- ✅ User accounts
- ✅ Player records
- ✅ Team information
- ✅ Uploaded images
- ✅ Exported files
- ✅ Audit logs

### What Gets Cleaned Up

During update, these are safely removed/updated:
- Python dependencies (reinstalled)
- Node modules (reinstalled)
- Temporary files (recreated if needed)

## 🔒 Privacy During Update

### What's NOT Sent to GitHub

- ❌ Your database
- ❌ Player data
- ❌ Images
- ❌ User accounts
- ❌ Thai ID numbers
- ❌ Any personal information

### What IS Sent (Code Only)

- ✅ Open-source application code
- ✅ Configuration templates
- ✅ Documentation

## 📝 Update History

See: [CHANGELOG.md](../CHANGELOG.md) for what's new in each version

## 🆘 Still Have Issues?

### Check Log Files

1. Application logs in console windows
2. Test output when running tests

### Check Backup

```batch
dir backups\
```

Make sure your backup file exists before trying anything else.

### Manual Recovery

Always possible:
1. Stop application (`stop.bat`)
2. Delete `thai_id_ocr.db`
3. Copy backup database back
4. Restart (`start.bat`)

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| Check version | `python scripts/check_version.py` |
| Update safely | `update-windows.bat` |
| Create backup | Admin UI → สำรองข้อมูล |
| Restore backup | Admin UI → สำรองข้อมูล → Restore |
| See what changed | `git log --oneline -10` |
| Manual git pull | `git pull origin main` |

---

**Important:** Always create a backup before updating!  
**Safety First:** If something goes wrong, you can always restore.

**Last Updated:** 2026-06-25  
**Tested On:** Windows 10/11  
