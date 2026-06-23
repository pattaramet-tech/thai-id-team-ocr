# Thai ID Team OCR Exporter - Project Instructions

## 🎯 Goal

Build a local-first, privacy-preserving web application for competition admins to:
1. Upload Thai national ID card copies or application document images
2. Automatically extract first name and surname using OCR
3. Manually review and verify extracted names
4. Export verified player rosters to XLSX, organized by team

The application must never store Thai national ID numbers and must emphasize local processing for privacy.

## 🔐 Privacy Rules (CRITICAL)

These are hard requirements:

1. **No ID Numbers Stored**
   - Thai national ID numbers (13 digits) MUST NEVER be stored in database
   - Automatically detect and redact ID numbers to `[REDACTED_ID]` before processing
   - Validate: grep database for `\d{13}` should return nothing

2. **No ID Numbers Exported**
   - Excel exports must NOT contain any ID numbers
   - Only export: first name, surname, team name, age group, gender, source filename

3. **Local Processing Only**
   - All OCR processing happens on user's machine
   - Images are never sent to cloud services
   - No external APIs for text extraction
   - Tesseract OCR must run locally

4. **Minimal Data Collection**
   - Only store what's necessary: first name, surname, full name, team info, source filename, confidence score, verification status
   - No addresses, phone numbers, email addresses, or other personal data
   - No government-issued numbers of any kind

5. **Image Handling**
   - Images should be treated as temporary files
   - Provide option to auto-delete uploaded files after OCR
   - Do not store original image files permanently
   - Clear explanation of image data handling in UI

6. **Transparent Data Model**
   - Users must understand exactly what data is stored
   - Provide privacy policy in UI explaining data storage
   - Allow data export and deletion on demand

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 16+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **State**: Client-side React state only
- **API Client**: Fetch API with TypeScript types

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite (local only, no remote database)
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic
- **OCR**: Tesseract OCR with Thai language data
- **Image Processing**: OpenCV
- **Excel Export**: openpyxl
- **API Documentation**: Swagger/OpenAPI auto-generated

### Development
- **Testing**: pytest for backend, ESLint for frontend
- **Version Control**: Git with GitHub
- **CI/CD**: GitHub Actions
- **Code Quality**: Type checking, linting, tests required before merge
- **Package Management**: npm (frontend), pip (backend)

## 📊 Data Model

### Teams Table
```
id              - Primary key
name            - Team name (required)
ageGroup        - Age group/category (required)
gender          - Gender category (required)
createdAt       - Creation timestamp
```

### Players Table
```
id              - Primary key
teamId          - Foreign key to Teams
firstName       - First name (extracted, nullable)
lastName        - Last name/surname (extracted, nullable)
fullName        - Complete name (nullable)
sourceFilename  - Original image filename
ocrText         - Raw OCR text (with IDs redacted)
confidence      - OCR confidence score (0.0 - 1.0)
status          - Status: pending | verified | rejected
createdAt       - Creation timestamp
verifiedAt      - Verification timestamp (nullable)
```

**Security Note**: Never store ID numbers anywhere, including ocrText. Redact them to `[REDACTED_ID]`.

## 🔌 API Endpoints Plan

### Teams
- `POST /teams` - Create team
- `GET /teams` - List all teams
- `GET /teams/{id}` - Get team details
- `PATCH /teams/{id}` - Update team
- `DELETE /teams/{id}` - Delete team

### OCR Processing
- `POST /ocr/upload` - Upload image file and extract names
  - File validation (JPG/PNG only, max 10MB)
  - Automatic ID redaction
  - Returns extracted Player record with status="pending"

### Players
- `GET /players` - List players with optional filters
  - Query params: team_id, status (pending|verified|rejected)
- `GET /players/{id}` - Get player details
- `PATCH /players/{id}` - Update player (edit names, verify/reject)
- `DELETE /players/{id}` - Delete player record

### Export
- `GET /export/team/{id}` - Export single team to XLSX
- `GET /export/all` - Export all teams to XLSX (separate sheets)
- `GET /export/team/{id}/duplicates` - Check for duplicate names in team

### Health
- `GET /health` - API health check

## 📋 Development Phases

### Phase 0.1: Project Foundation (Current)
- ✅ Project structure and setup
- ✅ Documentation (README, CLAUDE, DEVELOPMENT guide)
- ✅ GitHub workflow and CI/CD
- ✅ Git branching strategy
- ✅ .gitignore for sensitive data
- ⏳ Team collaboration tools setup

**Deliverables**: Complete documentation, GitHub Actions workflows

### Phase 1: Teams Management
- [ ] Create database schema (Teams table)
- [ ] Teams CRUD API endpoints
- [ ] Teams management UI page
- [ ] List teams with creation dates
- [ ] Delete team functionality
- [ ] Dashboard home page

**Deliverables**: Teams management fully functional with UI

