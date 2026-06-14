import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from backend.auth.dependencies import get_current_user
from backend.auth.models import UserResponse
from backend.auth.jwt import decode_token
from backend.db.collections import applications_collection
from backend.core.config import settings

router = APIRouter()

@router.get("")
async def list_applications(current_user: UserResponse = Depends(get_current_user)):
    """Lists all previously tracked applications for this user."""
    cursor = applications_collection.find({"user_id": current_user.user_id}).sort("created_at", -1)
    apps = await cursor.to_list(length=100)
    
    for app in apps:
        app["_id"] = str(app["_id"])
        app["company"] = app.get("company", "Unknown Company")
        app["role"] = app.get("role", "Unknown Role")
        
    return apps

@router.get("/vault")
async def get_vault(current_user: UserResponse = Depends(get_current_user)):
    """Returns all interview prep questions generated across all applications."""
    cursor = applications_collection.find(
        {"user_id": current_user.user_id, "interview_qa": {"$exists": True, "$ne": ""}},
        {"company": 1, "role": 1, "interview_qa": 1, "created_at": 1}
    ).sort("created_at", -1)
    
    apps = await cursor.to_list(length=100)
    for app in apps:
        app["_id"] = str(app["_id"])
    return apps

@router.get("/{app_id}")
async def get_application(app_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get details and outputs of a specific application."""
    app_record = await applications_collection.find_one({"_id": app_id, "user_id": current_user.user_id})
    if not app_record:
        raise HTTPException(status_code=404, detail="Not found")
    
    app_record["_id"] = str(app_record["_id"])
    return {"application": app_record, "outputs": []}

@router.get("/export/{app_id}/{format}")
async def export_application(app_id: str, format: str, token: str):
    """Returns a downloadable PDF or DOCX file."""
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub", "")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    app_record = await applications_collection.find_one({"_id": app_id, "user_id": user_id})
    if not app_record:
        raise HTTPException(status_code=404, detail="Not found")

    if format not in ["docx", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid format")
        
    file_path = os.path.join(settings.UPLOAD_DIR, "outputs", app_id, "tailored_resume.docx")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not generated yet")
        
    company_clean = "".join(c if c.isalnum() else "_" for c in app_record.get("company", "Company"))
    return FileResponse(path=file_path, filename=f"tailored_resume_{company_clean}.docx")

@router.delete("/{app_id}")
async def delete_application(app_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Deletes an application record."""
    result = await applications_collection.delete_one({"_id": app_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found or already deleted")
    return {"status": "success", "message": "Application deleted"}

