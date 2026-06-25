"""Structured OCR result model for Thai ID card with verification scoring.

Inspired by OCR slip system - separates raw OCR from structured field extraction
and provides confidence scoring for verification.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum


class FieldSource(str, Enum):
    """Source of extracted field."""
    THAI_NAME_ROI = "thai_name_roi"
    ENGLISH_FIRST_ROI = "english_first_roi"
    ENGLISH_LAST_ROI = "english_last_roi"
    DOB_ENGLISH_ROI = "dob_english_roi"
    DOB_THAI_ROI = "dob_thai_roi"
    LABELED_FULL_OCR = "labeled_full_ocr"
    FULL_OCR_FALLBACK = "full_ocr_fallback"


class ReviewReasonCode(str, Enum):
    """Reason codes for when verification is needed."""
    CARD_NOT_DETECTED = "CARD_NOT_DETECTED"
    ROI_EXTRACTION_FAILED = "ROI_EXTRACTION_FAILED"
    MISSING_FIRST_NAME = "MISSING_FIRST_NAME"
    MISSING_LAST_NAME = "MISSING_LAST_NAME"
    MISSING_DATE_OF_BIRTH = "MISSING_DATE_OF_BIRTH"
    LOW_OCR_CONFIDENCE = "LOW_OCR_CONFIDENCE"
    WEAK_NAME_EVIDENCE = "WEAK_NAME_EVIDENCE"
    FULL_OCR_FALLBACK_ONLY = "FULL_OCR_FALLBACK_ONLY"
    DOB_PARSE_FAILED = "DOB_PARSE_FAILED"
    NEED_MANUAL_REVIEW = "NEED_MANUAL_REVIEW"


@dataclass
class FieldCandidate:
    """A candidate value for a field with source and confidence."""
    fieldName: str  # firstName | lastName | dateOfBirth
    value: Any  # string or date
    source: FieldSource
    confidence: float  # 0.0-1.0
    evidenceText: str  # redacted text snippet
    parser: str  # e.g., "parse_thai_full_name_from_roi"
    warnings: List[str] = field(default_factory=list)
    score: float = 0.0  # calculated score


@dataclass
class IDOCRStructuredResult:
    """Structured OCR result for Thai ID card with verification scoring."""

    # Extracted fields
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    dateOfBirth: Optional[date] = None
    birthYearBE: Optional[int] = None

    # Field candidates (for verification UI)
    fieldCandidates: Dict[str, List[FieldCandidate]] = field(default_factory=dict)

    # Confidence scores
    ocrConfidence: float = 0.0  # Average confidence from ROI extractions
    structuredConfidence: float = 0.0  # Score based on field presence/validity
    finalConfidence: float = 0.0  # Weighted: ocrConfidence*0.4 + structuredConfidence*0.6

    # Extraction metadata
    extractionMode: str = "full_ocr_fallback"  # thai_id_template_warped, thai_id_template_card_like, full_ocr_fallback
    cardDetected: bool = False
    cardWarped: bool = False
    cardLikeFallbackUsed: bool = False
    roiPresetUsed: Optional[str] = None

    # Verification info
    reviewReasons: List[ReviewReasonCode] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Debug info
    debugInfo: Dict[str, Any] = field(default_factory=dict)

    def needs_review(self) -> bool:
        """Check if result needs manual review."""
        return (
            len(self.reviewReasons) > 0 or
            self.finalConfidence < 0.7 or
            self.firstName is None or
            self.lastName is None or
            self.dateOfBirth is None
        )
