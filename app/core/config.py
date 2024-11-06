from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = f"postgresql+asyncpg://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@localhost/televito"
TG_GROUP_NAME = os.environ.get("TG_GROUP_NAME")
TG_API_HASH = os.environ.get("TG_API_HASH")
TG_API_ID = os.environ.get("TG_API_ID")
SECRET_KEY = os.environ.get("SECRET_KEY")
MODEL = os.environ.get("MODEL")
