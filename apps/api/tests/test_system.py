"""Tests for system health and backup services."""
import pytest
import os
from pathlib import Path
from app.services.health import HealthService
from app.services.backup import BackupService
from app.models import Team, Player


class TestHealthService:
    """Test system health service."""

    def test_check_directories(self):
        """Check directories are created and writable."""
        results = HealthService.check_directories()

        assert "uploads" in results
        assert "exports" in results
        assert "temp" in results
        assert "backups" in results

        for name, result in results.items():
            assert "status" in result
            assert "writable" in result
            assert "path" in result

    def test_tesseract_check(self):
        """Check tesseract status."""
        result = HealthService.check_tesseract()

        assert "status" in result
        # Status is either "installed" or "not_found"
        assert result["status"] in ["installed", "not_found"]

    def test_thai_language_check(self):
        """Check Thai language data availability."""
        result = HealthService.check_thai_language_data()

        assert "status" in result
        # Status is "available", "missing", or "unknown"
        assert result["status"] in ["available", "missing", "unknown"]

    def test_poppler_check(self):
        """Check Poppler PDF support."""
        result = HealthService.check_poppler()

        assert "status" in result
        assert result["status"] in ["available", "not_found"]

    def test_database_check(self, db_session):
        """Check database connectivity."""
        result = HealthService.check_database(db_session)

        assert "status" in result
        assert result["status"] in ["healthy", "unhealthy"]

    def test_get_system_health(self, db_session):
        """Get complete system health status."""
        result = HealthService.get_system_health(db_session)

        assert "version" in result
        assert "database" in result
        assert "directories" in result
        assert "tesseract" in result
        assert "thai_language" in result
        assert "poppler" in result
        assert "statistics" in result
        assert "disk_usage" in result

        # Check statistics
        assert "teams" in result["statistics"]
        assert "players" in result["statistics"]
        assert "audit_logs" in result["statistics"]

    def test_get_directory_size(self):
        """Get directory size."""
        # Create test file
        Path("uploads").mkdir(exist_ok=True)
        test_file = Path("uploads") / "test_file.txt"
        test_file.write_text("test content")

        size = HealthService.get_directory_size("uploads")

        assert size > 0
        assert "test" in test_file.read_text()

        # Cleanup
        test_file.unlink()


