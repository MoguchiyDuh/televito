from colorama import Fore
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from .parser import update_db

from .db.connection import get_db
from .routes import *


scheduler = AsyncIOScheduler()


async def update_db_task():
    print(Fore.YELLOW + "Updating DB..." + Fore.RESET)
    async for db in get_db():
        await update_db(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        update_db_task, "cron", hour=12, timezone="Europe/Moscow"
    )  # every day at 12:00 Moscow time
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(user_route, prefix="/users")


@app.get("/")
async def home():
    return {"message": "Welcome to the User Management API!"}
