from typing import List
from pydantic import BaseModel


class BaseEventMessage(BaseModel):
    event: str
    time: float
    strategy_id: str

class BaseEventMessageArray(BaseModel):
    event: str
    time: float
    strategy_id: str
    exchange: str
    messages: List[BaseEventMessage]