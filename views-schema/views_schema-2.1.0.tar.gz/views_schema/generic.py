"""
views_schema.generic
====================

Generic type classes.

"""

from typing import TypeVar, List, Generic
from pydantic import BaseModel

T = TypeVar("T")

class ListView(BaseModel, Generic[T]):
    data: List[T]
