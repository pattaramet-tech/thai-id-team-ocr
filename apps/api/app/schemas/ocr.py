from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class OCRPreviewResponse(BaseModel):
    """OCR preview result before saving to database."""
    sourceFilename: str
    ocrText: str  # Redacted text
    firstName: Optional[str]
    lastName: Optional[str]
    fullName: Optional[str]
    dateOfBirth: Optional[date]
    birthYearBE: Optional[int]
    confidence: float
    eligibilityStatus: str  # eligible | over_age | unknown
    eligibilityNote: Optional[str]
    warnings: List[str]  # Warnings about OCR quality or missing data

    class Config:
        from_attributes = True
