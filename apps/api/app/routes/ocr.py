from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import get_db
from app.models import Player, Team
from app.services.ocr import OCRService
from app.schemas.player import PlayerResponse
from datetime import datetime

router = APIRouter()

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@router.post("/upload", response_model=PlayerResponse)
async def upload_ocr(
    team_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image file and perform OCR."""
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

        # Create full name
        full_name = None
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name

        # Create player record
        player = Player(
            teamId=team_id,
            firstName=first_name,
            lastName=last_name,
            fullName=full_name,
            sourceFilename=file.filename,
            ocrText=redacted_text,
            confidence=confidence,
            status="pending"
        )

        db.add(player)
        db.commit()
        db.refresh(player)

        return player

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
