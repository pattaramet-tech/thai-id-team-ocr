from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.health import HealthService
from app.services.backup import BackupService
from app.services.auth import AuthService
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import io

router = APIRouter()


def get_current_user_from_header(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )

    user = AuthService.get_user_from_token(parts[1], db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user


def require_admin(user: User = Depends(get_current_user_from_header)) -> User:
    """Require admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@router.get("/system/health")
async def get_health(db: Session = Depends(get_db)):
    """Get system health status."""
    return HealthService.get_system_health(db)


@router.post("/backup/create")
async def create_backup(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a backup (admin only)."""
    result = BackupService.create_backup(db, actor_name=admin.display_name)
    if result["success"]:
        return result
    raise HTTPException(status_code=500, detail=result.get("error", "Backup failed"))


@router.get("/backup/list")
async def list_backups(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all backups (admin only)."""
    backups = BackupService.list_backups()
    return {"backups": backups, "count": len(backups)}


@router.delete("/backup/{filename}")
async def delete_backup(
    filename: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a backup (admin only)."""
    result = BackupService.delete_backup(filename, db, actor_name=admin.display_name)
    if result["success"]:
        return {"status": "deleted", "filename": filename}
    raise HTTPException(status_code=400, detail=result.get("error", "Delete failed"))


class RestoreRequest(BaseModel):
    filename: str
    confirm_phrase: str


@router.post("/backup/restore")
async def restore_backup(
    request: RestoreRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Restore from backup (admin only, requires confirmation)."""
    # Check confirmation phrase
    if request.confirm_phrase != "RESTORE_CONFIRM":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation phrase. Must be: RESTORE_CONFIRM"
        )

    result = BackupService.restore_backup(
        request.filename,
        db,
        actor_name=admin.display_name
    )

    if result["success"]:
        return result
    raise HTTPException(status_code=400, detail=result.get("error", "Restore failed"))


@router.get("/backup/download/{filename}")
async def download_backup(
    filename: str,
    admin: User = Depends(require_admin)
):
    """Download a backup file (admin only)."""
    backup_path = BackupService.get_backup_path(filename)

    if not backup_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup not found"
        )

    return FileResponse(
        path=backup_path,
        filename=filename,
        media_type="application/zip"
    )
