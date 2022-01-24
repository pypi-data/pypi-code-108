from typing import Union, Tuple, Any, List, Type, Dict
from dataclasses import dataclass
from pathlib import Path
from collections import OrderedDict
from enum import Enum

from . import ModelFormat, ModelDataType
from ..common import get_class_name




@dataclass
class Tensor:
    name: str
    shape: Union[None, Tuple[int, ...]] = None
    dtype: Union[None, ModelDataType] = None

    def dump(self) -> Dict:
        data = {
            "name": self.name,
            "shape": self.shape,
        }

        data["type"] = self.dtype.name if isinstance(self.dtype,
                                                     ModelDataType) else None

        return data


class Model():
    def __init__(self, src: Union[str, Path, object]):
        self.src = src
        self.inputs: List[Tensor] = []
        self.outputs: List = []
        self.format: ModelFormat = ModelFormat.NON_SPECIFIED
        self._name: str

        if isinstance(src, str):
            self._name = Path(src).stem
        elif isinstance(src, Path):
            self._name = src.stem
        else:
            self._name = str(type(object))

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, _name: str):
        self._name = _name

    def add_input(self, input_: Tensor) -> None:
        self.inputs.append(input_)

    def add_output(self, output_: Tensor) -> None:
        self.outputs.append(output_)

    def clone_attributes(self, model: Any) -> None:
        """Clone user defined attributes from input

        Iter all user-defined attributes and check if they have values.
        If the attribute of the destination object has value, then skip
        the clone.

        Args:
            model (Type[Dataset]): The model object to be cloned
        """
        _to_be_cloned: List = []
        for attr_name in model.__dict__:

            dst_value = getattr(self, attr_name)
            src_value = getattr(model, attr_name)

            if (isinstance(dst_value, OrderedDict)) or (isinstance(dst_value,
                                                                   List)):
                if len(dst_value) == 0:
                    _to_be_cloned.append([attr_name, src_value])

            elif dst_value is None:
                _to_be_cloned.append([attr_name, src_value])

        for attr_name, src_value in _to_be_cloned:
            setattr(self, attr_name, src_value)

    def dump(self) -> Dict:


        data = {
            "src": "",
            "name": self.name,
            "inputs": {x.name: x.dump() for x in self.inputs},
            "outputs": {x.name: x.dump() for x in self.outputs},
            "format": self.format.name
        }
        if isinstance(self.src, str):
            data["src"] = self.src
        elif isinstance(self.src, Path):
            data["src"] = str(self.src)
        else:
            data["src"] = get_class_name(self.src)

        return data

    def load(self, obj: Dict):
        raise NotImplementedError()
