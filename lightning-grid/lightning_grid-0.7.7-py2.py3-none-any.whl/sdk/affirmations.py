from typing import Callable
from functools import wraps


def affirm(*contracts: Callable):
    def decorator(func):
        for contract in contracts:
            # equivalent of doing @wraps(func)
            contract = wraps(func)(contract)
            func = contract(func)
        return func

    return decorator


def is_not_deleted(func):
    """Decorator which raises an exception at access time if the run has been deleted.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._is_deleted:
            raise RuntimeError('Cannot perform operation on deleted run') from None
        return func(self, *args, **kwargs)

    return wrapper


def is_created(func):
    """Decorator which raises an exception at access time if the run has already been created.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._is_created:
            raise RuntimeError('Invalid Operation: Allowed only after run is created') from None
        return func(self, *args, **kwargs)

    return wrapper


def is_not_created(func):
    """Decorator which raises an exception at access time if the run has not been created.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._is_created:
            raise RuntimeError('Invalid Operation: Allowed only before run is created') from None
        return func(self, *args, **kwargs)

    return wrapper


def is_not_shallow(func):
    """Decorator that un-shallow the function if it is shallow
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._is_shallow:
            self._unshallow()
        return func(self, *args, **kwargs)

    return wrapper
