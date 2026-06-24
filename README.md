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

### Phase 4: Advanced Features (Future)
- Batch upload with progress indicator
- Fuzzy duplicate detection
- Team-specific OCR confidence thresholds
- Audit log for all operations
- User authentication and roles

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

## 🚀 Running Locally

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

## 📞 Support

- Check **CLAUDE.md** for project requirements
- Check **DEVELOPMENT.md** for setup help
- Check **GITHUB_SETUP.md** for workflow questions
- Review git commits for implementation details

## 📄 License

This project is created for competition administration purposes with strict privacy controls.

---

**Status:** Phase 0.1 Foundation (In Progress)  
**Last Updated:** 2026-06-23  
**Repository:** https://github.com/pattaramet-tech/thai-id-team-ocr
