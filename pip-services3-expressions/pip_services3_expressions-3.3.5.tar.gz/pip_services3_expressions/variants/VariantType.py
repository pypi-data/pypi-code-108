# -*- coding: utf-8 -*-

from enum import Enum, auto


class VariantType(Enum):
    """
    Defines supported types of variant values.
    """
    Null = 0,
    Integer = auto()
    Long = auto()
    Float = auto()
    Double = auto()
    String = auto()
    Boolean = auto()
    DateTime = auto()
    TimeSpan = auto()
    Object = auto()
    Array = auto()
