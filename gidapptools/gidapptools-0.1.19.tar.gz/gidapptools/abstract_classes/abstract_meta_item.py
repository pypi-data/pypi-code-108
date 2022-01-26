"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from abc import ABC, abstractmethod
from typing import Any, Callable
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.string_helper import StringCaseConverter

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractMetaItem(ABC):

    @classmethod
    @property
    def __default_configuration__(cls) -> dict[str, Any]:
        return {}

    @classmethod
    @property
    def name(cls) -> str:
        return StringCaseConverter.convert_to(cls.__name__, StringCaseConverter.SNAKE)

    @abstractmethod
    def as_dict(self, pretty: bool = False) -> dict[str, Any]:
        ...

    @abstractmethod
    def to_storager(self, storager: Callable = None) -> None:
        ...

    @abstractmethod
    def clean_up(self, **kwargs) -> None:
        ...


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