class TestBackupService:
    """Test backup service."""

    def test_backup_dir_creation(self):
        """Backup directory is created."""
        BackupService._ensure_backup_dir()
        assert BackupService.BACKUP_DIR.exists()

    def test_is_safe_path(self):
        """Path safety validation."""
        assert BackupService._is_safe_path("backup-2024-01-01-120000.zip")
        assert not BackupService._is_safe_path("../backup.zip")
        assert not BackupService._is_safe_path("backup/file.zip")
        assert not BackupService._is_safe_path("backup.txt")

    def test_create_backup(self, db_session):
        """Create backup creates zip file."""
        BackupService._ensure_backup_dir()

        # Create a test file to backup
        Path("exports").mkdir(exist_ok=True)
        test_file = Path("exports") / "test.txt"
        test_file.write_text("test data for backup")

        result = BackupService.create_backup(db_session)

        assert result["success"]
        assert "backup" in result
        assert "filename" in result["backup"]
        assert result["backup"]["filename"].endswith(".zip")
        assert result["backup"]["size_bytes"] > 0

        # Verify file exists
        backup_path = BackupService.BACKUP_DIR / result["backup"]["filename"]
        assert backup_path.exists()

        # Cleanup
        backup_path.unlink()
        test_file.unlink()

    def test_list_backups(self, db_session):
        """List backups returns backup list."""
        BackupService._ensure_backup_dir()

        # Create a test backup
        result = BackupService.create_backup(db_session)
        filename = result["backup"]["filename"]

        backups = BackupService.list_backups()

        assert isinstance(backups, list)
        assert len(backups) > 0
        assert any(b["filename"] == filename for b in backups)

        # Cleanup
        backup_path = BackupService.BACKUP_DIR / filename
        backup_path.unlink()

    def test_get_backup_path(self, db_session):
        """Get backup path validation."""
        BackupService._ensure_backup_dir()

        result = BackupService.create_backup(db_session)
        filename = result["backup"]["filename"]

        # Valid path
        path = BackupService.get_backup_path(filename)
        assert path is not None
        assert path.exists()

        # Invalid paths
        assert BackupService.get_backup_path("../etc/passwd.zip") is None
        assert BackupService.get_backup_path("nonexistent.zip") is None
        assert BackupService.get_backup_path("test.txt") is None

        # Cleanup
        path.unlink()

    def test_delete_backup(self, db_session):
        """Delete backup removes file."""
        BackupService._ensure_backup_dir()

        result = BackupService.create_backup(db_session)
        filename = result["backup"]["filename"]

        # Verify exists
        backup_path = BackupService.BACKUP_DIR / filename
        assert backup_path.exists()

        # Delete
        delete_result = BackupService.delete_backup(filename, db_session)
        assert delete_result["success"]
        assert not backup_path.exists()

    def test_delete_invalid_backup(self, db_session):
        """Delete invalid backup returns error."""
        result = BackupService.delete_backup("../invalid.zip", db_session)
        assert not result["success"]
        assert "error" in result

    def test_safe_extract_prevents_zip_slip(self, db_session):
        """Zip Slip attack prevention - path traversal via ZIP."""
        import zipfile
        BackupService._ensure_backup_dir()

        # Create malicious ZIP with path traversal
        zip_path = BackupService.BACKUP_DIR / "malicious.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            # Try to extract to parent directory
            zf.writestr("../../../etc/passwd", "malicious content")

        # Attempt to extract to temp directory
        extract_dir = Path("temp_test_zip_slip")
        extract_dir.mkdir(exist_ok=True)

        # Should raise ValueError for unsafe path
        try:
            BackupService._safe_extract_zip(zip_path, extract_dir)
            assert False, "Should have raised ValueError for Zip Slip"
        except ValueError as e:
            assert "escapes destination" in str(e) or "Unsafe path" in str(e)

        # Cleanup
        zip_path.unlink()
        import shutil
        if extract_dir.exists():
            shutil.rmtree(extract_dir)

    def test_safe_extract_blocks_absolute_paths(self, db_session):
        """ZIP member with absolute path is blocked."""
        import zipfile
        BackupService._ensure_backup_dir()

        zip_path = BackupService.BACKUP_DIR / "absolute_path.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("/etc/passwd", "malicious")

        extract_dir = Path("temp_test_absolute")
        extract_dir.mkdir(exist_ok=True)

        try:
            BackupService._safe_extract_zip(zip_path, extract_dir)
            assert False, "Should have raised ValueError for absolute path"
        except ValueError as e:
            assert "Unsafe path" in str(e)

        # Cleanup
        zip_path.unlink()
        import shutil
        if extract_dir.exists():
            shutil.rmtree(extract_dir)

    def test_create_backup_include_exports_param(self, db_session):
        """Create backup respects include_exports parameter."""
        BackupService._ensure_backup_dir()

        # Create test file in exports
        Path("exports").mkdir(exist_ok=True)
        test_file = Path("exports") / "test.txt"
        test_file.write_text("export data")

        # Test with include_exports=False (default)
        result = BackupService.create_backup(db_session, include_exports=False)
        assert result["success"]
        assert result["backup"]["include_exports"] is False

        # Cleanup
        backup_path = BackupService.BACKUP_DIR / result["backup"]["filename"]
        backup_path.unlink()

        # Test with include_exports=True
        result = BackupService.create_backup(db_session, include_exports=True)
        assert result["success"]
        assert result["backup"]["include_exports"] is True

        # Cleanup
        backup_path = BackupService.BACKUP_DIR / result["backup"]["filename"]
        backup_path.unlink()
        test_file.unlink()

    def test_restore_temp_cleanup_on_success(self, db_session):
        """Temp directory is cleaned up after successful restore."""
        BackupService._ensure_backup_dir()

        # Create and backup database
        result = BackupService.create_backup(db_session)
        backup_filename = result["backup"]["filename"]

        # Restore
        restore_result = BackupService.restore_backup(backup_filename, db_session)
        assert restore_result["success"]

        # Verify no restore_temp directories exist
        temp_dirs = list(Path(".").glob("restore_temp*"))
        assert len(temp_dirs) == 0, f"Found orphaned temp dirs: {temp_dirs}"

        # Cleanup
        backup_path = BackupService.BACKUP_DIR / backup_filename
        backup_path.unlink()

    def test_restore_temp_cleanup_on_error(self, db_session):
        """Temp directory is cleaned up even on restore error."""
        # Try to restore non-existent backup
        restore_result = BackupService.restore_backup("nonexistent.zip", db_session)
        assert not restore_result["success"]

        # Verify no restore_temp directories exist
        temp_dirs = list(Path(".").glob("restore_temp*"))
        assert len(temp_dirs) == 0, f"Found orphaned temp dirs: {temp_dirs}"

    def test_backup_path_traversal_defense(self):
        """Backup filename validation prevents path traversal."""
        # These should all be rejected
        assert not BackupService._is_safe_path("../backup.zip")
        assert not BackupService._is_safe_path("backup/../file.zip")
        assert not BackupService._is_safe_path("backup/subdir.zip")
        assert not BackupService._is_safe_path("/etc/backup.zip")
        assert not BackupService._is_safe_path("C:\\Windows\\backup.zip")
        assert not BackupService._is_safe_path("backup.txt")  # Not .zip
        assert not BackupService._is_safe_path("..\\backup.zip")  # Windows traversal

        # These should be accepted
        assert BackupService._is_safe_path("backup-2024-01-01.zip")
        assert BackupService._is_safe_path("thai-id-team-ocr-backup-20240101-120000.zip")
