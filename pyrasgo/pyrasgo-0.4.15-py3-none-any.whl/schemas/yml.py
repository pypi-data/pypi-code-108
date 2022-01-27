from pydantic import BaseModel
from typing import Any, List, Optional

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
    status: Optional[str]
    tags: Optional[List[str]]
    attributes: Optional[dict]
    class Config:
        allow_population_by_field_name = True

class FeaturesYML(BaseModel):
    name: Optional[str] = ''
    sourceTable: str
    dimensions: Optional[List[DimensionYML]]
    features: Optional[List[FeatureYML]]
    sourceCode: Optional[str]
    sourceType: Optional[str]
    class Config:
        allow_population_by_field_name = True