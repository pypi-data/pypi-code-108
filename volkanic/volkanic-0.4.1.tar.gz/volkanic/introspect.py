#!/usr/bin/env python3
# coding: utf-8

import warnings
import copy
import datetime
import hashlib
import inspect
import itertools
import os
import re
import string
import sys
import traceback

import setuptools

from volkanic.compat import cached_property


def format_class_path(obj):
    if isinstance(obj, type):
        klass = obj
    else:
        klass = type(obj)
    m = getattr(klass, '__module__', None)
    q = getattr(klass, '__qualname__', None)
    n = getattr(klass, '__name__', None)
    name = q or n or ''
    if m:
        return '{}.{}'.format(m, name)
    return name


def _regular_attr_lookup(dictlike, *keys):
    for key in keys:
        try:
            return getattr(dictlike, key)
        except AttributeError:
            pass


def format_function_path(func):
    if not inspect.ismethod(func):
        mod = getattr(func, '__module__', None)
        qualname = _regular_attr_lookup(func, '__qualname__', '__name__')
        qualname = qualname or '<func>'
        if mod is None:
            return qualname
        else:
            return '{}.{}'.format(mod, qualname)
    klass_path = format_class_path(func.__self__)
    return '{}.{}'.format(klass_path, func.__name__)


def _dot_path(path: str):
    """Convert unix path to python module dot-path"""
    path, ext = os.path.splitext(path)
    parts = path.split(os.sep)
    if len(parts) > 1 and parts[-1] == '__init__':
        parts = parts[:-1]
    regex = re.compile(r'[_A-Za-z][_A-Za-z0-9]*$')
    for part in parts:
        if not regex.match(part):
            return
    return '.'.join(parts)


def find_all_py_files(search_dir: str, relative=False):
    for path in setuptools.findall(search_dir):
        if not path.endswith('.py'):
            continue
        if relative:
            path = os.path.relpath(path, search_dir)
        yield path


def find_all_plain_modules(search_dir: str):
    for path in find_all_py_files(search_dir, relative=True):
        dotpath = _dot_path(path)
        if not dotpath:
            continue
        yield dotpath


def _trim_str(obj: str, limit: int):
    obj = str(obj)
    if len(obj) > limit:
        obj = obj[:limit - 10] + ' ... ' + obj[-5:]
    return obj


def _trim_list(obj: list, limit: int):
    n = len(obj)
    if n > limit:
        obj = obj[:limit]
        suffix = '*list[{}-{}]'.format(n, limit)
        obj.append(suffix)
    return obj


def _trim_dict(obj: dict, limit: int):
    n = len(obj)
    if n > limit:
        pairs = itertools.islice(obj.items(), limit)
        obj = {_trim_str(k, limit): v for k, v in pairs}
        obj['...'] = '**dict[{}-{}]'.format(n, limit)
    return obj


