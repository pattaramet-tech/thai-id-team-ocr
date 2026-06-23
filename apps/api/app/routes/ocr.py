from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models import Player, Team
from app.services.ocr import OCRService
from app.services.eligibility import date_to_birth_year_be, check_eligibility_for_player
from app.schemas.ocr import OCRPreviewResponse, OCRBatchResponse, OCRBatchItemResponse
from datetime import datetime, date
from typing import Optional, Tuple

router = APIRouter()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB per file for batch
MAX_BATCH_FILES = 30

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_ocr_file(
    filename: str,
    contents: bytes,
    team: Team
) -> Tuple[Optional[OCRBatchItemResponse], Optional[str]]:
    """
    Process a single OCR file and return result or error.
    Returns (result, error) where one is None.
    """
    try:
        # Validate file
        if not allowed_file(filename):
            return None, "Only JPG and PNG files are allowed"

        if len(contents) > MAX_FILE_SIZE:
            return None, f"File size exceeds {MAX_FILE_SIZE // (1024*1024)} MB limit"

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

        return OCRBatchItemResponse(
            sourceFilename=filename,
            success=True,
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
        ), None

    except Exception as e:
        return None, f"OCR processing failed: {str(e)}"

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

        # Read file
        contents = await file.read()

        # Use shared OCR processing logic
        result, error = process_ocr_file(file.filename, contents, team)

        if error:
            raise HTTPException(status_code=400, detail=error)

        if result.success:
            return OCRPreviewResponse(**result.dict())
        else:
            raise HTTPException(status_code=500, detail=result.error)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.post("/batch-upload", response_model=OCRBatchResponse)
async def batch_upload_ocr(
    team_id: int = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Batch upload multiple image files for OCR preview.
    Returns array of results without saving to database.
    Errors in individual files do not fail the entire batch.
    """
    try:
        # Validate team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Validate number of files
        if len(files) > MAX_BATCH_FILES:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot upload more than {MAX_BATCH_FILES} files at once"
            )

        if len(files) == 0:
            raise HTTPException(status_code=400, detail="No files provided")

        # Process each file
        items = []
        success_count = 0
        error_count = 0

        for file in files:
            contents = await file.read()
            result, error = process_ocr_file(file.filename, contents, team)

            if error:
                items.append(OCRBatchItemResponse(
                    sourceFilename=file.filename,
                    success=False,
                    error=error
                ))
                error_count += 1
            else:
                items.append(result)
                success_count += 1

        return OCRBatchResponse(
            totalFiles=len(files),
            successCount=success_count,
            errorCount=error_count,
            items=items
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch OCR processing failed: {str(e)}")
