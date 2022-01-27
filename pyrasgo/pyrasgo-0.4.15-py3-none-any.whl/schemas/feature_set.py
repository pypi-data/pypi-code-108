from pydantic import BaseModel, Field
from typing import Any, List, Optional

from pyrasgo.schemas.attributes import Attribute
from pyrasgo.schemas.data_source import DataSource
from pyrasgo.schemas.enums import DataType
from pyrasgo.schemas.granularity import Granularity


# Schemas to be used for general pyrasgo
class Dimension(BaseModel):
    columnName: str
    dataType: DataType
    granularity: Optional[str]

class Feature(BaseModel):
    id: Optional[int]
    columnName: str
    dataType: DataType
    description: Optional[str]
    displayName: Optional[str]
    status: Optional[str]
    tags: Optional[List[str]]
    attributes: Optional[List[Attribute]]
    class Config:
        allow_population_by_field_name = True

class FeatureSet(BaseModel):
    id: Optional[int]
    name: Optional[str]
    sourceTable: str
    sourceCode: Optional[str]
    dimensions: Optional[List[Dimension]]
    features: Optional[List[Feature]]
    dataSource: Optional[DataSource]
    granularities: Optional[List[Granularity]]


class BasicFeatureSet(BaseModel):
    id: Optional[int]
    name: Optional[str]
    snowflakeTable: str = Field(alias='sourceTable')
    sourceCode: Optional[str]
    dataSourceId: Optional[int]
    class Config:
        allow_population_by_field_name = True


class FeatureSetCreate(BaseModel):
    name: str
    snowflakeTable: str
    dataSourceId: int
    rawFilePath: Optional[str]
    sourceCode: Optional[str]


class FeatureSetUpdate(BaseModel):
    id: Optional[int]
    name: Optional[str]
    sourceCode: Optional[str]


# Schema to be used for YML files
# TODO: sync with new schema when customers' legacy files are converted
class DimensionYML(BaseModel):
    columnName: str
    dataType: str
    granularity: str
    class Config:
        allow_population_by_field_name = True

class FeatureYML(BaseModel):
    columnName: str
    dataType: str
    description: Optional[str]
    displayName: Optional[str]
    tags: Optional[List[str]]
    class Config:
        allow_population_by_field_name = True

class DataSourceYML(BaseModel):
    name: Optional[str]

class FeatureSetYML(BaseModel):
    name: Optional[str] = ''
    sourceTable: str
    dimensions: Optional[List[DimensionYML]]
    features: Optional[List[FeatureYML]]
    dataSource: Optional[DataSourceYML]
    script: Optional[str] = ''
    sourceCode: Optional[str]
    class Config:
        allow_population_by_field_name = True