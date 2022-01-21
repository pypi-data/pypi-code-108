from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Extra


class HeaderMeta(BaseModel):
    class Config:
        extra = Extra.allow

    _ts: int
    _ser: int


class FactHeader(BaseModel):
    class Config:
        extra = Extra.allow

    id: UUID
    ns: str
    aggIds: Optional[List[UUID]] = None
    type: Optional[str] = None
    meta: Optional[HeaderMeta] = None


class FactPayload(BaseModel):
    class Config:
        extra = Extra.allow


class FactOut(BaseModel):
    header: FactHeader
    payload: FactPayload
