# Changelog - Thai ID Team OCR

All notable changes to this project are documented here.

## [0.5.2] - 2026-06-25

### Added
- Windows one-click startup scripts (`start.bat`, `stop.bat`)
- Setup automation for Windows (`setup-windows.bat`)
- Dependency checker tool (`check-deps.bat`, `check_deps.py`)
- Windows setup documentation (`docs/WINDOWS_SETUP.md`)
- Update workflow for safe GitHub pulls (`update-windows.bat`)
- Pre-update backup automation
- Version checker script (`check_version.py`)
- Update guide documentation (`docs/UPDATE_GUIDE.md`)
- Release checklist (`docs/RELEASE_CHECKLIST.md`)
- Backup before update functionality
- Rollback guidance and procedures

### Changed
- Improved startup reliability with health checks
- Enhanced dependency validation before startup
- Better error messages for Windows users (Thai/English)

### Fixed
- Unicode encoding issues in Windows batch scripts
- Port conflict handling with clear guidance

## [0.5.1] - 2026-06-25

### Added
- Admin UI for system management (`/admin/system`, `/admin/backup`, `/admin/help`)
- System health monitoring dashboard
- Backup and restore management interface
- Local help and setup guide in admin panel
- Header navigation component with admin menu
- Status badge component (Thai labels)
- Confirmation modal component for destructive operations
- User login page (`/auth/login`)
- Admin bootstrap page (`/auth/bootstrap-admin`)
- Phase 5.1 testing checklist (58 test items)

### Features
- System health displays database, directories, dependencies status
- Backup creation with optional exports inclusion
- Secure restore with "RESTORE_CONFIRM" phrase verification
- Backup download and delete functionality
- Thai language support throughout admin UI
- Local help guide with installation instructions
- Clear status badges for system components

### Security
- Admin-only page access control
- Authentication required for sensitive operations
- Restore confirmation to prevent accidental data loss
- No sensitive data exposure in UI

## [0.5.0] - 2026-06-25

### Added
- Backup and restore functionality
- System health monitoring endpoint
- Zip Slip vulnerability prevention in backup restore
- Safe temporary directory cleanup
- Centralized version management (`apps/api/app/version.py`)
- Pre-restore backup creation
- Include exports option for backups
- Secure backup filename validation

### Security
- Zip Slip attack prevention with path validation
- Temp directory cleanup in finally blocks
- Path traversal defense
- Backup filename validation (no ../, /)
- 9 new security tests

### Changed
- Separated `/health` (public) from `/system/health` (admin-only)
- Updated backup service with safe extraction

### Testing
- All 182 backend tests pass
- Frontend build successful
- Security tests for Zip Slip, path traversal, temp cleanup

## [0.4.0] - 2026-06-23

### Added
- Local authentication system (no backend required)
- User login functionality
- Role-based access control (admin, operator, viewer)
- Permission matrix for each role
- Audit logging for all operations
- User bootstrap endpoint for first admin creation
- JWT token authentication
- Password hashing with Argon2

### Features
- Three user roles: admin (all), operator (limited), viewer (read-only)
- Secure password storage with Argon2
- 8-hour JWT token expiration
- Audit logging with action tracking
- User info endpoints

### Security
- No plaintext passwords
- Argon2 password hashing
- JWT token validation
- Role-based endpoint protection

## [0.3.0] - 2026-06-20

### Added
- Audit logging for all operations
- Data retention policies
- Cleanup tools for old logs and data
- Audit log API endpoints
- Manual cleanup trigger
- Cleanup status monitoring

### Features
- Comprehensive audit logging
- Configurable retention periods
- Automatic log cleanup
- Data deletion workflows

### Security
- Audit trail for compliance
- Data minimization practices

## [0.2.x] - 2026-06-18

### Added
- Batch OCR upload functionality
- PDF support with Poppler
- Fuzzy duplicate detection using difflib
- Advanced date extraction (Thai/English formats)
- Batch processing progress tracking

### Features
- Multiple file upload at once
- PDF to image conversion
- Fuzzy name matching for duplicates
- Thai date format support
- English month name parsing
- Buddhist year (BE) conversion

### Fixed
- Thai name title removal (longest-first matching)
- Date extraction improvements
- Duplicate detection accuracy

## [0.1.x] - 2026-06-16

### Added
- Teams management (CRUD operations)
- OCR upload and processing
- Manual player review and verification
- Export to XLSX functionality
- Player duplicate detection
- Status tracking (pending/verified/rejected)
- Basic database schema (Teams, Players tables)

### Features
- Create and manage competition teams
- Upload ID card images
- Tesseract OCR with Thai support
- Manual name verification
- Export verified players to Excel
- Player editing and status updates

### Security
- No Thai ID number storage
- ID number redaction to [REDACTED_ID]
- Local processing only

---

## Semantic Versioning

This project uses Semantic Versioning (MAJOR.MINOR.PATCH):

- **MAJOR** (X in X.0.0): Breaking changes
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes

## Migration Guide

### From v0.4.x to v0.5.0
- Database schema unchanged
- Backup/restore added (not required)
- No manual migration needed

### From v0.3.x to v0.4.0
- Authentication system added
- Users must create admin account at `/auth/bootstrap-admin`
- Existing data preserved

### From v0.2.x to v0.3.0
- Audit logging added
- No data migration needed
- Cleanup tools available

---

**Last Updated:** 2026-06-25  
**Current Version:** 0.5.2 (Phase 5.2)
