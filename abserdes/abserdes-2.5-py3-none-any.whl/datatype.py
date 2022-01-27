from __future__ import annotations
from collections.abc import Iterable
import re
import numpy
from typing import Union, TypeVar, NamedTuple, Sequence, Deque, Optional, List, Type, Dict, Any
from types import ModuleType

def is_instance(
        data: Any,
        ) -> bool:
    if hasattr(data, '__dict__'):
        if hasattr(data, '__module__'):
            return True

def is_namedtuple(
        data: Any,
        ) -> bool:
    typ = type(data)
    bases = typ.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(typ, '_fields', None)
    if not isinstance(fields, tuple):
        return False
    return all(type(ele) == str for ele in fields)

def is_dict(
        data: Any,
        ) -> bool:
    if isinstance(data, dict):
        return True 

def is_list(
        data: Any,
        ) -> bool:
    if isinstance(data, list):
        return True 

def is_ndarray(
        data: Any,
        ) -> bool:
    if isinstance(data, numpy.ndarray):
        return True 

def is_tuple(
        data: Any,
        ) -> bool:
    if isinstance(data, tuple):
        return True 

def data_type(
        data: Any,
        ) -> str: 
    if is_instance(data):
        return 'instance'
    elif is_namedtuple(data):
        return 'namedtuple'
    elif is_dict(data):
        return 'dict'
    elif is_list(data):
        return 'list'
    elif is_tuple(data):
        return 'tuple'
    elif is_ndarray(data):
        return 'ndarray'


