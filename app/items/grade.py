from pydantic import BaseModel


class Grade(BaseModel):
    system: str
    grade: str
