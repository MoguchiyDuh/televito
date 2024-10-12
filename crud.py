from database import async_session, Base, engine
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas import UserLogin, UserSignup


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


async def get_user(db: AsyncSession, credentials: str):
    async with db as session:
        if "@" in credentials:
            result = await session.execute(
                select(User).filter(User.email == credentials)
            )
        else:
            result = await session.execute(
                select(User).filter(User.username == credentials)
            )
        user = result.scalars().first()
    return user


async def create_user(user: UserSignup, db: AsyncSession):
    user_obj = User(
        username=user.username,
        email=user.email,
        hashed_password=user.hashed_password,
        disabled=False,
    )
    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)
    return user_obj
