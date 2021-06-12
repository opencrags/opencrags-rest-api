import os
from pymongo import MongoClient

client = MongoClient(os.environ["DB"])
db = client.opencrags

__all__ = [
    "client",
    "db",
]
