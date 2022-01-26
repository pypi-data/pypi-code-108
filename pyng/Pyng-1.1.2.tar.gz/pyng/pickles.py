#!/usr/bin/python
"""\
@file   pickles.py
@author Nat Goodspeed
@date   2020-04-28
@brief  Utilities helpful for [un]pickling
"""

class PickleableProxy(object):
    """
    Evidently unpickling tests for some method by trying to access it and
    catching AttributeError. But since unpickling creates an empty object with
    no data attributes, bypassing the constructor, when pickle tries to access
    that method, our proxy-object __getattr__() would try to access
    self._target, which is *not yet defined*, so recursively calls
    __getattr__() again... Before introducing this class, we were blowing up
    with infinite recursion on unpickling.

    This class by itself, initialized with (a reference to) some other object,
    should behave pretty much exactly like that other object. The point is to
    derive a subclass, whose methods will intercept any calls to the
    corresponding methods on the target object. Your subclass override method
    can forward calls to the original target object by calling
    self._target.method().
    """
    # Define the initial _target as a class attribute so that, on unpickling,
    # getattr() will find the class attribute even before the instance
    # attribute is reloaded. Therefore self._target.whatever will raise
    # AttributeError instead of recursively calling __getattr__().
    _target = None

    def __init__(self, target):
        self._target = target

    def __getattr__(self, attr):
        """
        When our consumer references any attribute not specifically
        overridden, return the corresponding one from our target object.
        """
        return getattr(self._target, attr)
