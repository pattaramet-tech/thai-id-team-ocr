# Thai ID Team OCR Exporter

A local-first web application for competition admins to securely extract Thai first names and surnames from Thai national ID card copies or application documents using OCR, review results manually, and export verified player rosters to XLSX by team.

## 🔒 Privacy & Security First

**This project prioritizes privacy and local-first architecture:**

- ✅ **Local Processing Only**: All OCR processing happens on your machine
- ✅ **No Cloud Upload**: Images never leave your computer
- ✅ **No ID Storage**: Thai national ID numbers (13 digits) are NEVER stored
- ✅ **Data Minimization**: Only extracts first name, surname, and team info
- ✅ **Secure by Design**: Automatic ID redaction before any processing
- ✅ **Full Control**: You own your data - export or delete anytime

## 📋 Features Roadmap

### Phase 0.1: Project Foundation (Current) ✅
- Project structure and documentation
- Local development setup
- GitHub workflow and CI/CD
- Privacy policy documentation
- Team collaboration tools

### Phase 1: Teams Management (Planned)
- Create and manage competition teams
- Team list with filtering
- Delete team functionality
- Team statistics dashboard

### Phase 2: OCR Upload & Review ✅
- Upload JPG/PNG/PDF images
- Tesseract OCR with Thai language support
- Automatic Thai ID number detection and redaction
- Extract first name and surname automatically
- Manual review and verification workflow
- Edit names before verification
- Fuzzy duplicate detection
- Advanced date extraction (Thai/English formats)

### Phase 3: Export XLSX (Planned)
- Export verified players to Excel
- Single team or all teams export
- Professional formatting with headers
- Duplicate name detection and warnings
- Verified player count statistics

### Phase 3: Export XLSX ✅
- Export verified players to Excel
- Single team or all teams export
- Professional formatting with headers
- Duplicate name detection and warnings
- Verified player count statistics

### Phase 4: Local Authentication + Roles + Permission Control ✅
- Local user authentication (no backend required)
- User login with role-based access
- Role types: admin, operator, viewer
- Permission matrix for each role
- Audit logging for all operations
- Password hashing with Argon2

### Phase 5: Local Production Packaging + Backup/Restore + System Health ✅
- Database backup and restore functionality
- Zip Slip vulnerability prevention
- Automatic temp directory cleanup
- System health monitoring endpoint
- Local packaging for distribution

### Phase 5.1: Admin UI for Backup, Restore, System Health, and Local Help ✅
- Admin dashboard with system health status
- Backup creation with export inclusion option
- Backup/restore management UI
- Delete backup functionality
- Restore confirmation with phrase verification
- Local help and setup guide
- Thai language UI labels
- Authentication and authorization checks

### Phase 5.2: Windows One-Click Local Startup + Dependency Checker ✅
- Windows batch scripts for startup/shutdown
- One-click application launch
- Automatic dependency validation
- Folder creation if missing
- Backend health check
- Automatic browser launch
- Clear error messages (Thai/English)
- Port conflict detection and guidance

### Phase 5.3: Update / Release Workflow + Backup Before Update ✅
- Safe update script with GitHub pull
- Automatic backup before update
- Working tree validation
- Dependency installation
- Test suite execution
- Rollback guidance
- Version checking
- Comprehensive update documentation
- Release checklist for maintainers
- Changelog tracking all versions

### Phase 4+: Advanced Features (Future)
- Batch upload with progress indicator
- Team-specific OCR confidence thresholds
- User management and roles configuration
- Desktop app wrapper (Electron/Tauri)

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Fetch API
- **Node.js**: v18+ (LTS recommended)

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (local)
- **ORM**: SQLAlchemy
- **OCR**: Tesseract (Thai + English)
- **Image Processing**: OpenCV
- **PDF Support**: pdf2image + Poppler
- **Duplicate Detection**: difflib (fuzzy name matching)
- **Excel Generation**: openpyxl
- **Python**: 3.8+

### Development & Testing
- **Backend Tests**: pytest
- **Frontend Linting**: ESLint
- **CI/CD**: GitHub Actions
- **Version Control**: Git
- **Package Manager**: npm (frontend), pip (backend)

## 📦 Installation

### Prerequisites

1. **Node.js & npm** (v18+)
   - Download: https://nodejs.org/
   - Verify: `node --version && npm --version`

