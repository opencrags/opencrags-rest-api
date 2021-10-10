from pymongo import MongoClient

from app.config import config


client = MongoClient(config.database_url)
db = client.opencrags

__all__ = [
    "client",
    "db",
]
