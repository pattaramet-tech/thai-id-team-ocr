import re
import json
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import AuditLog


class AuditService:
    """Service for logging audit events and tracking actions."""

    @staticmethod
    def _sanitize_metadata(metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Sanitize metadata to ensure no Thai ID numbers are logged.
        Raises ValueError if Thai ID found in metadata.
        """
        if not metadata:
            return metadata

        # Convert to JSON string for sanitization check
        metadata_str = json.dumps(metadata, default=str)

        # Pattern 1: Consecutive 13 digits (Thai ID)
        if re.search(r'\d{13}', metadata_str):
            raise ValueError("Metadata contains Thai ID number - cannot log")

        # Pattern 2: Spaced digits (1 2345 67890 12 3)
        if re.search(r'\d\s+\d\s+\d\s+\d\s+\d', metadata_str):
            raise ValueError("Metadata contains formatted ID number - cannot log")

        # Pattern 3: Dashed digits (1-2345-67890-12-3)
        if re.search(r'\d-\d+-\d+-\d+-\d+', metadata_str):
            raise ValueError("Metadata contains dashed ID number - cannot log")

        return metadata

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        entity_type: str,
        message: str,
        entity_id: Optional[int] = None,
        team_id: Optional[int] = None,
        player_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actor_name: str = "local_admin"
    ) -> AuditLog:
        """
        Log an action to the audit log.

        Args:
            db: Database session
            action: Action name (create_team, verify_player, export_team, etc.)
            entity_type: Type of entity (team, player, ocr, export, system)
            message: Human-readable message
            entity_id: ID of the entity being acted upon (optional)
            team_id: Team ID if applicable (optional)
            player_id: Player ID if applicable (optional)
            metadata: Additional context - will be sanitized
            actor_name: Name of the actor (default: local_admin)

        Returns:
            Created AuditLog instance

        Raises:
            ValueError: If metadata contains Thai ID numbers
        """
        # Sanitize metadata
        metadata = AuditService._sanitize_metadata(metadata)

        # Create audit log entry
        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id or team_id or player_id,
            team_id=team_id,
            player_id=player_id,
            message=message,
            context=metadata,
            actor_name=actor_name
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def get_audit_logs(
        db: Session,
        team_id: Optional[int] = None,
        player_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> list[AuditLog]:
        """
        Retrieve audit logs with optional filters.

        Args:
            db: Database session
            team_id: Filter by team ID
            player_id: Filter by player ID
            entity_type: Filter by entity type
            action: Filter by action
            date_from: Filter logs from this date
            date_to: Filter logs until this date
            limit: Maximum number of logs to return

        Returns:
            List of AuditLog entries
        """
        query = db.query(AuditLog)

        if team_id:
            query = query.filter(AuditLog.team_id == team_id)
        if player_id:
            query = query.filter(AuditLog.player_id == player_id)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        if action:
            query = query.filter(AuditLog.action == action)
        if date_from:
            query = query.filter(AuditLog.created_at >= date_from)
        if date_to:
            query = query.filter(AuditLog.created_at <= date_to)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def delete_old_logs(db: Session, days: int) -> int:
        """
        Delete audit logs older than specified days.

        Args:
            db: Database session
            days: Number of days to keep

        Returns:
            Number of deleted logs
        """
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = db.query(AuditLog).filter(AuditLog.created_at < cutoff_date).delete()
        db.commit()

        return deleted_count
