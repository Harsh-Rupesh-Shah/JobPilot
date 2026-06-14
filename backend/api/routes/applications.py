from typing import List
from fastapi import APIRouter, Depends

from backend.auth.dependencies import get_current_user
from backend.auth.models import UserResponse

router = APIRouter()

@router.get("/")
async def list_applications(current_user: UserResponse = Depends(get_current_user)):
    """Lists all previously tracked applications for this user."""
    # Stub
    return []

@router.get("/{app_id}")
async def get_application(app_id: str, current_user: UserResponse = Depends(get_current_user)):
    """Get details and outputs of a specific application."""
    # Stub
    return {"application": {}, "outputs": []}

@router.get("/export/{app_id}/{format}")
async def export_application(app_id: str, format: str, current_user: UserResponse = Depends(get_current_user)):
    """Returns a downloadable PDF or DOCX file."""
    # Stub
    return {"detail": f"Export {format} stub"}
