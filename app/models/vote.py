from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.db.base import Base


class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    voted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="votes")
    video = relationship("Video", back_populates="votes")
    
    # Constraint: one vote per user per video
    __table_args__ = (
        UniqueConstraint('user_id', 'video_id', name='unique_user_video_vote'),
    )

