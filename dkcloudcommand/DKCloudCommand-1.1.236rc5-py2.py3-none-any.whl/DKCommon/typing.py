from types import TracebackType
from typing import Any, Dict, Type, TypeVar, Tuple


ExcInfo = Tuple[Type[Exception], Exception, TracebackType]

# Generic Type for use in various types
T = TypeVar("T")
"""Generic type."""

JSONData = Dict[str, Any]
"""Common dict structure for API calls."""
