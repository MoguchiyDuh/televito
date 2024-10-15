import asyncio
from pyrogram import Client
from dotenv import load_dotenv
from datetime import datetime
from time import sleep
import psycopg2
import os
import schedule

load_dotenv()

db_config = {
    "user": os.environ.get("DB_USERNAME"),
    "password": os.environ.get("DB_PASSWORD"),
    "database": "televito",
    "host": "localhost",
    "port": 5432,
}

group_name = "belgraderent"

app = Client(
    "televito", api_id=os.environ.get("API_ID"), api_hash=os.environ.get("API_HASH")
)


def insert_data(conn, cursor, description: str, imgs: list[str], date: str):
    query = """
    INSERT INTO posts (description, imgs, date)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (description, imgs, date))
    conn.commit()


def parse_all_posts():

    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(date) FROM posts;")
    latest_date = cursor.fetchone()[0]

    imgs = []

    with app:
        for message in app.get_chat_history(group_name):
            if message.date < latest_date:
                cursor.close()
                conn.close()
                break

            if message.caption != None:
                print(message.date)
                insert_data(conn, cursor, message.caption, imgs, message.date)
                imgs = []
                sleep(0.1)
            elif message.photo != None:
                print(message.photo.file_id)
                imgs.append(message.photo.file_id)


schedule.every().day.at("12:00").do(parse_all_posts)


async def start_schedule():
    while True:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE date < NOW() - INTERVAL '1 year';")
        conn.commit()
        cursor.close()
        conn.close()
        schedule.run_pending()
        print("db updated")
        await asyncio.sleep(60 * 10)


asyncio.run(start_schedule())
