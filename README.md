# Thai ID Team OCR Exporter

A local-first web app for competition admins to extract Thai first name and surname from Thai national ID card copies or application documents using OCR, review results manually, and export verified players to XLSX by team.

## 📋 Project Status

### ✅ Phase 1: Teams Management - COMPLETE
- Monorepo setup with Next.js + FastAPI
- Teams CRUD operations
- Dashboard home page

### ✅ Phase 2: OCR Upload & Review - COMPLETE
- Image upload with JPG/PNG support
- Thai name extraction with Tesseract OCR
- Thai ID number redaction ([REDACTED_ID])
- Manual review and verification workflow
- Player status tracking (pending/verified/rejected)

### ✅ Phase 3: Export XLSX - COMPLETE
- Single team and all-teams export
- Professional Excel formatting with styling
- Duplicate name detection with warnings
- Frozen headers and alternating row colors
- Timestamp in filename

## 🏗️ Project Structure

```
.
├── apps/
│   ├── web/          # Next.js + React + TypeScript frontend
│   │   ├── app/
│   │   │   ├── page.tsx          # Dashboard
│   │   │   ├── teams/            # Teams management
│   │   │   ├── ocr/              # Upload & OCR
│   │   │   ├── review/           # Review players
│   │   │   └── export/           # Export XLSX
│   │   ├── lib/api.ts            # API client
│   │   └── package.json
│   └── api/          # Python FastAPI backend
│       ├── app/
│       │   ├── main.py           # FastAPI app
│       │   ├── database.py       # SQLite config
│       │   ├── models/           # SQLAlchemy ORM
│       │   ├── routes/           # API endpoints
│       │   ├── schemas/          # Pydantic models
│       │   ├── services/         # Business logic
│       │   └── __init__.py
│       ├── tests/                # Pytest test suites
│       ├── requirements.txt
│       └── thai_id_ocr.db        # SQLite database
├── CLAUDE.md         # Project guidelines
└── README.md         # This file
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Node**: v18+ (LTS recommended)

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: SQLite3
- **ORM**: SQLAlchemy 2.0
- **OCR**: Tesseract (Thai + English support)
- **Image Processing**: OpenCV
- **Excel Export**: openpyxl
- **Python**: 3.8+

## 📦 Installation on Windows

### Prerequisites

1. **Node.js & npm** (v18+)
   - Download from https://nodejs.org/
   - Verify: `node --version` and `npm --version`

2. **Python** (3.8+)
   - Download from https://www.python.org/
   - During installation, **check "Add Python to PATH"**
   - Verify: `python --version`

3. **Tesseract OCR** (required for OCR features)
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Or install via Scoop: `scoop install tesseract`
   - Add to PATH or configure in pytesseract

4. **Git** (optional but recommended)
   - Download from https://git-scm.com/

### Step 1: Install Frontend Dependencies

```powershell
cd apps/web
npm install
```

### Step 2: Install Backend Dependencies

```powershell
cd ../api
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Note on PowerShell execution policy:**
If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🚀 Running the Application

### Terminal 1: Start Backend API

```powershell
cd apps/api
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Start Frontend

```powershell
cd apps/web
npm run dev
```

Expected output:
```
- Local:        http://localhost:3000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## 📊 Features

### 1. Teams Management
- Create teams with name, age group, and gender
- List all teams with creation dates
- Delete teams with confirmation
- View team statistics

### 2. OCR Upload & Processing
- Upload JPG/PNG image files (max 10MB)
- Automatic image preprocessing (grayscale, denoise, threshold)
- Thai & English OCR using Tesseract
- Automatic Thai ID number detection and redaction
- Extract first name and last name automatically
- Display confidence scores

### 3. Manual Review & Verification
- Review pending OCR results
- View raw OCR text with confidence scores
- Edit extracted names manually
- Verify approved players (status = verified)
- Reject poor quality OCR
- Track verification status and dates
- Organized view by status (Pending/Verified/Rejected)

### 4. XLSX Export
- Export verified players to Excel
- Choose single team or all teams
- Separate sheets for each team
- Professional formatting:
  - Blue header row with white text
  - Alternating row colors for readability
  - Frozen header row
  - Auto-sized columns
- Duplicate name warnings before export
- Timestamp in filename for tracking

## 🧪 Testing

### Run Test Suites

```powershell
cd apps/api
.\venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ocr.py -v
pytest tests/test_export.py -v
```

### Test Coverage

**OCR Service Tests (test_ocr.py):**
- ID redaction: single, multiple, non-13-digit numbers
- Thai name extraction from OCR text
- Mixed Thai/English content handling
- Whitespace normalization
- Empty text edge cases

**Export Service Tests (test_export.py):**
- XLSX generation and file validity
- Multi-team export with separate sheets
- Column headers and widths
- Data integrity preservation
- Duplicate detection logic
- Empty team handling

### Manual Testing via UI

1. **Create Teams** (`http://localhost:3000/teams`)
   - Create 2-3 test teams with different age groups

2. **Upload Images** (`http://localhost:3000/ocr`)
   - Upload test images with Thai text
   - Verify OCR results and confidence scores

3. **Review Players** (`http://localhost:3000/review`)
   - Edit extracted names if needed
   - Verify some players
   - Reject any low-confidence results

4. **Export XLSX** (`http://localhost:3000/export`)
   - Export single team XLSX
   - Export all teams XLSX
   - Check formatting in Excel
   - Verify duplicate warnings appear

### Test API Endpoints

```powershell
# Health check
curl http://localhost:8000/health

# List teams
curl http://localhost:8000/teams

# Create team
curl -X POST http://localhost:8000/teams `
  -H "Content-Type: application/json" `
  -d '{"name":"Test Team","ageGroup":"U18","gender":"Male"}'

# Upload file for OCR
curl -F "team_id=1" -F "file=@test_image.jpg" `
  http://localhost:8000/ocr/upload

