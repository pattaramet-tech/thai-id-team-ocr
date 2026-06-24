import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import AuditLog


# Default retention settings (in days/hours)
DEFAULT_OCR_TEMP_RETENTION_HOURS = 24
DEFAULT_EXPORT_RETENTION_DAYS = 7
DEFAULT_AUDIT_LOG_RETENTION_DAYS = 180


class CleanupService:
    """Service for cleaning up old temporary files and data."""

    @staticmethod
    def _is_safe_path(file_path: str, allowed_base_dirs: list[str]) -> bool:
        """
        Check if a file path is within allowed directories.
        Prevents path traversal attacks (../../, etc).

        Args:
            file_path: Path to check
            allowed_base_dirs: List of allowed base directories

        Returns:
            True if path is safe and within allowed dirs
        """
        # Resolve to absolute path
        try:
            resolved_path = Path(file_path).resolve()
        except (ValueError, OSError):
            return False

        # Check if path is within allowed directories
        for allowed_dir in allowed_base_dirs:
            try:
                allowed_resolved = Path(allowed_dir).resolve()
                resolved_path.relative_to(allowed_resolved)
                return True
            except ValueError:
                # Path is not relative to this directory
                continue

        return False

    @staticmethod
    def _ensure_directories_exist(base_path: str) -> None:
        """Create directories if they don't exist."""
        for subdir in ['uploads', 'exports', 'temp']:
            dir_path = Path(base_path) / subdir
            dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def cleanup_temp_uploads(
        base_path: str = ".",
        retention_hours: int = DEFAULT_OCR_TEMP_RETENTION_HOURS
    ) -> Dict[str, Any]:
        """
        Delete temporary OCR files older than retention period.

        Args:
            base_path: Base directory path
            retention_hours: Hours to keep files

        Returns:
            Summary of cleanup operation
        """
        CleanupService._ensure_directories_exist(base_path)

        uploads_dir = Path(base_path) / "uploads"
        if not uploads_dir.exists():
            return {"deleted_files": 0, "errors": []}

        deleted_count = 0
        errors = []
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        try:
            for file_path in uploads_dir.glob("*"):
                # Safety check
                allowed_dirs = [str(uploads_dir)]
                if not CleanupService._is_safe_path(str(file_path), allowed_dirs):
                    errors.append(f"Unsafe path detected: {file_path}")
                    continue

                if file_path.is_file():
                    # Get file modification time
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            errors.append(f"Failed to delete {file_path}: {str(e)}")
        except Exception as e:
            errors.append(f"Error during cleanup: {str(e)}")

        return {"deleted_files": deleted_count, "errors": errors}

    @staticmethod
    def cleanup_old_exports(
        base_path: str = ".",
        retention_days: int = DEFAULT_EXPORT_RETENTION_DAYS
    ) -> Dict[str, Any]:
        """
        Delete exported XLSX files older than retention period.

        Args:
            base_path: Base directory path
            retention_days: Days to keep files

        Returns:
            Summary of cleanup operation
        """
        CleanupService._ensure_directories_exist(base_path)

        exports_dir = Path(base_path) / "exports"
        if not exports_dir.exists():
            return {"deleted_files": 0, "errors": []}

        deleted_count = 0
        errors = []
        cutoff_time = datetime.now() - timedelta(days=retention_days)

        try:
            for file_path in exports_dir.glob("*"):
                # Safety check
                allowed_dirs = [str(exports_dir)]
                if not CleanupService._is_safe_path(str(file_path), allowed_dirs):
                    errors.append(f"Unsafe path detected: {file_path}")
                    continue

                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            deleted_count += 1
                        except Exception as e:
                            errors.append(f"Failed to delete {file_path}: {str(e)}")
        except Exception as e:
            errors.append(f"Error during cleanup: {str(e)}")

        return {"deleted_files": deleted_count, "errors": errors}

    @staticmethod
    def cleanup_old_audit_logs(
        db: Session,
        retention_days: int = DEFAULT_AUDIT_LOG_RETENTION_DAYS
    ) -> Dict[str, Any]:
        """
        Delete audit logs older than retention period.

        Args:
            db: Database session
            retention_days: Days to keep logs

        Returns:
            Summary of cleanup operation
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            deleted_count = db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            db.commit()

            return {"deleted_logs": deleted_count, "errors": []}
        except Exception as e:
            return {"deleted_logs": 0, "errors": [str(e)]}

    @staticmethod
    def get_cleanup_status(
        base_path: str = ".",
        ocr_retention_hours: int = DEFAULT_OCR_TEMP_RETENTION_HOURS,
        export_retention_days: int = DEFAULT_EXPORT_RETENTION_DAYS,
        audit_retention_days: int = DEFAULT_AUDIT_LOG_RETENTION_DAYS,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Get status of files/logs that would be cleaned up.

        Args:
            base_path: Base directory path
            ocr_retention_hours: OCR temp retention
            export_retention_days: Export file retention
            audit_retention_days: Audit log retention
            db: Database session (optional, for audit log count)

        Returns:
            Status information
        """
        CleanupService._ensure_directories_exist(base_path)

        status = {
            "ocr_temp_retention_hours": ocr_retention_hours,
            "export_retention_days": export_retention_days,
            "audit_log_retention_days": audit_retention_days,
            "files_to_cleanup": {
                "temp_uploads": 0,
                "old_exports": 0
            },
            "logs_to_cleanup": 0
        }

        # Count temp upload files
        uploads_dir = Path(base_path) / "uploads"
        if uploads_dir.exists():
            cutoff_time = datetime.now() - timedelta(hours=ocr_retention_hours)
            for file_path in uploads_dir.glob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        status["files_to_cleanup"]["temp_uploads"] += 1

        # Count old export files
        exports_dir = Path(base_path) / "exports"
        if exports_dir.exists():
            cutoff_time = datetime.now() - timedelta(days=export_retention_days)
            for file_path in exports_dir.glob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_time:
                        status["files_to_cleanup"]["old_exports"] += 1

        # Count old audit logs
        if db:
            try:
                cutoff_date = datetime.utcnow() - timedelta(days=audit_retention_days)
                status["logs_to_cleanup"] = db.query(AuditLog).filter(
                    AuditLog.created_at < cutoff_date
                ).count()
            except Exception:
                status["logs_to_cleanup"] = 0

        return status
