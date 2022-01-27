from collections import UserDict as _UserDict
from typing import TYPE_CHECKING, Any, Callable, KeysView, NewType

from jetpack import utils

Symbol = NewType("Symbol", str)


class DuplicateKeyError(LookupError):
    pass


# https://github.com/python/mypy/issues/5264
if TYPE_CHECKING:
    UserDict = _UserDict[Symbol, Callable[..., Any]]
else:
    UserDict = _UserDict


class _SymbolTable(UserDict):
    def register(self, func: Callable[..., Any]) -> Symbol:
        name = Symbol(utils.qualified_func_name(func))
        if name in self.data:
            raise DuplicateKeyError(f"Function name {name} is already registered")
        self.data[name] = func
        return name

    def defined_symbols(self) -> KeysView[Symbol]:
        return self.data.keys()


_symbol_table = _SymbolTable()


def get_symbol_table() -> _SymbolTable:
    return _symbol_table


def clear_symbol_table_for_test() -> None:
    _symbol_table.data = {}