# List pending players
curl "http://localhost:8000/players?team_id=1&status=pending"

# Verify player
curl -X PATCH http://localhost:8000/players/1 `
  -H "Content-Type: application/json" `
  -d '{"status":"verified"}'

# Export single team
curl -o team_export.xlsx http://localhost:8000/export/team/1

# Export all teams
curl -o all_teams.xlsx http://localhost:8000/export/all

# Check duplicates
curl http://localhost:8000/export/team/1/duplicates
```

## 📁 Database

SQLite database is stored at:
```
apps/api/thai_id_ocr.db
```

### Data Model

**Team**
- `id` (primary key)
- `name` (string)
- `ageGroup` (string)
- `gender` (string)
- `createdAt` (datetime)

**Player**
- `id` (primary key)
- `teamId` (foreign key)
- `firstName` (string, nullable)
- `lastName` (string, nullable)
- `fullName` (string, nullable)
- `sourceFilename` (string)
- `ocrText` (string, nullable, with IDs redacted)
- `confidence` (float, 0-1)
- `status` (enum: pending | verified | rejected)
- `createdAt` (datetime)
- `verifiedAt` (datetime, nullable)

To reset the database:
```powershell
# Delete the database file
Remove-Item apps/api/thai_id_ocr.db

# Restart backend - new database will be created automatically
```

## 🔒 Privacy & Security

### ID Number Protection
- ✅ 13-digit Thai ID numbers automatically detected
- ✅ Redacted to `[REDACTED_ID]` before storage
- ✅ Never exported to Excel
- ✅ Never displayed in UI

### File Security
- ✅ File type validation (JPG/PNG only)
- ✅ File size limit (10MB max)
- ✅ Temporary file handling
- ✅ CORS configured for local access only

### Data Storage
- ✅ First name, surname, full name, team info
- ✅ Source filename for tracking
- ✅ OCR confidence scores
- ✅ Verification status and dates
- ❌ NO ID numbers stored
- ❌ NO personal addresses
- ❌ NO phone numbers

## 🎯 API Endpoints

### Teams
- `POST /teams` - Create team
- `GET /teams` - List all teams
- `GET /teams/{id}` - Get team details
- `PATCH /teams/{id}` - Update team
- `DELETE /teams/{id}` - Delete team

### OCR
- `POST /ocr/upload` - Upload image and extract names

### Players
- `GET /players` - List players (with filtering)
- `GET /players/{id}` - Get player details
- `PATCH /players/{id}` - Update player (edit/verify)
- `DELETE /players/{id}` - Delete player

### Export
- `GET /export/team/{id}` - Export single team to XLSX
- `GET /export/all` - Export all teams to XLSX
- `GET /export/team/{id}/duplicates` - Check duplicate names

### Health
- `GET /health` - API health check

## 📝 Export Format

The exported Excel file includes these columns:

| Column | Description |
|--------|-------------|
| No | Row number (auto-increment) |
| Team | Team name |
| Age Group | Team age group category |
| Gender | Team gender classification |
| First Name | Extracted/verified first name |
| Last Name | Extracted/verified last name |
| Full Name | Complete name |
| Source File | Original image filename |
| Verified Date | Date of verification (YYYY-MM-DD) |

**Formatting:**
- Blue header row with white text
- Alternating row colors (white/light blue)
- Frozen header row for scrolling
- Auto-sized columns
- Borders on all cells
- One sheet per team (multi-team mode)

## 🚦 Troubleshooting

### Backend won't start
```powershell
# Check if venv is activated
.\venv\Scripts\activate

# Check if port 8000 is in use
netstat -ano | findstr :8000

# Reset database
Remove-Item apps/api/thai_id_ocr.db
```

### Frontend can't reach API
- Verify backend is running on `http://localhost:8000`
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Clear browser cache
- Check browser console for CORS errors

### Tesseract not found
- Install from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to Windows PATH or configure in pytesseract config
- Verify: `tesseract --version`

### Python import errors
```powershell
# Reinstall venv and dependencies
Remove-Item apps/api/venv -Recurse
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Excel file won't open
- Verify openpyxl is installed: `pip list | findstr openpyxl`
- Try opening with Excel 2016+ (older versions may have issues)
- Check file wasn't corrupted during download

## 📚 Documentation

- `CLAUDE.md` - Project requirements and guidelines
- `apps/web/package.json` - Frontend dependencies
- `apps/api/requirements.txt` - Backend dependencies

## 🔄 Development Workflow

1. **Create feature branch**
   ```powershell
   git checkout -b feature/feature-name
   ```

2. **Make changes and test**
   - Run tests: `pytest tests/ -v`
   - Test UI manually
   - Check API with curl

3. **Commit changes**
   ```powershell
   git add -A
   git commit -m "Description of changes"
   ```

4. **Verify everything works**
   - Run full test suite
   - Test all workflows
   - Check database integrity

## 📈 Performance Tips

- Database is SQLite (suitable for local testing, small teams)
- Image preprocessing takes ~1-2 seconds per image
- OCR processing takes ~3-5 seconds per image
- Export generation takes ~1 second per 1000 players

For better performance:
- Use SSD for database
- Optimize image preprocessing
- Consider caching OCR results

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Next.js**: https://nextjs.org/docs
- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki
- **openpyxl**: https://openpyxl.readthedocs.io/

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review CLAUDE.md for project guidelines
- Check git commit messages for implementation details
- Run test suites to verify functionality

## 📄 License

This project follows the guidelines in CLAUDE.md.

---

**Last Updated**: 2026-06-23  
**Version**: 0.1.0 (All Phases Complete)
