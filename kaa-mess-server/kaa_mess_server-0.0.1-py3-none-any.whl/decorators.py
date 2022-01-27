import sys
import inspect
from functools import wraps
from logging import getLogger

from logs import client_logger_config, server_logger_config


if sys.argv[0].find('server.py') == -1:
    LOG = getLogger('client_logger')
else:
    LOG = getLogger('server_logger')


def log_decorator(_function):
    '''Decorator for  logging classes and methods of the project'''

    @wraps(_function)
    def decorator(*args, **kwargs):
        result = _function(*args, **kwargs)
        stack = inspect.stack()[1][3]
        LOG.info(f'Called function "{_function.__name__}" '
                 f'from function "{stack}"')
        LOG.info(f'Function "{_function.__name__}" from module '
                 f'"{_function.__module__}" with arguments ({args}, {kwargs})')
        return result
    return decorator

