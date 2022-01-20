from pydantic import (
    BaseModel,
    HttpUrl, root_validator
)

from typing import Optional, List

from captur_ml_sdk.dtypes.generics import Image
from captur_ml_sdk.dtypes.interfaces.validators import check_images_or_imagefile_has_data


class TrainPreRunEventData_MetaField(BaseModel):
    webhooks: Optional[HttpUrl]
    budget_milli_node_hours: int


class PreRunEventData(BaseModel):
    request_id: str
    meta: Optional[TrainPreRunEventData_MetaField]
    images: Optional[List[Image]]
    imagesfile: Optional[str]
    model_name: str
    base_model_id: str
    include_data: Optional[str]
    exclude_classes: Optional[List[str]]
    base_dataset_id: str

    root_validator(check_images_or_imagefile_has_data)
