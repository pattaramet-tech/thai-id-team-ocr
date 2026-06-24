"""Tests for audit logging and cleanup services."""
import pytest
from datetime import datetime, timedelta
from app.services.audit import AuditService
from app.services.cleanup import CleanupService
from app.models import AuditLog, Team, Player


class TestAuditService:
    """Test audit logging service."""

    def test_log_action_creates_audit_log(self, db_session):
        """Log action creates audit log entry."""
        AuditService.log_action(
            db_session,
            action="test_action",
            entity_type="test",
            message="Test message"
        )

        logs = db_session.query(AuditLog).all()
        assert len(logs) == 1
        assert logs[0].action == "test_action"
        assert logs[0].message == "Test message"

    def test_log_action_with_team_id(self, db_session):
        """Log action with team ID."""
        team = Team(name="Test Team", ageGroup="U18", gender="Male", competitionYearBE=2569)
        db_session.add(team)
        db_session.commit()

        AuditService.log_action(
            db_session,
            action="create_team",
            entity_type="team",
            message="Team created",
            team_id=team.id
        )

        logs = db_session.query(AuditLog).filter(AuditLog.team_id == team.id).all()
        assert len(logs) == 1
        assert logs[0].team_id == team.id

    def test_log_action_with_player_id(self, db_session):
        """Log action with player ID."""
        team = Team(name="Test Team", ageGroup="U18", gender="Male", competitionYearBE=2569)
        db_session.add(team)
        db_session.commit()

        player = Player(
            teamId=team.id,
            firstName="Test",
            lastName="Player",
            fullName="Test Player",
            sourceFilename="test.jpg",
            ocrText="test",
            confidence=0.9,
            status="pending"
        )
        db_session.add(player)
        db_session.commit()

        AuditService.log_action(
            db_session,
            action="verify_player",
            entity_type="player",
            message="Player verified",
            player_id=player.id,
            team_id=team.id
        )

        logs = db_session.query(AuditLog).filter(AuditLog.player_id == player.id).all()
        assert len(logs) == 1

    def test_log_action_sanitizes_metadata(self, db_session):
        """Log action sanitizes metadata."""
        valid_metadata = {"count": 5, "status": "success"}

        AuditService.log_action(
            db_session,
            action="test",
            entity_type="test",
            message="Test",
            metadata=valid_metadata
        )

        logs = db_session.query(AuditLog).all()
        assert logs[0].context == valid_metadata

    def test_log_action_rejects_thai_id_in_metadata(self, db_session):
        """Log action rejects Thai ID in metadata."""
        bad_metadata = {"id": "1234567890123"}  # 13-digit Thai ID

        with pytest.raises(ValueError, match="Thai ID number"):
            AuditService.log_action(
                db_session,
                action="test",
                entity_type="test",
                message="Test",
                metadata=bad_metadata
            )

    def test_get_audit_logs_by_team(self, db_session):
        """Get audit logs filtered by team."""
        team1 = Team(name="Team 1", ageGroup="U18", gender="Male", competitionYearBE=2569)
        team2 = Team(name="Team 2", ageGroup="U20", gender="Female", competitionYearBE=2569)
        db_session.add_all([team1, team2])
        db_session.commit()

        AuditService.log_action(db_session, "test", "test", "msg1", team_id=team1.id)
        AuditService.log_action(db_session, "test", "test", "msg2", team_id=team2.id)

        logs = AuditService.get_audit_logs(db_session, team_id=team1.id)
        assert len(logs) == 1
        assert logs[0].team_id == team1.id

    def test_get_audit_logs_by_action(self, db_session):
        """Get audit logs filtered by action."""
        AuditService.log_action(db_session, "verify", "player", "msg1")
        AuditService.log_action(db_session, "reject", "player", "msg2")

        logs = AuditService.get_audit_logs(db_session, action="verify")
        assert len(logs) == 1
        assert logs[0].action == "verify"

    def test_get_audit_logs_limit(self, db_session):
        """Get audit logs respects limit."""
        for i in range(5):
            AuditService.log_action(db_session, "test", "test", f"msg{i}")

        logs = AuditService.get_audit_logs(db_session, limit=3)
        assert len(logs) == 3

    def test_delete_old_logs(self, db_session):
        """Delete old audit logs."""
        # Create old log
        old_log = AuditLog(
            action="test",
            entity_type="test",
            message="old",
            created_at=datetime.utcnow() - timedelta(days=200)
        )
        db_session.add(old_log)

        # Create new log
        new_log = AuditLog(
            action="test",
            entity_type="test",
            message="new",
            created_at=datetime.utcnow()
        )
        db_session.add(new_log)
        db_session.commit()

        deleted = AuditService.delete_old_logs(db_session, days=180)

        assert deleted == 1
        remaining = db_session.query(AuditLog).all()
        assert len(remaining) == 1
        assert remaining[0].message == "new"


class TestCleanupService:
    """Test cleanup service."""

    def test_is_safe_path_allows_safe_paths(self):
        """Safe paths are allowed."""
        allowed_dirs = ["/app/uploads", "/app/exports"]

        # These should be safe
        assert CleanupService._is_safe_path("/app/uploads/file.jpg", allowed_dirs)
        assert CleanupService._is_safe_path("/app/exports/file.xlsx", allowed_dirs)

    def test_is_safe_path_rejects_path_traversal(self):
        """Path traversal is rejected."""
        allowed_dirs = ["/app/uploads"]

        # These should be rejected
        assert not CleanupService._is_safe_path("/app/other/file.jpg", allowed_dirs)
        assert not CleanupService._is_safe_path("/root/secret", allowed_dirs)

    def test_cleanup_status_returns_settings(self, db_session):
        """Cleanup status returns retention settings."""
        status = CleanupService.get_cleanup_status(db=db_session)

        assert "ocr_temp_retention_hours" in status
        assert "export_retention_days" in status
        assert "audit_log_retention_days" in status
        assert "files_to_cleanup" in status
        assert "logs_to_cleanup" in status

    def test_cleanup_status_counts_old_logs(self, db_session):
        """Cleanup status counts old audit logs."""
        # Create old log
        old_log = AuditLog(
            action="test",
            entity_type="test",
            message="old",
            created_at=datetime.utcnow() - timedelta(days=200)
        )
        db_session.add(old_log)
        db_session.commit()

        status = CleanupService.get_cleanup_status(
            db=db_session,
            audit_retention_days=180
        )

        assert status["logs_to_cleanup"] == 1
