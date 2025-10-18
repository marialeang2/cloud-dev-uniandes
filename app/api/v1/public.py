from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.video import VideoListItem, PublicVideoItem
from app.schemas.vote import VoteResponse, RankingItem
from app.repositories.video_repository import video_repository
from app.repositories.vote_repository import vote_repository
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.exceptions import ValidationException, NotFoundException

router = APIRouter()


@router.get(
    "/videos",
    status_code=status.HTTP_200_OK,
    response_model=List[PublicVideoItem],
    summary="List public videos",
    description="Get all public videos. **No authentication required**.",
    responses={
        200: {"description": "List of public videos"}
    }
)
async def list_public_videos(
    limit: int = Query(20, ge=1, le=100, description="Number of videos to return"),
    offset: int = Query(0, ge=0, description="Number of videos to skip"),
    db: AsyncSession = Depends(get_db)
):
    """List all public videos (No authentication required)"""
    videos = await video_repository.get_public_videos(db, limit=limit, offset=offset)
    
    return [
        PublicVideoItem(
            video_id=str(v.id),
            title=v.title,
            processed_url=v.file_path,
            username=f"{v.user.first_name} {v.user.last_name}",
            city=v.user.city,
            votes=v.votes_count
        )
        for v in videos
    ]


@router.post(
    "/videos/{video_id}/vote",
    status_code=status.HTTP_200_OK,
    response_model=VoteResponse,
    summary=" Vote for a video",
    description="Vote for a public video. **Requires JWT authentication**.",
    responses={
        200: {"description": "Vote registered successfully"},
        401: {"description": "Unauthorized"},
        400: {"description": "Already voted"},
        404: {"description": "Video not found"}
    }
)
async def vote_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Vote for a video (JWT Protected)"""
    try:
        video_uuid = UUID(video_id)
    except ValueError:
        raise ValidationException("Invalid UUID format")
    
    video = await video_repository.get_by_id(db, video_uuid)
    
    if not video or not video.is_public:
        raise NotFoundException("Video not found or not public")
    
    existing_vote = await vote_repository.get_vote(db, current_user.id, video_uuid)
    
    if existing_vote:
        raise ValidationException("You have already voted for this video")
    
    await vote_repository.create(db, current_user.id, video_uuid)
    await video_repository.increment_votes(db, video_uuid)
    
    return VoteResponse(message="Vote registered successfully")


@router.get(
    "/rankings",
    status_code=status.HTTP_200_OK,
    response_model=List[RankingItem],
    summary="Get video rankings",
    description="Get users ranked by total votes. **No authentication required**.",
    responses={
        200: {"description": "List of rankings"}
    }
)
async def get_rankings(
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
):
    """Get video rankings (No authentication required)"""
    videos = await video_repository.get_rankings(
        db,
        city=city,
        limit=limit,
        offset=offset
    )
    
    rankings = []
    for idx, video in enumerate(videos, start=offset + 1):
        rankings.append(RankingItem(
            position=idx,
            username=f"{video.user.first_name} {video.user.last_name}",
            city=video.user.city,
            votes=video.votes_count
        ))
    
    return rankings