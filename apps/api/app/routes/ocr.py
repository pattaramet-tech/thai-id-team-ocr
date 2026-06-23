from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models import Player, Team
from app.services.ocr import OCRService
from app.services.eligibility import date_to_birth_year_be, check_eligibility_for_player
from app.schemas.ocr import OCRPreviewResponse
from datetime import datetime

router = APIRouter()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload", response_model=OCRPreviewResponse)
async def upload_ocr(
    team_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload image file and perform OCR preview.
    Returns extracted data without saving to database.
    """
    try:
        # Validate team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Validate file
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Only JPG and PNG files are allowed"
            )

        # Read file
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds 10 MB limit"
            )

        # Extract text with confidence
        ocr_text, confidence = OCRService.extract_text_with_confidence(contents)

        # Redact ID numbers
        redacted_text = OCRService.redact_thai_id_numbers(ocr_text)

        # Extract names
        first_name, last_name = OCRService.extract_thai_names(redacted_text)

        # Extract date of birth
        date_of_birth = OCRService.extract_date_of_birth(ocr_text)

        # Calculate birth year BE if we have date
        birth_year_be = date_to_birth_year_be(date_of_birth) if date_of_birth else None

        # Create full name
        full_name = None
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name

        # Check eligibility
        eligibility_result = check_eligibility_for_player(
            team.ageGroup,
            team.competitionYearBE,
            date_of_birth
        )

        # Collect warnings
        warnings = []
        if not first_name:
            warnings.append("Could not extract first name from OCR")
        if not last_name:
            warnings.append("Could not extract last name from OCR")
        if not date_of_birth:
            warnings.append("Could not extract date of birth from OCR")
        if confidence < 0.7:
            warnings.append(f"Low OCR confidence: {confidence:.1%}")

        return OCRPreviewResponse(
            sourceFilename=file.filename,
            ocrText=redacted_text,
            firstName=first_name,
            lastName=last_name,
            fullName=full_name,
            dateOfBirth=date_of_birth,
            birthYearBE=birth_year_be,
            confidence=confidence,
            eligibilityStatus=eligibility_result["status"],
            eligibilityNote=eligibility_result["note"],
            warnings=warnings
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
