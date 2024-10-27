from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from . import Base
from ..core.config import DB_USERNAME, DB_PASSWORD


db_url = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@localhost/televito"
engine = create_async_engine(db_url)
SessionLocal = async_sessionmaker(engine)


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
