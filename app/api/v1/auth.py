from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserSignupRequest, UserLoginRequest, UserResponse
from app.repositories.user_repository import user_repository
from app.utils.security import get_password_hash, verify_password
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


@router.post("/login", response_model=UserResponse)
async def login(
    credentials: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    # Find user by email
    user = await user_repository.get_by_email(db, credentials.email)
    if not user:
        raise UnauthorizedException("Invalid credentials")
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException("Invalid credentials")
    
    return UserResponse(
        message="Login successful",
        user_id=str(user.id),
        email=user.email
    )

