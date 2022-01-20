"""Miscellaneous (catch all) tools Copyright 2020 Caliber Data Labs."""

#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import hashlib
import json
import os
import platform
import re
import time
import uuid
import requests
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Callable, Dict, Iterable, Optional
from tqdm import tqdm as tqdm_base

from ..custom_exceptions import ResponseError
from ..constants import MAX_THREADS


def decorate_all_inherited_methods(decorator):
    """Add a decorator to all methods which are not private.

    Usage:
        @decorate_all_inherited_methods(decorator)
        class C(object):
            def m1(self): pass
            def m2(self, x): pass
    ...
    """

    def decorate(cls):
        for attr in dir(cls):
            # Only callable methods and those that don't start with _ are
            # eligible
            if callable(getattr(cls, attr)) and not attr.startswith("_"):
                # Only inherited or overrided methods are eligible
                if attr not in cls.__dict__ or hasattr(super(cls), attr):
                    setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate


def chunk_list(list_elements, chunk_size):
    """Chunks a list into chunk_size chunks, with last chunk the remaining
    elements.

    :param list_elements:
    :param chunk_size:
    :return:
    """
    chunks = []
    while True:
        if len(list_elements) > chunk_size:
            chunk = list_elements[0:chunk_size]
            list_elements = list_elements[chunk_size:]
            chunks.append(chunk)
        else:
            chunks.append(list_elements)
            break
    return chunks


def as_bool(s):
    if s is None:
        return False

    if isinstance(s, bool):
        return s
    else:
        s = str(s)  # In Python 2, handle case when s is unicode
        if s.lower() in {"t", "true"}:
            return True
        elif s.lower() in {"f", "false"}:
            return False
        else:
            raise ValueError(
                "Input of type ::: {} cannot be converted to bool ::: {}".format(
                    type(s), s))


def get_truncated_uid(n: int = 5):
    return get_guid()[0:n]


def get_guid():
    return str(uuid.uuid4()).replace('-', '_')


def get_md5_from_file(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def is_valid_hex(color: str) -> bool:

    if re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color):
        return True
    else:
        return False


def hex2rgb(hex: str) -> (int, int, int):
    hex = hex.lstrip('#')
    return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(r: int, g: int, b: int) -> str:
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def rgb2gray(rgb: tuple) -> int:
    r, g, b = rgb
    return min(round(0.2989 * r + 0.5870 * g + 0.1140 * b), 255)


def get_md5_from_string(string):
    m = hashlib.md5()
    m.update(string.encode("utf-8"))
    return m.hexdigest()


def hash_string_into_positive_integer(string) -> int:
    """return a signed 64-bit."""
    return abs((hash(string) + 2**63) % 2**64 - 2**63)


def hash_string_into_positive_integer_reproducible(string) -> int:
    """return a signed 64-bit."""
    return abs((int(string, 16) + 2**63) % 2**64 - 2**63)


def get_md5_from_json_object(json_object: Dict):
    """get the md5 from a json object (dic, list, etc). We take care of sorting
    the keys here for repeatability.

    :param json_object: list, dic, etc
    :return: md5 of the object
    """
    return get_md5_from_string(json.dumps(json_object, sort_keys=True))


def parse_file_path(input_str: str) \
        -> (str, str, str, str):
    cleaned_str = input_str.replace("\\", "/")
    filename = cleaned_str.split("/")[-1]
    extension = filename.split(".")[-1]
    filename_no_extension = filename.replace("." + extension, "")
    path = cleaned_str.replace(filename, "")
    return filename, path, filename_no_extension, extension


def flatten_json(y: dict, seperator="_") -> dict:
    out = {}

    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + seperator)
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + seperator)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def retry(
        exceptions,
        total_tries=4,
        initial_wait=0.5,
        backoff_factor=2,
        logger=None):
    """calling the decorated function applying an exponential backoff.

    Args:
        exceptions: Exception(s) that trigger a retry, can be a tuple
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
        logger: logger to be used, if none specified print
    """
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            retry_flag = kwargs.get("retry", False)
            if retry_flag:
                _tries, _delay = total_tries + 1, initial_wait
                while _tries > 1:
                    try:
                        return f(*args, **kwargs)
                    except exceptions as e:
                        logger.info(f'{total_tries + 2 - _tries}. try:')
                        _tries -= 1
                        print_args = args if args else 'no args'
                        if _tries == 1:
                            msg = str(
                                f'Function: {f.__name__}\n'
                                f'Failed despite best efforts after {total_tries} tries.\n'
                                f'args: {print_args}, kwargs: {kwargs}')
                            logger.info(msg)
                            raise
                        msg = str(
                            f'Function: {f.__name__}\n'
                            f'Exception: {e}\n'
                            f'Retrying in {_delay} seconds!, args: {print_args}, kwargs: {kwargs}\n')
                        logger.info(msg)
                        time.sleep(_delay)
                        _delay *= backoff_factor
            else:
                return f(*args, **kwargs)
        return func_with_retries
    return retry_decorator


@retry(exceptions=(Exception, ResponseError), initial_wait=10, backoff_factor=2)
def requests_with_retry(url, payload, headers, type="post"):
    if type == "post":
        resp = requests.post(url,
                             data=payload,
                             headers=headers)
    elif type == "put":
        resp = requests.put(url,
                            data=payload,
                            headers=headers)
    else:
        raise NotImplementedError

    if not resp.ok:
        raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
    else:
        return resp

class tqdm(tqdm_base):
    def __init__(self,
                 progress_callback: Optional[Callable] = None,
                 **kwargs):
        self.progress_callback = progress_callback
        super(tqdm, self).__init__(**kwargs)

    def update(self, n=1):
        super(tqdm, self).update(n)
        if self.total and self.progress_callback:
            progress = float(100.0 * self.n/self.total)
            self.progress_callback(progress)


def run_threaded(func: Callable,
                 iterable: Iterable,
                 num_threads: int = MAX_THREADS,
                 disable_threading: bool = False,
                 disable_tqdm: bool = False,
                 expand_iterable: bool = False,
                 desc: Optional[str] = None,
                 second_iterable: Optional[Iterable] = None,
                 progress_callback: Optional[Callable] = None,
                 **kwargs):
    def _func(_it, _second_it=None):
        if _second_it:
            func(_it, _second_it, **kwargs)
        else:
            func(*_it, **kwargs) if expand_iterable else func(_it, **kwargs)

    if disable_threading is False:
        if second_iterable is None:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                list(
                    tqdm(
                        progress_callback=progress_callback,
                        iterable=executor.map(
                            _func,
                            iterable),
                        total=len(
                            list(iterable)),
                        desc=desc,
                        disable=disable_tqdm))
        else:
            assert len(list(iterable)) == len(list(second_iterable))
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                list(
                    tqdm(
                        progress_callback=progress_callback,
                        iterable=executor.map(
                            _func,
                            iterable,
                            second_iterable),
                        total=len(
                            list(iterable)),
                        desc=desc,
                        disable=disable_tqdm))
    else:
        if second_iterable is None:
            for it in tqdm(progress_callback=progress_callback, iterable=iterable, desc=desc, disable=disable_tqdm):
                _func(it)
        else:
            raise NotImplementedError("using second iterable in non threaded mode is not supported")


def join(*args):
    if platform.system() == "Windows":
        return os.path.join(*args).replace("\\", "/")
    else:
        return os.path.join(*args)