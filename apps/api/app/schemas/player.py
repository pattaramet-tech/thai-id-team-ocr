from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PlayerCreate(BaseModel):
    teamId: int
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    sourceFilename: str
    ocrText: Optional[str] = None
    confidence: float = 0.0

class PlayerUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    status: Optional[str] = None
    verifiedAt: Optional[datetime] = None

class PlayerResponse(BaseModel):
    id: int
    teamId: int
    firstName: Optional[str]
    lastName: Optional[str]
    fullName: Optional[str]
    sourceFilename: str
    ocrText: Optional[str]
    confidence: float
    status: str
    createdAt: datetime
    verifiedAt: Optional[datetime]

    class Config:
        from_attributes = True
