# GitHub Workflow Setup

This document provides the complete GitHub configuration for the Thai ID Team OCR Exporter project.

## ✅ GitHub Repository Status

**Repository:** https://github.com/pattaramet-tech/thai-id-team-ocr  
**Access:** Private (secure for development)  
**Default Branch:** `main`  
**Status:** ✅ Ready for team collaboration

---

## 🔐 Security Checklist

### ✅ Verified Safe for GitHub

- **No sensitive data:** ✅
  - No Thai ID card images
  - No actual export files
  - No database files
  - No .env files with credentials
  - No node_modules or venv directories

- **No user data:** ✅
  - No uploaded image files
  - No personal information
  - No export files with names

- **.gitignore comprehensive:** ✅
  - Excludes: `*.db`, `*.sqlite`, `.env`, `.env.local`
  - Excludes: `node_modules/`, `.venv/`, `venv/`
  - Excludes: `uploads/`, `exports/`, `*.xlsx`
  - Excludes: `__pycache__/`, `.pytest_cache/`

### Git Security Status

```bash
# Check what files are tracked
git ls-files | wc -l  # Should be ~50 files

# Verify no sensitive files
git ls-files | grep -E "(\.db|\.env|node_modules|venv)"  # Should return nothing
```

---

## 📦 Files Organized for GitHub

### Project Files ✅
```
.gitignore              - Comprehensive exclusions
README.md               - Main documentation
CLAUDE.md               - Project requirements
DEVELOPMENT.md          - Local setup guide
PHASES.md               - Development timeline
```

### Workflow Files ✅
```
.github/workflows/
├── test-backend.yml    - Python tests on every push
└── test-frontend.yml   - Next.js build on every push
```

### Environment Files ✅
```
apps/api/.env.example     - Backend config template
apps/web/.env.example     - Frontend config template
```

### Example Files (NOT ACTUAL DATA)
```
All example files are safe to commit
No real user data included
```

---

## 🌿 Branch Structure

### Main Branch
```
main (default)
├── Production-ready code
├── All tests passing
├── Automated CI/CD checks
└── Latest stable version
```

### Development Branches
```
phase-1-teams            - Snapshot of Phase 1 completion
feature/feature-name     - Feature branches for new work
bugfix/bug-description   - Bug fix branches
```

### Tagging Convention
```
v0.1.0 - Phase 1: Teams Management
v0.2.0 - Phase 2: OCR Upload & Review
v0.3.0 - Phase 3: Export XLSX
```

---

## 🔄 GitHub Actions (CI/CD)

### Automated Testing

**Backend Tests** (`test-backend.yml`)
```
Triggered: On push to main in apps/api/**
- Install Python 3.10
- Install dependencies from requirements.txt
- Run pytest tests/ -v
- Reports results
```

**Frontend Tests** (`test-frontend.yml`)
```
Triggered: On push to main in apps/web/**
- Install Node.js 18
- Install dependencies with npm
- Run npm run lint
- Run npm run build
- Reports build status
```

### Viewing Results

1. Go to: https://github.com/pattaramet-tech/thai-id-team-ocr/actions
2. Click on workflow run
3. See test results and logs
4. Green ✅ = all tests passed
5. Red ❌ = fix required before merge

---

## 📝 Git Commands Reference

### Initial Setup (Already Done ✅)
```bash
# Repository initialized
git init

# GitHub remote configured
git remote add origin https://github.com/pattaramet-tech/thai-id-team-ocr.git

# All commits pushed
git push -u origin main
```

### Creating Feature Branches

```bash
# Create branch from main
git checkout -b feature/feature-name

# Or for phase work
git checkout -b phase-2-ocr

# Push branch for first time
git push -u origin feature/feature-name

# Later: just push
git push origin feature/feature-name
```

### Committing Changes

```bash
# See what changed
git status

# Stage specific files
git add apps/api/app/services/new_file.py

# Or stage all (VERIFY FIRST - check git status)
git add -A

# Commit with message
git commit -m "feat: add new feature

- Detail 1 of what was changed
- Detail 2
- Detail 3"

# Or for fixes
git commit -m "fix: fix bug description

- Root cause
- Solution applied"

# Or for documentation
git commit -m "docs: update README with new sections"

# Or for code cleanup
git commit -m "refactor: simplify function logic

- Before: 50 lines
- After: 30 lines
- No behavior change"
```

### Pushing Changes

```bash
# Push current branch
git push

# Or explicitly
git push origin branch-name

# Push all branches
git push origin --all

# Push with tags
git push origin --tags
```

### Creating Pull Requests

```bash
# After pushing your branch, go to GitHub:
# https://github.com/pattaramet-tech/thai-id-team-ocr/compare

# Or use GitHub CLI:
gh pr create --title "Feature title" --body "Description of changes"
```

### Merging Changes

```bash
# Merge branch to main (locally)
git checkout main
git pull origin main
git merge feature/feature-name

# Or via GitHub:
# 1. Go to pull request
# 2. Click "Merge pull request"
# 3. Click "Confirm merge"
# 4. Delete branch option appears
```