2. **Python** (3.8+)
   - Download: https://www.python.org/
   - ⚠️ **Important**: Check "Add Python to PATH" during installation
   - Verify: `python --version`

3. **Git**
   - Download: https://git-scm.com/
   - Verify: `git --version`

4. **Poppler** (Required for PDF OCR support)
   - **Windows**: 
     - Download: https://github.com/oschwartz10612/poppler-windows/releases/
     - Extract and add to system PATH, or install via Chocolatey: `choco install poppler`
   - **macOS**: 
     - Install via Homebrew: `brew install poppler`
   - **Linux**: 
     - Ubuntu/Debian: `sudo apt-get install poppler-utils`
     - Already included in GitHub Actions workflow
   - ⚠️ **Note**: PDF support is optional. JPG/PNG OCR works without Poppler.

### Clone Repository

```bash
git clone https://github.com/pattaramet-tech/thai-id-team-ocr.git
cd thai-id-team-ocr
```

### Install All Dependencies

```bash
npm run install-all
```

Or install separately:

**Frontend:**
```bash
cd apps/web
npm install
```

**Backend:**
```bash
cd apps/api
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## 🖥️ Windows Quick Start (One-Click)

**For Windows 10/11 users, the easiest way:**

### First Time Setup
```batch
setup-windows.bat
```
This installs everything in 2-5 minutes.

### Every Day - Just Double-Click
```batch
start.bat
```
Then:
- Browser opens automatically at http://localhost:3000
- Backend runs on http://localhost:8000
- Close the two windows or run `stop.bat` to stop

### Shutdown
```batch
stop.bat
```

### Update the App
```batch
update-windows.bat
```
This safely:
- Creates backup of your database
- Pulls latest code from GitHub
- Installs new dependencies
- Runs tests to verify
- Provides rollback guidance if needed

For details, see: **[docs/UPDATE_GUIDE.md](docs/UPDATE_GUIDE.md)**

For detailed Windows setup, see: **[docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md)**

## 🚀 Running Locally (All Platforms)

### Option 1: Run Backend Only

```bash
cd apps/api
.\venv\Scripts\activate  # Windows

python -m uvicorn app.main:app --reload --port 8000
```

Server runs at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### Option 2: Run Frontend Only

```bash
cd apps/web
npm run dev
```

App runs at: `http://localhost:3000`

### Option 3: Run Both (Recommended)

**Terminal 1 - Backend:**
```bash
cd apps/api
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
```

Then open: `http://localhost:3000`

## 🧪 Running Tests

### Backend Tests

```bash
cd apps/api
.\venv\Scripts\activate  # Windows

pytest tests/ -v              # Run all tests
pytest tests/test_ocr.py -v   # Run specific test
pytest tests/ --cov=app       # Run with coverage
```

### Frontend Linting

```bash
cd apps/web
npm run lint
npm run build  # Build check
```

## 📁 Folder Structure

```
thai-id-team-ocr/
├── apps/
│   ├── api/                    # Python FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py         # FastAPI app entry point
│   │   │   ├── database.py     # SQLite configuration
│   │   │   ├── models/         # SQLAlchemy ORM models
│   │   │   │   ├── team.py
│   │   │   │   └── player.py
│   │   │   ├── routes/         # API endpoints
│   │   │   │   ├── teams.py
│   │   │   │   ├── ocr.py
│   │   │   │   ├── players.py
│   │   │   │   └── export.py
│   │   │   ├── schemas/        # Pydantic validation models
│   │   │   ├── services/       # Business logic
│   │   │   │   ├── ocr.py      # OCR processing
│   │   │   │   └── export.py   # XLSX generation
│   │   │   └── __init__.py
│   │   ├── tests/              # Test files
│   │   │   ├── test_ocr.py
│   │   │   └── test_export.py
│   │   ├── requirements.txt    # Python dependencies
│   │   ├── .env.example        # Environment template
│   │   └── thai_id_ocr.db      # SQLite database (git-ignored)
│   │
│   └── web/                    # Next.js React frontend
│       ├── app/
│       │   ├── page.tsx        # Dashboard
│       │   ├── layout.tsx      # Root layout
│       │   ├── teams/          # Teams page
│       │   ├── ocr/            # Upload page
│       │   ├── review/         # Review page
│       │   ├── export/         # Export page
│       │   ├── globals.css     # Global styles
│       │   └── favicon.ico
│       ├── lib/
│       │   └── api.ts          # API client
│       ├── public/             # Static assets
│       ├── package.json        # Node dependencies
│       ├── .env.local          # Local config (git-ignored)
│       ├── .env.example        # Config template
│       ├── next.config.ts      # Next.js config
│       └── tsconfig.json       # TypeScript config
│
├── .github/
│   └── workflows/              # GitHub Actions CI/CD
│       ├── test-backend.yml
│       └── test-frontend.yml
│
├── .gitignore                  # Git exclusions
├── package.json                # Root npm scripts
├── README.md                   # This file
├── CLAUDE.md                   # Project instructions
├── DEVELOPMENT.md              # Development guide
├── PHASES.md                   # Phase tracking
└── GITHUB_SETUP.md             # GitHub workflow guide
```

