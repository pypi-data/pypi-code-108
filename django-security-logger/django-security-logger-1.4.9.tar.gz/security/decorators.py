from functools import WRAPPER_ASSIGNMENTS, wraps

from .utils import get_throttling_validators
from .logging.common import SecurityLogger


def add_attribute_wrapper(name, value):

    def decorator(view_func):
        def _wrapper(*args, **kwargs):
            return view_func(*args, **kwargs)
        setattr(_wrapper, name, value)
        return wraps(view_func, assigned=WRAPPER_ASSIGNMENTS)(_wrapper)

    return decorator


def throttling(*validators, keep_default=True):
    """
    Adds throttling validators to a function.
    """

    throttling_validators = list(validators)
    if keep_default:
        throttling_validators += list(get_throttling_validators('default_validators'))
    return add_attribute_wrapper('throttling_validators', throttling_validators)


def throttling_all(*validators, keep_default=True):
    """
    Adds throttling validators to a class.
    """
    def decorator(klass):
        dispatch = getattr(klass, 'dispatch')
        setattr(klass, 'dispatch', throttling(*validators, keep_default=keep_default)(dispatch))
        return klass
    return decorator


def throttling_exempt():
    """
    Marks a function as being exempt from the throttling protection.
    """
    return add_attribute_wrapper('throttling_validators', ())


def throttling_exempt_all(klass):
    """
    Marks a class as being exempt from the throttling protection.
    """
    dispatch = getattr(klass, 'dispatch')
    setattr(klass, 'dispatch', throttling_exempt()(dispatch))
    return klass


def hide_request_body():
    """
    Marks a function as being exempt from storing request base to DB.
    """
    return add_attribute_wrapper('hide_request_body', True)


def hide_request_body_all(klass):
    """
    Marks a class as being exempt from storing request base to DB.
    """
    dispatch = getattr(klass, 'dispatch')
    setattr(klass, 'dispatch', hide_request_body()(dispatch))
    return klass


def log_exempt():
    """
    Marks a function as being exempt from whole log.
    """
    return add_attribute_wrapper('log_exempt', True)


def log_exempt_all(klass):
    """
    Marks a class as being exempt from whole log.
    """
    dispatch = getattr(klass, 'dispatch')
    setattr(klass, 'dispatch', log_exempt()(dispatch))
    return klass


def log_with_data(related_objects=None, slug=None, extra_data=None):
    return SecurityLogger(related_objects=related_objects, slug=slug, extra_data=extra_data)
