"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.meta_data.config_kwargs import ConfigKwargs
from gidapptools.abstract_classes.abstract_meta_item import AbstractMetaItem

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class AbstractMetaFactory(ABC):
    product_class: AbstractMetaItem = None
    default_configuration: dict[str, Any] = {}

    def __init__(self, config_kwargs: ConfigKwargs) -> None:
        if self.product_class is None:
            raise TypeError("Can't instantiate abstract class MetaInfoFactory with abstract class attribute 'product_class'")

        self.is_setup = False
        self.config_kwargs = config_kwargs

    @classmethod
    @property
    def __default_configuration__(cls) -> dict[str, Any]:

        return cls.default_configuration | cls.product_class.__default_configuration__

    @classmethod
    @property
    def product_name(cls) -> str:
        return cls.product_class.name

    @abstractmethod
    def setup(self) -> None:
        self.is_setup = True

    @abstractmethod
    def _build(self) -> AbstractMetaItem:
        ...

    @classmethod
    def build(cls, config_kwargs: ConfigKwargs) -> AbstractMetaItem:
        factory_instance = cls(config_kwargs=config_kwargs)
        instance = factory_instance._build()
        instance.to_storager(factory_instance.config_kwargs.get('storager'))
        factory_instance.config_kwargs.created_meta_items[factory_instance.product_name] = instance
        return instance


# region[Main_Exec]
if __name__ == '__main__':
    pass

# endregion[Main_Exec]