## 🔄 Development Workflow

### Create Feature Branch

```bash
git checkout -b feature/feature-name
# Or for phases: git checkout -b phase-1-teams
```

### Make Changes

```bash
# Edit files, test locally
npm run dev    # Frontend
pytest tests/  # Backend
```

### Commit & Push

```bash
git add .
git commit -m "feat: describe your changes"
git push -u origin feature/feature-name
```

### Create Pull Request

1. Go to: https://github.com/pattaramet-tech/thai-id-team-ocr
2. Click "New Pull Request"
3. Describe changes
4. Wait for CI/CD checks
5. Merge when approved

## 🔐 Security & Privacy

### What Gets Stored
- ✅ First name (extracted from ID/document)
- ✅ Surname (extracted from ID/document)
- ✅ Full name (combined for easy searching)
- ✅ Team information (team name, age group, gender)
- ✅ Source file name (which image was processed)
- ✅ OCR confidence score
- ✅ Verification status
- ✅ Verification timestamp

### What NEVER Gets Stored
- ❌ Thai ID numbers (13-digit)
- ❌ Personal ID numbers of any kind
- ❌ Addresses
- ❌ Phone numbers
- ❌ Email addresses
- ❌ Raw ID card images (only extracts names)
- ❌ Any government-issued numbers

### How Security is Implemented
- All processing happens locally on your machine
- Images are processed and discarded after OCR
- ID numbers are automatically detected and redacted to `[REDACTED_ID]`
- No data is sent to external servers
- SQLite database is stored locally and can be backed up/deleted

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | Project overview and setup (this file) |
| **CLAUDE.md** | Project requirements and constraints |
| **DEVELOPMENT.md** | Local development guide |
| **PHASES.md** | Phase tracking and timeline |
| **GITHUB_SETUP.md** | GitHub workflow and CI/CD |

## 🆘 Troubleshooting

### Port Already In Use
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### Python Module Not Found
```bash
cd apps/api
.\venv\Scripts\activate  # Ensure venv is activated
pip install -r requirements.txt
```

### Frontend Won't Connect to API
- Check backend is running on `http://localhost:8000`
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Clear browser cache

### PDF Upload Fails (poppler-utils error)
- Install Poppler (see Prerequisites section above)
- **Windows**: Add Poppler `/bin` folder to system PATH
- **Linux/macOS**: Use package manager as shown above
- **Workaround**: Use JPG/PNG files instead (OCR still works without PDF support)

## 🔍 When OCR Doesn't Work - Troubleshooting Guide

Sometimes OCR results are inaccurate or missing data. Here's how to troubleshoot:

### Problem: Names Not Extracting (Empty First/Last Name)

**Why it happens:**
- Text in ID/document is blurry or low-quality
- Unusual name format or font the OCR engine doesn't recognize
- Text color/background contrast is poor
- Image is too small (less than 100x100 pixels)

**How to fix:**
1. **Check Image Quality**
   - Ensure image is clear, well-lit, and in focus
   - Scan at higher resolution (300 DPI minimum)
   - JPG/PNG format works best; PDF requires Poppler

2. **Improve Lighting**
   - Avoid shadows and glare on the ID card
   - Use natural daylight or bright indoor lighting
   - No flash reflection on the document

3. **Adjust Image Size**
   - Image should be at least 300x300 pixels
   - Crop to show only the relevant text area
   - Avoid excessive empty space

