import psycopg2
from dotenv import load_dotenv
import pyrogram
import os
from pyrogram.types import Message

load_dotenv()

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


async def parse():
    await client.start()

    content = []
    try:
        async for message in client.get_chat_history(os.environ.get("GROUP_ID")):
            message: Message
            if "Локация" in str(message.caption):
                cur.execute(
                    """
    INSERT INTO parse_db (text, imgs, date)
    VALUES (%s, %s, %s);""",
                    (str(message.caption), content, message.date),
                )
                conn.commit()
                content = []
                print(message.date)
            else:
                content.append(str(message.photo.file_id))
    except AttributeError:
        cur.close()
        conn.close()

    await client.stop()


def start_parse():
    client.run(parse())
