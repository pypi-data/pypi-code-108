from dataclasses import dataclass
from typing import Callable, Dict, Any, Type
import pickle

from ..dataset.dataset import Dataset
from ..model.model import Model


@dataclass
class Metric:
    name: str
    value: float


class Evaluator:
    def __init__(self, name: str, func: Callable, params: Dict[str, Any]):

        self.name = name
        self.func = func
        self.params = params

    def evaluate(self, model: Type[Model], dataset: Type[Dataset]) -> Metric:
        pass

    def dump(self) -> Dict[str, str]:
        data = {
            "func": pickle.dumps(self.func).decode("utf-8"),
            "params": pickle.dumps(self.params).decode("utf-8")
        }
        return {}