4. **Manual Entry**
   - If OCR fails completely, you can manually enter names
   - Click on the name fields in the review screen and type in the correct names
   - The system will accept manually-entered names

### Problem: Low Confidence Score (Warning: "Low OCR confidence")

**Why it happens:**
- Text extraction succeeded but the OCR engine is uncertain about accuracy
- Confidence below 70% shows a warning but doesn't block entry
- Common with handwritten text or poor image quality

**How to fix:**
1. **Verify Extracted Names**
   - Even with low confidence, OCR result may be correct
   - Compare with original ID/document
   - Only correct if names are actually wrong

2. **Re-upload Better Image**
   - Recapture image with better lighting/focus
   - Larger, clearer images improve confidence
   - Each upload tries multiple preprocessing techniques automatically

3. **Accept with Caution**
   - Low confidence warnings let you save the result
   - You can always edit names later in the Review page
   - Confidence is an indicator, not a blocker

### Problem: Date of Birth Not Extracting

**Why it happens:**
- Date missing from OCR: "Could not extract date of birth"
- Common if ID doesn't have clearly visible birthdate
- Special date formats may not be recognized

**How to fix:**
1. **Check Image Contains Date**
   - Verify birthdate is visible in image
   - Must have day, month, year format
   - Supported formats:
     - Thai: `23 ก.ย. 2552` or `23 กย 2552` (with/without dots)
     - English: `23 September 2009` or `Sep. 23 2009`
     - ISO: `2009-09-23` or Slash: `23/09/2009`

2. **Manual Entry**
   - Click the date field in review screen
   - Select date from calendar picker
   - Manually type if calendar doesn't work

3. **Thai Date Tips**
   - Buddhist Era dates (BE) work: 2552 BE = 2009 AD
   - Accepted month abbreviations:
     - Thai: ม.ค., กพ., มีค., เมย., พค., มิย., กค., สค., กย., ตค., พย., ธค.
     - Also: มค, กพ, มีค, เมย, พค, มิย, กค, สค, กย, ตค, พย, ธค (without dots)

### Problem: ID Number Shows in Debug Info

**Why it happens:**
- Debug info shows redacted text (with `[REDACTED_ID]` placeholder)
- This is for troubleshooting purposes only
- ID numbers are never stored in the database

**How to use:**
1. **View Debug Info**
   - Click "Show Debug Info" in OCR result (if available)
   - Shows what the OCR engine extracted
   - Helps diagnose why name extraction failed

2. **Copy Redacted Text**
   - Debug info displays redacted version
   - Safe to share for support/troubleshooting
   - Original ID numbers remain private

3. **Privacy Assurance**
   - No ID numbers are stored in database
   - No ID numbers are exported to Excel
   - Debug info is temporary (not persisted)

### Problem: Too Many Names Being Extracted (Multiple Names as One)

**Why it happens:**
- OCR extracted text from multiple lines as single name
- Name fields may contain suffix or title words
- Mixed text from document labels

**How to fix:**
1. **Edit Names**
   - Review screen shows extracted names
   - Click to edit individual fields
   - Remove extra words/suffixes

2. **Expected Extraction**
   - First name: Given name (ชื่อ)
   - Last name: Family name (นามสกุล)
   - Title like "นาย" or "นางสาว" is removed automatically

### Enabling Debug Mode for Support

If problems persist:

1. **Export Debug Info**
   - After upload, click "Show Debug Info"
   - Copy the redacted OCR text
   - Note the preprocessing method and confidence score

2. **Share for Support**
   - Include which image file caused issue
   - Share debug info (redacted text only)
   - Describe what information is missing/wrong

3. **Technical Details**
   - Preprocessing methods: default, resize2x, resize3x, adaptive, contrast, sharpen
   - Tesseract PSM modes: 6 (block), 11 (sparse text), 12 (raw line)
   - System tries all combinations and picks best result

## 📊 Project Statistics

- **Total Files**: 50+
- **Lines of Code**: ~2,900
- **Test Coverage**: 20+ test cases
- **Documentation**: 5 comprehensive guides
- **CI/CD**: 2 GitHub Actions workflows

## 🤝 Contributing

1. Clone the repository
2. Create a feature branch
3. Make changes following commit message guidelines
4. Push to GitHub
5. Create pull request
6. Wait for CI checks to pass
7. Request review from team

