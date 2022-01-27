from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from pyrasgo.schemas.attributes import Attribute
from pyrasgo.schemas.dw import SimpleTable
from pyrasgo.schemas.granularity import Granularity

class DataSourceBase(BaseModel):
    id: int


class DataSourceColumn(BaseModel):
    id: int
    name: str
    dataType: str


class DimensionColumn(BaseModel):
    id: int
    columnName: str
    displayName: Optional[str]
    dataType: Optional[str]
    description: Optional[str]
    granularity: Optional[Granularity]
    dataSourceColumnId: Optional[int]


class FeatureColumn(BaseModel):
    id: int
    columnName: str
    displayName: Optional[str]
    dataType: Optional[str]
    status: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    attributes: Optional[List[Attribute]]
    gitRepo: Optional[str]
    dataSourceColumnId: Optional[int]
    collectionCount: Optional[int]


class DataSourceParent(DataSourceBase):
    id: int
    name: str
    table: Optional[str]
    tableDatabase: Optional[str]
    tableSchema: Optional[str]
    sourceType: Optional[str]
    domain: Optional[str]
    authorId: Optional[int]
    dataTable: Optional[SimpleTable]


class DataSource(DataSourceBase):
    id: int
    name: str
    table: Optional[str]
    tableDatabase: Optional[str]
    tableSchema: Optional[str]
    sourceCode: Optional[str]
    sourceType: Optional[str]
    domain: Optional[str]
    authorId: Optional[int]
    organizationId: int
    parentId: Optional[int]
    parentSource: Optional[DataSourceParent]
    columns: Optional[List[DataSourceColumn]]
    dimensions: Optional[List[DimensionColumn]]
    features: Optional[List[FeatureColumn]]
    dataTable: Optional[SimpleTable]


class DataSourceCreate(BaseModel):
    name: str
    table: Optional[str]
    tableDatabase: Optional[str]
    tableSchema: Optional[str]
    sourceCode: Optional[str]
    sourceType: Optional[str]
    domain: Optional[str]
    tableStatus: Optional[str]
    parentId: Optional[int]


class DataSourceUpdate(BaseModel):
    name: Optional[str]
    table: Optional[str]
    tableDatabase: Optional[str]
    tableSchema: Optional[str]
    sourceCode: Optional[str]
    sourceType: Optional[str]
    domain: Optional[str]
    tableStatus: Optional[str]
    parentId: Optional[int]


class DataSourceColumnPut(BaseModel):
    name: str
    dataType: str


class DimensionColumnPut(BaseModel):
    dataSourceColumnId: Optional[int]
    columnName: str
    displayName: Optional[str]
    description: Optional[str]
    granularityName: str
    dimensionType: Optional[str]


class FeatureColumnPut(BaseModel):
    dataSourceColumnId: Optional[int]
    columnName: str
    displayName: Optional[str]
    description: Optional[str]
    status: Optional[str]
    tags: Optional[List[str]]
    attributes: Optional[List[Attribute]]


class DataSourcePut(BaseModel):
    name: str
    table: str
    tableDatabase: Optional[str]
    tableSchema: Optional[str]
    sourceType: str
    domain: Optional[str]
    parentId: Optional[int]
    sourceCode: Optional[str]
    columns: List[DataSourceColumnPut]
    features: Optional[List[FeatureColumnPut]]
    dimensions: Optional[List[DimensionColumnPut]]
    organizationId: int