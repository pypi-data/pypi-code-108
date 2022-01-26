# coding:utf-8
import base64
import csv
import functools
import inspect
import os
import platform
import signal
import subprocess
import sys
import time
import warnings
from functools import wraps
from pprint import pprint
from typing import Dict, List, Optional, Set, Tuple, Union

import smart_open
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from termcolor import colored

from .logger import Logger


def underline(text: str) -> str:
    '''Print underlined text in terminal.'''
    return f"\033[4m{text}\033[0m"


def b64decode(text_str: str) -> str:
    return base64.urlsafe_b64decode(text_str.encode()).decode()


def b64encode(text_str: str) -> str:
    return base64.urlsafe_b64encode(text_str.encode()).decode()


def uuid():
    import uuid
    return str(uuid.uuid4())


class _os():
    def platform(self) -> str:
        return platform.platform().lower()


# =========================================================== display
def p(*s):
    for i in s:
        print(i)


def pp(d: dict):
    pprint(d)


def sleep(countdown: int) -> None:
    time.sleep(countdown)


# =========================================================== IO
def show_func_name():
    p(f"\n--------------- {sys._getframe(1).f_code.co_name} ---------------")


def smartopen(file_path: str):
    with smart_open.open(file_path) as f:
        return f.readlines()


def syscall(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    except Exception as e:
        print('Error:', e)
        return ''


def shell(cmd: str,
          print_str: bool = False,
          surpress_error: bool = False,
          ignore_result: bool = False) -> str:

    if ignore_result:
        os.system(cmd)
        return

    ret_str = ''
    try:
        ret_str = subprocess.check_output(cmd,
                                          stderr=subprocess.DEVNULL,
                                          shell=True).decode('utf8').rstrip()
    except Exception as e:
        if not surpress_error:
            print(e)
    finally:
        if print_str:
            p(ret_str)
        return ret_str


class CSVIO:
    '''CSV manager'''
    @classmethod
    def read(cls, filename: str, delimiter: str = ',') -> List[List]:
        ''' read a CSV file and export it to a list '''
        with open(filename, newline='') as f:
            return [row for row in csv.reader(f, delimiter=delimiter)]

    @classmethod
    def iterator(cls, filename: str, delimiter: str = ',') -> csv.reader:
        return csv.reader(open(filename, 'r').readlines(),
                          delimiter=delimiter,
                          quoting=csv.QUOTE_MINIMAL)

    @classmethod
    def write(cls,
              texts: List,
              filename: str,
              delimiter: str = ',',
              column: int = 0) -> None:
        with open(filename, mode='w') as f:
            wt = csv.writer(f,
                            delimiter=delimiter,
                            quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
            for row in texts:
                if column > 0:
                    n_row = row[:column - 1]
                    n_row.append(' '.join(row[column - 1:]))
                    n_row = [e.strip() for e in n_row]
                    wt.writerow(n_row)
                else:
                    wt.writerow(row)


# =========================================================== Decorators
def set_timeout(countdown: int, callback=print):
    def decorator(func):
        def handle(signum, frame):
            raise RuntimeError

        def wrapper(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)
                signal.alarm(countdown)     # set countdown
                r = func(*args, **kwargs)
                signal.alarm(0)     # close alarm
                return r
            except RuntimeError as e:
                print(e)
                callback()

        return wrapper

    return decorator


def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


def logged(logger_func, name=None, message=None):
    """
    Add logging to a function. name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.
    """
    import logging

    def decorate(func):
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            logger_func(logmsg)
            return func(*args, **kwargs)

        return wrapper

    return decorate


def retry(total_tries=3, initial_wait=0.5, backoff_factor=2):
    """calling the decorated function applying an exponential backoff.
    Args:
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
    """
    logger = Logger()

    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while _tries > 0:
                try:
                    logger.info(
                        f'{f.__name__} {total_tries + 1 - _tries} try:')
                    return f(*args, **kwargs)
                except Exception as e:
                    _tries -= 1
                    print_args = args if args else 'no args'
                    if _tries == 0:
                        msg = "Fuction [{}] failed after {} tries. Args: [{}], kwargs [{}]".format(
                            f.__name__, total_tries, print_args, kwargs)
                        logger.info(msg)
                        raise
                    msg = "Function [{}] exception [{}]. Retrying in {} seconds. Args: [{}], kwargs: [{}]".format(
                        f.__name__, e, _delay, print_args, kwargs)
                    logger.info(msg)
                    time.sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries

    return retry_decorator


# -------------------------------------- End of decorators
def wrap_mod(mod, deprecated):
    """Return a wrapped object that warns about deprecated accesses"""
    deprecated = set(deprecated)

    class Wrapper(object):
        def __getattr__(self, attr):
            if attr in deprecated:
                previous_frame = inspect.currentframe().f_back
                Logger().info(str(previous_frame))
                warnings.warn(f"Alias {attr} is deprecated")
            return getattr(mod, attr)

        def __setattr__(self, attr, value):
            if attr in deprecated:
                warnings.warn("Property %s is deprecated" % attr)
            return setattr(mod, attr, value)

    return Wrapper()


def cipher(key: str, text: str) -> str:
    key = (key * 100)[:32]
    BLOCK_SIZE = 32
    _cipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
    msg = _cipher.encrypt(pad(text.encode(), BLOCK_SIZE))
    return str(msg, encoding='latin-1')


def decipher(key: str, msg: str) -> str:
    key = (key * 100)[:32]
    BLOCK_SIZE = 32
    _decipher = AES.new(key.encode('utf8'), AES.MODE_ECB)
    msg_dec = _decipher.decrypt(msg.encode('latin-1'))
    return unpad(msg_dec, BLOCK_SIZE).decode('utf8')


class deprecated:
    """Decorator to mark a function or class as deprecated.

    Issue a warning when the function is called/the class is instantiated and
    adds a warning to the docstring.

    The optional extra argument will be appended to the deprecation message
    and the docstring. Note: to use this with the default value for extra, put
    in an empty of parentheses:

    >>> from codefast.utils import deprecated
    >>> deprecated()

    >>> @deprecated()
    ... def some_function(): pass

    Parameters
    ----------
    extra : string
          to be added to the deprecation messages
    """

    # Adapted from https://wiki.python.org/moin/PythonDecoratorLibrary,
    # but with many changes.

    def __init__(self, extra=''):
        self.extra = extra

    def __call__(self, obj):
        """Call method

        Parameters
        ----------
        obj : object
        """
        if isinstance(obj, type):
            return self._decorate_class(obj)
        elif isinstance(obj, property):
            # Note that this is only triggered properly if the `property`
            # decorator comes before the `deprecated` decorator, like so:
            #
            # @deprecated(msg)
            # @property
            # def deprecated_attribute_(self):
            #     ...
            return self._decorate_property(obj)
        else:
            return self._decorate_fun(obj)

    def _decorate_class(self, cls):
        msg = "Class %s is deprecated" % cls.__name__
        if self.extra:
            msg += "; %s" % self.extra

        # FIXME: we should probably reset __new__ for full generality
        init = cls.__init__

        def wrapped(*args, **kwargs):
            warnings.warn(msg, category=FutureWarning)
            return init(*args, **kwargs)

        cls.__init__ = wrapped

        wrapped.__name__ = '__init__'
        wrapped.__doc__ = self._update_doc(init.__doc__)
        wrapped.deprecated_original = init

        return cls

    def _decorate_fun(self, fun):
        """Decorate function fun"""

        msg = "Function %s is deprecated" % fun.__name__
        if self.extra:
            msg += "; %s" % self.extra

        @functools.wraps(fun)
        def wrapped(*args, **kwargs):
            warnings.warn(msg, category=FutureWarning)
            return fun(*args, **kwargs)

        wrapped.__doc__ = self._update_doc(wrapped.__doc__)
        # Add a reference to the wrapped function so that we can introspect
        # on function arguments in Python 2 (already works in Python 3)
        wrapped.__wrapped__ = fun

        return wrapped

    def _decorate_property(self, prop):
        msg = self.extra

        @property
        def wrapped(*args, **kwargs):
            warnings.warn(msg, category=FutureWarning)
            return prop.fget(*args, **kwargs)

        return wrapped

    def _update_doc(self, olddoc):
        newdoc = "DEPRECATED"
        if self.extra:
            newdoc = "%s: %s" % (newdoc, self.extra)
        if olddoc:
            newdoc = "%s\n\n    %s" % (newdoc, olddoc)
        return newdoc
