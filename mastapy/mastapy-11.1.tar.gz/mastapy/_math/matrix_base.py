'''matrix_base.py'''


from typing import List, Iterable, Union, Iterator, Tuple, Callable, TypeVar
from abc import ABC, abstractmethod

from mastapy._math.vector_base import VectorBase, VectorException
from mastapy._math.scalar import NUM


ERROR_TUPLE = (KeyError, TypeError, AttributeError, IndexError)
MATRIX_TYPE = Union[Iterable[NUM], Iterable[Iterable[NUM]]]
MATRIX_TYPE_OR_NUM = Union[NUM, Iterable[NUM], Iterable[Iterable[NUM]]]


def flatten(value: MATRIX_TYPE) -> Tuple[NUM]:
    try:
        return tuple(float(v) for i in value for v in i)
    except TypeError:
        try:
            return tuple(float(v) for v in value)
        except TypeError:
            raise MatrixException(
                'Failed to flatten matrix. Check dimensions.') from None


T = TypeVar('T')


def _safe_matrix_op(message: str):
    def _safe_matrix_op_wrapped(
            func: Callable[[], T], *args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ERROR_TUPLE:
            raise MatrixException(message) from None
    return _safe_matrix_op_wrapped


class MatrixException(VectorException):
    '''MatrixExcetion

    Exception raised for errors occurring in the Matrix classes.
    '''


class MatrixBase(ABC):
    '''MatrixBase

    Abstract Base Class for all matrix types.
    '''

    def __init__(self, values: List[float]):
        self._values = list(map(lambda x: 0.0 if x == -0.0 else x, values))

    @classmethod
    @abstractmethod
    def broadcast(cls, value: NUM) -> 'MatrixBase':
        pass

    @classmethod
    @abstractmethod
    def diagonal(cls, value: NUM) -> 'MatrixBase':
        pass

    @classmethod
    @abstractmethod
    def from_iterable(cls, t: Iterable[NUM]) -> 'MatrixBase':
        pass

    @classmethod
    @abstractmethod
    def identity(cls) -> 'MatrixBase':
        pass

    @abstractmethod
    def __add__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __sub__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __mul__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __matmul__(self, other) -> Union['MatrixBase', 'VectorBase']:
        pass

    @abstractmethod
    def __truediv__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __floordiv__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __abs__(self) -> 'MatrixBase':
        pass

    @abstractmethod
    def __mod__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __pow__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __pos__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __neg__(self, other) -> 'MatrixBase':
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    def __contains__(self, value: object) -> bool:
        return value in self._values

    @abstractmethod
    def __getitem__(self, index: Union[int, slice]) -> 'VectorBase':
        pass

    @abstractmethod
    def __setitem__(
            self,
            index: Union[int, slice],
            value: MATRIX_TYPE):
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[float]:
        pass

    @abstractmethod
    def __eq__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        pass

    @abstractmethod
    def __lt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        pass

    @abstractmethod
    def __le__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        pass

    @abstractmethod
    def __gt__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        pass

    @abstractmethod
    def __ge__(
            self,
            value: MATRIX_TYPE) -> Tuple[bool]:
        pass

    def __not__(self) -> Tuple[bool]:
        return tuple(map(lambda x: not x, self._values))

    @abstractmethod
    def __format__(self, format_spec) -> str:
        pass

    def __str__(self) -> str:
        return self.__format__('')

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def determinant(cls, value: MATRIX_TYPE) -> float:
        pass

    @classmethod
    @abstractmethod
    def inverse(cls, value: MATRIX_TYPE) -> 'MatrixBase':
        pass

    @classmethod
    @abstractmethod
    def transpose(cls, value: MATRIX_TYPE) -> 'MatrixBase':
        pass
