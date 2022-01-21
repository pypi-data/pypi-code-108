"""NanamiLang Data Types Package"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import List

from .base import Base
from .boolean import Boolean
from .date import Date
from .floatnumber import FloatNumber
from .function import Function
from .hashmap import HashMap
from .integernumber import IntegerNumber
from .keyword import Keyword
from .macro import Macro
from .nil import Nil
from .hashset import HashSet
from .string import String
from .undefined import Undefined
from .vector import Vector
from .nexception import NException
from .collection import Collection
from .numeric import Numeric
from .callable import Callable
from .symbol import Symbol


class DataType:
    """NanamiLang DataType class"""

    Base: dict = {'name': Base.name, 'class': Base}
    Nil: dict = {'name': Nil.name, 'class': Nil}
    Boolean: dict = {'name': Boolean.name, 'class': Boolean}
    String: dict = {'name': String.name, 'class': String}
    Date: dict = {'name': Date.name, 'class': Date}
    FloatNumber: dict = {'name': FloatNumber.name, 'class': FloatNumber}
    IntegerNumber: dict = {'name': IntegerNumber.name, 'class': IntegerNumber}
    Keyword: dict = {'name': Keyword.name, 'class': Keyword}
    HashSet: dict = {'name': HashSet.name, 'class': HashSet}
    Vector: dict = {'name': Vector.name, 'class': Vector}
    HashMap: dict = {'name': HashMap.name, 'class': HashMap}
    NException: dict = {'name': NException.name, 'class': NException}
    Undefined: dict = {'name': Undefined.name, 'class': Undefined}
    Macro: dict = {'name': Macro.name, 'class': Macro}
    Function: dict = {'name': Function.name, 'class': Function}
    Symbol: dict = {'name': Symbol.name, 'class': Symbol}
    Collection: dict = {'name': Collection.name, 'class': Collection}
    Numeric: dict = {'name': Numeric.name, 'class': Numeric}
    Callable: dict = {'name': Callable.name, 'class': Callable}

    complex: List[str] = [HashSet.get('name'),
                          Vector.get('name'),
                          HashMap.get('name')]
    simple: List[str] = [Nil.get('name'), Boolean.get('name'),
                         String.get('name'), Date.get('name'),
                         FloatNumber.get('name'),
                         IntegerNumber.get('name'),
                         Keyword.get('name'),
                         NException.get('name'),
                         Undefined.get('name'), Macro.get('name'),
                         Function.get('name'), Symbol.get('name')]

    @staticmethod
    def resolve(data_type_class_name: str):
        """NanamiLang DataType, resolve which class was actually requested"""

        return DataType.__dict__.get(data_type_class_name, None).get('class', None)
