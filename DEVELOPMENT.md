# Development Guide

This guide explains how to set up and develop the Thai ID Team OCR Exporter locally.

## 🔧 Local Development Setup

### Prerequisites

1. **Node.js & npm** (v18+)
   - [Download from nodejs.org](https://nodejs.org/)
   - Verify: `node --version` && `npm --version`

2. **Python** (3.8+)
   - [Download from python.org](https://www.python.org/)
   - Verify: `python --version`
   - Ensure "Add Python to PATH" is checked during installation

3. **Tesseract OCR** (for OCR features)
   - Windows: [Download from GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - Or: `scoop install tesseract` (if using Scoop)
   - Verify: `tesseract --version`

4. **Git**
   - [Download from git-scm.com](https://git-scm.com/)
   - Verify: `git --version`

### Clone Repository

```bash
git clone https://github.com/pattaramet-tech/thai-id-team-ocr.git
cd thai-id-team-ocr
```

### Backend Setup

```bash
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install

# Create .env.local from example
copy .env.example .env.local
```

## 🚀 Running Locally

### Start Backend (Terminal 1)

```bash
cd apps/api
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

python -m uvicorn app.main:app --reload --port 8000
```

Server will run at: `http://localhost:8000`

Check health: `curl http://localhost:8000/health`

### Start Frontend (Terminal 2)

```bash
cd apps/web
npm run dev
```

App will run at: `http://localhost:3000`

## 🧪 Testing

### Backend Tests

```bash
cd apps/api
.\venv\Scripts\activate  # Windows

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ocr.py -v
pytest tests/test_export.py -v

# Run with coverage
pytest tests/ --cov=app
```

### Frontend Linting

```bash
cd apps/web

# Run ESLint
npm run lint

# Build check
npm run build
```

## 📝 Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for functions
- Keep functions focused and single-responsibility

### TypeScript/React
- Use functional components
- Props should be typed
- Use meaningful variable names
- Component files should be in PascalCase
- Keep components focused

## 🔄 Git Workflow

### Creating a Feature Branch

```bash
# Create and checkout new branch
git checkout -b feature/feature-name

# Or for specific phases
git checkout -b phase-{number}-{description}

# Example:
git checkout -b phase-1-teams
```

### Committing Changes

```bash
# Check status
git status

# Stage specific files
git add apps/api/app/services/new_service.py

# Or stage all changes (ensure nothing sensitive is included)
git add -A

# Commit with descriptive message
git commit -m "feat: add new feature description

- Detail 1
- Detail 2
- Detail 3"
```

### Pushing Changes

```bash
# Push to remote
git push origin feature/feature-name

# First time pushing new branch
git push -u origin feature/feature-name
```

### Creating Pull Requests

1. Push your branch to GitHub
2. Go to [Repository](https://github.com/pattaramet-tech/thai-id-team-ocr)
3. Click "New Pull Request"
4. Select your branch
5. Write PR description:
   - What changes were made
   - Why the changes were needed
   - How to test the changes
6. Submit and wait for review

## 📊 Project Structure

```
apps/api/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLite & SQLAlchemy setup
│   ├── models/              # ORM models (Team, Player)
│   ├── routes/              # API endpoints
│   │   ├── teams.py         # Team CRUD
│   │   ├── ocr.py           # OCR upload
│   │   ├── players.py       # Player CRUD
│   │   └── export.py        # Export XLSX
│   ├── schemas/             # Pydantic validation
│   ├── services/            # Business logic
│   │   ├── ocr.py           # OCR processing
│   │   └── export.py        # XLSX generation
│   └── __init__.py
├── tests/                   # Test files
│   ├── test_ocr.py
│   └── test_export.py
├── requirements.txt
└── thai_id_ocr.db          # SQLite database (git-ignored)

apps/web/
├── app/
│   ├── page.tsx             # Dashboard
│   ├── teams/page.tsx       # Teams page
│   ├── ocr/page.tsx         # Upload page
│   ├── review/page.tsx      # Review page
│   ├── export/page.tsx      # Export page
│   ├── layout.tsx           # Root layout
│   └── globals.css
├── lib/
│   └── api.ts               # API client
├── package.json
└── .env.local              # Local env (git-ignored)
```

## 🔐 Environment Variables

### Backend (.env)
```
# No env vars required for local development
# Database: uses local SQLite
# OCR: uses system Tesseract installation
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger API documentation.

### Key Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | /teams | List all teams |
| POST | /teams | Create team |
| POST | /ocr/upload | Upload image for OCR |
| GET | /players | List players (with filters) |
| PATCH | /players/{id} | Update player |
| GET | /export/team/{id} | Export single team |
| GET | /export/all | Export all teams |

## 🐛 Debugging

### Backend

```bash
# Run with debug logging
python -m uvicorn app.main:app --reload --port 8000 --log-level debug

# Test endpoints with curl
curl -X POST http://localhost:8000/teams \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","ageGroup":"U18","gender":"Male"}'
```

### Frontend

```bash
# Check browser console (F12)
# Network tab shows API calls
# React DevTools extension recommended
```

## 📦 Adding Dependencies

### Backend
```bash
cd apps/api
pip install package-name
pip freeze > requirements.txt
git add requirements.txt
```

### Frontend
```bash
cd apps/web
npm install package-name
git add package.json package-lock.json
```

## 🧹 Clean Up

### Remove Virtual Environment
```bash
cd apps/api
Remove-Item -Recurse venv/  # Windows
# rm -rf venv  # macOS/Linux
```

### Reset Database
```bash
Remove-Item apps/api/thai_id_ocr.db  # Windows
# rm apps/api/thai_id_ocr.db  # macOS/Linux
# New database will be created on next backend run
```

### Clear Cache
```bash
# Frontend
cd apps/web
Remove-Item -Recurse .next/

# Python
cd apps/api
Remove-Item -Recurse __pycache__/
Remove-Item -Recurse .pytest_cache/
```

## 📖 Useful Commands

```bash
# Check git status
git status

# See commit history
git log --oneline -10

# See changes before committing
git diff

# Undo uncommitted changes
git restore file.txt

# Create .gitignore for tracked files
git rm --cached filename

# Stash uncommitted changes
git stash
git stash pop
```

## 🆘 Troubleshooting

### Port already in use
```bash
# Find process on port 8000
netstat -ano | findstr :8000

# Kill process (Windows)
taskkill /PID <PID> /F
```

### Module not found
```bash
# Ensure venv is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tesseract not found
```bash
# Install Tesseract
scoop install tesseract

# Or download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### CORS error in frontend
- Check backend is running on port 8000
- Check .env.local has correct API URL
- Check main.py CORS configuration

## 🚀 Deployment

See main README.md for production deployment instructions.

## 📞 Questions?

- Check CLAUDE.md for project guidelines
- Review test files for usage examples
- Check git commit messages for context

---

Happy coding! 🎉
