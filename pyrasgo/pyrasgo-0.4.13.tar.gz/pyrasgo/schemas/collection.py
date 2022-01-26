from pydantic import BaseModel, Field
from typing import Any, List, Optional

from pyrasgo.schemas.dw import SimpleTable
from pyrasgo.schemas.enums import ModelTypes
from pyrasgo.schemas.feature import Feature


class CollectionBase(BaseModel):
    id: int

class DimensionColumn(BaseModel):
    id: int
    name: str
    dataType: str
    granularity: Optional[Any]

class Collection(CollectionBase):
    name: Optional[str]
    authorId: Optional[int]
    dataTableName: Optional[str]
    type: Optional[ModelTypes] = None
    organizationId: Optional[int]
    dimensions: Optional[List[DimensionColumn]]
    features: Optional[List[Feature]]
    description: Optional[str]
    isShared: Optional[bool]
    dataTable: Optional[SimpleTable]

class CollectionUpdate(BaseModel):
    id: int
    name: Optional[str]