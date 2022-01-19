from __future__ import annotations

from copy import deepcopy
from functools import cached_property
from typing import Any, Dict

from ..common import IS_DICT
from ..parsing import Parser as AbstractParser


class Parser(AbstractParser):
    """
    Parser initializes itself by parsing the provided argument at initialization.

    During parsing, it will treat the value as a Dictionary and parse the property
    under a key same as the class name.

    The exact action for handling parsed value should be in `_do_parse`.

    Standardization of data format should be specified in `_init_simplifications`.
    """

    declaration: Any
    definition: Any

    @cached_property
    def name(self) -> str:
        return self.__class__.__name__.lower()

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def verify(cls, value: Any) -> None:
        """
        Validate whether a value is appropriate for parsing.

        Should return nothing but throw exception for illegal input format.
        """
        return

    def __init__(self, value: Any) -> None:
        self.declaration = deepcopy(value)
        super().__init__()
        self.definition = self.parse(value)
        self._init_from_parsed(self.definition)

    def _init_from_parsed(self, parsed: Dict[str, Any]) -> None:
        for name, value in parsed.items():
            setattr(self, name, value)

    def parse(self, value: Any) -> Dict[str, Any]:
        if IS_DICT(value):
            value = value.get(self.name, value)
            return super().parse(value)
        else:
            raise TypeError(f"Expect {value} to be a Dictionary")
