from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app import mongo

# Reuse for other items
class CreateVote(mongo.BaseBSONModel):
    public: bool = True


class Vote(CreateVote):
    created: datetime = Field(default_factory=datetime.utcnow)
    modified: datetime = Field(default_factory=datetime.utcnow)
    user_id: mongo.ObjectId
    public: bool = True


class MongoCragNameVote(mongo.Model):
    crag_id: mongo.ObjectId
    name: str
    vote: Vote


# POST /cragNameVotes
# POST /crags/{crag_id}/nameVotes
class CreateCragNameVote(mongo.BaseBSONModel):
    name: str
    vote: CreateVote


# GET /crags/{crag_id}/nameVotes/{crag_name_vote_id}
class CragNameVote(MongoCragNameVote):
    pass


class MongoCrag(mongo.Model):
    created: datetime = mongo.Field(default_factory=datetime.utcnow)
    user_id: mongo.ObjectId
    # polygon?


# Add non mongo classes for more correct documentation?
# POST /crags
class CreateCrag(mongo.BaseBSONModel):
    pass

# Nicer response model for viewing crags?
# GET /crags/{crag_id}
class Crag(mongo.BaseBSONModel):
    crag_id: mongo.ObjectId = Field(..., alias="id")
    created: datetime
    user_id: mongo.ObjectId
    crag_name_votes: List[CragNameVote]

