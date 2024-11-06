import asyncio
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from colorama import Fore

from .db.models import ParseModel
from .core.config import *
from .parser_re import parse_text

app = Client("televito", api_hash=TG_API_HASH, api_id=TG_API_ID)
DAYS_TO_PARSE_IF_EMPTY = 3 * 30


def parser(
    caption: str, google_maps_url: str, images: list[str], post_datetime: datetime
) -> ParseModel:
    parsed_text = parse_text(caption, post_datetime)

    model = ParseModel(
        google_maps_url=google_maps_url,
        **parsed_text,
        images=images,
        publication_datetime=post_datetime,
    )
    return model


async def insert_data(db: AsyncSession, model: ParseModel):
    result = await db.execute(
        select(ParseModel).filter(
            ParseModel.location == model.location,
            ParseModel.area == model.area,
            ParseModel.floor == model.floor,
            ParseModel.floors_in_building == model.floors_in_building,
        )
    )

    similar_post = result.scalars().first()

    if not similar_post:  # IF UNIQUE POST
        db.add(model)
        print(
            f"{Fore.GREEN}✓ New post added to the DB.{Fore.CYAN}Location:{Fore.RESET} {model.location}, {Fore.CYAN}Area:{Fore.RESET} {model.area}, {Fore.CYAN}Published on:{Fore.RESET} {model.publication_datetime}",
        )

        await db.commit()

    elif (
        model.publication_datetime > similar_post.publication_datetime
    ):  # UPDATE THE POST
        print(f"{Fore.BLUE}Existing post updated in the db.{Fore.RESET}")
        for key, value in model.__dict__.items():
            if key != "_sa_instance_state":
                if value != getattr(similar_post, key):  # CHANGE LOG
                    print(
                        f"{Fore.CYAN}{key.upper()}:{Fore.RESET} {Fore.YELLOW}Changed from:{Fore.RESET} {getattr(similar_post, key)}, "
                        f"{Fore.YELLOW}to:{Fore.RESET} {value}\n{Fore.MAGENTA}{'-' * 40}{Fore.RESET}"
                    )

                setattr(similar_post, key, value)
        await db.commit()

    if similar_post:  # SKIP THE OUTDATED POST
        print(
            f"{Fore.YELLOW}⚠️  Similar post found in the DB. Insertion skipped.{Fore.RESET} "
            f"{Fore.CYAN}Location:{Fore.RESET} {model.location}, "
            f"{Fore.CYAN}Area:{Fore.RESET} {model.area}, "
            f"{Fore.CYAN}Published on:{Fore.RESET} {model.publication_datetime}"
        )


async def get_posts(db: AsyncSession):
    latest_date_query = await db.execute(
        select(func.max(ParseModel.publication_datetime))
    )
    latest_date = latest_date_query.scalar()
    if latest_date is None:
        latest_date = datetime.now() - timedelta(days=DAYS_TO_PARSE_IF_EMPTY)

    images = []

    async with app:
        async for post in app.get_chat_history(TG_GROUP_NAME):
            post: Message
            if post.date <= latest_date:
                print(Fore.GREEN + "THE DB IS UP TO DATE." + Fore.RESET)
                break

            if post.caption is not None:
                images.append(post.photo.file_id)
                model = parser(
                    post.caption, post.caption_entities[0].url, images, post.date
                )
                await insert_data(db, model)
                await asyncio.sleep(0.07)
                images = []
            elif post.photo is not None:
                images.append(post.photo.file_id)


async def update_db(db: AsyncSession):
    await get_posts(db)
