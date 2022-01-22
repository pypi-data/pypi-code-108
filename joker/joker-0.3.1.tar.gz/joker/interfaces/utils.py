#!/usr/bin/env python3
# coding: utf-8

import fnmatch
import importlib
import os
import re

from volkanic.introspect import find_all_plain_modules
from volkanic.utils import printerr


def multicheck(func, target, rules, positive_val: bool) -> bool:
    for rule in rules:
        if func(target, rule):
            return positive_val
    return not positive_val


def check_inclusive_prefixes(string: str, prefixes) -> bool:
    return multicheck(str.startswith, string, prefixes, True)


def check_exclusive_prefixes(string: str, prefixes) -> bool:
    return multicheck(str.startswith, string, prefixes, False)


def check_inclusive_patterns(string: str, patterns, case=True) -> bool:
    func = fnmatch.fnmatchcase if case else fnmatch.fnmatch
    return multicheck(func, string, patterns, True)


def check_exclusive_patterns(string: str, patterns, case=True) -> bool:
    func = fnmatch.fnmatchcase if case else fnmatch.fnmatch
    return multicheck(func, string, patterns, False)


def _regex_search(string: str, regex: str):
    return re.search(regex, string)


def check_inclusive_regexes(string: str, patterns) -> bool:
    return multicheck(_regex_search, string, patterns, True)


def check_exclusive_regexes(string: str, patterns) -> bool:
    return multicheck(_regex_search, string, patterns, True)


def load_modules_under_dir(project_dir: str, *dotpath_prefixes):
    if not project_dir or not dotpath_prefixes:
        return
    for dotpath in find_all_plain_modules(project_dir):
        if check_inclusive_prefixes(dotpath, dotpath_prefixes):
            printerr('importing', dotpath)
            importlib.import_module(dotpath)


def load_modules_under_package(package, module_names=None):
    import re
    import importlib
    if isinstance(package, str):
        package = importlib.import_module(package)
    prefix = package.__name__
    match = re.compile(r'^[^_].*\.pyc?$').match

    # by default import all modules under package
    if module_names is None:
        d = os.path.split(package.__file__)[0]
        module_names = (x for x in os.listdir(d) if match(x))
        module_names = (x.split('.')[0] for x in module_names)
        module_names = list(module_names)

    loaded = list()
    for name in module_names:
        mp = '{}.{}'.format(prefix, name)
        loaded.append(importlib.import_module(mp))
    return loaded


__all__ = [
    'multicheck',
    'check_exclusive_patterns',
    'check_exclusive_prefixes',
    'check_exclusive_regexes',
    'check_inclusive_patterns',
    'check_inclusive_prefixes',
    'check_inclusive_regexes',
    'find_all_plain_modules',
    'load_modules_under_dir',
    'load_modules_under_package',
]