def razor(obj, depth=3, limit=512):
    depth -= 1
    if isinstance(obj, str):
        return _trim_str(obj, limit)
    if isinstance(obj, (int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        if depth > -1:
            obj = _trim_dict(obj, limit)
            return {k: razor(v, depth) for k, v in obj.items()}
        else:
            return 'dict[{}]'.format(len(obj)) if obj else {}
    if isinstance(obj, list):
        if depth > -1:
            obj = _trim_list(obj, limit)
            return [razor(el, depth) for el in obj]
        else:
            return 'list[{}]'.format(len(obj)) if obj else []
    return razor(repr(obj))


def inspect_object(obj, depth=3):
    if not isinstance(obj, (dict, list, int, bool, float, str)):
        # if you argue for using __dict__, consider this:
        # https://stackoverflow.com/a/21300376/2925169
        try:
            obj = {'__dict__': vars(obj)}
            depth += 1
        except TypeError:
            pass
    return razor(obj, depth)


def query_object(obj, dotpath: str):
    for part in dotpath.split('.'):
        try:
            obj = getattr(obj, part)
            continue
        except AttributeError:
            pass
        if isinstance(obj, dict):
            try:
                obj = obj[part]
                continue
            except KeyError:
                return
        if isinstance(obj, list):
            try:
                obj = obj[int(part)]
                continue
            except (IndexError, ValueError):
                return
        break
    return obj


def get_caller_locals(depth: int):
    """
    Get the local variables in one of the outer frame.
    See Also: https://stackoverflow.com/a/6618825/2925169
    """
    # not sure what error is raise if sys._getframe is not implemented
    try:
        frame = getattr(sys, '_getframe')(depth)
    except (AttributeError, NotImplementedError, TypeError):
        return {'_': 'sys._getframe not implemented'}
    return razor(frame.f_locals)


class ErrorBase(Exception):
    extra = {}

    @property
    def error_key(self):
        try:
            return str(self.args[1])
        except IndexError:
            return self.__class__.__name__

    def __str__(self):
        if not self.args:
            return ''
        return str(self.args[0])

    def to_dict(self):
        if len(self.args) > 2 and isinstance(self.args[2], dict):
            return self.args[2]
        dic = {'message': str(self), 'error_key': self.error_key}
        dic.update(self.extra)
        return dic

    @classmethod
    def from_dict(cls, dic: dict):
        return cls(
            dic.get('message', ''),
            dic.get('error_key', cls.__name__),
            dic,
        )


class ErrorInfo(object):
    module_prefix = ''
    message = 'Application Error'

    @staticmethod
    def calc_error_hash(exc_string: str):
        warnings.warn(
            "ErrorInfo.calc_error_hash is deprecated",
            DeprecationWarning
        )
        h = hashlib.md5(exc_string.encode('utf-8')).hexdigest()[:4]
        hexdigits = string.hexdigits[:16]
        trans = str.maketrans(hexdigits, 'ACEFHKOPQSTUVWXY')
        return h.translate(trans)

    def __init__(self, exc: BaseException = None, exc_string: str = None):
        if not exc:
            exc = sys.exc_info()[1]
        if not exc_string:
            a = type(exc), exc, exc.__traceback__
            exc_string = ''.join(traceback.format_exception(*a))
        self.exc = exc
        self.exc_string = exc_string
        self.created_at = datetime.datetime.now()

    @cached_property
    def error_hex(self):
        b = self.exc_string.encode('utf-8')
        return hashlib.md5(b).hexdigest()

    @cached_property
    def _error_hash(self):
        hexdigits = string.hexdigits[:16]
        trans = str.maketrans(hexdigits, 'ACEFHKOPQSTUVWXY')
        return self.error_hex[:4].translate(trans)

    @cached_property
    def error_hash(self):
        warnings.warn(
            "ErrorInfo.error_hash is deprecated",
            DeprecationWarning
        )
        return self._error_hash

    @cached_property
    def error_key(self):
        return '{}-{:%H%M}'.format(self._error_hash, self.created_at)

    def print_exc(self):
        print(self.exc_string, file=sys.stderr)

    def to_dict(self, code=3):
        if isinstance(self.exc, ErrorBase):
            return self.exc.to_dict()
        return {
            'code': code,
            'error_key': self.error_key,
            'message': f'{self.message} <{self.error_key}>',
        }

    @cached_property
    def debug_info(self):
        tb = self.exc.__traceback__
        if tb is None:
            return
        while tb.tb_next:
            tb = tb.tb_next
        frame = tb.tb_frame
        # looking for the first frame
        # whose code is defined in package
        # whose full-qual-name starts with `self.module_prefix`
        info = {
            'exc': self.exc_string,
            'error_key': self.error_key,
            'created_at': self.created_at.isoformat(),
        }
        while frame:
            name = inspect.getmodule(frame).__name__
            if name.startswith(self.module_prefix):
                _globals = copy.copy(frame.f_globals)
                # __builtins__ is large but not very useful
                _globals.pop('__builtins__', None)
                f_info = {
                    'line': frame.f_lineno,
                    'func': frame.f_code.co_name,
                    'file': frame.f_code.co_filename,
                    'locals': razor(frame.f_locals),
                    'globals': razor(_globals),
                }
                info.update(f_info)
                break
            frame = frame.f_back
        return info
