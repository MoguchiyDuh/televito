import shutil
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from ..db.models import UserModel
from ..schemas import UserChangePassword, UserCreate, UserUpdate


async def get_user(
    db: AsyncSession, username: str | None = None, email: str | None = None
) -> UserModel:
    if username:
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
    elif email:
        result = await db.execute(select(UserModel).where(UserModel.email == email))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is required",
        )

    user = result.scalars().first()

    return user


async def create_user_logic(user_schema: UserCreate, db: AsyncSession) -> UserModel:
    if await get_user(username=user_schema.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    if await get_user(email=user_schema.email, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    user_schema.password = hash_password(user_schema.password)
    user = UserModel(**user_schema.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, credentials: str, password: str):
    if "@" in credentials:
        user = await get_user(db=db, email=credentials)
    else:
        user = await get_user(db=db, username=credentials)

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    access_token = create_access_token(username=user.username)
    return access_token


PHOTOS_DIR = "./app/content/profile_photos"


async def save_profile_photo(profile_photo: UploadFile) -> str:
    file_extension = profile_photo.filename.split(".")[-1]
    if file_extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image format"
        )
    file_name = f"{uuid4()}.{file_extension}"
    file_path = f"{PHOTOS_DIR}/{file_name}"
    print(file_path)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profile_photo.file, buffer)

    return str(file_name)


async def update_user_logic(
    username: str,
    update_data: UserUpdate,
    db: AsyncSession,
    profile_photo: UploadFile | str = None,
) -> UserModel:
    user = await get_user(username=username, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if profile_photo:
        photo_path = await save_profile_photo(profile_photo)
        user.profile_photo = photo_path

    for key, value in update_data.model_dump(
        exclude_unset=True, exclude_none=True
    ).items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def change_user_password_logic(
    username: str, password_schema: UserChangePassword, db: AsyncSession
) -> UserModel:
    user = await get_user(username=username, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(password_schema.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid old password"
        )

    user.password = hash_password(password_schema.new_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user_logic(
    username: str, password: str, db: AsyncSession
) -> dict[str, str]:
    user = await get_user(username=username, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    await db.execute(delete(UserModel).where(UserModel.username == username))
    await db.commit()
    return {"message": "User has been deleted successfully"}
