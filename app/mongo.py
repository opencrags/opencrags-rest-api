from pymongo import MongoClient

client = MongoClient('mongodb://mongo:27017/')
db = client.wire_annotations

__all__ = [
    "client",
    "db",
]
