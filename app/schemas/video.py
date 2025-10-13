from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoUploadResponse(BaseModel):
    message: str
    task_id: str  # Changed from video_id to match contract


class VideoListItem(BaseModel):
    video_id: str
    title: str
    status: str
    uploaded_at: datetime
    file_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class VideoDetail(BaseModel):
    video_id: str
    title: str
    status: str
    uploaded_at: datetime
    file_path: str
    votes: int
    duration_seconds: Optional[int] = None
    file_size_bytes: int
    is_public: bool
    
    class Config:
        from_attributes = True


class VideoDeleteResponse(BaseModel):
    message: str
    video_id: str


class PublicVideoItem(BaseModel):
    """Schema for public videos list (includes user info and votes)"""
    video_id: str
    title: str
    processed_url: str
    username: str
    city: str
    votes: int
    
    class Config:
        from_attributes = True


class VideoPublishResponse(BaseModel):
    message: str
    video_id: str

