from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.schemas.video import VideoListItem, PublicVideoItem
from app.schemas.vote import VoteRequest, VoteResponse, RankingItem
from app.repositories.video_repository import video_repository
from app.repositories.vote_repository import vote_repository
from app.core.exceptions import ValidationException, NotFoundException

router = APIRouter()


@router.get("/videos", status_code=status.HTTP_200_OK, response_model=List[PublicVideoItem])
async def list_public_videos(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """List all public videos with user info and votes"""
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


@router.post("/videos/{video_id}/vote", status_code=status.HTTP_200_OK, response_model=VoteResponse)
async def vote_video(
    video_id: str,
    vote_request: VoteRequest,
    db: AsyncSession = Depends(get_db)
):
    """Vote for a video"""
    try:
        video_uuid = UUID(video_id)
        user_uuid = UUID(vote_request.user_id)
    except ValueError:
        raise ValidationException("Invalid UUID format")
    
    # Check if video exists and is public
    video = await video_repository.get_by_id(db, video_uuid)
    
    if not video or not video.is_public:
        raise NotFoundException("Video not found or not public")
    
    # Check if user already voted
    existing_vote = await vote_repository.get_vote(db, user_uuid, video_uuid)
    
    if existing_vote:
        raise ValidationException("You have already voted for this video")
    
    # Create vote
    await vote_repository.create(db, user_uuid, video_uuid)
    
    # Increment vote count
    await video_repository.increment_votes(db, video_uuid)
    
    return VoteResponse(message="Vote registered successfully")


@router.get("/rankings", status_code=status.HTTP_200_OK, response_model=List[RankingItem])
async def get_rankings(
    city: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get video rankings"""
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

