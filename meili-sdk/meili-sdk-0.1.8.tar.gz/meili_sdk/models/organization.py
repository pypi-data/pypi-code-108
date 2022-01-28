import typing as t

from meili_sdk.models.base import BaseModel


class Organization(BaseModel):
    uuid: t.Optional[str] = None
    title: str
    slug: t.Optional[str] = None
    default_email: t.Optional[str] = None
