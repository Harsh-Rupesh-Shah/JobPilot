"""
service.py
Core business logic for user registration, login, and token management.
"""

import uuid
import hashlib
from datetime import datetime, timezone
from passlib.context import CryptContext
from fastapi import HTTPException, status

from backend.db.collections import users_collection, refresh_tokens_collection
from backend.auth.models import UserCreate, UserLogin, UserResponse, Token
from backend.auth.jwt import create_access_token, create_refresh_token

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def hash_token(token: str) -> str:
    """Hashes a refresh token for safe storage in the database."""
    return hashlib.sha256(token.encode()).hexdigest()

async def register_user(user_in: UserCreate) -> UserResponse:
    """Registers a new user, hashes password, and saves to MongoDB."""
    # Check if email exists
    existing = await users_collection.find_one({"email": user_in.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )

    user_id = f"usr_{uuid.uuid4().hex[:16]}"
    now = datetime.now(timezone.utc)
    
    user_doc = {
        "user_id": user_id,
        "email": user_in.email.lower(),
        "hashed_password": get_password_hash(user_in.password),
        "full_name": user_in.full_name,
        "created_at": now,
        "updated_at": now
    }
    
    await users_collection.insert_one(user_doc)
    
    return UserResponse(
        user_id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=now.isoformat()
    )

async def login_user(user_in: UserLogin) -> tuple[Token, str]:
    """
    Authenticates a user and returns (Token object, plain_refresh_token).
    Stores the hashed refresh token in the database.
    """
    user_doc = await users_collection.find_one({"email": user_in.email.lower()})
    if not user_doc or not verify_password(user_in.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = user_doc["user_id"]
    
    # Generate tokens
    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token(subject=user_id)
    
    # Save refresh token hash to DB
    from backend.core.config import settings
    from datetime import timedelta
    expire_date = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    await refresh_tokens_collection.insert_one({
        "user_id": user_id,
        "token_hash": hash_token(refresh_token),
        "expires_at": expire_date,
        "revoked": False,
        "created_at": datetime.now(timezone.utc)
    })
    
    user_resp = UserResponse(
        user_id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=user_doc["created_at"].isoformat()
    )
    
    token_obj = Token(
        access_token=access_token,
        token_type="bearer",
        user=user_resp
    )
    
    return token_obj, refresh_token

async def refresh_access_token(refresh_token: str) -> Token:
    """
    Validates a refresh token against the database and returns a new Token object.
    """
    from backend.auth.jwt import decode_token
    from jose import JWTError
    
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "refresh":
            raise ValueError()
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    t_hash = hash_token(refresh_token)
    
    # Check DB
    token_doc = await refresh_tokens_collection.find_one({
        "token_hash": t_hash,
        "revoked": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not token_doc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is invalid or expired")
        
    # Get user
    user_doc = await users_collection.find_one({"user_id": user_id})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    # Create new access token ONLY (keep same refresh token)
    access_token = create_access_token(subject=user_id)
    
    user_resp = UserResponse(
        user_id=user_id,
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=user_doc["created_at"].isoformat()
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user_resp
    )

async def logout_user(refresh_token: str) -> None:
    """Revokes the given refresh token."""
    t_hash = hash_token(refresh_token)
    await refresh_tokens_collection.update_one(
        {"token_hash": t_hash},
        {"$set": {"revoked": True}}
    )
