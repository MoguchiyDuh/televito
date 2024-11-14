import asyncio
from datetime import date, datetime, timedelta
from pyrogram import Client
from pyrogram.types.messages_and_media.message import Message
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from colorama import Fore

from .db.models import TGPostModel
from .core.config import TG_API_HASH, TG_API_ID, TG_GROUP_NAME
from .parser_re import parse_text

app = Client("televito", api_hash=TG_API_HASH, api_id=TG_API_ID)
DAYS_TO_PARSE = 6 * 90  # 6 months


class Parser:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def text_to_model(
        parsed_text: str,
        google_maps_url: str,
        images: list[str],
        post_datetime: datetime,
    ) -> TGPostModel:
        """Converts parsed text and metadata into a ParseModel object."""
        return TGPostModel(
            google_maps_url=google_maps_url,
            **parsed_text,
            images=images,
            publication_datetime=post_datetime,
        )

    async def insert_data(self, item: TGPostModel):
        """Inserts or updates a post in the database if needed."""
        result = await self.db.execute(
            select(TGPostModel).filter(
                TGPostModel.location == item.location,
                TGPostModel.area == item.area,
                TGPostModel.floor == item.floor,
                TGPostModel.floors_in_building == item.floors_in_building,
            )
        )

        similar_post = result.scalars().first()

        # if there is no similar post in the DB, add it to the DB
        if not similar_post:
            self.db.add(item)
            print(
                f"{Fore.GREEN}✓ NEW POST ADDED TO THE DB.{Fore.RESET}\n"
                f"{Fore.CYAN}Location:{Fore.RESET} {item.location}, {Fore.CYAN}Area:{Fore.RESET} {item.area}, {Fore.CYAN}Published on:{Fore.RESET} {item.publication_datetime}"
            )
            await self.db.commit()

        # if the post in the DB is outdated, update it
        elif item.publication_datetime > similar_post.publication_datetime:
            print(f"{Fore.BLUE}🔄 UPDATING EXISTING POST IN THE DB.{Fore.RESET}")
            for key, value in item.__dict__.items():
                if key != "_sa_instance_state" and value != getattr(similar_post, key):
                    print(
                        f"{Fore.CYAN}{key.upper()}: {Fore.YELLOW}Updated from{Fore.RESET} {getattr(similar_post, key)} {Fore.YELLOW}to{Fore.RESET} {value}"
                    )
                    setattr(similar_post, key, value)
            await self.db.commit()

        # if the post in the DB is newer than the parsing post, skip it
        else:
            print(
                f"{Fore.YELLOW}⚠️ SKIPPED OUTDATED POST.{Fore.RESET}\n"
                f"{Fore.CYAN}Location:{Fore.RESET} {item.location}, {Fore.CYAN}Area:{Fore.RESET} {item.area}, {Fore.CYAN}Published on:{Fore.RESET} {item.publication_datetime}"
            )

    async def delete_item(self, item: TGPostModel):
        """Deletes an item from the database."""
        print(
            f"{Fore.RED}🗑️ OUTDATED POST DELETED FROM THE DB{Fore.RESET}\n",
            f"{Fore.CYAN}Location:{Fore.RESET} {item.location}, {Fore.CYAN}Area:{Fore.RESET} {item.area}, {Fore.CYAN}Published on:{Fore.RESET} {item.publication_datetime}",
        )
        query = delete(TGPostModel).where(TGPostModel == item)
        await self.db.execute(query)
        await self.db.commit()

    async def update_db(self):
        """Fetches and updates database with posts from the Telegram chat."""
        latest_item_date = await self.db.execute(
            select(func.max(TGPostModel.publication_datetime))
        )
        latest_date = latest_item_date.scalar() or (
            datetime.now() - timedelta(days=DAYS_TO_PARSE)
        )
        cutoffdata = datetime.now() - timedelta(days=DAYS_TO_PARSE)

        outdated_items_query = select(TGPostModel).filter(
            TGPostModel.publication_datetime < cutoffdata
        )
        outdated_items = await self.db.execute(outdated_items_query)
        items_to_delete = outdated_items.scalars().all()

        for item in items_to_delete:
            await self.delete_item(item)

        image_list = []

        async with app:
            async for post in app.get_chat_history(TG_GROUP_NAME):
                post: Message
                if post.date <= latest_date:
                    print(
                        f"{Fore.GREEN}🔄💾 THE DATABASE IS UP-TO-DATE AS OF{Fore.RESET} {datetime.now()}"
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
