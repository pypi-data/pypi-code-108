from typing import Optional
from pydantic import BaseModel
from pyrasgo.schemas.dimensionality import Dimensionality


class ColumnCreate(BaseModel):
    name: str
    dataType: str
    featureSetId: int
    dimensionId: Optional[int]


class ColumnUpdate(BaseModel):
    id: int
    name: Optional[str]
    dataType: Optional[str]
    featureSetId: Optional[int]
    dimensionId: Optional[int]


class Column(BaseModel):
    id: Optional[int]
    name: Optional[str]
    dataType: Optional[str]
    featureSetId: Optional[int]
    dimensionId: Optional[int]
    granularity: Optional[str]