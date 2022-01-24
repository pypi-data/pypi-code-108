from datetime import datetime

from pydantic import BaseModel


class Tag(BaseModel):
    id: str
    name: str
    created: datetime
