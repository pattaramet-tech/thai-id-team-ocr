# Thai ID Team OCR Exporter

## Goal
Build a local-first web app for competition admins to extract Thai first name and surname from Thai national ID card copies or application documents using OCR, review the result manually, and export verified players to XLSX by team.

## Privacy Rules
- Do not store Thai national ID numbers.
- Do not export ID numbers.
- Store only first name, surname, full name, team, age group, source filename, OCR confidence, and verified status.
- Uploaded images should be treated as temporary files.
- Add a setting to auto-delete uploaded files after OCR.
- OCR must run locally by default.

## Tech Stack
- Frontend: Next.js + React + TypeScript
- Backend: Python FastAPI
- OCR: Tesseract OCR with Thai and English language data
- Image processing: OpenCV
- Database: SQLite
- XLSX export: openpyxl
- Development: VS Code + Claude Code

## Main Features
1. Create and manage teams.
2. Upload image or PDF files for a selected team.
3. Preprocess images before OCR.
4. Extract Thai first name and surname.
5. Show OCR result in a review table.
6. Allow manual correction before saving.
7. Export verified player list to XLSX by team.
8. Detect duplicate full names within the same team.

## UX Requirement
The app must never auto-finalize OCR results. Every OCR result must be reviewed and confirmed by an admin.

## Data Model
Team:
- id
- name
- ageGroup
- gender
- createdAt

Player:
- id
- teamId
- firstName
- lastName
- fullName
- sourceFilename
- ocrText
- confidence
- status: pending | verified | rejected
- createdAt
- verifiedAt

## API Endpoints
- POST /teams
- GET /teams
- POST /ocr/upload
- GET /players?teamId=
- PATCH /players/:id
- POST /export/team/:teamId

## Development Rule
Implement in small phases. After each phase, provide:
- changed files
- how to run
- how to test
- known limitations