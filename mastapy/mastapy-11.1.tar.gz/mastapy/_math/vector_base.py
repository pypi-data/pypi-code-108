'''vector_base.py'''


from typing import Tuple, List, Union, Iterable, Iterator, Callable, TypeVar
from abc import ABC, abstractmethod

from mastapy._math.scalar import NUM


ERROR_TUPLE = (KeyError, TypeError, AttributeError, IndexError)

ERROR_COMP_MESSAGE = (
    'Vectors must have equal number of '
    'dimensions for comparison.')
ERROR_SET_MESSAGE = (
    'Can only set a vector to a '
    'number or an iterable of numbers.')
ERROR_COMP_ELEM_MESSAGE = (
    'Can only compare a vector to a '
    'number or an iterable of numbers.')
ERROR_SET_ELEM_MESSAGE = (
    'Can only set elements of a vector to a '
    'number or an iterable of numbers.')
ERROR_SET_PROPERTY = (
    'Can not set individual components. Try setting the property '
    'directly instead.')


T = TypeVar('T')


def _safe_vector_op(message: str):
    def _safe_vector_op_wrapped(
            func: Callable[[], T], *args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ERROR_TUPLE:
            raise VectorException(message) from None
    return _safe_vector_op_wrapped


class VectorException(Exception):
    '''VectorException

    Exception raised for errors occurring in the Vector classes.
    '''


class VectorBase(ABC):
    '''VectorBase

    Abstract Base Class for all vector types.
    '''

    def __init__(self, values: List[float]):
        self._values = list(map(lambda x: 0.0 if x == -0.0 else x, values))

    def _iter_conv_comp(self, iterable: Iterable[NUM]) -> Tuple[NUM]:
        values = tuple(float(v) for v in iterable)
        if len(values) != len(self):
            raise VectorException(ERROR_COMP_MESSAGE) from None
        return values

    def _iter_conv_set(
            self, iterable: Iterable[NUM], length: int) -> Tuple[NUM]:
        values = tuple(float(v) for v in iterable)
        if len(values) != length:
            raise VectorException(ERROR_SET_MESSAGE) from None
        return values

    @classmethod
    @abstractmethod
    def broadcast(cls, value: NUM) -> 'VectorBase':
        pass

    @classmethod
    @abstractmethod
    def from_iterable(cls, t: Iterable[NUM]) -> 'VectorBase':
        pass

    @abstractmethod
    def __add__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __sub__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __mul__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __truediv__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __floordiv__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __abs__(self) -> 'VectorBase':
        pass

    @abstractmethod
    def __mod__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __pow__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __pos__(self, other) -> 'VectorBase':
        pass

    @abstractmethod
    def __neg__(self, other) -> 'VectorBase':
        pass

    def __len__(self) -> int:
        return len(self._values)

    def __contains__(self, value: object) -> bool:
        return value in self._values

    def __getitem__(self, index: Union[int, slice]) -> float:
        return self._values[index]

    def __setitem__(
            self,
            index: Union[int, slice],
            value: Union[NUM, Iterable[NUM]]):
        try:
            if hasattr(value, '__iter__'):
                self._values[index] = [float(x) for x in value]
            else:
                self._values[index] = float(value)
            if self.wrapped:
                raise VectorException(ERROR_SET_PROPERTY) from None
        except ValueError:
            raise VectorException(ERROR_SET_ELEM_MESSAGE) from None

    def __iter__(self) -> Iterator[float]:
        return iter(self._values)

    def __eq__(self, value: Union[NUM, Iterable[NUM]]) -> Tuple[bool]:
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_comp(value)
                return tuple(
                    map(lambda t: t[0] == t[1], zip(self._values, values)))
            else:
                value = float(value)
                return tuple(map(lambda x: x == value, self._values))
        except ValueError:
            raise VectorException(ERROR_COMP_MESSAGE) from None

    def __lt__(self, value: Union[NUM, Iterable[NUM]]) -> Tuple[bool]:
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_comp(value)
                return tuple(
                    map(lambda t: t[0] < t[1], zip(self._values, values)))
            else:
                value = float(value)
                return tuple(map(lambda x: x < value, self._values))
        except ValueError:
            raise VectorException(ERROR_COMP_MESSAGE) from None

    def __le__(self, value: Union[NUM, Iterable[NUM]]) -> Tuple[bool]:
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_comp(value)
                return tuple(
                    map(lambda t: t[0] <= t[1], zip(self._values, values)))
            else:
                value = float(value)
                return tuple(map(lambda x: x <= value, self._values))
        except ValueError:
            raise VectorException(ERROR_COMP_MESSAGE) from None

    def __gt__(self, value: Union[NUM, Iterable[NUM]]) -> Tuple[bool]:
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_comp(value)
                return tuple(
                    map(lambda t: t[0] > t[1], zip(self._values, values)))
            else:
                value = float(value)
                return tuple(map(lambda x: x > value, self._values))
        except ValueError:
            raise VectorException(ERROR_COMP_ELEM_MESSAGE) from None

    def __ge__(self, value: Union[NUM, Iterable[NUM]]) -> Tuple[bool]:
        try:
            if hasattr(value, '__iter__'):
                values = self._iter_conv_comp(value)
                return tuple(
                    map(lambda t: t[0] >= t[1], zip(self._values, values)))
            else:
                value = float(value)
                return tuple(map(lambda x: x >= value, self._values))
        except ValueError:
            raise VectorException(ERROR_COMP_ELEM_MESSAGE) from None

    def __not__(self) -> Tuple[bool]:
        return tuple(map(lambda x: not x, self._values))

    def __format__(self, format_spec: str) -> str:
        return '({})'.format(', '.join(
            map(lambda x: format(x, format_spec), self._values)))

    def __str__(self) -> str:
        return self.__format__('')

    def __repr__(self) -> str:
        return '{}({})'.format(
            self.__class__.__qualname__, ', '.join(
                (str(x) for x in self._values)))
