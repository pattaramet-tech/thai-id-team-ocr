from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TeamCreate(BaseModel):
    name: str
    ageGroup: str
    gender: str

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    ageGroup: Optional[str] = None
    gender: Optional[str] = None

class TeamResponse(BaseModel):
    id: int
    name: str
    ageGroup: str
    gender: str
    createdAt: datetime

    class Config:
        from_attributes = True
