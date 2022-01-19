from abc import ABCMeta, abstractmethod
from typing import Any, Dict, List, Tuple

from .reference import ReferenceFieldGenerator


class FieldGenerator(object, metaclass=ABCMeta):
    def __init__(self, options: Dict[str, str] = {}, type: str = None):
        super(FieldGenerator, self).__init__()
        self.options = options
        self.type = type
        self.validate()

    @abstractmethod
    def generate(self, schema_name: str, res: Dict, iter_res: Dict):
        raise NotImplementedError()

    def validate(self):
        pass

    def val_to_str(self, value: Any) -> str:
        return str(value)

    def prepare_options(self, schema_name: str = None, res: Dict[str, Tuple[Tuple, List[List]]] = {}, iter_res={}):
        options = self.options.copy()
        for (key, value) in options.items():
            if not isinstance(value, ReferenceFieldGenerator):
                continue

            schema = iter_res.get(value.type, res.get(value.type))
            if schema is None:
                raise Exception(
                    f"Cannot find schema: '{value.type}' in current result")

            entry = list(filter(
                lambda header: header[1][0] == value.options["field_attr"], enumerate(schema[0])))[0]

            options[key] = schema[1][-1][entry[0]]

        return options
