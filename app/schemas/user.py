from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserSignupRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password1: str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('password2')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password1' in info.data and v != info.data['password1']:
            raise ValueError('Passwords do not match')
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    message: str
    user_id: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True

