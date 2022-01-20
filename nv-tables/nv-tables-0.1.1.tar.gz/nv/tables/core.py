from abc import abstractmethod
from functools import wraps
from importlib.util import find_spec
from pathlib import Path
from typing import Collection, Any, Mapping, Type, Tuple, ParamSpec, TypeVar, Callable, Iterator, Protocol

from .typing import DataTable, DataStructure, ParsedDataRow, ParsedDataTable, ParsedDataStructure


class Serializer:
    @abstractmethod
    def write_table(self, table: DataTable, fp: Path | str, headers: Collection[str] = None, default: Any = None,
                    **serializer_kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def append_table(self, table: DataTable, fp: Path | str, headers: Collection[str] = None, default: Any = None,
                     **serializer_kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def dump(self, structure: DataStructure, fp: Path | str, schema: Mapping[str, Collection[str]], default: Any = None,
             **serializer_kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def iter_table(self, fp: Path | str, constructor: Type = None, default: Any = None,
                   **parser_kwargs) -> Iterator[ParsedDataRow]:
        raise NotImplementedError

    @abstractmethod
    def iter_structure(self, fp: Path | str, constructor: Type = None, default: Any = None,
                       **parser_kwargs) -> Iterator[Tuple[str, ParsedDataRow]]:
        raise NotImplementedError

    @abstractmethod
    def read_table(self, fp: Path | str, constructor: Type = None, default: Any = None,
                   **parser_kwargs) -> ParsedDataTable:
        raise NotImplementedError

    @abstractmethod
    def load(self, fp: Path | str, constructor: Type = None, default: Any = None,
             **parser_kwargs) -> ParsedDataStructure:
        raise NotImplementedError

    @abstractmethod
    def read_headers(self, fp: Path | str, **parser_kwargs) -> Collection[str]:
        pass

    @abstractmethod
    def read_schema(self, fp: Path | str, **parser_kwargs) -> Mapping[str, Collection[str]]:
        pass


P = ParamSpec('P')
V = TypeVar('V')


class DecoratedCallable(Protocol):
    __globals__: Mapping[str, Any]

    @abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        pass


def requires(module_name: str, package: str = None, pypi_name: str = None
             ) -> Callable[[DecoratedCallable], DecoratedCallable]:
    """
    requires(module_name: str, package: str = None, pypi_name: str = None
             ) -> Callable[[Callable[[*P.args, *P.kwargs], V]], Callable[[*P.args, *P.kwargs], V]]:
    """

    def decorate(f: DecoratedCallable) -> DecoratedCallable:
        check = find_spec(module_name, package=package) is not None

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> V:
            nonlocal check

            if not check:
                if f.__globals__.get(module_name, None) is None:
                    raise ModuleNotFoundError(f"{pypi_name or module_name} required by {f.__name__ } is not installed")
                else:
                    check = True

            return f(*args, **kwargs)

        return wrapper

    return decorate
