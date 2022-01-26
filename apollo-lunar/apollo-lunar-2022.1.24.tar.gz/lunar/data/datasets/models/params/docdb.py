from pydantic import BaseModel


class DocDBParams(BaseModel):
    collection: str

    class Config:
        fields = {"collection": {"title": "Name of a DocDB collection"}}
