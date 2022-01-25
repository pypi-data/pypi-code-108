from typing import Type, FrozenSet

from .constants import ErrorMessages
from .extension import Extension
from .methods import Methods


class Extendable:
    def __init__(self):
        self._extension_data = {}  # Intended to temporarily hold metadata - can be modified by extensions

    @property
    def extensions(self) -> FrozenSet[Type[Extension]]:
        return self._extensions

    @property
    def extension_data(self) -> dict:
        """
        Returns a snapshot of the instance's extension data
        """

        return Methods.try_copy(self._extension_data)

    @classmethod
    def with_extensions(cls, *extensions: Type[Extension]) -> Type["Extendable"]:
        """
        Returns a copy of the class with the provided extensions applied to it
        """

        class Extended(cls):
            pass

        Extended._extensions = frozenset(extensions)

        for extension_cls in Extended._extensions:
            if not issubclass(extension_cls, Extension):
                ErrorMessages.not_extension(extension_cls)

            if not extension_cls.can_extend(cls):
                ErrorMessages.invalid_extension(extension_cls)

            extension_cls.extend(Extended)

        return Extended
