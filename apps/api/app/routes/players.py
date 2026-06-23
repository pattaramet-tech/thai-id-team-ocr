from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Player, Team
from app.schemas.player import PlayerResponse, PlayerUpdate
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("", response_model=List[PlayerResponse])
async def list_players(
    team_id: int = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """List players with optional filtering."""
    query = db.query(Player)

    if team_id:
        query = query.filter(Player.teamId == team_id)
    if status:
        query = query.filter(Player.status == status)

    players = query.all()
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
    """Update player information."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    if player_update.firstName is not None:
        player.firstName = player_update.firstName
    if player_update.lastName is not None:
        player.lastName = player_update.lastName
    if player_update.fullName is not None:
        player.fullName = player_update.fullName
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
