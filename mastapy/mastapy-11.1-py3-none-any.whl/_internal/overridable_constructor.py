from typing import TypeVar, Optional, Tuple, Union


T = TypeVar('T')


def _unpack_overridable(v: Union[Tuple[T, bool], T]) -> Tuple[T, bool]:
    if hasattr(v, '__iter__'):

        if len(v) > 2:
            raise ValueError('Overridable tuple must be of length 2.')

        value, is_overridden = v
        is_overridden = bool(is_overridden)

        return value, is_overridden

    return v, True


def overridable(
        override_value: T,
        is_overridden: Optional[bool] = True) -> Tuple[T, bool]:
    ''' Helper method for creating overridable values. You can use this
    method to set whether an overridable property should use the overridden
    value or not.

    Alternatively, you can just pass a tuple to the overridable property.

    Args:
        override_value (T): value to override the property with
        is_overridden (bool, optional): whether the property should use
            the overridden value. Default is True.

    Returns:
        Tuple[T, bool]

    Examples:
        >>> my_gear_set.mass = overridable(100.0, False)
        >>> my_gear_set.mass = 100.0, False

    '''

    return override_value, is_overridden
