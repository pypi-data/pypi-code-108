__all__ = [
    'DBModelError',
    'PrimaryKeyError',
    'NullValueError',
    'EnumValueError',
    'FieldDefaultValueError',
    'DBModelWarning',
    'ArrayLengthWarning'
]


class DBModelError(Exception):
    ...


class PrimaryKeyError(DBModelError):
    ...


class NullValueError(DBModelError):
    ...


class EnumValueError(DBModelError):
    ...


class FieldDefaultValueError(DBModelError):
    ...


class DBModelWarning(RuntimeWarning):
    ...


class ArrayLengthWarning(DBModelWarning):
    ...
