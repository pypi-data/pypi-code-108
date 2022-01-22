# -*- coding: utf-8 -*-
"""Proxy class that forwards __special__ methods too.
"""
# pylint:disable=R0903


class proxy(object):
    "Proxy class that forwards __special__ methods too."
    __slots__ = ['_value']

    def __init__(self, obj):
        self._value = obj

    ####################################################################
    # attribute control

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            setattr(self._value, name, value)

    #
    ####################################################################

    def __repr__(self):
        return 'proxy(%s)' % repr(self._value)

    def __str__(self):
        return str(self._value)

    def __len__(self):
        return len(self._value)

    def __index__(self):
        return self._value

    def __iter__(self):
        return iter(self._value)

    def __oct__(self):
        return oct(self._value)

    def __hex__(self):
        return hex(self._value)

    def __pos__(self):
        return +self._value

    def __hash__(self):
        return self._value.__hash__()

    def __nonzero__(self):
        return self._value.__nonzero__()

    def __call__(self, *args, **kwargs):
        return self._value(*args, **kwargs)

    ####################################################################
    # comparators

    def __lt__(self, other):
        return self._value < other

    def __le__(self, other):
        return self._value <= other

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __ge__(self, other):
        return self._value >= other

    def __gt__(self, other):
        return self._value > other

    ####################################################################
    # logical

    def __and__(self, other):
        return self._value and other

    def __bool__(self):
        return bool(self._value)

    ####################################################################
    # numerical

    def __add__(self, other):
        return self._value + other

    def __radd__(self, other):
        return other + self._value

    def __iadd__(self, other):
        self._value += other
        return self

    def __abs__(self):
        return abs(self._value)

    def __div__(self, other):
        return self._value / other

    def __idiv__(self, other):
        self._value /= other
        return self

    def __rdiv__(self, other):
        return other / self._value

    def __truediv__(self, other):
        return self._value / other

    def __rtruediv__(self, other):
        return other / self._value

    def __floordiv__(self, other):
        return self._value // other

    def __rfloordiv__(self, other):
        return other // self._value

    def __mul__(self, other):
        return self._value * other

    def __imul__(self, other):
        self._value *= other
        return self

    def __rmul__(self, other):
        return other * self._value

    def __sub__(self, other):
        return self._value - other

    def __isub__(self, other):
        self._value -= other
        return self

    def __rsub__(self, other):
        return other - self._value

    ####################################################################
    # binary

    def __inv__(self):
        return ~self._value

    def __lshift__(self, other):
        return self._value << other

    def __rlshift__(self, other):
        return other << self._value

    def __mod__(self, other):
        return self._value % other

    def __neg__(self):
        return -self._value

    def __or__(self, other):
        return self._value or other

    def __pow__(self, other):
        return self._value ** other

    def __rpow__(self, other):
        return other ** self._value

    def __rshift__(self, other):
        return self._value >> other

    def __xor__(self, other):
        return self._value ^ other

    def __contains__(self, other):
        return other in self._value

    def __delitem__(self, other):
        del self._value[other]

    def __getitem__(self, other):
        return self._value[other]

    def __repeat__(self, other):
        return self._value * other

    def __setitem__(self, other, v):
        self._value[other] = v
