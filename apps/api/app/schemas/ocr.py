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


class OCRBatchItemResponse(BaseModel):
    """Single item result in batch OCR response."""
    sourceFilename: str
    success: bool
    error: Optional[str] = None
    ocrText: Optional[str] = None  # Redacted text
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    dateOfBirth: Optional[date] = None
    birthYearBE: Optional[int] = None
    confidence: Optional[float] = None
    eligibilityStatus: Optional[str] = None  # eligible | over_age | unknown
    eligibilityNote: Optional[str] = None
    warnings: Optional[List[str]] = None

    class Config:
        from_attributes = True


class OCRBatchResponse(BaseModel):
    """Batch OCR upload response."""
    totalFiles: int
    successCount: int
    errorCount: int
    items: List[OCRBatchItemResponse]

    class Config:
        from_attributes = True
