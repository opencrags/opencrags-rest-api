from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import List, Optional


class CreateVote(BaseModel):
    public: bool = True


class Vote(CreateVote):
    user_id: UUID
    created: datetime = Field(default_factory=datetime.utcnow)
    modified: datetime = Field(default_factory=datetime.utcnow)


class CreateCragNameVote(CreateVote):
    name: str


class CragNameVote(CreateCragNameVote, Vote):
    pass


class CreateCrag(BaseModel):
    name_votes: List[CreateCragNameVote]


class Crag(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created: datetime = Field(default_factory=datetime.utcnow)
    name_votes: List[CragNameVote]
