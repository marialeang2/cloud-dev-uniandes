from pydantic import BaseModel
from typing import List


class VoteRequest(BaseModel):
    user_id: str


class VoteResponse(BaseModel):
    message: str
    video_id: str
    votes: int


class RankingItem(BaseModel):
    position: int
    username: str
    city: str
    votes: int
    
    class Config:
        from_attributes = True

