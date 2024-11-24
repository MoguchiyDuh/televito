import os
import re

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from ..db.models import UserModel
from ..schemas import UserChangePassword, UserCreate, UserUpdate
from ..core.utils import save_image


async def get_user(
    db: AsyncSession,
    user_id: int | None = None,
    username: str | None = None,
    email: str | None = None,
    phone: int | None = None,
) -> UserModel:
    if user_id:
        result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    elif username:
        result = await db.execute(
            select(UserModel).where(UserModel.username == username)
        )
    elif email:
        result = await db.execute(select(UserModel).where(UserModel.email == email))
    elif phone:
        result = await db.execute(select(UserModel).where(UserModel.phone == phone))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
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
    elif re.match(r"^\+?\d{10,15}$", credentials):
        user = await get_user(db=db, phone=credentials)
    else:
        user = await get_user(db=db, username=credentials)

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token(username=user.username)

    return access_token


PHOTOS_DIR = "./app/content/profile_photos"
MAX_PHOTO_SIZE = 1024 * 1024  # 1 mb in bytes


async def update_user_logic(
    username: str,
    update_data: UserUpdate,
    db: AsyncSession,
) -> UserModel:
    user = await get_user(username=username, db=db)

    user_dir = os.path.join(PHOTOS_DIR, f"user{str(user.id)}")

    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)

    # Updating profile photo if it was changed
    if update_data.profile_photo:
        if update_data.profile_photo.size > MAX_PHOTO_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Profile photo is too large",
            )

        update_data.profile_photo = save_image(
            image=update_data.profile_photo,
            dir=os.path.join(PHOTOS_DIR, f"user{str(user.id)}"),
        )

        if os.path.exists(user.profile_photo):
            os.remove(user.profile_photo)

    # Updating user data
    for key, value in update_data.model_dump(
        exclude_unset=True, exclude_none=True
    ).items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return user


async def change_user_password_logic(
    username: str, password_schema: UserChangePassword, db: AsyncSession
) -> UserModel:
    user = await get_user(username=username, db=db)

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

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid password")

    if os.path.exists(user.profile_photo):
        os.remove(user.profile_photo)

    await db.execute(delete(UserModel).where(UserModel.username == username))
    await db.commit()

    return {"message": "User has been deleted successfully"}
