from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserInfo(BaseModel):
    username: str
    email: EmailStr
    profile_photo: Optional[str]
    description: Optional[str]
    rating: Optional[float]
    creation_date: datetime


class UserCreate(BaseModel):
    username: str = Field(..., min_length=4)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    description: Optional[str]


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


class UserDelete(BaseModel):
    password: str
