"""
These closures are intended to be used as a ``Mock`` object's ``side_effect``, allowing a mocked function's
return value to be specified at the same time as the expected arguments. This is a very concise way of doing
things for simple uses where the mocked function is only ever called once (or with one set of arguments) and
can also be used to raise an ``Exception`` at the actual offending call site when there is an argument mismatch,
leading to easy debugging.

>>> from unittest.mock import Mock
>>> mymock = Mock()
>>> mymock.side_effect = assert_args_and_return("two eggs", "two bottles", yards=50)
>>> mymock('two bottles', yards=50)
'two eggs'
>>> mymock('two bottles', metres=50)
Traceback (most recent call last):
    ...
AssertionError

>>> class EggBottleException(Exception):
...     pass

>>> mymock.side_effect = assert_args_and_raise(EggBottleException, "two bottles", yards=50)
>>> mymock('two bottles', yards=50)
Traceback (most recent call last):
    ...
mocking.EggBottleException
>>> mymock('two bottles', metres=50)
Traceback (most recent call last):
    ...
AssertionError

>>> mymock.side_effect = assert_args_and_return_or_raise("two eggs", EggBottleException, "two bottles", yards=50)
>>> mymock('two bottles', yards=50)
'two eggs'
>>> mymock('two bottles', metres=50)
Traceback (most recent call last):
    ...
mocking.EggBottleException
"""
from typing import Callable, Iterable


def assert_args_and_return(retval, *args, **kwargs) -> Callable:
    """
    Given a return value and an arbitrary set of arguments, returns a callable which will return ``retval`` when called
    with arguments matching those specified here, otherwise will raise an ``AssertionError``.
    """
    def _inner(*inner_args, **inner_kwargs):
        assert args == inner_args
        assert kwargs == inner_kwargs
        return retval
    return _inner


def assert_args_and_raise(e: Exception, *args, **kwargs) -> Callable:
    """
    Given a return value and an arbitrary set of arguments, returns a callable which will raise the ``Exception`` ``e``
    when called with arguments matching those specified here.
    """
    def _inner(*inner_args, **inner_kwargs):
        assert args == inner_args
        assert kwargs == inner_kwargs
        raise e
    return _inner


def assert_args_and_return_or_raise(retval, e, *args, **kwargs) -> Callable:
    """
    Given a return value and an arbitrary set of arguments, returns a callable which will return ``retval`` when called
    with arguments matching those specified here, otherwise will raise the exception ``e``.
    """
    def _inner(*inner_args, **inner_kwargs):
        if args == inner_args and kwargs == inner_kwargs:
            return retval
        else:
            raise e
    return _inner


def assert_args_and_return_iter_over(retval: Iterable, *args, **kwargs) -> Callable:
    """
    Given an iterable return value and an arbitrary set of arguments, returns a callable which will return
    a fresh iterator over ``retval`` when called with arguments matching those specified here, otherwise will raise
    an ``AssertionError``.
    """
    def _inner(*inner_args, **inner_kwargs):
        assert args == inner_args
        assert kwargs == inner_kwargs
        return iter(retval)
    return _inner
