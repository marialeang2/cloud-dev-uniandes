from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models.video import Video
from app.models.user import User


class VideoRepository:
    
    async def create(
        self,
        db: AsyncSession,
        user_id: UUID,
        title: str,
        original_filename: str,
        file_path: str,
        duration_seconds: int,
        file_size_bytes: int,
        status: str = "processed"
    ) -> Video:
        """Create a new video record"""
        video = Video(
            user_id=user_id,
            title=title,
            original_filename=original_filename,
            file_path=file_path,
            duration_seconds=duration_seconds,
            file_size_bytes=file_size_bytes,
            status=status,
            is_public=False,
            votes_count=0
        )
        db.add(video)
        await db.flush()
        await db.refresh(video)
        return video
    
    async def get_by_id(self, db: AsyncSession, video_id: UUID) -> Optional[Video]:
        """Get video by ID"""
        result = await db.execute(
            select(Video)
            .options(joinedload(Video.user))
            .where(Video.id == video_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(self, db: AsyncSession, user_id: UUID) -> List[Video]:
        """Get all videos for a user"""
        result = await db.execute(
            select(Video)
            .where(Video.user_id == user_id)
            .order_by(desc(Video.uploaded_at))
        )
        return list(result.scalars().all())
    
    async def get_public_videos(
        self,
        db: AsyncSession,
        limit: int = 20,
        offset: int = 0
    ) -> List[Video]:
        """Get public videos with pagination"""
        result = await db.execute(
            select(Video)
            .options(joinedload(Video.user))  # Load user relationship
            .where(and_(Video.is_public == True, Video.status == 'processed'))
            .order_by(desc(Video.uploaded_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    async def delete(self, db: AsyncSession, video_id: UUID) -> None:
        """Delete a video"""
        await db.execute(delete(Video).where(Video.id == video_id))
        await db.flush()
    
    async def increment_votes(self, db: AsyncSession, video_id: UUID) -> None:
        """Increment vote count for a video"""
        video = await self.get_by_id(db, video_id)
        if video:
            video.votes_count += 1
            await db.flush()
    
    async def get_rankings(
        self,
        db: AsyncSession,
        city: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Video]:
        """Get video rankings with user info"""
        query = select(Video).options(joinedload(Video.user))
        
        if city:
            query = query.join(User).where(User.city == city)
        
        query = query.where(and_(
            Video.is_public == True,
            Video.status == 'processed'
        ))
        
        query = query.order_by(desc(Video.votes_count)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return list(result.scalars().all())


# Singleton instance
video_repository = VideoRepository()

