from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Dict, Any

class OCRDebugInfo(BaseModel):
    """Debug information about OCR processing."""
    ocrText: str  # Redacted OCR output for display/copying
    preprocessingMethod: str  # Which preprocessing method was best
    psmMode: int  # Tesseract PSM mode used
    confidence: float
    extractionMode: Optional[str] = None  # "thai_id_template_warped", "thai_id_template_card_like", or "full_ocr_fallback"
    cardDetected: Optional[bool] = None  # Whether Thai ID card was detected with contours
    cardWarped: Optional[bool] = None  # Whether card was successfully warped
    cardLikeFallbackUsed: Optional[bool] = None  # Whether card-like fallback was used
    roiPresetUsed: Optional[str] = None  # "v1", "v2", "v3" ROI preset
    roiResults: Optional[Dict[str, Any]] = None  # Individual ROI extraction results
    fieldCandidates: Optional[Dict[str, Any]] = None  # All field candidates from structured extraction
    selectedCandidates: Optional[Dict[str, Any]] = None  # Best selected candidate per field
    reviewReasons: Optional[List[str]] = None  # Reasons for manual review

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
    # Structured OCR fields
    extraction_mode: Optional[str] = None
    roi_preset: Optional[str] = None
    card_detected: Optional[bool] = None
    card_warped: Optional[bool] = None
    card_like_fallback_used: Optional[bool] = None
    field_candidates: Optional[Dict[str, Any]] = None
    selected_candidates: Optional[Dict[str, Any]] = None
    review_reasons: Optional[List[str]] = None
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
    # Structured OCR fields
    extraction_mode: Optional[str] = None
    roi_preset: Optional[str] = None
    card_detected: Optional[bool] = None
    card_warped: Optional[bool] = None
    card_like_fallback_used: Optional[bool] = None
    field_candidates: Optional[Dict[str, Any]] = None
    selected_candidates: Optional[Dict[str, Any]] = None
    review_reasons: Optional[List[str]] = None
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
