from typing import Any, Dict
from abc import ABC, abstractmethod
import pickle

from .model import Model


class ModelTransformer():

    NAME = 'ModelTransformer'

    def __init__(self):
        self.params = {}

    def transform(self, model: Model) -> object:
        raise NotImplementedError("`transform` has to be implemented")

    def add_param(self, key: str, value: Any) -> None:
        self.params[key] = value

    def get_param(self, key: str) -> Any:
        return self.params[key]

    def dump(self) -> str:
        return pickle.dumps(self).decode("utf-8")
