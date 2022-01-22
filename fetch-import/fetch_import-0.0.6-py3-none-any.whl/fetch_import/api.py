import importlib
import os
import sys
import time
import traceback
from functools import wraps
import hashlib
from typing import List, Union

import requests


def _calc_hash(text: str):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    return md5.hexdigest()


def _mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def _import_v1(url: str, module: bool = False, filename=None, dir_path=""):
    _attrs = {}
    if filename is None:
        filename = url.split("/")[-1].split(".")[0]
    try:
        content = requests.get(url)
        if content.status_code != 200:
            return
        with open(f"{filename}.py", "w") as f:
            f.write(content.text)
    except Exception as e:
        traceback.format_exc()
        return _attrs
    _mod = f"{filename}"
    mdl = importlib.import_module(_mod)

    if module:
        _attrs.update({filename: mdl})
        return _attrs

    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
        _attrs.update({k: getattr(mdl, k) for k in names})
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
        _attrs.update({k: getattr(mdl, k) for k in names})
    return _attrs


def __has_cache(mdc_filename: str, time_out: int = 30):
    if time_out <= 0:
        return False, ""
    if not os.path.exists(mdc_filename):
        return False, ""
    update_time = os.path.getmtime(mdc_filename)

    time_difference = time.time() - update_time
    if time_difference < time_out:
        with open(mdc_filename, "r") as f:
            file_path = f.read()
        return True, file_path
    else:
        return False, ""


def _import(url: str, module: bool = False, alias=None, dir_path="/var/tmp/fetch_import", *args, **kwargs):
    """

    :param url: remote url,https://example.com/name.py
    :param module: if True, return {"name":"name_module"}, or return module attrs dict.
    :param alias:
    :param dir_path:
    :return:
    """
    _attrs = {}

    if os.name != 'posix':
        dir_path = "./"
    else:
        _mkdir(dir_path)
        sys.path.append(dir_path)

    filename = url.split("/")[-1].split(".")[0]

    if alias is None:
        module_name = filename
    else:
        module_name = alias

    try:

        content = requests.get(url)
        if content.status_code != 200:
            return _attrs
        md5 = _calc_hash(content.text)
        url_md5 = _calc_hash(url)
        mdc_filename = f"{dir_path}/{url_md5}.mdc"

        time_out = kwargs.get("cache_time_out", 30)

        res, file_name = __has_cache(mdc_filename, time_out)

        if res:
            filename = file_name
        else:
            with open(mdc_filename, "w") as f:
                f.write(f"{md5}_{filename}")

            filename = f"{md5}_{filename}"
            with open(f"{dir_path}/{filename}.py", "w") as f:
                f.write(content.text)
    except Exception:
        print(traceback.format_exc())
        return _attrs

    mdl = importlib.import_module(filename)

    if module:
        _attrs.update({module_name: mdl})
        return _attrs

    if "__all__" in mdl.__dict__:
        names = mdl.__dict__["__all__"]
        _attrs.update({k: getattr(mdl, k) for k in names})
    else:
        names = [x for x in mdl.__dict__ if not x.startswith("_")]
        _attrs.update({k: getattr(mdl, k) for k in names})
    return _attrs


def _im_fetch(url, attrs: List = None, _globals: dict = None, *args, **kwargs):
    """
    :param url: https://example.com/{module_name}.py
    :param attrs:
            - None
              equal "import module_name "
            - ["*"]
              equal "from module_name import *"
            - ["AbstractClass","AbstractMetaClass","ObjectClass","TypeClass","def_function"]
              equal "from module_name import AbstractClass,AbstractMetaClass,ObjectClass,TypeClass,def_function"
    :param _globals:
    :param args:
    :param kwargs:
    :return:
    """
    ready_add_attrs = {}
    if attrs is None:
        module_attrs = _import(url=url, module=True, *args, **kwargs)
        ready_add_attrs.update(module_attrs)
    elif len(attrs) == 1 and attrs[0] == "*":
        module_attrs = _import(url=url)
        ready_add_attrs.update(module_attrs)
    else:
        module_attrs = _import(url=url, *args, **kwargs)
        _ready_pop_attr = []
        for attr_item in module_attrs:
            if attr_item in attrs:
                continue
            _ready_pop_attr.append(attr_item)
        for attr_item in _ready_pop_attr:
            module_attrs.pop(attr_item)
        ready_add_attrs.update(module_attrs)

    if _globals is None:
        globals().update(ready_add_attrs)
    else:
        _globals.update(ready_add_attrs)


def im_fetch(url, attrs: List = None, _globals: dict = None, *args, **kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            if _globals is None:
                _im_fetch(url, attrs, _globals=func.__globals__, *args, **kwargs)
            else:
                _im_fetch(url, attrs, _globals=_globals, *args, **kwargs)
            return func(*func_args, **func_kwargs)

        return wrapper

    return decorator


if __name__ == '__main__':
    url = "https://fastly.jsdelivr.net/gh/zmaplex/fetch_import@main/example/sets.py"
    attrs = _import(url, module=True)
    print(attrs)
