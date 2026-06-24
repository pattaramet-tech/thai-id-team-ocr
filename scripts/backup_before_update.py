#!/usr/bin/env python3
"""Create backup before updating the application."""

import subprocess
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

def backup_database():
    """Create offline backup of database."""
    db_path = Path("thai_id_ocr.db")

    if not db_path.exists():
        print("[WARN] Database not found - nothing to backup")
        return None

    # Create backups folder if needed
    backups_dir = Path("backups")
    backups_dir.mkdir(exist_ok=True)

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_filename = f"thai-id-team-ocr-backup-{timestamp}.zip"
    backup_path = backups_dir / backup_filename

    try:
        # Simple database backup: just copy the file
        # In a real scenario with concurrent access, we'd use SQLite backup API
        shutil.copy2(db_path, backups_dir / f"thai_id_ocr-{timestamp}.db")

        # Create a metadata file
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "backup_type": "pre-update",
            "database_file": f"thai_id_ocr-{timestamp}.db",
            "includes_exports": False,
            "includes_uploads": False,
        }

        metadata_file = backups_dir / f"backup-{timestamp}.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"[OK] Database backup created: backups/{metadata_file.name}")
        print(f"     Database file: backups/{metadata['database_file']}")
        return str(backup_path)
    except Exception as e:
        print(f"[ERROR] Failed to create backup: {str(e)}")
        return None

def backup_via_api():
    """Try to create backup via API."""
    try:
        import requests

        # Get token from localStorage (for Windows)
        # For update script, we don't have browser access
        # So we'll use API directly

        print("[INFO] Attempting to create backup via API...")

        # Check if backend is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code != 200:
                print("[WARN] Backend health check failed")
                return None
        except Exception:
            print("[INFO] Backend not running, using offline backup")
            return None

        # Backend is running but we can't authenticate without token
        # Fall back to offline backup
        print("[INFO] Backend running but need authentication")
        return None

    except ImportError:
        # requests not installed, use offline backup
        return None

def main():
    """Create backup before update."""
    print("\n" + "="*60)
    print("Creating Backup Before Update")
    print("="*60 + "\n")

    # Try API backup first (if backend running)
    backup_file = backup_via_api()

    # Fall back to offline backup
    if not backup_file:
        backup_file = backup_database()

    if backup_file:
        print("\n[OK] Backup created successfully!")
        print(f"     Location: {backup_file}")
        print("\nYou can restore this backup later using:")
        print("  - Admin UI → สำรองข้อมูล → Restore")
        print("  - Or Python script")
        return True
    else:
        print("\n[ERROR] Failed to create backup!")
        print("Aborting update to prevent data loss")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
