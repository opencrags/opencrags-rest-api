from pymongo import MongoClient

client = MongoClient('mongodb://mongo:27017/')
db = client.opencrags

__all__ = [
    "client",
    "db",
]
