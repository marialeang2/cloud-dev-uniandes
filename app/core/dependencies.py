from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.repositories.user_repository import user_repository
from app.models.user import User
from app.utils.jwt import decode_access_token
from app.core.exceptions import UnauthorizedException


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Extracts token from Authorization header: "Bearer <token>"
    Validates token and returns User object
    
    Raises:
        UnauthorizedException: If token is missing, invalid, or user not found
    """
    if not authorization:
        raise UnauthorizedException("Authorization header missing")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException("Invalid authorization header format. Use: Bearer <token>")
    
    token = parts[1]
    
    # Decode token
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired token")
    
    # Extract user_id from payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user_id in token")
    
    # Get user from database
    user = await user_repository.get_by_id(db, user_id)
    if not user:
        raise UnauthorizedException("User not found")
    
    return user


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided
    Useful for endpoints that can work with or without authentication
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, db)
    except UnauthorizedException:
        return None