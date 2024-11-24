from datetime import datetime
from fastapi import File, UploadFile
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone: Optional[str] = None
    profile_photo: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    creation_date: datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=32)
    email: EmailStr = Field(...)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=4, max_length=32)
    email: Optional[EmailStr] = Field(None)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    description: Optional[str] = Field(None)
    profile_photo: Optional[UploadFile] = File(default=[])


class UserChangePassword(BaseModel):
    old_password: str = Field(..., min_length=4)
    new_password: str = Field(..., min_length=4)


class UserDelete(BaseModel):
    password: str = Field(..., min_length=4)
