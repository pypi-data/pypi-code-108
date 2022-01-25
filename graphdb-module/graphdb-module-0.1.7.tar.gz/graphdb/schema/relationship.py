from pydantic import BaseModel


class Relationship(BaseModel):
    relationship_name: str
