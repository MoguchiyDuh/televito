from time import sleep
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from pyrogram import Client

from .core.config import *
from .db.models import ParserModel

app = Client("televito", api_hash=TG_API_HASH, api_id=TG_API_ID)

db_url = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@localhost/televito"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
CD_TIME = 0.07


def insert_data(session, description: str, imgs: list[str], post_date: datetime):
    post = ParserModel(description=description, imgs=imgs, datetime=post_date)
    session.add(post)
    try:
        session.commit()
        print("commited:", post_date)
    except IntegrityError:
        session.rollback()  # Rollback in case of error
        print("Error inserting data.")


def parse_all_posts(session):
    # Get the latest date from the database
    latest_date = session.query(func.max(ParserModel.datetime)).scalar()
    if not latest_date:
        latest_date = datetime.now() - timedelta(days=365)

    imgs = []

    with app:
        for message in app.get_chat_history(TG_GROUP_NAME):
            if message.date <= latest_date:
                print("message date < latest date")
                break

            if message.caption is not None:
                insert_data(session, message.caption, imgs, message.date)
                imgs = []
                sleep(CD_TIME)
            elif message.photo is not None:
                imgs.append(message.photo.file_id)


def start_parser():
    session = Session()

    # Remove records older than 1 year
    session.query(ParserModel).filter(
        ParserModel.datetime < datetime.now() - timedelta(days=365)
    ).delete()
    session.commit()

    parse_all_posts(session)

    session.close()
    print("Database updated")
