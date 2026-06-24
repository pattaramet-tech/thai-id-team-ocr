# Release Checklist - Thai ID Team OCR

**Checklist before releasing a new version**

## 🔍 Code Quality Checks

### Backend Tests
- [ ] Run all tests
  ```bash
  cd apps/api
  python -m pytest tests/ -v
  ```
- [ ] All tests pass (no failures)
- [ ] No critical warnings
- [ ] Test coverage maintained or improved
- [ ] New features have tests

### Frontend Build
- [ ] Build succeeds
  ```bash
  cd apps/web
  npm run build
  ```
- [ ] No TypeScript errors
- [ ] No ESLint warnings (if enabled)
- [ ] All pages load correctly

### Code Review
- [ ] No hardcoded credentials
- [ ] No console.log left in production code
- [ ] No sensitive data in logs
- [ ] No Thai ID numbers in database
- [ ] No Cloud API usage
- [ ] All privacy constraints met

## 🔐 Security Checks

### File Integrity
- [ ] No `uploads/` files committed
- [ ] No `exports/` files committed
- [ ] No `backups/` files committed
- [ ] No `temp/` files committed
- [ ] No database file (`.db`) committed
- [ ] No `.env` with real values committed
- [ ] No real ID card images committed

### Dependencies
- [ ] All dependencies are secure
- [ ] No vulnerable packages
- [ ] requirements.txt updated
- [ ] package.json updated

### Authentication
- [ ] No passwords stored in plain text
- [ ] No tokens in code
- [ ] API endpoints properly authenticated
- [ ] Admin endpoints require authorization

## 🖥️ Windows Integration Tests

### Startup Script
- [ ] `setup-windows.bat` creates venv
- [ ] `setup-windows.bat` installs dependencies
- [ ] `start.bat` starts backend (port 8000)
- [ ] `start.bat` starts frontend (port 3000)
- [ ] `start.bat` opens browser automatically
- [ ] `stop.bat` stops both services gracefully
- [ ] `check-deps.bat` shows correct status

### First Time User Experience
- [ ] Extract project folder
- [ ] Run `setup-windows.bat` (completes without errors)
- [ ] Run `start.bat` (application starts)
- [ ] Browser opens at http://localhost:3000
- [ ] Login page appears
- [ ] Create admin user via bootstrap
- [ ] Login with admin credentials
- [ ] Admin pages accessible
- [ ] Can see System Health page
- [ ] Database is empty but functional

### Update Experience
- [ ] `update-windows.bat` checks working tree
- [ ] `update-windows.bat` creates backup
- [ ] `update-windows.bat` pulls from GitHub
- [ ] Dependencies update correctly
- [ ] Tests run and pass
- [ ] Database is not affected
- [ ] Old backup files still exist
- [ ] Rollback guidance provided

## 📋 Feature Testing

### Core Features
- [ ] Teams management works
- [ ] OCR upload and processing works
- [ ] Player review and verification works
- [ ] Export to XLSX works
- [ ] Backup creation works
- [ ] Backup restoration works
- [ ] System health shows correct info
- [ ] User authentication works

### Admin Features
- [ ] System Health page shows all status
- [ ] Backup page lists backups correctly
- [ ] Backup download works
- [ ] Restore requires confirmation phrase
- [ ] Help guide displays properly
- [ ] User logout works

### Edge Cases
- [ ] Port 3000 already in use (startup shows error)
- [ ] Port 8000 already in use (startup shows error)
- [ ] Backend offline (frontend still loads)
- [ ] Database missing (creates new one)
- [ ] Large backup file (download works)
- [ ] Many players in team (export works)

## 📚 Documentation Checks

### README.md
- [ ] Windows Quick Start section exists
- [ ] Installation instructions accurate
- [ ] Features list updated
- [ ] Known issues documented
- [ ] Links working (not broken)

### WINDOWS_SETUP.md
- [ ] Installation steps clear
- [ ] Troubleshooting comprehensive
- [ ] Tesseract instructions step-by-step
- [ ] Poppler instructions step-by-step
- [ ] Privacy checklist complete

### UPDATE_GUIDE.md
- [ ] Update steps clear
- [ ] Backup instructions complete
- [ ] Rollback procedures documented
- [ ] Troubleshooting section comprehensive

### CHANGELOG.md
- [ ] All changes documented
- [ ] Version number matches code
- [ ] Date is correct
- [ ] Categories are clear
- [ ] Breaking changes highlighted

### RELEASE_CHECKLIST.md (This file)
- [ ] Checklist is complete
- [ ] All items tested
- [ ] No gaps in coverage

## 🏷️ Version Management

### Version File
- [ ] `apps/api/app/version.py` has new version
- [ ] Version follows semantic versioning (X.Y.Z)
- [ ] Version incremented correctly:
  - Major: Breaking changes
  - Minor: New features (backward compatible)
  - Patch: Bug fixes

### Git Tags
- [ ] Create git tag: `git tag vX.Y.Z`
- [ ] Tag message describes version
- [ ] Tag matches code version

### Changelog
- [ ] CHANGELOG.md updated with new version
- [ ] All changes listed
- [ ] Categories: Added, Changed, Fixed, Removed
- [ ] Breaking changes noted

## 🚀 Release Steps

### Final Preparation
- [ ] All checklist items above are ✓
- [ ] All tests pass locally
- [ ] Code reviewed
- [ ] No uncommitted changes

### Git Operations
```bash
# Create commit (if needed)
git add .
git commit -m "vX.Y.Z: Release notes"

# Create tag
git tag -a vX.Y.Z -m "Release vX.Y.Z: Description"

# Push to GitHub
git push origin main
git push origin vX.Y.Z
```

### Post-Release
- [ ] GitHub release created (optional)
- [ ] Release notes published
- [ ] Users notified (if applicable)
- [ ] Monitor for issues

## ✅ Sign-Off

Before releasing:

- [ ] Developer: Code quality complete
- [ ] Tester: All features work
- [ ] Security: No vulnerabilities
- [ ] Documentation: All updated
- [ ] Project Lead: Approval

## 📊 Checklist Statistics

This checklist has:
- 50+ items to check
- 5 major categories
- Covers: code, security, features, docs, release

**Time to complete:** ~1-2 hours depending on changes

## 🔄 Version History

| Version | Date | Status |
|---------|------|--------|
| v0.5.2 | 2026-06-25 | In Progress |
| v0.5.1 | 2026-06-25 | Released ✓ |
| v0.5.0 | 2026-06-25 | Released ✓ |
| v0.4.0 | 2026-06-23 | Released ✓ |
| v0.3.0 | 2026-06-20 | Released ✓ |
| v0.2.x | 2026-06-18 | Released ✓ |
| v0.1.x | 2026-06-16 | Released ✓ |

---

**Last Updated:** 2026-06-25  
**Applicable To:** All releases  
