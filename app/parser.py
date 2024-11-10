import asyncio
from datetime import date, datetime, timedelta
from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from colorama import Fore

from .db.models import ParseModel
from .core.config import TG_API_HASH, TG_API_ID, TG_GROUP_NAME
from .parser_re import parse_text

app = Client("televito", api_hash=TG_API_HASH, api_id=TG_API_ID)
DAYS_TO_PARSE_IF_EMPTY = 90  # 3 months


class Parser:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def text_to_model(
        parsed_text: str,
        google_maps_url: str,
        images: list[str],
        post_datetime: datetime,
    ) -> ParseModel:
        """Converts parsed text and metadata into a ParseModel object."""
        return ParseModel(
            google_maps_url=google_maps_url,
            **parsed_text,
            images=images,
            publication_datetime=post_datetime,
        )

    async def insert_data(self, model: ParseModel):
        """Inserts or updates a post in the database if needed."""
        result = await self.db.execute(
            select(ParseModel).filter(
                ParseModel.location == model.location,
                ParseModel.area == model.area,
                ParseModel.floor == model.floor,
                ParseModel.floors_in_building == model.floors_in_building,
            )
        )

        similar_post = result.scalars().first()

        # if there is no similar post in the DB, add it to the DB
        if not similar_post:
            self.db.add(model)
            print(
                f"{Fore.GREEN}✓ New post added to the DB.{Fore.RESET}\n"
                f"{Fore.CYAN}Location:{Fore.RESET} {model.location}, {Fore.CYAN}Area:{Fore.RESET} {model.area}, {Fore.CYAN}Published on:{Fore.RESET} {model.publication_datetime}"
            )
            await self.db.commit()
        # if the post in the DB is outdated, update it
        elif model.publication_datetime > similar_post.publication_datetime:
            print(f"{Fore.BLUE}Updating existing post in the DB.{Fore.RESET}")
            for key, value in model.__dict__.items():
                if key != "_sa_instance_state" and value != getattr(similar_post, key):
                    print(
                        f"{Fore.CYAN}{key.upper()}: {Fore.YELLOW}Updated from {getattr(similar_post, key)} "
                        f"to {value}{Fore.RESET}"
                    )
                    setattr(similar_post, key, value)
            await self.db.commit()

        # if the post in the DB is newer than the parsing post, skip it
        else:
            print(
                f"{Fore.YELLOW}⚠️  Skipped outdated post.{Fore.RESET}\n"
                f"{Fore.CYAN}Location:{Fore.RESET} {model.location}, {Fore.CYAN}Area:{Fore.RESET} {model.area}, {Fore.CYAN}Published on:{Fore.RESET} {model.publication_datetime}"
            )

    async def update_db(self):
        """Fetches and updates database with posts from the Telegram chat."""
        latest_date_query = await self.db.execute(
            select(func.max(ParseModel.publication_datetime))
        )
        latest_date = latest_date_query.scalar() or (
            datetime.now() - timedelta(days=DAYS_TO_PARSE_IF_EMPTY)
        )
        image_list = []

        async with app:
            async for post in app.get_chat_history(TG_GROUP_NAME):
                post: Message
                if post.date <= latest_date:
                    print(
                        f"{Fore.GREEN}🔄💾 The database is up-to-date as of {latest_date}{Fore.RESET}"
                    )
                    break

                # add the last image to the image_list and parse the caption of the image
                if post.caption:
                    image_list.append(post.photo.file_id)
                    parsed_text = parse_text(post.caption, post.date)
                    if parsed_text:
                        model = self.text_to_model(
                            parsed_text,
                            post.caption_entities[0].url,
                            image_list,
                            post.date,
                        )
                        await self.insert_data(model)
                        # timeout to avoid flooding Telegram API with requests
                        await asyncio.sleep(0.07)
                    image_list = []

                # append the message to image_list if it's a photo
                elif post.photo:
                    image_list.append(post.photo.file_id)
