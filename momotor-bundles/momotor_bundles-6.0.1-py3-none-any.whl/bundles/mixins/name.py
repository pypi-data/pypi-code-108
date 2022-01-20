import typing
from pathlib import PurePath, PurePosixPath

__all__ = ["NameStrMixin", "NamePathMixin"]


NTS = typing.TypeVar("NTS")  # setter type
NTG = typing.TypeVar("NTG")  # getter type


class NameMixin(typing.Generic[NTS, NTG]):
    """ Abstract base class for name mixin. See `NameStrMixin` and `NamePathMixin`
    """
    __unset: typing.ClassVar = object()
    _name: typing.Optional[NTG] = __unset

    @property
    def name(self) -> typing.Optional[NTG]:
        """ The `name` attribute """
        assert self._name is not self.__unset, "Uninitialized attribute `name`"
        return self._name

    # noinspection PyShadowingBuiltins
    @name.setter
    def name(self, name: typing.Optional[NTS]):
        assert self._name is self.__unset, "Immutable attribute `name`"
        self._name = self._convert_name(name) if name is not None else None

    @staticmethod
    def _convert_name(name: NTS) -> NTG:
        raise NotImplementedError


class NameStrMixin(NameMixin[str, str]):
    """ A mixin for elements with a `name` attribute of type `str`
    """
    @staticmethod
    def _convert_name(name: str) -> str:
        assert isinstance(name, str), "Invalid type for attribute `name`"
        return name


class NamePathMixin(NameMixin[typing.Union[str, PurePath], PurePosixPath]):
    """ A mixin for elements with a `name` attribute of types `str` or `PurePath`.
    The getter will always return a `PurePosixPath`
    """
    @staticmethod
    def _convert_name(name: typing.Union[str, PurePath]) -> PurePosixPath:
        if isinstance(name, str):
            name = PurePath(name)

        assert isinstance(name, PurePath), "Invalid type for attribute `name`"
        return typing.cast(
            PurePosixPath,
            name.as_posix() if hasattr(name, 'as_posix') else name
        )
