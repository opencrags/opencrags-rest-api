import struct
import pydantic
from bson.objectid import ObjectId as OriginalObjectId
from pymongo import MongoClient


client = MongoClient("mongodb://mongo:27017")
db = client.opencrags


# https://github.com/tiangolo/fastapi/issues/1515
class ObjectId(OriginalObjectId):
    # fix for FastApi/docs
    __origin__ = pydantic.typing.Literal
    __args__ = (str, )

    @property
    def timestamp(self):
        timestamp = struct.unpack(">I", self.binary[0:4])[0]
        return timestamp

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, OriginalObjectId):
            raise ValueError("Not a valid ObjectId")
        return v

# fix ObjectId & FastApi conflict
pydantic.json.ENCODERS_BY_TYPE[OriginalObjectId]=str
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str
