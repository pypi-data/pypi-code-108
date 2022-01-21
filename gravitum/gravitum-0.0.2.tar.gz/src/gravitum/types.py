from functools import wraps
from typing import Union

import numpy as np


class IntMeta(type):
    """
    Meta of type int.

    Type conversion is reprocessed relative to int of numpy.
    """

    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)

        methods = [
            '__neg__', '__pos__', '__invert__',
            '__add__', '__radd__', '__iadd__',
            '__sub__', '__rsub__', '__isub__',
            '__mul__', '__rmul__', '__imul__',
            '__truediv__', '__rtruediv__', '__itruediv__',
            '__floordiv__', '__rfloordiv__', '__ifloordiv__',
            '__mod__', '__rmod__', '__imod__',
            '__and__', '__rand__', '__iand__',
            '__or__', '__ror__', '__ior__',
            '__xor__', '__rxor__', '__ixor__',
            '__lshift__', '__rlshift__', '__ilshift__',
            '__rshift__', '__rrshift__', '__irshift__',
            '__eq__'
        ]

        for method in methods:
            if not hasattr(cls, method):
                continue
            setattr(cls, method, cls.operator_wrapper(getattr(cls, method)))

    @staticmethod
    def operator_wrapper(f):
        """
        Wrap operator method for type conversion.

        If it is a unary operator, ensure that the result is still
        the current type. If the operand is of type basic int, the type
        is converted to the current type. If the signed type of the operand
        is inconsistent with the current value, they will be converted to
        large data size or unsigned.

        :param f: Operator method.
        :return:
        """

        @wraps(f)
        def decorator(self, *args):
            data_type = type(self)
            if args:
                other = args[0]

                # cast type
                if isinstance(other, IntMeta):
                    if f.__name__ == '__eq__':
                        data_type = other
                        return data_type(self)

                # implicit conversion
                if isinstance(other, int):
                    other = data_type(other)
                elif isinstance(self, np.integer):
                    if isinstance(self, np.signedinteger) != \
                            isinstance(other, np.signedinteger):
                        if self.itemsize < other.itemsize:
                            data_type = type(other)
                        elif self.itemsize > other.itemsize:
                            data_type = type(self)
                        else:
                            data_type = type(other) \
                                if isinstance(self, np.signedinteger) \
                                else type(self)
                        operator = getattr(data_type, f.__name__)
                        return operator(data_type(self), data_type(other))

                return data_type(f(self, other))

            return data_type(f(self))

        return decorator


class Int8(np.int8, metaclass=IntMeta):
    """ Int8 """


class Int16(np.int16, metaclass=IntMeta):
    """ Int16 """


class Int32(np.int32, metaclass=IntMeta):
    """ Int32 """


class Int64(np.int64, metaclass=IntMeta):
    """ Int64 """


class Uint8(np.uint8, metaclass=IntMeta):
    """ Uint8 """


class Uint16(np.uint16, metaclass=IntMeta):
    """ Uint8 """


class Uint32(np.uint32, metaclass=IntMeta):
    """ Uint32 """


class Uint64(np.uint64, metaclass=IntMeta):
    """ Uint64 """


int8 = Int8
int16 = Int16
int32 = Int32
int64 = Int64

uint8 = Uint8
uint16 = Uint16
uint32 = Uint32
uint64 = Uint64

IntTypes = Union[
    int8, int16, int32, int64,
    uint8, uint16, uint32, uint64
]
