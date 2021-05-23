import struct
import pydantic
from odmantic import AIOEngine, Model, EmbeddedModel, ObjectId, Field
from odmantic.bson import BaseBSONModel
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://mongo:27017/")
engine = AIOEngine(motor_client=client, database="opencrags")
