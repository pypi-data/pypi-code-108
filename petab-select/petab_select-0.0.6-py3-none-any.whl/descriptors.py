from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import numpy as np

# `float` for `np.inf`
TYPE_LIMIT = Union[float, int]


class LimitHandler():
    """A handler for classes that have a limit on an object attribute."""

    def __init__(
        self,
        reached: Callable[[object], bool],
        limit: TYPE_LIMIT = None,
        #limit: TYPE_LIMIT = None,
    ):
        self.reached = reached
        self.limit = limit
        #if upper_limit is None:
        #    self.set(np.inf)
        #else:
        #    self.set(upper_limit)

    @staticmethod
    def from_attribute(
        obj: Any,
        attribute: str,
        limit: TYPE_LIMIT,
    ) -> LimitHandler:
        """Create a limit handler based on an object attribute.

        Args:
            obj:
                The object with the attribute.
            attribute:
                The length of this attribute will be compared to the limit value to
                determine whether the limit is reached.
            limit:
                The (upper) limit of the attribute.

        Returns:
            The corresponding limit handler instance.
        """
        def reached(obj=obj, attribute=attribute, limit=limit):
            if len(getattr(obj, attribute)) >= limit:
                return True
            return False
        return LimitHandler(reached=reached, limit=limit)

    #def reached(self) -> bool:
    #    """Whether the limit has been reached."""
    #    if len(getattr(caller, self.attribute)) >= self.upper_limit:
    #        return True
    #    return False

    #def set(self, obj, limit: TYPE_LIMIT) -> None:
    #    """Set the limit.

    #    Args:
    #        limit:
    #            The new limit.
    #    """
    #    obj._limit = limit
    #    #if value is not None:
    #    #    obj._limit_upper = value
    #    #    #self.upper_limit = value
    #    if self.__get__(obj, type(obj)):
    #        warnings.warn(f'The limit ({obj._limit_upper}) for this class ({type(obj)}) attribute ({obj.limited_attribute}) has now been reached.')  # noqa: E501

    #def get(self) -> bool:
    #    """Get whether the limit has been reached.

    #    Returns:
    #        Whether the limit has been reached.
    #    """
    #    if obj._limit is None:
    #        return False
    #    if len(getattr(obj, obj.limited_attribute)) >= obj._limit:
    #        return True
    #    return False
