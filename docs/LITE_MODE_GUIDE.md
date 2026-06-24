# Lite Mode Guide - Thai ID Team OCR

**Simple usage for small teams - OCR names and export to Excel**

## 🎯 What is Lite Mode?

Lite Mode simplifies the application to focus on the main tasks:
- ✅ Create teams
- ✅ Upload and process ID card images (OCR)
- ✅ Review and verify names
- ✅ Export verified names to Excel
- ✅ Simple backup

Advanced features like audit logs, system health, and user management are hidden.

## 🚀 How to Use Lite Mode

### 1. Enable Lite Mode

The application comes with Lite Mode enabled by default.

To verify it's enabled:
- Check `apps/web/.env.lite` exists
- If using Lite Mode: advanced menus should be hidden

### 2. Daily Workflow (7 Steps)

#### Step 1: Start the Application
```batch
start.bat
```

Then:
- Backend starts on port 8000
- Frontend starts on port 3000
- Browser opens automatically
- Login with your admin account

#### Step 2: View Teams
After login, you go directly to Teams page.

Create a new team if needed:
- Click "สร้างทีม" (Create Team)
- Enter team name (e.g., "U18 Male")
- Select age group and gender
- Click "สร้าง" (Create)

#### Step 3: Upload Images

Go to: **Upload & OCR**

- Select the team
- Click "เลือกไฟล์" (Select Files)
- Choose image files (JPG, PNG, or PDF)
- OCR runs automatically
- Names are extracted

#### Step 4: Review Players

Go to: **Review**

For each player:
- Check extracted first name
- Check extracted last name
- Check date of birth (if extracted)
- Edit if needed
- Click "ยืนยัน" (Verify) to approve
- Or click "ปฏิเสธ" (Reject) to remove

#### Step 5: Export to Excel

Go to: **Export XLSX**

- Select the team
- Click "ส่งออก" (Export)
- File downloads as Excel (.xlsx)

Contains:
- First names (verified)
- Last names (verified)
- Team name
- Age group
- Gender
- Source filename

#### Step 6: Backup Data

Go to: **สำรองข้อมูล** (Backup)

- Click "สร้างไฟล์สำรอง" (Create Backup)
- File saves automatically
- Shows filename and size

Use backup if you want to save your work.

#### Step 7: Clean Up (Optional)

After finishing a batch:
- Delete individual players if needed (from Review page)
- Delete upload files if done processing
- Keep backup file safe

## 📋 Common Tasks

### Create a Team

```
1. Click "สร้างทีม"
2. Enter team name
3. Select age group
4. Select gender
5. Click "สร้าง"
```

### Upload Images

```
1. Go to "Upload & OCR"
2. Select team
3. Choose image files
4. OCR runs automatically
```

### Edit Player Name

```
1. Go to "Review"
2. Find player
3. Click "แก้ไข" (Edit)
4. Change first/last name
5. Save changes
```

### Verify Player

```
1. Go to "Review"
2. Check extracted information
3. Click "ยืนยัน" (Verify)
```

### Export Team to Excel

```
1. Go to "Export XLSX"
2. Select team
3. Click "ส่งออก"
4. File downloads
```

### Backup Database

```
1. Go to "สำรองข้อมูล"
2. Click "สร้างไฟล์สำรอง"
3. Note the filename
4. Keep safe
```

## 🔒 Privacy & Security

### What's Stored
- ✅ First name and surname (from OCR)
- ✅ Team information
- ✅ Verification status
- ✅ Source filename

### What's NOT Stored
- ❌ Thai ID numbers (13 digits)
- ❌ ID card images
- ❌ Personal addresses
- ❌ Phone numbers
- ❌ Government-issued numbers

### Local Processing
- ✅ All OCR happens on your machine
- ✅ Images never go to cloud
- ✅ Database is local file
- ✅ You have full control

## ⚠️ Important Notes

### Thai ID Numbers

**IMPORTANT**: This application does NOT store Thai national ID numbers.

If ID numbers are visible in extracted text:
- They are automatically redacted to `[REDACTED_ID]`
- Not stored in database
- Not included in Excel export

### Image Upload

**Important**:
- Images are processed locally
- Only names are extracted
- Images are temporary files
- You can delete them after processing

### Backup Your Work

Before finishing a session:
- Go to "สำรองข้อมูล"
- Click "สร้างไฟล์สำรอง"
- Keep the backup file safe
- You can download it later

## 🆘 Troubleshooting

### Application Won't Start
```
Run: start.bat
If error appears:
  1. Read error message carefully
  2. Run: setup-windows.bat
  3. Try again
```

### OCR Not Working
```
If images don't process:
  1. Check image format (JPG, PNG, or PDF)
  2. Try smaller image file
  3. Check file size < 10 MB
  4. Restart application
```

### Can't Export to Excel
```
If export fails:
  1. Make sure some players are verified
  2. Check team has verified players
  3. Save again
  4. Try again
```

### Lost Data / Want to Restore
```
If you have backup:
  1. Go to "สำรองข้อมูล"
  2. Select backup file
  3. Click "ฟื้นฟู" (Restore)
  4. Type: RESTORE_CONFIRM
  5. Confirm
  6. Restart application
```

## 📊 Typical Session

**Time: ~30 minutes for 20 people**

```
1. Create team (2 min)
2. Upload 20 image files (5 min)
3. Review 20 names (15 min)
4. Export to Excel (1 min)
5. Backup (1 min)
6. Total: ~24 minutes
```

**Performance:**
- Faster for clear images
- Slower for blurry/tilted images
- Average: 1-2 minutes per person

## 💾 Backup Strategy

### Recommended Backup Schedule

- **After each session**: Create backup
- **Before major changes**: Create backup
- **Weekly**: Create backup
- **Monthly**: Archive old backups

### Backup Location
```
backups/ folder in project
File format: thai-id-team-ocr-backup-YYYYMMDD-HHMMSS.zip
```

## 🔧 System Requirements

**Minimum:**
- Windows 10/11
- 2 GB RAM
- 500 MB disk space

**Recommended:**
- Windows 10/11
- 4+ GB RAM
- 2+ GB disk space
- SSD for faster processing

**Optional (for PDF support):**
- Poppler (PDF to image converter)
- Not required if using JPG/PNG only

## ✨ Tips & Tricks

### Faster OCR Processing
- Use clear, well-lit photos
- Avoid rotation or tilt
- Use JPG format (smaller files)
- One person per image is best

### Accurate Name Extraction
- Photos should show full ID card
- Names should be clearly visible
- Font should be legible
- Avoid shadows on text

### Faster Team Setup
- Have team name, age group, gender ready
- Create all teams at start
- Then upload batches of images

### Verification Workflow
1. Review flagged duplicates first
2. Verify clear names quickly
3. Edit unclear names carefully
4. Reject obvious errors immediately

## 📞 Support

### Quick Help
1. Read error messages carefully
2. Try the Troubleshooting section above
3. Check main README.md in project

### More Help
- See: docs/WINDOWS_SETUP.md
- See: docs/UPDATE_GUIDE.md
- See: README.md

---

**Thai ID Team OCR - Lite Mode**

Designed for small teams needing simple OCR for names and Excel export.

**Status**: Stable ✅  
**Privacy**: 100% Local ✅  
**Cost**: Free ✅