**Commit Message Format:**
```
type: short description

- Detail 1
- Detail 2

Types: feat, fix, docs, refactor, test, chore
```

## 🧪 Phase 5.3 Update/Release Testing Checklist

### Update Script Test
- [ ] Run `update-windows.bat` with clean working tree
- [ ] Script checks git is installed
- [ ] Script validates working tree is clean
- [ ] Script creates backup before pull
- [ ] Backup file created in backups/ folder
- [ ] Git pull succeeds
- [ ] Python dependencies install
- [ ] Node dependencies install
- [ ] Backend tests run and pass
- [ ] Frontend builds successfully
- [ ] Success message shows
- [ ] Old backup files still exist (not deleted)

### Backup Before Update Test
- [ ] Backup created successfully
- [ ] Backup has timestamp in filename
- [ ] Backup metadata file created
- [ ] Backup contains database file
- [ ] Backup size > 0 bytes
- [ ] Multiple backups can coexist

### Version Check Test
- [ ] Run `python scripts/check_version.py`
- [ ] Shows current local version
- [ ] Shows latest git tag
- [ ] Shows latest commit
- [ ] Correctly identifies if update available
- [ ] Returns proper exit code

### Rollback Test (After Failed Update)
- [ ] Restore from Admin UI works
- [ ] Restore from backup file works
- [ ] Old data restored correctly
- [ ] Database queries work after restore
- [ ] User accounts intact
- [ ] Player records intact

### Working Tree Validation Test
- [ ] Make uncommitted changes (edit file)
- [ ] Run `update-windows.bat`
- [ ] Script detects changes and stops
- [ ] Clear error message shown
- [ ] Suggests git add/commit/stash
- [ ] No update happens

### Edge Cases
- [ ] Database missing (creates backup anyway)
- [ ] Network timeout (clear error message)
- [ ] Large database (backup succeeds)
- [ ] Many files changed in update
- [ ] New dependencies added
- [ ] Dependencies removed

### Documentation Test
- [ ] UPDATE_GUIDE.md is comprehensive
- [ ] RELEASE_CHECKLIST.md is accurate
- [ ] CHANGELOG.md lists all versions
- [ ] README update section works
- [ ] Links to all docs are valid
- [ ] Instructions are clear

## 🧪 Phase 5.2 Windows Startup Testing Checklist

### Setup Script Test
- [ ] Run `setup-windows.bat` from project root
- [ ] Python venv created successfully
- [ ] Python dependencies installed (no errors)
- [ ] Node modules installed (no errors)
- [ ] All required folders created (uploads/, exports/, temp/, backups/)
- [ ] Dependency check shows correct status

### Dependency Checker Test
- [ ] Run `check-deps.bat` 
- [ ] Shows Python version
- [ ] Shows Node.js version
- [ ] Shows npm version
- [ ] Shows Tesseract status (OK or missing)
- [ ] Shows Thai language status (OK, missing, or N/A)
- [ ] Shows Poppler status (OK or missing)
- [ ] Shows venv status (found or missing)
- [ ] Shows node_modules status (found or missing)
- [ ] Summary shows OK/WARN/ERROR counts
- [ ] Returns correct exit code

### Start Script Test
- [ ] Run `start.bat` from project root
- [ ] Dependency check passes
- [ ] Creates folders if missing
- [ ] Backend starts in separate window (Port 8000)
- [ ] Backend health check passes
- [ ] Frontend starts in separate window (Port 3000)
- [ ] Browser opens automatically at http://localhost:3000
- [ ] Shows clear message with port numbers
- [ ] No errors in either window
- [ ] Can access backend docs: http://localhost:8000/docs
- [ ] Can login and access admin pages

### Stop Script Test
- [ ] Run `stop.bat`
- [ ] Backend process (port 8000) stops or shows message
- [ ] Frontend process (port 3000) stops or shows message
- [ ] Shows clear shutdown message
- [ ] No error messages

### Port Conflict Test
- [ ] Use something on port 8000 to cause conflict
- [ ] `start.bat` shows clear error message
- [ ] `stop.bat` can recover if possible
- [ ] Instructions provided for manual cleanup

### Dependency Missing Test
- [ ] Temporarily remove/rename Python venv
- [ ] Run `setup-windows.bat` - should recreate it
- [ ] Run `check-deps.bat` - should show missing then OK
- [ ] Clear browser cache, login works

