""" utility.py

This module holds utility classes and methods to be used internally by mastapy.
These should not be accessed by package users.
"""


import os


class Setter:
    """ Setter

    Decorator class for setter-only properties. By using this instead of
    @property and @func.setter for setter-only properties, we remove some
    minor overheads.

    Args:
        func: the function to be decorated.
        doc (str, optional): documentation for the setter.


    Attributes:
        func: the decorated function.
    """

    def __init__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc if doc is not None else func.__doc__

    def __set__(self, obj, value):
        return self.func(obj, value)
