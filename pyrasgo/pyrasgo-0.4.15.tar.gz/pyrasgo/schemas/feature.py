from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, TypeVar, Union

from pyrasgo.schemas.attributes import Attribute
from pyrasgo.schemas.data_source import DataSourceParent, DimensionColumn
from pyrasgo.schemas.granularity import Granularity

UnknownValue = TypeVar('UnknownValue', float, int, str, date, datetime)

class FeatureBase(BaseModel):
    id: int


class FeatureCreate(BaseModel):
    name: str
    code: str
    description: Optional[str]
    dataSourceColumnId: Optional[int]
    dataSourceId: int
    orchestrationStatus: Optional[str]
    tags: Optional[List[str]]
    gitRepo: Optional[str]

class FeatureUpdate(BaseModel):
    id: int
    name: Optional[str]
    code: Optional[str]
    description: Optional[str]
    gitRepo: Optional[str]
    orchestrationStatus: Optional[str]

class Feature(FeatureBase):
    id: int
    displayName: Optional[str]
    columnName: str
    dataType: Optional[str]
    description: Optional[str]
    dataSourceColumnId: Optional[int]
    dataSource: Optional[DataSourceParent]
    dimensions: Optional[List[DimensionColumn]]
    granularities: Optional[List[Granularity]]
    orchestrationStatus: Optional[str] = Field(alias="status")
    tags: Optional[List[str]]
    attributes: Optional[List[Attribute]]
    gitRepo: Optional[str]
    organizationId: Optional[int]
    class Config:
        allow_population_by_field_name = True

class Bucket(BaseModel):
    bucketCeiling: Optional[UnknownValue]
    bucketCeilingLabel: Optional[str]
    bucketFloor: Optional[UnknownValue]
    bucketFloorLabel: Optional[str]
    beginVal: Optional[UnknownValue]
    endVal: Optional[UnknownValue]
    height: Optional[UnknownValue]
    histBucket: Optional[Union[int, str]]
    outlierCt: Optional[UnknownValue]


class Value(BaseModel):
    freq: Optional[float]
    isOutlier: Optional[int]
    recCt: Optional[int]
    val: Optional[UnknownValue]


class FeatureStats(BaseModel):
    recCt: Optional[int]
    distinctCt: Optional[int]
    nullRecCt: Optional[int]
    zeroValRecCt: Optional[int]
    meanVal: Optional[str]
    medianVal: Optional[str]
    maxVal: Optional[str]
    minVal: Optional[str]
    sumVal: Optional[str]
    stdDevVal: Optional[str]
    varianceVal: Optional[str]
    rangeVal: Optional[str]
    skewVal: Optional[str]
    kurtosisVal: Optional[str]
    q1Val: Optional[str]
    q3Val: Optional[str]
    IQRVal: Optional[str]
    pct5Val: Optional[str]
    pct95Val: Optional[str]
    outlierCt: Optional[str]
    lowOutlier: Optional[str]
    highOutlier: Optional[str]


class ColumnStats(BaseModel):
    columnName: Optional[str]
    dataType: Optional[str]
    featureGranularity: Optional[str]
    featureId: Optional[str]
    featureName: Optional[str]
    featureStats: Optional[FeatureStats]
    histogram: Optional[List[Bucket]]
    commonValues: Optional[List[Value]]


class ColumnProfiles(BaseModel):
    columnProfiles: Optional[List[ColumnStats]]
    timestamp: str


class modelPerformance(BaseModel):
    R2: Optional[float]
    RMSE: Optional[float]
    AUC: Optional[float]
    Logloss: Optional[float]
    Precision: Optional[float]
    Recall: Optional[float]


class FeatureImportanceStats(BaseModel):
    targetFeature: str
    featureShapleyDistributions: dict
    featureImportance: Dict[str, UnknownValue]
    modelPerformance: modelPerformance
    timestamp: str
    modelId: Optional[int]
