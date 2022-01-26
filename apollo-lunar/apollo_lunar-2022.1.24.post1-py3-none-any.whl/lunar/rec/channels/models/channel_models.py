from typing import Optional
from pydantic import BaseModel


class ChannelBase(BaseModel):
    experiment_id: Optional[str] = None

    class Config:
        fields = {
            "id": {"title": "Unique identifier of a channel"},
            "experiment_id": {"title": "Unique identifier of an experiment assigned"},
        }


class Channel(ChannelBase):
    id: str


class ChannelPutIn(ChannelBase):
    pass


class ChannelPatchIn(ChannelBase):
    pass
