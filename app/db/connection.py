from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import DB_URL
from . import Base


engine = create_async_engine(DB_URL)
SessionLocal = async_sessionmaker(engine)


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
