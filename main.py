from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
)
from crud import create_user, get_db
from crud import get_user
from models import User
from schemas import UserLogin, UserSignup

app = FastAPI()


@app.post("/signup")
async def create_new_user(user: UserSignup, db: AsyncSession = Depends(get_db)):
    db_user_email = await get_user(db, user.email)
    db_user_name = await get_user(db, user.username)
    if db_user_email or db_user_name:
        raise HTTPException(status_code=400, detail="Email/Username already in use")

    user.hashed_password = get_password_hash(user.hashed_password)

    user = await create_user(user, db)

    return user


@app.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="Authorization", value=f"Bearer {access_token}", httponly=True
    )
    return response


@app.get("/users/me", response_model=UserLogin)
async def profile(user: UserLogin = Depends(get_current_user)):
    return user
