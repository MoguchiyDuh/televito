from datetime import datetime, timedelta
import os
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from crud import get_db, get_user
from models import User
from schemas import UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(user: User, expires_delta: timedelta = 30):
    user_obj = UserLogin.model_validate(user, from_attributes=True)
    expire = (datetime.now() + timedelta(minutes=expires_delta)).timestamp()
    to_encode = user_obj.model_dump()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("JWT_SECRET"), algorithm="HS256")

    return encoded_jwt


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get("Authorization").replace("Bearer ", "")

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, os.environ.get("JWT_SECRET"), algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    if datetime.now().timestamp() > payload.get("exp"):
        raise HTTPException(status_code=401, detail="Token expired")

    username = payload.get("username")
    user = await get_user(db, username)

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user
