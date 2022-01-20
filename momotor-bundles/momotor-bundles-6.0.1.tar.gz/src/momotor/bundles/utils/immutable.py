from collections import OrderedDict
import typing


KT = typing.TypeVar("KT")
VT = typing.TypeVar("VT")


class ImmutableOrderedDict(typing.Generic[KT, VT], typing.Mapping[KT, VT], OrderedDict):
    """ An immutable :py:class:`~collections.OrderedDict` """
    def __init__(self, *args, **kwargs):
        self.__init = True
        super().__init__(*args, **kwargs)
        self.__init = False

    def __setitem__(self, key: KT, value: VT):
        if not self.__init:
            raise TypeError("immutable")
        OrderedDict.__setitem__(self, key, value)

    def __delitem__(self, key: KT, *args, **kwargs) -> typing.NoReturn:
        raise TypeError("immutable")

    def clear(self) -> typing.NoReturn:
        raise TypeError("immutable")

    def popitem(self, last=True) -> typing.NoReturn:
        raise TypeError("immutable")

    def update(self, *args, **kwargs) -> typing.NoReturn:
        raise TypeError("immutable")

    def pop(self, key: KT) -> typing.NoReturn:
        raise TypeError("immutable")

    def setdefault(self, key: KT, default=None) -> typing.NoReturn:
        raise TypeError("immutable")


class ImmutableDict(typing.Generic[KT, VT], typing.Mapping[KT, VT], dict):
    """ An immutable :py:class:`dict` """
    def __init__(self, *args, **kwargs):
        self.__init = True
        super().__init__(*args, **kwargs)
        self.__init = False

    def __setitem__(self, key: KT, value: VT):
        if not self.__init:
            raise TypeError("immutable")
        dict.__setitem__(self, key, value)

    def __delitem__(self, key: KT) -> typing.NoReturn:
        raise TypeError("immutable")

    def clear(self) -> typing.NoReturn:
        raise TypeError("immutable")

    def popitem(self, last=True) -> typing.NoReturn:
        raise TypeError("immutable")

    def update(self, *args, **kwargs) -> typing.NoReturn:
        raise TypeError("immutable")

    def pop(self, key: KT) -> typing.NoReturn:
        raise TypeError("immutable")

    def setdefault(self, key: KT, default=None) -> typing.NoReturn:
        raise TypeError("immutable")

    def move_to_end(self, key: KT, last=None) -> typing.NoReturn:
        raise TypeError("immutable")
