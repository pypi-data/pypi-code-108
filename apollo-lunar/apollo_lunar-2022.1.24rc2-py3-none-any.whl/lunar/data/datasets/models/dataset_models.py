from typing import Generic, TypeVar

from pydantic import validator
from pydantic.generics import GenericModel

from lunar.data.datasets.models.params import PARAMS

T = TypeVar("T")


class DatasetBase(GenericModel, Generic[T]):
    data_type: str
    params: T

    class Config:
        fields = {
            "id": {"title": "Unique identifier of a dataset"},
            "data_type": {"title": "Dataset type"},
            "params": {"title": "Dataset parameters"},
        }

    @validator("data_type")
    def check_data_types(cls, data_type):
        if data_type not in PARAMS:
            raise ValueError(f"'data_type' {data_type} is not supported.")
        return data_type


class Dataset(DatasetBase, Generic[T]):
    id: str


class DatasetPutIn(DatasetBase, Generic[T]):
    pass


class DatasetPatchIn(DatasetBase, Generic[T]):
    pass
