from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Team
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse
from typing import List

router = APIRouter()

@router.post("", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    db_team = Team(
        name=team.name,
        ageGroup=team.ageGroup,
        gender=team.gender
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.get("", response_model=List[TeamResponse])
async def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return teams

@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.patch("/{team_id}", response_model=TeamResponse)
async def update_team(team_id: int, team: TeamUpdate, db: Session = Depends(get_db)):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team.name is not None:
        db_team.name = team.name
    if team.ageGroup is not None:
        db_team.ageGroup = team.ageGroup
    if team.gender is not None:
        db_team.gender = team.gender

    db.commit()
    db.refresh(db_team)
    return db_team

@router.delete("/{team_id}")
async def delete_team(team_id: int, db: Session = Depends(get_db)):
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete(db_team)
    db.commit()
    return {"message": "Team deleted successfully"}
