#!/usr/bin/env python3
"""
Module JSONTOOLS -- Tools for JSON and similar file formats
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

These are convenience functions for loading/saving JSON
from/to filenames. Also, functions are added to support
"extended" JSON, which includes tuples and other non-dynamic
Python types that standard JSON does not support. Note that
no checking is done in the "extended" methods to ensure that
only "allowed" types are used when saving/dumping; the only
check is done on loading, since ``ast.literal_eval`` will
only accept certain types.
"""

import ast
from json import load, dump


def load_json(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as f:
        return load(f)


def save_json(data, filename, encoding='utf-8'):
    with open(filename, 'w', encoding=encoding) as f:
        dump(data, f)


loads_ext = ast.literal_eval


def load_ext(f):
    return loads_ext(f.read())


dumps_ext = repr


def dump_ext(data, f):
    f.write(dumps_ext(data))


def load_json_ext(filename, encoding='utf-8'):
    with open(filename, 'r', encoding=encoding) as f:
        return load_ext(f)


def save_json_ext(data, filename, encoding='utf-8'):
    with open(filename, 'w', encoding=encoding) as f:
        dump_ext(data, f)
