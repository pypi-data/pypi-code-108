from pydantic import BaseModel, AnyUrl
from .photo import Photo


class Link(BaseModel):
    url: AnyUrl

    title: str
    description: str

    photo: Photo = None
