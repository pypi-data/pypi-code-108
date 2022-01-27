import functools
import logging

def parametrized(decorator):
    @functools.wraps(decorator)
    def decorator_maker(*args, **kwargs):
        def decorator_wrapper(func):
            return decorator(func, *args, **kwargs)
        return decorator_wrapper
    return decorator_maker

@parametrized
def deprecated_without_replacement(func, version):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.warning(f"Function {func.__name__} will be deprecated in version {version}.")
        return func(*args, **kwargs)
    return wrapper

@parametrized
def deprecated_with_replacement(func, version, replacement):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.warning(f"Function {func.__name__} will be deprecated in version {version}, use {replacement} instead.")
        return func(*args, **kwargs)
    return wrapper
