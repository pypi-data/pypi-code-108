#!/usr/bin/env python3
# coding: utf-8

import functools
import importlib
import os
import sys


def attr_query(obj, *attrnames):
    for x in attrnames:
        obj = getattr(obj, x)
    return obj


def attr_setdefault(obj, attrname, value):
    try:
        return getattr(obj, attrname)
    except AttributeError:
        setattr(obj, attrname, value)
        return value


# deprecated names; both will be remove at ver 0.5.0
query_attr = attr_query
subattr = query_attr


def merge_dicts(*dicts):
    # a list of dicts is acceptable
    if len(dicts) == 1 and isinstance(dicts[0], list):
        dicts = dicts[0]
    retdic = {}
    for dic in dicts:
        retdic.update(dic)
    return retdic


def select_from_dict(dict_: dict, fields: list, pop=False):
    sub_dict = {}
    method = dict_.pop if pop else dict_.get
    for key in fields:
        if key in dict_:
            sub_dict[key] = method(key, None)
    return sub_dict


def load_symbol(symbolpath):
    parts = symbolpath.split(':', 1)
    symbol = importlib.import_module(parts.pop(0))
    if parts:
        symbol = query_attr(symbol, *parts[0].split('.'))
    return symbol


def load_variables(*contexts):
    import re
    scope = {}
    for ctx in contexts:
        if not isinstance(ctx, dict):
            ctx = {re.split(r'[.:]', x)[-1]: x for x in ctx}
        for key, val in ctx.items():
            scope[key] = load_symbol(val)
    return scope


def _abs_path_join(*paths):
    path = os.path.join(*paths)
    return os.path.abspath(path)


def abs_path_join(*paths) -> str:
    if not paths:
        msg = 'abs_path_join() requires at least 1 argument'
        raise TypeError(msg)
    if paths[0].startswith('~'):
        paths = list(paths)
        paths[0] = os.path.expanduser(paths[0])
    return _abs_path_join(*paths)


def abs_path_join_and_mkdirs(*paths):
    path = abs_path_join(*paths)
    if paths[-1].endswith('/'):
        os.makedirs(path, exist_ok=True)
    else:
        os.makedirs(os.path.split(path)[0], exist_ok=True)
    return path


def under_parent_dir(ref_path: str, *paths) -> str:
    ref_path = os.path.abspath(ref_path)
    parent_dir = os.path.dirname(ref_path)
    return abs_path_join(parent_dir, *paths)


def under_home_dir(*paths):
    if sys.platform == 'win32':
        homedir = os.environ["HOMEPATH"]
    else:
        homedir = os.path.expanduser('~')
    return _abs_path_join(homedir, *paths)


def under_package_dir(package, *paths):
    if isinstance(package, str):
        package = importlib.import_module(package)
    pkg_dir = os.path.dirname(package.__file__)
    return _abs_path_join(pkg_dir, *paths)


def _linux_open(path):
    import subprocess
    subprocess.run(['xdg-open', path])


def _macos_open(path):
    import subprocess
    subprocess.run(['open', path])


def _windows_open(path):
    getattr(os, 'startfile')(path)


def desktop_open(*paths):
    import platform
    osname = platform.system().lower()
    if osname == 'darwin':
        handler = _macos_open
    elif osname == 'windows':
        handler = _windows_open
    else:
        handler = _linux_open
    for path in paths:
        handler(path)


def where(name):
    mod = importlib.import_module(name)
    path = getattr(mod, '__file__', 'NotAvailable')
    dir_, filename = os.path.split(path)
    if filename.startswith('__init__.'):
        return dir_
    return path


def where_site_packages():
    for name in ['pip', 'easy_install']:
        try:
            return os.path.split(where(name))[0]
        except ModuleNotFoundError:
            continue
    for p in sys.path:
        if p.endswith('site-packages'):
            return p


def indented_json_dumps(obj, dumps=None, **kwargs):
    if dumps is None:
        import json
        dumps = json.dumps
    kwargs.setdefault('indent', 4)
    kwargs.setdefault('default', str)
    kwargs.setdefault('sort_keys', True)
    kwargs.setdefault('ensure_ascii', False)
    return dumps(obj, **kwargs)


def indented_json_print(obj, dumps=None, **kwargs):
    print_kwargs = {}
    print_keywords = ['sep', 'end', 'file', 'flush']
    for key in print_keywords:
        if key in kwargs:
            print_kwargs[key] = kwargs.pop(key)
    if dumps is None:
        dumps = indented_json_dumps
    print(dumps(obj, **kwargs), **print_kwargs)


def load_json5_file(path: str):
    if path.endswith('.json'):
        import json
        return json.loads(open(path).read())
    import json5
    return json5.load(open(path))


def ignore_arguments(func):
    """Discard arguments and call a argument-less function"""

    @functools.wraps(func)
    def _func(*_args, **_kwargs):
        return func()

    return _func


# discard_arguments will be remove at ver 0.5.0
discard_arguments = ignore_arguments


def printerr(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    print(*args, **kwargs)


def printfmt(*args, sep=' ', end=os.linesep):
    sep = str(sep)
    end = str(end)
    return sep.join(str(x) for x in args) + end
