from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from functools import wraps
from importlib.util import find_spec

from typing import Any, Mapping, ParamSpec, TypeVar, Callable, Protocol, List


P = ParamSpec('P')
V = TypeVar('V')


__ALL__ = ['requires']


class DecoratedCallable(Protocol):
    __globals__: Mapping[str, Any]

    @abstractmethod
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V:
        pass


@dataclass
class ModuleInfo:
    name: str
    package: str | None
    pypi_name: str | None

    def __str__(self):
        return self.pypi_name or self.name


ModuleArg = str | ModuleInfo | Sequence[str] | Sequence[str, str | None] | Sequence[str, str | None, str | None]


def _parse_module_arg(arg: ModuleArg | Sequence[ModuleArg], package: str = None,
                      pypi_name: str = None) -> ModuleInfo:

    match arg:
        case module if isinstance(module, ModuleInfo):
            return module
        case module_name if isinstance(module_name, str):
            return ModuleInfo(module_name, package or None, pypi_name or None)
        case [module_name, package]:
            return ModuleInfo(module_name, package or None, None)
        case [module_name, package, pypi_name]:
            return ModuleInfo(module_name, package or None, pypi_name or None)
        case _:
            raise TypeError(f"{arg} is not a valid module argument: "
                            f"(module_name, package | None, pypi_name | None)")


def _parse_args(modules: Sequence[ModuleArg], package: str = None, pypi_name: str = None) -> List[ModuleInfo]:
    if pypi_name and len(modules) > 1:
        raise ValueError("pypi_name can't be specified as a *kwarg when modules is a sequence.")
    return [_parse_module_arg(module, package, pypi_name) for module in modules]


def _message_not_found(modules: List[ModuleInfo], caller_name) -> str:
    if len(modules) == 1:
        return f"{modules[0]} is not installed and is required by {caller_name}"
    else:
        modules_txt = ", ".join(str(m) for m in modules)
        return f"{caller_name} requires modules that are not installed: {modules_txt}"


def requires(*modules: ModuleArg, package: str = None, pypi_name: str = None, runtime_check=True
             ) -> Callable[[DecoratedCallable], DecoratedCallable]:

    modules = _parse_args(modules, package, pypi_name)

    def decorate(f: DecoratedCallable) -> DecoratedCallable:
        check = not all(m for m in modules if not find_spec(m.name, package=m.package))

        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> V:
            nonlocal check

            if not check:
                not_found = [m for m in modules if not f.__globals__.get(m.name, None)]
                if not_found:
                    error_msg = _message_not_found(not_found, f.__name__)
                    raise ModuleNotFoundError(error_msg)
            else:
                check = True

            return f(*args, **kwargs)

        return wrapper

    return decorate
