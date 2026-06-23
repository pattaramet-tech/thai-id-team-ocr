# Thai ID Team OCR Exporter

A local-first web app for competition admins to extract Thai first name and surname from Thai national ID card copies or application documents using OCR, review results manually, and export verified players to XLSX by team.

## 🏗️ Project Structure

```
.
├── apps/
│   ├── web/          # Next.js + React + TypeScript frontend
│   └── api/          # Python FastAPI backend
├── CLAUDE.md         # Project guidelines
└── README.md         # This file
```

## 📋 Phase 1 - Teams Management (Current)

✅ Complete:
- Monorepo structure (apps/web, apps/api)
- Next.js frontend with TypeScript
- Python FastAPI backend with SQLite
- Teams CRUD API endpoints
- Teams management UI page
- Dashboard home page

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

3. **Git** (optional but recommended)
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

**Note**: On PowerShell, if you get an execution policy error:
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

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Start Frontend

```powershell
cd apps/web
npm run dev
```

You should see:
```
- Local:        http://localhost:3000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## 🧪 Testing

### Test Teams API

1. **List Teams**
   ```powershell
   curl http://localhost:8000/teams
   ```

2. **Create Team**
   ```powershell
   curl -X POST http://localhost:8000/teams `
     -H "Content-Type: application/json" `
     -d '{"name":"Team A","ageGroup":"U18","gender":"Male"}'
   ```

3. **Check Health**
   ```powershell
   curl http://localhost:8000/health
   ```

### Test UI

1. Navigate to http://localhost:3000/teams
2. Click "Create Team"
3. Fill in:
   - Team Name: "Test Team"
   - Age Group: "U18"
   - Gender: "Male"
4. Click "Create Team"
5. Verify the team appears in the table
6. Test Delete button

## 📁 Database

SQLite database is stored at:
```
apps/api/thai_id_ocr.db
```

To reset the database, delete this file and restart the backend.

## 🔒 Privacy Rules (Phase 1)

- ✅ Only storing: first name, surname, full name, team, age group, source filename, OCR confidence, verified status
- ✅ Not storing Thai national ID numbers
- ✅ No ID number exports
- Uploaded images treated as temporary files (auto-delete feature coming in Phase 2)

## 📝 Data Model

### Team
- `id` (int, primary key)
- `name` (string)
- `ageGroup` (string)
- `gender` (string)
- `createdAt` (datetime)

### Player (coming in Phase 2)
- `id` (int, primary key)
- `teamId` (int, foreign key)
- `firstName` (string)
- `lastName` (string)
- `fullName` (string)
- `sourceFilename` (string)
- `ocrText` (string, nullable)
- `confidence` (float)
- `status` (string: pending | verified | rejected)
- `createdAt` (datetime)
- `verifiedAt` (datetime, nullable)

## 🔌 API Endpoints

### Teams
- `POST /teams` - Create team
- `GET /teams` - List all teams
- `GET /teams/{team_id}` - Get team details
- `PATCH /teams/{team_id}` - Update team
- `DELETE /teams/{team_id}` - Delete team

### Health
- `GET /health` - API health check

## 🚦 Troubleshooting

### Backend won't start
- Make sure venv is activated: `.\venv\Scripts\activate`
- Check port 8000 is not in use: `netstat -ano | findstr :8000`
- Delete `thai_id_ocr.db` to reset database

### Frontend can't reach API
- Verify backend is running on http://localhost:8000
- Check `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Clear browser cache if needed

### Python import errors
- Delete `venv` folder and reinstall: `python -m venv venv`
- Reinstall dependencies: `pip install -r requirements.txt`

## 📚 Next Steps (Phase 2)

- [ ] OCR file upload (POST /ocr/upload)
- [ ] Tesseract OCR integration
- [ ] Player review table
- [ ] Manual name correction
- [ ] Duplicate detection within team
- [ ] Image preprocessing

## 📞 Support

For issues or questions, refer to CLAUDE.md in the project root.
