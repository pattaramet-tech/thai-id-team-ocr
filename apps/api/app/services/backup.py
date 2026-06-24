import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import AuditLog
from app.services.audit import AuditService


class BackupService:
    """Service for creating and restoring backups."""

    BACKUP_DIR = Path("backups")
    DATABASE_FILE = "thai_id_ocr.db"
    INCLUDE_DIRS = ["exports"]  # Include exports but not uploads/temp
    EXCLUDE_DIRS = ["uploads", "temp", "__pycache__", ".pytest_cache", "venv"]

    @staticmethod
    def _ensure_backup_dir():
        """Create backup directory if it doesn't exist."""
        BackupService.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _is_safe_path(backup_filename: str) -> bool:
        """Check if backup filename is safe (no path traversal)."""
        if ".." in backup_filename or "/" in backup_filename or "\\" in backup_filename:
            return False

        # Should end with .zip
        if not backup_filename.endswith(".zip"):
            return False

        return True

    @staticmethod
    def create_backup(db: Session, db_path: str = "thai_id_ocr.db", actor_name: str = "system") -> Dict[str, Any]:
        """
        Create a backup of the database and exports.

        Args:
            db: Database session
            db_path: Path to database file
            actor_name: User creating backup

        Returns:
            Backup info dict
        """
        BackupService._ensure_backup_dir()

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_filename = f"thai-id-team-ocr-backup-{timestamp}.zip"
        backup_path = BackupService.BACKUP_DIR / backup_filename

        try:
            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
                # Add database file
                if os.path.exists(db_path):
                    zf.write(db_path, arcname="thai_id_ocr.db")

                # Add exports directory
                for include_dir in BackupService.INCLUDE_DIRS:
                    if os.path.exists(include_dir):
                        for file_path in Path(include_dir).rglob("*"):
                            if file_path.is_file():
                                arcname = file_path.relative_to(".")
                                zf.write(file_path, arcname=arcname)

            backup_info = {
                "filename": backup_filename,
                "created_at": datetime.now().isoformat(),
                "size_bytes": backup_path.stat().st_size,
                "size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2)
            }

            # Log backup creation
            AuditService.log_action(
                db,
                action="backup_created",
                entity_type="system",
                message=f"Backup created: {backup_filename}",
                metadata=backup_info,
                actor_name=actor_name
            )

            return {
                "success": True,
                "backup": backup_info
            }

        except Exception as e:
            AuditService.log_action(
                db,
                action="backup_failed",
                entity_type="system",
                message=f"Backup failed: {str(e)}",
                actor_name=actor_name
            )
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def list_backups() -> List[Dict[str, Any]]:
        """List all available backups."""
        BackupService._ensure_backup_dir()

        backups = []
        for file_path in sorted(BackupService.BACKUP_DIR.glob("*.zip"), reverse=True):
            stat = file_path.stat()
            backups.append({
                "filename": file_path.name,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return backups

    @staticmethod
    def get_backup_path(filename: str) -> Optional[Path]:
        """Get safe backup path if filename is valid."""
        if not BackupService._is_safe_path(filename):
            return None

        backup_path = BackupService.BACKUP_DIR / filename
        if backup_path.exists() and backup_path.is_file():
            return backup_path

        return None

    @staticmethod
    def delete_backup(filename: str, db: Session, actor_name: str = "system") -> Dict[str, Any]:
        """Delete a backup file."""
        backup_path = BackupService.get_backup_path(filename)

        if not backup_path:
            return {
                "success": False,
                "error": "Backup not found or invalid filename"
            }

        try:
            backup_path.unlink()

            AuditService.log_action(
                db,
                action="backup_deleted",
                entity_type="system",
                message=f"Backup deleted: {filename}",
                actor_name=actor_name
            )

            return {"success": True}

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def restore_backup(
        filename: str,
        db: Session,
        db_path: str = "thai_id_ocr.db",
        actor_name: str = "system"
    ) -> Dict[str, Any]:
        """
        Restore from a backup file.

        Args:
            filename: Backup filename to restore
            db: Database session
            db_path: Path to database file
            actor_name: User performing restore

        Returns:
            Restore result dict
        """
        backup_path = BackupService.get_backup_path(filename)

        if not backup_path:
            return {
                "success": False,
                "error": "Backup not found or invalid filename"
            }

        try:
            # Create pre-restore backup
            pre_restore_backup = BackupService.create_backup(
                db,
                db_path=db_path,
                actor_name=f"{actor_name} (pre-restore)"
            )

            # Extract backup
            extract_dir = Path("restore_temp")
            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(backup_path, "r") as zf:
                zf.extractall(extract_dir)

            # Restore database
            restored_db = extract_dir / "thai_id_ocr.db"
            if restored_db.exists():
                shutil.copy2(restored_db, db_path)

            # Restore exports
            restored_exports = extract_dir / "exports"
            if restored_exports.exists():
                exports_dir = Path("exports")
                if exports_dir.exists():
                    shutil.rmtree(exports_dir)
                shutil.copytree(restored_exports, exports_dir)

            # Cleanup
            shutil.rmtree(extract_dir)

            AuditService.log_action(
                db,
                action="backup_restored",
                entity_type="system",
                message=f"Backup restored: {filename}",
                actor_name=actor_name
            )

            return {
                "success": True,
                "message": f"Restored from {filename}",
                "pre_restore_backup": pre_restore_backup.get("backup", {}).get("filename")
            }

        except Exception as e:
            AuditService.log_action(
                db,
                action="backup_restore_failed",
                entity_type="system",
                message=f"Backup restore failed: {str(e)}",
                actor_name=actor_name
            )
            return {
                "success": False,
                "error": str(e)
            }
