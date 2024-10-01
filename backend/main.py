from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.services import (
    authenticate_user,
    create_token,
    create_user,
    get_current_user,
    get_db,
    get_user_by_email,
    get_user_by_username,
)
from backend.models import PostDB, UserDB
from backend.schemas import UserSchema, UserLogin, PostSchema


app = FastAPI()


@app.get("/posts/", response_model=List[PostSchema])
async def read_posts(db: Session = Depends(get_db)):
    items = db.query(PostDB).all()
    return items


@app.post("/users")
async def create_new_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user_email = await get_user_by_email(db, user.email)
    db_user_name = await get_user_by_username(db, user.username)
    if db_user_email or db_user_name:
        raise HTTPException(status_code=400, detail="Email/Username already in use")

    user = await create_user(user, db)

    return await create_token(user)


@app.post("/token")
async def generate_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Email or Password")
    token = await create_token(user)
    print(token)
    return token


@app.get("/users/me", response_model=UserSchema)
async def get_user(user: UserSchema = Depends(get_current_user)):
    return user


@app.get("/")
async def hello():
    return "hello"
