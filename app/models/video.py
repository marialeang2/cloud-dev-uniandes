from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="uploaded", nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False, index=True)
    votes_count = Column(Integer, default=0, nullable=False, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    votes = relationship("Vote", back_populates="video", cascade="all, delete-orphan")

