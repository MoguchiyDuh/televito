from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    email: str


class UserSignup(UserLogin):
    hashed_password: str
