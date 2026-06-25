from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any

class OCRDebugInfo(BaseModel):
    """Debug information about OCR processing."""
    ocrText: str  # Redacted OCR output for display/copying
    preprocessingMethod: str  # Which preprocessing method was best
    psmMode: int  # Tesseract PSM mode used
    confidence: float
    extractionMode: Optional[str] = None  # "thai_id_template" or "full_ocr_fallback"
    cardDetected: Optional[bool] = None  # Whether Thai ID card was detected
    cardWarped: Optional[bool] = None  # Whether card was successfully warped
    roiResults: Optional[Dict[str, Any]] = None  # Individual ROI extraction results

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
    debugInfo: Optional[OCRDebugInfo] = None  # For debugging/support

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
    debugInfo: Optional[OCRDebugInfo] = None  # For debugging/support

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
