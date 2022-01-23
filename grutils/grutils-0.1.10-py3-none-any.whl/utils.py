#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from typing import Dict, List, Optional, Tuple

from .configs import Configuration
from .error import Error


def sort_and_merge_ints(ints: List[int]):
    results: List[Tuple[int, int]] = []
    if len(ints) == 0:
        return results

    sorted_ints = sorted(ints)

    start: Optional[int] = None
    curr: Optional[int] = None
    for i in sorted_ints:
        if start is None:
            start = i
            curr = i
            continue

        if i == curr + 1:
            curr = i
            continue

        results.append((start, curr))
        start = i
        curr = i

    if start is not None:
        results.append((start, curr))

    return results


def get_simple_desc_of_int_groups(groups: List[Tuple[int, int]],
                                  formatter: str = "{}",
                                  linker: str = "-",
                                  joiner: str = ","
                                  ):
    items = list(map(lambda group: (formatter + linker + formatter).format(group[0], group[1]) if group[0] != group[
        1] else formatter.format(group[0]), groups))
    return joiner.join(items)


def compare_two_list(a: Optional[List], b: Optional[List]):
    if a is None and b is None:
        return True

    if a is None or b is None:
        return False

    for k in a:
        if k not in b:
            return False

    for k in b:
        if k not in a:
            return False

    return True


def get_os_user():
    return os.getenv('username')


def get_special_folder(err: Error, key: str, config: Configuration, test_os_user: str = 'liuleidong'):
    if err.has_error():
        return

    folder = config.get(key=key, default='', save_if_no=False)
    if os.path.exists(folder):
        return folder

    os_user = get_os_user()
    if os_user == test_os_user:
        folder = config.get(key='test_' + key, default='', save_if_no=False)
        if len(folder) == 0:
            return folder
        if os.path.exists(folder):
            return folder

    err.append('folder "' + folder + '" is not exists')


def get_from_dict(d: Dict, *keys):
    _d = d
    for key in keys:
        if key in _d:
            _d = _d[key]
        else:
            return None

    return _d


def set_to_dict(d: Dict, v, *keys):
    _d = d
    for key in keys[:-1]:
        if key not in _d:
            _d[key] = {}
        _d = _d[key]

    _d[keys[-1]] = v


def get_value_or_exception(err: Error, v_or_e, exception_formatter='{}'):
    if err.has_error():
        return

    if type(v_or_e) == Exception:
        err.append(exception_formatter.format(v_or_e))
        return
    return v_or_e
