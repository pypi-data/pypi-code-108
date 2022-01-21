import datetime

from pydantic import BaseModel

from .size import Size


class Photo(BaseModel):
    id: int
    post_id: int = None

    user_id: int
    album_id: int
    owner_id: int

    date: datetime.datetime

    text: str

    sizes: list[Size]
