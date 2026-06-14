"""
dependencies.py
FastAPI dependencies for route protection and user extraction.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError

from backend.auth.jwt import decode_token
from backend.auth.models import TokenPayload, UserResponse
from backend.db.collections import users_collection

# OAuth2 schema for dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Validates the Bearer token from the request header and returns the User profile.
    Raises 401 if invalid, expired, or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception
        
    if not token_data.sub:
        raise credentials_exception
        
    user_doc = await users_collection.find_one({"user_id": token_data.sub})
    if not user_doc:
        raise credentials_exception
        
    return UserResponse(
        user_id=user_doc["user_id"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=user_doc["created_at"].isoformat()
    )
