from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    
    async def create(
        self,
        db: AsyncSession,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        city: str,
        country: str
    ) -> User:
        """Create a new user"""
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email.lower(),
            password_hash=password_hash,
            city=city,
            country=country
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()


# Singleton instance
user_repository = UserRepository()

