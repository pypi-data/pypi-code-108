from pydantic import Field
from typing import List
from decimal import Decimal

from .base import DynamoBaseModel, str_uuid


class LayerModel(DynamoBaseModel):
    layer_id: str = Field(default_factory=str_uuid)
    client: str
    product: str
    title: str
    region_id: int = 1
    unit: str = None
    background_id: str = None
    colormap: str = None
    description: str = None

    _pk_tag = "layer"
    _sk_tag = "layer"
    _sk_value = "layer_id"


class PermissionModel(DynamoBaseModel):
    permission: str
    layer_id: str

    _pk_tag = "permission"
    _pk_value = "permission"
    _sk_tag = "layer"
    _sk_value = "layer_id"


class LayerStepModel(DynamoBaseModel):
    layer_id: str
    cog_filepath: str
    datetime: str
    sensor: str
    resolution: Decimal
    temporal_resolution: str
    maxzoom: int
    minzoom: int
    bbox: List[Decimal]

    _pk_tag = "step"
    _pk_value = "datetime"
    _sk_tag = "layer"
    _sk_value = "layer_id"

    def s3_object_name(self, bucket_name):
        return self.cog_filepath.replace(f"s3://{bucket_name}/", "")


class ColorMap(DynamoBaseModel):
    name: str
    description: str = None
    levels: List[Decimal]
    colors: List[List[Decimal]]

    _pk_tag = "cm"
    _sk_tag = "cm"
    _sk_value = "name"
