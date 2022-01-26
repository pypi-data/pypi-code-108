import typing as t

from meili_sdk.models.base import BaseModel

__all__ = ("RosTopic",)


class RosTopic(BaseModel):
    uuid: str
    topic: str
    message_type: str
    frequency: t.Optional[int] = 1
