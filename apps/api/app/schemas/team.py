from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TeamCreate(BaseModel):
    name: str
    ageGroup: str  # e.g., U18, U16, U14
    gender: str  # e.g., Male, Female, Mixed
    division: Optional[str] = None
    competitionYearBE: int = 2569

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    ageGroup: Optional[str] = None
    gender: Optional[str] = None
    division: Optional[str] = None
    competitionYearBE: Optional[int] = None

class TeamResponse(BaseModel):
    id: int
    name: str
    ageGroup: str
    gender: str
    division: Optional[str]
    competitionYearBE: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
