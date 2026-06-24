import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Team, Player, AuditLog


class HealthService:
    """Service for checking system health and dependencies."""

    @staticmethod
    def check_database(db: Session) -> Dict[str, Any]:
        """Check database status."""
        try:
            # Try a simple query
            db.query(Team).first()
            return {
                "status": "healthy",
                "message": "Database is accessible"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }

    @staticmethod
    def check_directories() -> Dict[str, Any]:
        """Check if required directories are writable."""
        results = {}
        directories = {
            "uploads": "uploads",
            "exports": "exports",
            "temp": "temp",
            "backups": "backups"
        }

        for name, path in directories.items():
            dir_path = Path(path)
            dir_path.mkdir(parents=True, exist_ok=True)

            try:
                # Test write capability
                test_file = dir_path / ".healthcheck"
                test_file.write_text("ok")
                test_file.unlink()

                results[name] = {
                    "status": "ok",
                    "writable": True,
                    "path": str(dir_path.absolute())
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "writable": False,
                    "path": str(dir_path.absolute()),
                    "error": str(e)
                }

        return results

    @staticmethod
    def check_tesseract() -> Dict[str, Any]:
        """Check if Tesseract OCR is installed."""
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return {
                    "status": "installed",
                    "version": result.stdout.split('\n')[0]
                }
        except Exception:
            pass

        return {
            "status": "not_found",
            "message": "Tesseract OCR not installed or not in PATH"
        }

    @staticmethod
    def check_thai_language_data() -> Dict[str, Any]:
        """Check if Thai language traineddata is available."""
        try:
            # Try to run tesseract with Thai language
            result = subprocess.run(
                ["tesseract", "--list-langs"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "tha" in result.stdout:
                return {
                    "status": "available",
                    "language": "Thai (tha)"
                }
            else:
                return {
                    "status": "missing",
                    "message": "Thai language data (tha) not found in Tesseract"
                }
        except Exception:
            return {
                "status": "unknown",
                "message": "Could not check language data"
            }

    @staticmethod
    def check_poppler() -> Dict[str, Any]:
        """Check if Poppler is available for PDF support."""
        try:
            result = subprocess.run(
                ["pdftoppm", "-v"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return {
                    "status": "available",
                    "message": "Poppler is installed"
                }
        except Exception:
            pass

        return {
            "status": "not_found",
            "message": "Poppler not installed (PDF support will be limited)"
        }

    @staticmethod
    def get_directory_size(directory: str) -> int:
        """Get size of directory in bytes."""
        try:
            total = 0
            for entry in Path(directory).rglob("*"):
                if entry.is_file():
                    total += entry.stat().st_size
            return total
        except Exception:
            return 0

    @staticmethod
    def get_system_health(db: Session) -> Dict[str, Any]:
        """Get complete system health status."""
        try:
            team_count = db.query(Team).count()
        except Exception:
            team_count = 0

        try:
            player_count = db.query(Player).count()
        except Exception:
            player_count = 0

        try:
            audit_count = db.query(AuditLog).count()
        except Exception:
            audit_count = 0

        dirs = HealthService.check_directories()
        uploads_size = HealthService.get_directory_size("uploads")
        exports_size = HealthService.get_directory_size("exports")
        temp_size = HealthService.get_directory_size("temp")

        return {
            "version": "0.5.0",
            "database": HealthService.check_database(db),
            "directories": dirs,
            "tesseract": HealthService.check_tesseract(),
            "thai_language": HealthService.check_thai_language_data(),
            "poppler": HealthService.check_poppler(),
            "statistics": {
                "teams": team_count,
                "players": player_count,
                "audit_logs": audit_count
            },
            "disk_usage": {
                "uploads_bytes": uploads_size,
                "uploads_mb": round(uploads_size / (1024 * 1024), 2),
                "exports_bytes": exports_size,
                "exports_mb": round(exports_size / (1024 * 1024), 2),
                "temp_bytes": temp_size,
                "temp_mb": round(temp_size / (1024 * 1024), 2)
            }
        }
