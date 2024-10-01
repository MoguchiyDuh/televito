from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from dotenv import load_dotenv
import os
import jwt
from backend.models import UserDB
from backend.schemas import UserSchema, UserLogin
from backend.database import engine, SessionLocal, Base


load_dotenv(dotenv_path="./backend/.env")
Base.metadata.create_all(engine)

JWT_SECRET = os.environ.get("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SEC = 60 * 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


async def get_user_by_email(db: Session, email: str):
    return db.query(UserDB).filter(UserDB.email == email).first()


async def get_user_by_username(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()


async def create_user(user: UserLogin, db: Session):
    user_obj = UserDB(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password_hash),
        token_expired=True,
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(db: Session, username_email: str, password: str):
    if "@" in username_email:
        user = await get_user_by_email(db, username_email)
    else:
        user = await get_user_by_username(db, username_email)

    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False

    return user


async def create_token(user: UserDB, expires_delta: int = ACCESS_TOKEN_EXPIRE_SEC):
    user_obj = UserSchema.model_validate(user, from_attributes=True)
    to_encode = user_obj.model_dump()
    expire = datetime.now().timestamp() + expires_delta
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return dict(access_token=token, token_type="bearer")


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])

        if datetime.now().timestamp() > payload.get("exp"):
            raise HTTPException(status_code=401, detail="Token expired")

        user = db.query(UserDB).get(payload["id"])
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid Email or Password")

    except:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")

    return UserSchema.model_validate(user, from_attributes=True)
