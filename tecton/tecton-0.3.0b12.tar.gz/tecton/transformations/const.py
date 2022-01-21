from typing import Optional
from typing import Union

from tecton._internals import errors


class Constant:
    ALLOWED_TYPES = [str, int, float, bool, type(None)]

    def __init__(self, value: Optional[Union[str, int, float, bool]]):
        self.value = value
        self.value_type = type(value)

        if self.value_type not in self.ALLOWED_TYPES:
            raise errors.InvalidConstantType(value, self.ALLOWED_TYPES)

    def __repr__(self):
        return f"Constant(value={self.value}, type={self.value_type})"


def const(value: Optional[Union[str, int, float, bool]]) -> Constant:
    """
    Wraps a const and returns a ``Constant`` object that can be used inside pipeline functions.

    :param value: The constant value that needs to be wrapped and used in the pipeline function.
    :return: A Constant object.
    """
    return Constant(value)
