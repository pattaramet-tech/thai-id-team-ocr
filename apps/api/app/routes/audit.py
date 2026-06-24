from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.services.audit import AuditService
from app.services.cleanup import CleanupService
from app.models import AuditLog
from typing import Optional

router = APIRouter()


@router.get("/audit-logs")
async def get_audit_logs(
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    player_id: Optional[int] = Query(None, description="Filter by player ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Max logs to return"),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with optional filtering.
    All timestamps in UTC.
    """
    try:
        date_from_dt = None
        date_to_dt = None

        if date_from:
            date_from_dt = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to.replace("Z", "+00:00"))

        logs = AuditService.get_audit_logs(
            db,
            team_id=team_id,
            player_id=player_id,
            entity_type=entity_type,
            action=action,
            date_from=date_from_dt,
            date_to=date_to_dt,
            limit=limit
        )

        return {
            "total": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": log.entity_id,
                    "team_id": log.team_id,
                    "player_id": log.player_id,
                    "message": log.message,
                    "context": log.context,
                    "actor_name": log.actor_name,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")


@router.get("/audit-logs/team/{team_id}")
async def get_team_audit_logs(
    team_id: int,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get audit logs for a specific team."""
    try:
        logs = AuditService.get_audit_logs(db, team_id=team_id, limit=limit)

        return {
            "team_id": team_id,
            "total": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "message": log.message,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve team audit logs: {str(e)}")


@router.get("/cleanup/status")
async def get_cleanup_status(db: Session = Depends(get_db)):
    """
    Get status of files/logs that would be cleaned up.
    Shows current retention settings and counts.
    """
    try:
        status = CleanupService.get_cleanup_status(db=db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleanup status: {str(e)}")


@router.post("/cleanup/run")
async def run_cleanup(db: Session = Depends(get_db)):
    """
    Run cleanup operation for expired files and logs.
    Returns summary of deleted items.
    """
    try:
        # Clean up temporary uploads
        temp_cleanup = CleanupService.cleanup_temp_uploads()

        # Clean up old exports
        export_cleanup = CleanupService.cleanup_old_exports()

        # Clean up old audit logs
        audit_cleanup = CleanupService.cleanup_old_audit_logs(db)

        # Log the cleanup operation
        AuditService.log_action(
            db,
            action="cleanup_run",
            entity_type="system",
            message="Automatic cleanup executed",
            metadata={
                "temp_uploads_deleted": temp_cleanup["deleted_files"],
                "old_exports_deleted": export_cleanup["deleted_files"],
                "audit_logs_deleted": audit_cleanup["deleted_logs"],
                "errors": temp_cleanup["errors"] + export_cleanup["errors"] + audit_cleanup["errors"]
            }
        )

        return {
            "success": True,
            "summary": {
                "temp_uploads_deleted": temp_cleanup["deleted_files"],
                "old_exports_deleted": export_cleanup["deleted_files"],
                "audit_logs_deleted": audit_cleanup["deleted_logs"],
                "temp_uploads_errors": temp_cleanup["errors"],
                "export_files_errors": export_cleanup["errors"],
                "audit_logs_errors": audit_cleanup["errors"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