### Phase 2: OCR Upload & Review
- [ ] Create Players table and ORM model
- [ ] Image upload endpoint with validation
- [ ] Tesseract OCR integration
- [ ] Image preprocessing with OpenCV
- [ ] Thai ID number detection and redaction
- [ ] Thai name extraction service
- [ ] Players CRUD API endpoints
- [ ] Review players UI page
- [ ] Manual name editing and verification workflow
- [ ] Status tracking (pending/verified/rejected)
- [ ] Comprehensive test suite

**Deliverables**: Full OCR upload and review workflow

### Phase 3: Export XLSX
- [ ] Export service with openpyxl
- [ ] Single team XLSX export endpoint
- [ ] Multi-team XLSX export (separate sheets)
- [ ] Duplicate name detection service
- [ ] Professional Excel formatting
- [ ] Export UI page
- [ ] Verified players count statistics
- [ ] Test suite for export

**Deliverables**: Complete export functionality with formatting

### Phase 4+: Advanced Features (Future)
- [ ] Batch upload UI with progress
- [ ] Fuzzy duplicate name matching
- [ ] User authentication and roles
- [ ] Audit logging
- [ ] Advanced OCR preprocessing options
- [ ] Team-specific configuration

## ⚠️ Forbidden Actions

**NEVER do these:**

1. **Store ID Numbers**
   - ❌ Never store Thai national ID numbers (13 digits)
   - ❌ Never export ID numbers to Excel
   - ❌ Never display ID numbers in UI
   - ✅ Always redact to `[REDACTED_ID]`

2. **Send Data to Cloud**
   - ❌ Never upload images to cloud services
   - ❌ Never send data to external APIs
   - ❌ Never use cloud OCR services (AWS Textract, Google Vision, etc.)
   - ✅ Always process locally with Tesseract

3. **Store Sensitive Data**
   - ❌ Never store addresses, phone numbers, email
   - ❌ Never store government-issued IDs/numbers
   - ❌ Never store biometric data
   - ✅ Only store first name, surname, team info

4. **Bypass Privacy Controls**
   - ❌ Never skip ID redaction
   - ❌ Never store raw image files permanently
   - ❌ Never collect data not explicitly needed
   - ✅ Always provide data export/deletion options

5. **Ignore Security Warnings**
   - ❌ Don't commit .env files with credentials
   - ❌ Don't commit database files
   - ❌ Don't commit node_modules or venv
   - ❌ Don't commit user uploads
   - ✅ Keep .gitignore comprehensive

## 🔍 Code Quality Standards

### All Code Must
- [ ] Have type hints (TypeScript/Python)
- [ ] Pass linting checks (ESLint/flake8)
- [ ] Have test coverage for new features
- [ ] Include documentation strings
- [ ] Follow commit message format
- [ ] Not have console.log/print debugging statements in production code

### Before Committing
```bash
# Backend
pytest tests/ -v          # All tests pass
pylint app/               # Code style check

# Frontend
npm run lint              # ESLint passes
npm run build             # Build succeeds
```

### Commit Message Format
```
type: short description

- Detailed change 1
- Detailed change 2

Types: feat, fix, docs, refactor, test, chore
```

## 🧪 Testing Requirements

### Backend (pytest)
- Unit tests for OCR service (ID redaction, name extraction)
- Unit tests for export service (XLSX generation, formatting)
- Integration tests for API endpoints
- At least 80% code coverage for critical functions

### Frontend
- ESLint must pass (no warnings)
- Build must succeed
- No console errors in development

## 📦 Dependencies

### Frontend (apps/web/package.json)
```json
{
  "dependencies": {
    "next": "16.2.9",
    "react": "19.2.4",
    "react-dom": "19.2.4"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^19",
    "typescript": "^5",
    "tailwindcss": "^4",
    "eslint": "^9"
  }
}
```

### Backend (apps/api/requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
python-dotenv==1.0.0
pydantic==2.5.0
opencv-python==4.8.1.78
pytesseract==0.3.10
pillow==10.1.0
python-multipart==0.0.6
openpyxl==3.1.2
pytest==7.4.3
```

## 🚀 Deployment Considerations

- Application should work offline (local processing)
- Database is local SQLite (no migrations needed yet)
- No environment secrets required for base functionality
- Optional: Docker containerization for easier distribution
- Optional: Desktop app wrapper using Electron/Tauri

## 📚 Documentation Requirements

Each phase must include:
- [ ] Changed files list
- [ ] Installation/setup instructions
- [ ] How to run the feature
- [ ] How to test the feature
- [ ] Known limitations
- [ ] Security/privacy notes

## ✅ Success Criteria

The project is successful when:
- ✅ Users can manage teams locally
- ✅ Users can upload images and extract names locally
- ✅ Users can manually verify OCR results
- ✅ Users can export verified players to Excel
- ✅ No Thai ID numbers are ever stored
- ✅ All data stays on user's machine
- ✅ Complete test coverage for critical paths
- ✅ Clear documentation for users and developers

## 🔗 References

- Next.js: https://nextjs.org/docs
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- openpyxl: https://openpyxl.readthedocs.io/

---

**Project Owner**: pattaramet.i@gmail.com  
**Created**: 2026-06-23  
**Status**: Phase 0.1 Foundation (In Progress)
