from typing import Optional
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vote import Vote


class VoteRepository:
    
    async def create(
        self,
        db: AsyncSession,
        user_id: UUID,
        video_id: UUID
    ) -> Vote:
        """Create a new vote"""
        vote = Vote(user_id=user_id, video_id=video_id)
        db.add(vote)
        await db.flush()
        await db.refresh(vote)
        return vote
    
    async def get_vote(
        self,
        db: AsyncSession,
        user_id: UUID,
        video_id: UUID
    ) -> Optional[Vote]:
        """Check if a vote exists"""
        result = await db.execute(
            select(Vote).where(
                and_(Vote.user_id == user_id, Vote.video_id == video_id)
            )
        )
        return result.scalar_one_or_none()


# Singleton instance
vote_repository = VoteRepository()

