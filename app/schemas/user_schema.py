from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserInfo(BaseModel):
    username: str
    email: EmailStr
    profile_photo: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    creation_date: datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=32)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None


class UserChangePassword(BaseModel):
    old_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=4)


class UserDelete(BaseModel):
    password: str = Field(..., min_length=4)
