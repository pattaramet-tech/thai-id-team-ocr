from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Player, Team
from app.schemas.player import PlayerCreate, PlayerResponse, PlayerUpdate
from app.services.eligibility import check_eligibility_for_player, date_to_birth_year_be
from typing import List
from datetime import datetime

router = APIRouter()


def _calculate_player_eligibility(player: Player, team: Team):
    """Calculate and update player eligibility status."""
    result = check_eligibility_for_player(
        team.ageGroup,
        team.competitionYearBE,
        player.dateOfBirth
    )
    player.eligibilityStatus = result["status"]
    player.eligibilityNote = result["note"]

    if player.dateOfBirth:
        player.birthYearBE = date_to_birth_year_be(player.dateOfBirth)


@router.post("", response_model=PlayerResponse)
async def create_player(player_create: PlayerCreate, db: Session = Depends(get_db)):
    """Create player record with eligibility checking."""
    # Validate team exists
    team = db.query(Team).filter(Team.id == player_create.teamId).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Validate required fields
    if not player_create.firstName or not player_create.firstName.strip():
        raise HTTPException(status_code=400, detail="First name is required")
    if not player_create.lastName or not player_create.lastName.strip():
        raise HTTPException(status_code=400, detail="Last name is required")

    # Create player
    db_player = Player(
        teamId=player_create.teamId,
        firstName=player_create.firstName,
        lastName=player_create.lastName,
        fullName=f"{player_create.firstName} {player_create.lastName}",
        dateOfBirth=player_create.dateOfBirth,
        sourceFilename=player_create.sourceFilename,
        ocrText=player_create.ocrText,
        confidence=player_create.confidence
    )

    # Calculate eligibility
    _calculate_player_eligibility(db_player, team)

    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


@router.get("", response_model=List[PlayerResponse])
async def list_players(
    team_id: int = Query(None),
    status: str = Query(None),
    eligibility: str = Query(None),
    db: Session = Depends(get_db)
):
    """List players with optional filtering."""
    query = db.query(Player)

    if team_id:
        query = query.filter(Player.teamId == team_id)
    if status:
        query = query.filter(Player.status == status)
    if eligibility:
        query = query.filter(Player.eligibilityStatus == eligibility)

    players = query.order_by(Player.createdAt.desc()).all()
    return players


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get player details."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.patch("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    db: Session = Depends(get_db)
):
    """Update player information and recalculate eligibility."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    team = db.query(Team).filter(Team.id == player.teamId).first()
    if not team:
        raise HTTPException(status_code=500, detail="Team not found")

    # Update fields
    if player_update.firstName is not None:
        player.firstName = player_update.firstName
    if player_update.lastName is not None:
        player.lastName = player_update.lastName
    if player_update.dateOfBirth is not None:
        player.dateOfBirth = player_update.dateOfBirth

    # Recalculate full name if names changed
    if player_update.firstName is not None or player_update.lastName is not None:
        player.fullName = f"{player.firstName} {player.lastName}"

    # Recalculate eligibility if date of birth changed
    if player_update.dateOfBirth is not None:
        _calculate_player_eligibility(player, team)

    if player_update.status is not None:
        player.status = player_update.status
        if player_update.status == "verified":
            player.verifiedAt = datetime.utcnow()

    db.commit()
    db.refresh(player)
    return player


@router.delete("/{player_id}")
async def delete_player(player_id: int, db: Session = Depends(get_db)):
    """Delete player record."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    db.delete(player)
    db.commit()
    return {"message": "Player deleted successfully"}
