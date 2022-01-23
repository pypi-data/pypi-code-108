"""Decorator that ckecks the types of the arguments in the functions"""

from functools import wraps
from inspect import signature

class Contract:
    @classmethod
    def check(cls, value):
        pass

class Typed(Contract):
    type = None
    @classmethod
    def check(cls, value):
        assert (
            isinstance(value, cls.type),
            f'Expected {cls.type}'
        )

def type_check(function):
    sig = signature(function)
    ann = function.__annotations__
    @wraps(function)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            if name in ann:
                ann[name].check(val)
        return func(*args, **kwargs)
    return wrapper
