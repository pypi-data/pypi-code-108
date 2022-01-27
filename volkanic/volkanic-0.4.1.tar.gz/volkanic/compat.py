#!/usr/bin/env python3
# coding: utf-8

import abc
import sys

try:
    from functools import cached_property
except ImportError:
    # noinspection PyPep8Naming
    class cached_property(object):
        """
        A property that is only computed once per instance and then replaces itself
        with an ordinary attribute. Deleting the attribute resets the property.
        Source:
            https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        Adapted from github:
            https://raw.githubusercontent.com/pydanny/cached-property/master/cached_property.py
        """

        def __init__(self, func):
            self.__doc__ = getattr(func, "__doc__")
            self.func = func

        def __get__(self, obj, cls):
            if obj is None:
                return self
            value = obj.__dict__[self.func.__name__] = self.func(obj)
            return value


def abstract_property(func):
    if sys.version_info > (3, 3):
        return property(abc.abstractmethod(func))
    else:
        return abc.abstractproperty(func)
