import psycopg2
from dotenv import load_dotenv
import pyrogram
import os
from pyrogram.types import Message
from datetime import datetime, timedelta

load_dotenv(dotenv_path="./backend/.env")

client = pyrogram.Client(
    name="televito",
    api_id=os.environ.get("API_ID"),
    api_hash=os.environ.get("API_HASH"),
)
conn = psycopg2.connect(
    dbname="postgres",
    user=os.environ.get("DB_USERNAME"),
    password=os.environ.get("DB_PASSWORD"),
    host="localhost",
    port="5432",
)
cur = conn.cursor()


async def parse(date_start, date_end):
    await client.start()

    imgs = []
    try:
        async for message in client.get_chat_history(
            os.environ.get("GROUP_ID"),
            offset_date=date_start,
        ):
            message: Message
            if message.date < date_end:
                cur.close()
                conn.close()
                break
            if "Локация" in str(message.caption):
                cur.execute(
                    """
    INSERT INTO parse_db (text, imgs, date)
    VALUES (%s, %s, %s);""",
                    (str(message.caption), imgs, message.date),
                )
                conn.commit()
                imgs = []
                print(message.date)
            else:
                imgs.append(str(message.photo.file_id))
    except AttributeError:
        cur.close()
        conn.close()

    await client.stop()


def start_parser(
    date_start=datetime.now(), date_end=datetime.now() - timedelta(weeks=1)
):
    client.run(parse(date_start, date_end))
