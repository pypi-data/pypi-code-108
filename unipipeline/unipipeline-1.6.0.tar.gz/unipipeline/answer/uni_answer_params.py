from uuid import UUID

from pydantic import BaseModel


class UniAnswerParams(BaseModel):
    topic: str
    id: UUID

    class Config:
        frozen = True
        extra = 'forbid'
