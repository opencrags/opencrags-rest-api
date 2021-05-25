from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from typing import List, Optional


# Reuse for other items
class CreateVote(BaseModel):
    public: bool = True


class Vote(CreateVote):
    vote_id: UUID = Field(default_factory=uuid4, alias="id")
    created: datetime = Field(default_factory=datetime.utcnow)
    modified: datetime = Field(default_factory=datetime.utcnow)
    user_id: UUID


# POST /cragNameVotes
# POST /crags/{crag_id}/nameVotes
class CreateCragNameVote(CreateVote):
    name: str


# GET /crags/{crag_id}/nameVotes/{crag_name_vote_id}
class CragNameVote(CreateCragNameVote, Vote):
    pass


# Add non mongo classes for more correct documentation?
# POST /crags
class CreateCrag(BaseModel):
    crag_name_votes: List[CreateCragNameVote]

# Nicer response model for viewing crags?
# GET /crags/{crag_id}
class Crag(BaseModel):
    crag_id: UUID = Field(default_factory=uuid4, alias="id")
    created: datetime = Field(default_factory=datetime.utcnow)
    user_id: UUID
    crag_name_votes: List[CragNameVote]
