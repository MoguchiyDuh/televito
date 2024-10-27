from dotenv import load_dotenv
import os

load_dotenv()

DB_USERNAME = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
TG_GROUP_NAME = os.environ.get("TG_GROUP_NAME")
TG_API_HASH = os.environ.get("TG_API_HASH")
TG_API_ID = os.environ.get("TG_API_ID")
SECRET_KEY = os.environ.get("SECRET_KEY")
