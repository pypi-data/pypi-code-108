from captur_ml_sdk.dtypes.generics import Image
from captur_ml_sdk.utils import get_image_components
from captur_ml_sdk.dtypes.exceptions import InvalidFilePathError
from captur_ml_sdk.dtypes.interfaces.validators import (
    check_model_exists,
    fetch_model_type,
    ensure_file_exists,
    check_images_or_imagesfile_is_included,
    enforce_mutual_exclusivity_between_images_and_imagesfile
)

from pydantic import (
    BaseModel, validator, root_validator, HttpUrl
)
from typing import Optional, List


class PredictMeta(BaseModel):
    webhooks: Optional[HttpUrl]


class Data(BaseModel):
    images: Optional[List[Image]] = None
    imagesfile: Optional[str] = None
    labelsfile: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    @ validator('imagesfile')
    def check_imagesfile_has_correct_components(cls, v):
        try:
            get_image_components(v, ".jsonl")
        except InvalidFilePathError as e:
            raise ValueError(str(e))
        return v

    _ensure_file_exists_imagesfile = validator(
        'imagesfile', allow_reuse=True)(ensure_file_exists)
    _ensure_file_exists_labelsfile = validator(
        'labelsfile', allow_reuse=True)(ensure_file_exists)

    _images_or_imagesfile_ = root_validator(
        check_images_or_imagesfile_is_included, allow_reuse=True)
    _mutual_exclusivity = root_validator(
        enforce_mutual_exclusivity_between_images_and_imagesfile, allow_reuse=True)


class Model(BaseModel):
    name: str
    version: Optional[str] = "HEAD"
    type: Optional[str]

    class Config:
        arbitrary_types_allowed = True

    _model_exists = root_validator(check_model_exists, allow_reuse=True)
    _get_model_type = root_validator(fetch_model_type, allow_reuse=True)


class ModelPredictRequest(BaseModel):
    meta: Optional[PredictMeta] = None
    models: List[Model]
    data: Data
