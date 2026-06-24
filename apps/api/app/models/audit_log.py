from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    """Audit log for tracking all important actions in the system."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # create_team, verify_player, export_team, etc.
    entity_type = Column(String(50), nullable=False, index=True)  # team, player, ocr, export, system
    entity_id = Column(Integer, nullable=True, index=True)  # team_id or player_id depending on context
    team_id = Column(Integer, nullable=True, index=True)  # team_id for team-specific actions
    player_id = Column(Integer, nullable=True, index=True)  # player_id for player-specific actions
    message = Column(Text, nullable=False)  # Human-readable message
    context = Column(JSON, nullable=True)  # Additional context (must not contain Thai IDs)
    actor_name = Column(String(100), nullable=False, default="local_admin")
    ip_address = Column(String(50), nullable=True)  # For future use with multi-user setups
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<AuditLog(action={self.action}, entity_type={self.entity_type}, created_at={self.created_at})>"
