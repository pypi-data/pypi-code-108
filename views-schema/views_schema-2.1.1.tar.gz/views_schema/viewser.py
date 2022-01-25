
import enum
import datetime
from typing import List
import pydantic

class MessageType(enum.Enum):
    HINT    = 1
    MESSAGE = 2
    DUMP    = 3

class Message(pydantic.BaseModel):
    content:    str
    message_type: MessageType = MessageType.MESSAGE

class Dump(pydantic.BaseModel):
    title:     str
    timestamp: datetime.datetime
    username:  str = "anonymous"
    messages:    List[Message]
