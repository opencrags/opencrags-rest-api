from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app import mongo


class Vote(BaseModel):
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    user_id: Optional[mongo.ObjectId] = None
    public: bool = True


class CragNameVote(mongo.Model):
    crag_id: Optional[mongo.ObjectId]
    name: str
    vote: Vote = dict()


class Crag(mongo.Model):
    created: Optional[datetime] = None
    user_id: Optional[mongo.ObjectId] = None
    # crag_name_votes: Optional[List[CragNameVote]] = None
    # polygon?
