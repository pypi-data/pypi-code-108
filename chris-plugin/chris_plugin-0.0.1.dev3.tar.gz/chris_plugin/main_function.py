"""
Helpers for inspecting the main function of a ChRIS plugin.
"""

from pathlib import Path
from argparse import Namespace
from typing import Union, Callable, TypeGuard
import inspect
from inspect import Signature, Parameter

FsMainFunction = Callable[[Namespace, Path], None]
DsMainFunction = Callable[[Namespace, Path, Path], None]
MainFunction = Union[FsMainFunction, DsMainFunction]


def get_function_params(_s: Signature) -> tuple[type, ...]:
    return tuple(p.annotation for p in _s.parameters.values())


def is_type_or_unspecified(e: type, t: type) -> bool:
    return t is e or t is Parameter.empty


def is_plugin_main(_f: Callable) -> TypeGuard[MainFunction]:
    s = inspect.signature(_f)
    params = get_function_params(s)
    if len(params) == 0 or not is_type_or_unspecified(Namespace, params[0]):
        raise ValueError("A ChRIS plugin's main function must accept "
                         "its options as its first argument")
    if len(params) < 2:
        raise ValueError("A ChRIS plugin's main function must accept "
                         "an argument for its output directory")
    if len(params) > 3:
        raise ValueError("A ChRIS plugin's main function cannot "
                         'take more than 3 arguments')
    if not all(map(lambda p: is_type_or_unspecified(Path, p), params[1:])):
        raise ValueError("A ChRIS plugin's data directory arguments "
                         "must have type pathlib.Path")
    if s.return_annotation is not None and s.return_annotation is not Signature.empty:
        raise ValueError("A ChRIS plugin's main function must be void")
    return True


def count_path_parameters(_f: MainFunction):
    return len(inspect.signature(_f).parameters) - 1


def is_fs(_f: MainFunction) -> TypeGuard[FsMainFunction]:
    return count_path_parameters(_f) == 1


def is_ds(_f: MainFunction) -> TypeGuard[DsMainFunction]:
    return count_path_parameters(_f) == 2
