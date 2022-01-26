from pydantic import BaseModel
from typing import Optional
from pyrasgo.schemas.organization import Organization


class Dimensionality(BaseModel):
    id: int
    name: Optional[str]
    organizationId: Optional[str]


class DimensionalityCreate(BaseModel):
    dimensionType: str
    granularity: str