# Windows Setup Guide - Thai ID Team OCR

**For Windows 10/11 users**

## 🚀 Quick Start (One-Click)

### First Time Setup

1. **Download and Extract Project**
   - Extract the project to a folder
   - Open File Explorer to the project folder
   - Example: `C:\Users\YourName\thai-id-team-ocr`

2. **Run Setup Script**
   - Double-click: `setup-windows.bat`
   - Wait for it to complete (2-5 minutes)
   - This installs all required Python and Node.js dependencies

3. **Install OCR (Optional but Recommended)**
   - See "Installing Tesseract & Poppler" section below

4. **Start Application**
   - Double-click: `start.bat`
   - Browser will open automatically at `http://localhost:3000`
   - Wait for both "Backend" and "Frontend" windows to show status messages

5. **Create Admin User (First Time Only)**
   - Go to: `http://localhost:3000/auth/bootstrap-admin`
   - Create your first admin account
   - Use that to login from now on

### Daily Startup

Just double-click: **`start.bat`**

That's it! The application will:
- ✓ Check dependencies
- ✓ Create required folders
- ✓ Start backend API (port 8000)
- ✓ Start frontend (port 3000)
- ✓ Open browser automatically

### Shutdown

Double-click: **`stop.bat`**

Or just close the two windows that pop up.

## 📋 Requirements

### Essential (Must Have)

- **Windows 10/11** (Pro, Home, or Education)
- **Python 3.8+**
  - Download: https://www.python.org/downloads/
  - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
  - Verify: Open Command Prompt, type: `python --version`

- **Node.js v18+**
  - Download: https://nodejs.org/ (LTS version)
  - Verify: Open Command Prompt, type: `node --version`

### Recommended (For Full Features)

- **Tesseract OCR**
  - Download: https://github.com/UB-Mannheim/tesseract/wiki
  - Get: UB-Mannheim installer (recommended)

- **Poppler (for PDF support)**
  - Download: https://github.com/oschwartz10612/poppler-windows/releases
  - Get: Release zip (latest)

- **Thai Language Data for Tesseract**
  - See installation instructions below

### Optional

- Git (for version control)
  - Download: https://git-scm.com/
  - Only needed if cloning from GitHub

## 🔧 Installing Tesseract & Poppler

### Tesseract OCR (Recommended)

1. Download UB-Mannheim Tesseract from:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Look for: **tesseract-ocr-w64** or **tesseract-ocr-w32** (depending on your Windows)
   - 64-bit Windows → tesseract-ocr-w64-latest.exe
   - 32-bit Windows → tesseract-ocr-w32-latest.exe

3. Run the installer
   - Accept default installation path
   - **Important**: Note the installation folder (usually `C:\Program Files\Tesseract-OCR`)

4. Verify installation:
   ```
   tesseract --version
   ```
   Should show version info in Command Prompt.

