import typing

try:
    from typing import final
except ImportError:
    from typing_extensions import final

__all__ = ["IdMixin"]


class IdMixin:
    """ A mixin for elements with an `id` attribute
    """
    __unset: typing.ClassVar = object()
    _id: str = __unset

    @final
    @property
    def id(self) -> typing.Optional[str]:
        """ The `id` attribute """
        assert self._id is not self.__unset, "Uninitialized attribute `id`"
        return self._id

    # noinspection PyShadowingBuiltins
    @id.setter
    def id(self, id: typing.Optional[str]):
        assert self._id is self.__unset, "Immutable attribute `id`"
        assert id is None or isinstance(id, str), "Invalid type for attribute `id`"
        self._id = id
