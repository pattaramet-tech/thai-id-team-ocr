from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class PlayerCreate(BaseModel):
    teamId: int
    firstName: str  # Required for Phase 1
    lastName: str  # Required for Phase 1
    dateOfBirth: Optional[date] = None
    sourceFilename: Optional[str] = None
    ocrText: Optional[str] = None
    confidence: float = 0.0

class PlayerUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    dateOfBirth: Optional[date] = None
    status: Optional[str] = None
    verifiedAt: Optional[datetime] = None

class PlayerResponse(BaseModel):
    id: int
    teamId: int
    firstName: str
    lastName: str
    fullName: Optional[str]
    dateOfBirth: Optional[date]
    birthYearBE: Optional[int]
    eligibilityStatus: str
    eligibilityNote: Optional[str]
    sourceFilename: Optional[str]
    ocrText: Optional[str]
    confidence: float
    status: str
    createdAt: datetime
    updatedAt: datetime
    verifiedAt: Optional[datetime]

    class Config:
        from_attributes = True
