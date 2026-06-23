from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Team, Player
from app.services.export import ExportService
from typing import Optional

router = APIRouter()


@router.get("/team/{team_id}")
async def export_team(team_id: int, db: Session = Depends(get_db)):
    """Export verified players for a specific team to XLSX."""
    try:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Get verified players for team
        players = db.query(Player).filter(
            Player.teamId == team_id,
            Player.status == "verified"
        ).all()

        # Format data for export
        teams_data = ExportService.format_export_data([team], players)

        # Create Excel file
        output, filename = ExportService.create_xlsx(teams_data, f"{team.name}")

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/all")
async def export_all(db: Session = Depends(get_db)):
    """Export all verified players from all teams to XLSX (separate sheets per team)."""
    try:
        # Get all teams
        teams = db.query(Team).all()
        if not teams:
            raise HTTPException(status_code=404, detail="No teams found")

        # Get all verified players
        players = db.query(Player).filter(Player.status == "verified").all()

        if not players:
            raise HTTPException(status_code=404, detail="No verified players found")

        # Format data for export
        teams_data = ExportService.format_export_data(teams, players)

        # Create Excel file
        output, filename = ExportService.create_xlsx(teams_data, "all_teams")

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/team/{team_id}/duplicates")
async def check_duplicates(team_id: int, db: Session = Depends(get_db)):
    """Check for duplicate names in a team."""
    try:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Get verified players
        players = db.query(Player).filter(
            Player.teamId == team_id,
            Player.status == "verified"
        ).all()

        # Group by full name
        name_groups = {}
        for player in players:
            full_name = player.fullName or f"{player.firstName or ''} {player.lastName or ''}".strip()
            if full_name:
                if full_name not in name_groups:
                    name_groups[full_name] = []
                name_groups[full_name].append({
                    "id": player.id,
                    "firstName": player.firstName,
                    "lastName": player.lastName,
                    "sourceFilename": player.sourceFilename
                })

        # Filter to only duplicates
        duplicates = {
            name: group for name, group in name_groups.items() if len(group) > 1
        }

        return {
            "teamId": team_id,
            "teamName": team.name,
            "duplicateCount": len(duplicates),
            "duplicates": duplicates if duplicates else {}
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate check failed: {str(e)}")
