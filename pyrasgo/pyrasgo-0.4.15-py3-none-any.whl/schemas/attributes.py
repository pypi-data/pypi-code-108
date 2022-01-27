from pydantic import BaseModel, Field
from typing import List

class Attribute(BaseModel):
    key: str
    value: str

class FeatureAttributes(BaseModel):
    featureId: int
    attributes: dict

class FeatureAttributesLog(BaseModel):
    featureId: int
    attributes: List[dict]

class FeatureAttributeBulkCreate(BaseModel):
    featureId: int
    attributes: List[Attribute]

class CollectionAttributes(BaseModel):
    modelId: int = Field(alias='collectionId')
    attributes: dict

class CollectionAttributesLog(BaseModel):
    modelId: int = Field(alias='collectionId')
    attributes: List[dict]

class CollectionAttributeBulkCreate(BaseModel):
    modelId: int = Field(alias='collectionId')
    attributes: List[Attribute]