'''constructor.py

Module for constructing new mastapy objects. This is a workaround for cyclic
imports, where this module only references sys.modules and does not keep
local copies of modules.
'''


import sys
from typing import Type, TypeVar

from mastapy._internal.constructor_map import _get_mastapy_type


T = TypeVar('T')


def new(class_: Type[T]):
    '''Indirect object constructor. Fetches classes from sys.modules.

    Args:
        class_ (Type[T]): Class to instantiate
    '''

    module_path = class_.__module__
    class_name = class_.__name__
    return getattr(sys.modules[module_path], class_name)


def new_override(class_: Type[T]):
    '''Indirect object constructor using Python.NET type.
    Fetches classes from sys.modules.

    Args:
        class_ (Type[T]): Python.NET Class to wrap
    '''

    new_class = _get_mastapy_type(class_)
    return new(new_class)

