from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
import os
import uuid

from backend.auth.dependencies import get_current_user
from backend.auth.models import UserResponse
from backend.config import settings
from backend.parsers.resume_parser import extract_text_from_file
from backend.tools.vector_search import embed_and_store_resume
from backend.db.collections import resumes_collection
from datetime import datetime, timezone

router = APIRouter()

class ParsedResume(BaseModel):
    resume_id: str
    text: str
    filename: str

class UpdateResumeRequest(BaseModel):
    text: str

@router.get("/resume", response_model=ParsedResume)
async def get_latest_resume(current_user: UserResponse = Depends(get_current_user)):
    """
    Returns the user's latest parsed resume if they have one stored.
    """
    doc = await resumes_collection.find_one({"user_id": current_user.user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="No resume found")
    
    return ParsedResume(
        resume_id=doc["resume_id"],
        text=doc["text"],
        filename=doc["filename"]
    )

@router.put("/resume", response_model=ParsedResume)
async def update_resume_text(
    req: UpdateResumeRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Updates the text of the Master Profile and regenerates the FAISS index.
    """
    doc = await resumes_collection.find_one({"user_id": current_user.user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="No master profile found. Please upload a resume first.")
        
    resume_id = doc["resume_id"]
    
    # Update DB
    await resumes_collection.update_one(
        {"user_id": current_user.user_id},
        {"$set": {
            "text": req.text,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    # Update FAISS
    try:
        embed_and_store_resume(
            resume_text=req.text,
            run_id=resume_id,
            user_id=current_user.user_id,
        )
    except Exception as embed_exc:
        import logging
        logging.getLogger(__name__).warning(
            "FAISS index update failed for resume_id=%s: %s", resume_id, embed_exc
        )
        
    return ParsedResume(
        resume_id=resume_id,
        text=req.text,
        filename=doc["filename"]
    )

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

    # Build FAISS vector index for the resume (used later by the Resume Agent)
    # Uses file_id as the resume_id so it can be retrieved during graph execution.
    try:
        embed_and_store_resume(
            resume_text=extracted_text,
            run_id=file_id,
            user_id=current_user.user_id,
        )
    except Exception as embed_exc:
        # Non-fatal: log but don't block the upload response
        import logging
        logging.getLogger(__name__).warning(
            "FAISS index build failed for file_id=%s: %s", file_id, embed_exc
        )

    # Store the master resume in MongoDB
    now = datetime.now(timezone.utc)
    await resumes_collection.update_one(
        {"user_id": current_user.user_id},
        {"$set": {
            "resume_id": file_id,
            "text": extracted_text,
            "filename": file.filename,
            "updated_at": now
        }},
        upsert=True
    )

    return ParsedResume(
        resume_id=file_id,
        text=extracted_text,
        filename=file.filename
    )
