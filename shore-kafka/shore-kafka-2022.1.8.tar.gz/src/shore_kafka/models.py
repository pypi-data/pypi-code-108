from pydantic import BaseModel

################################################################
# FakeMessageModel
################################################################
class Message(BaseModel):
    topic: str
    partition: int = 0
    offset: int = None
    key: str = None
    value: str = None
    headers: list = None
    timestamp: int = 0
