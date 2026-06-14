from fastapi import APIRouter, Depends, Response, Request, status
from backend.auth.models import UserCreate, UserLogin, UserResponse, Token
from backend.auth.service import register_user, login_user, refresh_access_token, logout_user
from backend.auth.dependencies import get_current_user

router = APIRouter()

REFRESH_COOKIE_NAME = "refresh_token"

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, response: Response):
    """Register a new user and return an access token (sets refresh cookie)."""
    # 1. Register user in DB
    new_user = await register_user(user_in)
    
    # 2. Login immediately to issue tokens
    token_obj, plain_refresh = await login_user(UserLogin(email=user_in.email, password=user_in.password))
    
    # 3. Set HttpOnly cookie for refresh token
    from backend.core.config import settings
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=plain_refresh,
        httponly=True,
        secure=False, # Set True in production with HTTPS
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return token_obj

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, response: Response):
    """Login and return an access token (sets refresh cookie)."""
    token_obj, plain_refresh = await login_user(user_in)
    
    from backend.core.config import settings
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=plain_refresh,
        httponly=True,
        secure=False, # Set True in production with HTTPS
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return token_obj

@router.post("/refresh", response_model=Token)
async def refresh(request: Request):
    """Exchange a valid refresh cookie for a new access token."""
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        from fastapi import HTTPException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token cookie found")
        
    token_obj = await refresh_access_token(refresh_token)
    return token_obj

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Revokes the current refresh token and clears the cookie."""
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_token:
        await logout_user(refresh_token)
        
    response.delete_cookie(REFRESH_COOKIE_NAME)
    return {"detail": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get the profile of the currently authenticated user."""
    return current_user
