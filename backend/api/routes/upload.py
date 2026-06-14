from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
import os
import uuid

from backend.auth.dependencies import get_current_user
from backend.auth.models import UserResponse
from backend.config import settings
from backend.parsers.resume_parser import extract_text_from_file

router = APIRouter()

class ParsedResume(BaseModel):
    resume_id: str
    text: str
    filename: str

@router.post("/resume", response_model=ParsedResume)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Accepts a PDF or DOCX file, saves it to the uploads directory, 
    and extracts text content for the LangGraph agent to use.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
        
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.{ext}")
    
    # Save file
    try:
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large. Max {settings.MAX_UPLOAD_SIZE_MB}MB")
            
        with open(file_path, "wb") as f:
            f.write(content)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    # Extract text
    try:
        extracted_text = await extract_text_from_file(file_path, ext)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {e}")
        
    return ParsedResume(
        resume_id=file_id,
        text=extracted_text,
        filename=file.filename
    )
