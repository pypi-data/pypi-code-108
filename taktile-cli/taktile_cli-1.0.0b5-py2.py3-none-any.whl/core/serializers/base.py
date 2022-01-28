import abc
from abc import ABC
from typing import Any, Type, Union

import pyarrow  # type: ignore
from pydantic import BaseModel


class ObjectSerializer(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def serialize(
        cls, value: Any, output_model: Type[BaseModel] = None
    ) -> Union[pyarrow.Table, BaseModel]:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, value: Any) -> Any:
        raise NotImplementedError


class CustomDeserializingModelT(ABC, BaseModel):
    def deserialize(self):
        ...