### User Experience Test
- [ ] Script messages are in clear English/Thai
- [ ] No cryptic error codes
- [ ] Instructions are actionable (run this, download that)
- [ ] Pauses between steps so user can read
- [ ] Progress is visible (not silent)

## 🧪 Phase 5.1 Testing Checklist

### Admin Access & Authorization
- [ ] Admin can navigate to `/admin/system` page
- [ ] Operator/Viewer cannot access admin pages (redirects to home)
- [ ] Login required to access admin pages
- [ ] User info displays correctly in header

### System Health Page
- [ ] App version displays correctly (v0.5.0)
- [ ] Database status shows "healthy"
- [ ] All directories show "พร้อมใช้งาน" (ok)
- [ ] Tesseract status shows correct installation status
- [ ] Thai language data shows correct status
- [ ] Poppler status shows correctly (warning if not installed)
- [ ] Statistics show correct counts (teams, players, audit logs)
- [ ] Disk usage shows correctly in MB
- [ ] Status badges use correct Thai labels and colors

### Backup & Restore Page
- [ ] Create backup button works
- [ ] `include_exports` checkbox defaults to unchecked
- [ ] Backup file appears in list after creation
- [ ] Backup filename, date, and size display correctly
- [ ] Download button downloads backup file
- [ ] Delete button removes backup after confirmation
- [ ] Delete requires confirmation modal
- [ ] Restore button opens confirmation modal
- [ ] Restore modal requires typing "RESTORE_CONFIRM"
- [ ] Restore works successfully (database is restored)
- [ ] After restore, shows message to restart backend
- [ ] include_exports checkbox works when checked
- [ ] Backup file size increases when include_exports=true

### Local Help Page
- [ ] All 7 sections load correctly
- [ ] Code blocks display with proper formatting
- [ ] Thai labels are correct (สร้างไฟล์สำรอง, ฟื้นฟูข้อมูล, etc.)
- [ ] Installation instructions are clear
- [ ] Setup guide is comprehensive
- [ ] Privacy checklist displays all items

### Header Navigation
- [ ] Main nav shows: ทีม, Upload & OCR, Review, Export
- [ ] Admin nav shows: สถานะระบบ, สำรองข้อมูล, คู่มือ (admin only)
- [ ] User info shows correct username and role
- [ ] Logout button works and clears token
- [ ] Active page highlights in nav

### Security
- [ ] /system/health requires admin token (test with curl)
- [ ] Restore requires confirmation phrase "RESTORE_CONFIRM"
- [ ] Backup files have .zip extension only
- [ ] Path traversal attempts blocked (../../../ etc)
- [ ] No password/token in response
- [ ] No Thai ID numbers displayed anywhere

### Performance
- [ ] System health page loads in < 2 seconds
- [ ] Backup list loads quickly
- [ ] No console errors in browser
- [ ] No TypeScript errors on build

### Edge Cases
- [ ] Create backup works with include_exports=true
- [ ] Create backup works with include_exports=false (default)
- [ ] Download works for large backup files
- [ ] Restore works from different backup
- [ ] Delete backup when no backups left shows "ยังไม่มีไฟล์สำรอง"
- [ ] Unauthorized access redirects to login

## 📞 Support

- Check **CLAUDE.md** for project requirements
- Check **DEVELOPMENT.md** for setup help
- Check **GITHUB_SETUP.md** for workflow questions
- Review git commits for implementation details

## 📄 License

This project is created for competition administration purposes with strict privacy controls.

---

**Status:** Phase 5.3 Update/Release Workflow (Complete) ✅  
**Current Version:** 0.5.3  
**Last Updated:** 2026-06-25  
**Repository:** https://github.com/pattaramet-tech/thai-id-team-ocr

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| **README.md** | Project overview and quick start (this file) |
| **CLAUDE.md** | Project requirements and constraints |
| **DEVELOPMENT.md** | Development workflow and standards |
| **CHANGELOG.md** | Version history and what changed |
| **docs/WINDOWS_SETUP.md** | Windows installation and troubleshooting |
| **docs/UPDATE_GUIDE.md** | How to safely update the application |
| **docs/RELEASE_CHECKLIST.md** | Pre-release validation checklist |
