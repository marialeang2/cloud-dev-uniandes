from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db.session import get_db
from app.schemas.user import UserSignupRequest, UserLoginRequest, UserResponse, TokenResponse
from app.repositories.user_repository import user_repository
from app.utils.security import get_password_hash, verify_password
from app.utils.jwt import create_access_token
from app.core.config import settings
from app.core.exceptions import DuplicateException, UnauthorizedException

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def signup(
    user_data: UserSignupRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    # Check if email already exists
    existing_user = await user_repository.get_by_email(db, user_data.email)
    if existing_user:
        raise DuplicateException("Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_data.password1)
    
    # Create user
    user = await user_repository.create(
        db=db,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        password_hash=hashed_password,
        city=user_data.city,
        country=user_data.country
    )
    
    return UserResponse(
        message="User created successfully",
        user_id=str(user.id)
    )


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user and return JWT token"""
    # Find user by email
    user = await user_repository.get_by_email(db, credentials.email)
    if not user:
        raise UnauthorizedException("Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Invalid credentials")
    
    # Create JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
        user_id=str(user.id),
        email=user.email
    )