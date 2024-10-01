from datetime import datetime
from typing import List
from pydantic import BaseModel


class PostSchema(BaseModel):
    id: int
    text: str
    imgs: List[str]
    date: datetime


class UserLogin(BaseModel):
    username: str
    email: str
    password_hash: str


class UserSchema(UserLogin):
    id: int