5. Install Thai Language Data (Optional but Recommended)

   **Option A: Download from UB-Mannheim**
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Find "Additional language data"
   - Download: `tha.traineddata` (for Thai)
   - Copy to: `C:\Program Files\Tesseract-OCR\tessdata\`

   **Option B: Auto-download (if available)**
   - First time you use OCR, Tesseract may auto-download

6. Verify Thai language:
   ```
   tesseract --list-langs
   ```
   Should show "tha" in the list.

### Poppler (For PDF Support)

1. Download from:
   https://github.com/oschwartz10612/poppler-windows/releases

2. Download the latest **Release** (not Pre-release)
   - Example: `Release-24.08.0`
   - Get the `.zip` file

3. Extract to a folder
   - Example: `C:\Users\YourName\poppler`
   - **Keep the path simple, no spaces**

4. Add to Windows PATH

   **Step-by-step:**
   - Right-click "This PC" or "My Computer" → Properties
   - Click "Advanced system settings"
   - Click "Environment Variables" button
   - Under "User variables", click "New..."
   - Variable name: `POPPLER_PATH`
   - Variable value: `C:\Users\YourName\poppler\Library\bin`
   - Click OK, OK, OK
   - Restart Command Prompt and try: `pdftoppm -v`

## 🔍 Checking Dependencies

Run this anytime to check what's installed:

```
check-deps.bat
```

Shows status like:
```
[OK] Python found: Python 3.11.2
[OK] Node.js found: v18.17.0
[OK] Tesseract found: tesseract 5.3.0
[WARN] Poppler not found - PDF OCR support disabled (optional)
[OK] Python venv found
[OK] Node modules found
```

## ⚠️ Troubleshooting

### Port Already In Use

If you get "Address already in use" error:

**For Port 3000 (Frontend):**
```
netstat -ano | findstr :3000
taskkill /PID <number> /F
```

**For Port 8000 (Backend):**
```
netstat -ano | findstr :8000
taskkill /PID <number> /F
```

Replace `<number>` with the PID shown.

Or use: `stop.bat` to try auto-stopping.

### Python Not Found

- Download Python 3.8+ from https://www.python.org/
- **IMPORTANT**: Check "Add Python to PATH" during installation
- Restart Command Prompt after installation

### Node.js Not Found

- Download Node.js LTS from https://nodejs.org/
- Run installer
- Restart Command Prompt after installation

### Tesseract Not Found (Optional)

- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH
- Or just use JPG/PNG images (works without Tesseract)

### PDF Upload Fails

- Install Poppler (see above)
- Or use JPG/PNG images instead (OCR still works)

### Backend Won't Start

1. Check logs in the Backend window
2. Try: `check-deps.bat`
3. Delete `apps/api/.venv` and re-run `setup-windows.bat`
4. Check port 8000 is not in use

### Frontend Won't Start

1. Check logs in the Frontend window
2. Try: `npm install` in `apps/web` folder
3. Delete `apps/web/node_modules` folder and re-run `setup-windows.bat`
4. Check port 3000 is not in use

### Can't Login / Admin Page Shows Error

1. Check backend is running: http://localhost:8000/health
2. Check browser console (F12) for errors
3. Try: `/auth/bootstrap-admin` to create first admin
4. Clear browser cookies and try again

## 💾 Backup & Restore

### Creating Backups

**Manual (via UI):**
1. Login as admin
2. Go to: Admin → สำรองข้อมูล
3. Click: "สร้างไฟล์สำรอง"
4. Optional: Check "รวมไฟล์ Export"
5. Files saved in: `backups/` folder

**Before Update:**
Always backup before updating the application!

### Restoring from Backup

1. Go to: Admin → สำรองข้อมูล
2. Select backup file
3. Click: "ฟื้นฟู"
4. Type: `RESTORE_CONFIRM`
5. Click: "ฟื้นฟู" again
6. Restart Backend (close and re-run `start.bat`)

## 🔄 Updating the Application

### From GitHub

```
git pull origin main
python -m pip install --upgrade pip
setup-windows.bat
start.bat
```

### Manual

1. Stop application: `stop.bat`
2. Download new version from GitHub
3. Run: `setup-windows.bat`
4. Run: `start.bat`

Always backup before updating!

## 🔒 Privacy & Security

### What Gets Stored

- ✅ First name and surname (extracted from ID)
- ✅ Team information
- ✅ Verification status
- ✅ Audit logs

### What's NEVER Stored

- ❌ Thai ID numbers (13 digits)
- ❌ ID card images
- ❌ Personal addresses
- ❌ Phone numbers or emails
- ❌ Any government IDs

### Local Processing

- ✅ OCR happens on YOUR computer only
- ✅ No data sent to any server
- ✅ Database is local file (can backup/delete anytime)
- ✅ All processing offline

### Data Deletion

You can delete:
- Individual player records (Review page)
- Entire teams (Teams page)
- All audit logs (Admin → Cleanup)
- Database completely: delete `thai_id_ocr.db`

## 📞 Support

### Common Issues

1. **Scripts won't run**
   - Make sure you're in the project root folder
   - Example: `C:\Users\YourName\thai-id-team-ocr\start.bat`

2. **Ports in use**
   - Close other applications using port 3000 or 8000
   - Use: `stop.bat` to kill the processes

3. **Dependencies missing**
   - Run: `check-deps.bat` to see what's needed
   - Run: `setup-windows.bat` again

4. **OCR not working**
   - Install Tesseract (optional but recommended)
   - Check: `check-deps.bat`

### Getting Help

1. Check: README.md in project root
2. Check: Admin → Local Help page in application
3. Check logs in console windows
4. Check: https://github.com/pattaramet-tech/thai-id-team-ocr

## 📋 Batch Scripts Reference

| Script | Purpose |
|--------|---------|
| `setup-windows.bat` | First-time setup (Python venv, npm install) |
| `start.bat` | Start backend and frontend |
| `stop.bat` | Stop backend and frontend |
| `check-deps.bat` | Check what dependencies are installed |

## 🎯 Typical Workflow

### First Time

```
1. Extract project
2. setup-windows.bat (one-time)
3. start.bat
4. http://localhost:3000/auth/bootstrap-admin (create admin)
5. Login and use app
6. stop.bat
```

### Every Day

```
1. start.bat
2. Use application
3. stop.bat
```

### Before Update

```
1. Admin → สำรองข้อมูล (create backup)
2. Download new version
3. setup-windows.bat
4. start.bat
```

---

**Last Updated:** 2026-06-25  
**Tested On:** Windows 10/11  
**Python:** 3.8+  
**Node.js:** 18+  
