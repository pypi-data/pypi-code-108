from captur_ml_sdk.dtypes.generics import Image

from pydantic import (
    BaseModel, HttpUrl
)
from typing import Optional


class LivePredictMeta(BaseModel):
    webhooks: Optional[HttpUrl]


class Model(BaseModel):
    endpoint: str
    type: str = "classification"

    class Config:
        arbitrary_types_allowed = True


class ModelLivePredictRequest(BaseModel):
    meta: Optional[LivePredictMeta] = None
    model: Model
    data: Image
