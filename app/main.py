from colorama import Fore
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

from .parser import Parser
from .db.connection import get_db
from .routes import user_route, tg_post_route

# Initialize the scheduler for periodic tasks
scheduler = AsyncIOScheduler()


async def update_db_task():
    """Task that updates the database by parsing new posts."""
    print(f"{Fore.YELLOW}🔄 Updating DB...{Fore.RESET}")
    async for db in get_db():
        async with db as session:
            parser = Parser(session)
            await parser.update_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifespan of the FastAPI app, including scheduled tasks."""
    await update_db_task()  # Initial DB update on startup
    scheduler.add_job(
        update_db_task, "cron", hour=12, timezone="Europe/Moscow"
    )  # Schedule daily DB update at 12:00 (Moscow time)
    scheduler.start()

    try:
        yield  # Yield control to run the app
    finally:
        scheduler.shutdown()
        print(f"{Fore.RED}Scheduler shut down gracefully.{Fore.RESET}")


app = FastAPI(lifespan=lifespan)

# Include user management routes
app.include_router(user_route, prefix="/users")
app.include_router(tg_post_route, prefix="/tg_posts")


@app.get("/")
async def home():
    """Root endpoint for the API."""
    return {"message": "Welcome to the User Management API!"}
