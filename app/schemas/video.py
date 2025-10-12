from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoUploadResponse(BaseModel):
    message: str
    video_id: str


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

