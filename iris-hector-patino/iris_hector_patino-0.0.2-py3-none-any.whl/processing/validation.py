from typing import List
from pydantic import BaseModel


class IrisInputSchema(BaseModel):
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float


class MultipleIrisInputSchema(BaseModel):
    inputs: List[IrisInputSchema]