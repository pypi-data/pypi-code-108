#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import pytest
from nabu.utils import get_folder_path
from nabu import __nabu_modules__ as nabu_modules


def get_modules_to_test(mods):
    sep = os.sep
    modules = []
    extra_args = []
    for mod in mods:
        if mod.startswith("-"):
            extra_args.append(mod)
            continue
        # Test a whole module
        if mod.lower() in nabu_modules:
            mod_abspath = os.path.join(get_folder_path(mod), "tests")
        # Test an individual file
        else:
            mod_path = mod.replace(".", sep) + ".py"
            mod_abspath = get_folder_path(mod_path)
            # test only one file
            mod_split = mod_abspath.split(sep)
            mod_split.insert(-1, "tests")
            mod_abspath = sep.join(mod_split)
        if not(os.path.exists(mod_abspath)):
            print("Error: no such file or directory: %s" % mod_abspath)
            exit(1)
        modules.append(mod_abspath)
    return modules, extra_args


def nabu_test():
    nabu_folder = get_folder_path()
    args = sys.argv[1:]
    modules_to_test, extra_args = get_modules_to_test(args)
    if len(modules_to_test) == 0:
        modules_to_test = [get_folder_path()]
    pytest_args = extra_args + modules_to_test
    return pytest.main(pytest_args)


if __name__ == "__main__":
    ret = nabu_test()
    exit(ret)
