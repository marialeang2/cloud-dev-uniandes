from fastapi import APIRouter, Depends, File, UploadFile, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import uuid
from pathlib import Path
import aiofiles

from app.db.session import get_db
from app.schemas.video import (
    VideoUploadResponse,
    VideoListItem,
    VideoDetail,
    VideoDeleteResponse,
    VideoPublishResponse
)
from app.repositories.video_repository import video_repository
from app.repositories.user_repository import user_repository
from app.storage.local_storage import storage
from app.utils.video_validator import validate_video
from app.core.config import settings
from app.core.exceptions import (
    ValidationException,
    NotFoundException,
    ForbiddenException
)

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=VideoUploadResponse)
async def upload_video(
    video_file: UploadFile = File(...),
    title: str = Form(..., min_length=1, max_length=200),
    user_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a video file"""
    # Validate user exists
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValidationException("Invalid user_id format")
    
    user = await user_repository.get_by_id(db, user_uuid)
    if not user:
        raise NotFoundException("User not found")
    
    # Validate file type
    if not video_file.content_type or not video_file.content_type.startswith("video/"):
        raise ValidationException("File must be a video")
    
    # Read file content and check size
    file_content = await video_file.read()
    file_size = len(file_content)
    
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise ValidationException(f"File size exceeds maximum allowed ({settings.MAX_FILE_SIZE_MB}MB)")
    
    # Save file temporarily for validation
    temp_filename = f"{uuid.uuid4()}.mp4"
    temp_path = Path(settings.STORAGE_PATH) / "temp" / temp_filename
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Write temp file
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(file_content)
        
        # Validate video with ffprobe
        metadata = await validate_video(str(temp_path))
        
        # Save to permanent storage
        final_filename = f"{uuid.uuid4()}.mp4"
        file_path = await storage.save_file(file_content, final_filename, "uploads")
        
        # Create video record in database
        video = await video_repository.create(
            db=db,
            user_id=user_uuid,
            title=title,
            original_filename=video_file.filename or "video.mp4",
            file_path=file_path,
            duration_seconds=int(metadata['duration']),
            file_size_bytes=file_size,
            status="processed"  # Immediately marked as processed (no async processing)
        )
        
        return VideoUploadResponse(
            message="Video uploaded successfully",
            task_id=str(video.id)  # Using video_id as task_id (no async processing)
        )
        
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[VideoListItem])
async def list_videos(
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """List all videos for a user"""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValidationException("Invalid user_id format")
    
    videos = await video_repository.get_by_user(db, user_uuid)
    
    return [
        VideoListItem(
            video_id=str(v.id),
            title=v.title,
            status=v.status,
            uploaded_at=v.uploaded_at,
            file_path=v.file_path if v.status == "processed" else None
        )
        for v in videos
    ]


@router.get("/{video_id}", status_code=status.HTTP_200_OK, response_model=VideoDetail)
async def get_video(
    video_id: str,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Get video details"""
    try:
        video_uuid = UUID(video_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValidationException("Invalid UUID format")
    
    video = await video_repository.get_by_id(db, video_uuid)
    
    if not video:
        raise NotFoundException("Video not found")
    
    if video.user_id != user_uuid:
        raise ForbiddenException("You don't have permission to view this video")
    
    return VideoDetail(
        video_id=str(video.id),
        title=video.title,
        status=video.status,
        uploaded_at=video.uploaded_at,
        file_path=video.file_path,
        votes=video.votes_count,
        duration_seconds=video.duration_seconds,
        file_size_bytes=video.file_size_bytes,
        is_public=video.is_public
    )


@router.put("/{video_id}/publish", status_code=status.HTTP_200_OK, response_model=VideoPublishResponse)
async def publish_video(
    video_id: str,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Make a video public (available for voting)"""
    try:
        video_uuid = UUID(video_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValidationException("Invalid UUID format")
    
    video = await video_repository.get_by_id(db, video_uuid)
    
    if not video:
        raise NotFoundException("Video not found")
    
    if video.user_id != user_uuid:
        raise ForbiddenException("You don't have permission to publish this video")
    
    if video.status != "processed":
        raise ValidationException("Video must be processed before publishing")
    
    # Make video public
    video.is_public = True
    await db.commit()
    
    return VideoPublishResponse(
        message="Video published successfully",
        video_id=str(video_id)
    )


@router.delete("/{video_id}", status_code=status.HTTP_200_OK, response_model=VideoDeleteResponse)
async def delete_video(
    video_id: str,
    user_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """Delete a video"""
    try:
        video_uuid = UUID(video_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise ValidationException("Invalid UUID format")
    
    video = await video_repository.get_by_id(db, video_uuid)
    
    if not video:
        raise NotFoundException("Video not found")
    
    if video.user_id != user_uuid:
        raise ForbiddenException("You don't have permission to delete this video")
    
    if video.is_public:
        raise ValidationException("Cannot delete a public video")
    
    # Delete file from storage
    await storage.delete_file(video.file_path)
    
    # Delete from database
    await video_repository.delete(db, video_uuid)
    
    return VideoDeleteResponse(
        message="Video deleted successfully",
        video_id=str(video_id)
    )