### Tagging Releases

```bash
# Create tag for version
git tag v0.3.0

# Create annotated tag
git tag -a v0.3.0 -m "Release version 0.3.0"

# Push tag
git push origin v0.3.0

# Push all tags
git push origin --tags
```

---

## 🚀 Common Workflows

### Starting New Feature Work

```bash
# Update main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/descriptive-name

# Make changes and commit
git add files
git commit -m "commit message"

# Push branch
git push -u origin feature/descriptive-name

# Create pull request on GitHub
```

### Working on Multiple Features

```bash
# Switch between branches
git checkout feature-1
git checkout feature-2

# See all branches
git branch -a

# See current branch
git status
```

### Keeping Branch Up to Date

```bash
# Get latest from main
git fetch origin main

# Rebase your branch on main (preferred)
git rebase origin/main

# Or merge (creates merge commit)
git merge origin/main

# Push your updated branch
git push origin feature-name
```

### Undoing Changes

```bash
# See what will change
git diff

# Undo unstaged changes
git checkout -- file.txt

# Undo staged changes
git reset HEAD file.txt

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Stash changes temporarily
git stash

# Get back stashed changes
git stash pop
```

---

## 📊 Commit Message Format

### Format
```
<type>: <subject>

<body>

<footer>
```

### Type
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Code style (no logic change)
- `refactor` - Refactoring (no behavior change)
- `test` - Adding tests
- `chore` - Build, dependencies, etc.

### Subject
- Imperative mood: "add" not "added"
- Don't capitalize first letter
- No period at end
- Maximum 50 characters

### Body
- Explain what and why, not how
- Wrap at 72 characters
- Can be multiple paragraphs
- Use bullet points

### Example
```bash
git commit -m "feat: add XLSX export with professional formatting

- Implement openpyxl-based export service
- Support single team and multi-team export modes
- Add duplicate name detection
- Format with blue headers and alternating colors
- Freeze header row for easy scrolling

Closes #42"
```

---

## 🔍 Code Review Practices

### Before Pushing
```bash
# Check what you're committing
git status
git diff

# Ensure tests pass
pytest tests/ -v  # Backend
npm run build     # Frontend

# Verify no sensitive files
git status | grep -E "(\.env|\.db|uploads)"
```

### Pull Request Review
1. Clear title describing what changed
2. Detailed description of why
3. Link related issues: "Fixes #123"
4. Test checklist:
   - [ ] All tests passing
   - [ ] No breaking changes
   - [ ] Code style followed
5. Screenshots for UI changes

### Review Checklist
- [ ] Tests included for new code
- [ ] Documentation updated
- [ ] No debug code or console.logs
- [ ] No hardcoded values
- [ ] Security implications considered
- [ ] Performance impact considered

---

## 📋 Release Checklist

When ready to release:

```bash
# 1. Update version in code/docs
# 2. Update CHANGELOG (if using one)
# 3. Create release commit
git commit -m "chore: bump version to 0.4.0"

# 4. Create tag
git tag -a v0.4.0 -m "Release version 0.4.0"

# 5. Push commits and tags
git push origin main
git push origin v0.4.0

# 6. Create GitHub Release
#    Go to: https://github.com/pattaramet-tech/thai-id-team-ocr/releases
#    Click "Draft new release"
#    Select tag v0.4.0
#    Add release notes
```

---

## 🆘 Help & Troubleshooting

### Git Authentication
```bash
# If push fails with auth error, set credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@github.com"

# For SSH (recommended):
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### Branch Conflicts
```bash
# If merge has conflicts:
# 1. Edit conflicting files
# 2. Remove conflict markers (<<<<<<, ======, >>>>>>)
# 3. Stage resolved files
git add resolved_file.py

# 4. Complete merge
git commit -m "chore: merge conflicts resolved"
```

### Lost Commits
```bash
# Find lost commits
git reflog

# Recover from reflog
git checkout <commit-hash>

# Create branch from recovery point
git checkout -b recovery-branch
```

### Checking Repository Size
```bash
# See repository size
git count-objects -v

# See largest files
git rev-list --all --objects | sort -k2 | tail -10
```

---

## 📚 Resources

- GitHub Guides: https://guides.github.com/
- Pro Git Book: https://git-scm.com/book/
- GitHub CLI: https://cli.github.com/

---

## ✅ Setup Complete

Your project is now configured for:
- ✅ Secure GitHub repository
- ✅ Automated testing on every push
- ✅ Code review with pull requests
- ✅ Version tagging and releases
- ✅ Team collaboration

**Next Steps:**
1. Share repository URL with team
2. Team members clone and set up locally
3. Create feature branches for new work
4. Submit pull requests for review
5. Merge to main when approved

---

**Repository:** https://github.com/pattaramet-tech/thai-id-team-ocr  
**Last Updated:** 2026-06-23  
**Status:** ✅ Ready for Production
