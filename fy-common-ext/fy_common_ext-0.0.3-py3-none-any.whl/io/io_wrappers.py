#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Some common IO wrappers."""

import csv
import os
import pickle
import shutil
from contextlib import contextmanager

__all__ = [
    'write_file_if_not_exist',
    'csv_reader', 'csv_writer',
    'pickle_load', 'pickle_dump',
    'copyfile_if_not_exist',
]


@contextmanager
def write_file_if_not_exist(filename, binary=False):
    """Context manager to write file if not exist.

    Usage:

    >>> with write_file_if_not_exist('xxx.txt') as f:
    ...     if f is not None:
    ...         # Do something
    ...         pass
    """

    if os.path.exists(filename):
        print(f'| {filename} already exists.')
        yield None
        return
    
    if binary:
        open_kwargs = {'mode': 'wb'}
    else:
        open_kwargs = {'mode': 'w', 'encoding': 'utf-8'}
    
    with open(filename, **open_kwargs) as f:
        yield f
    print(f'| Write to {filename}.')


@contextmanager
def csv_reader(filename, dict_reader=True, dialect=csv.excel):
    with open(filename, 'r', encoding='utf-8') as f:
        if dict_reader:
            reader = csv.DictReader(f, dialect=dialect)
        else:
            reader = csv.reader(f, dialect=dialect)
        yield reader


@contextmanager
def csv_writer(filename, fieldnames=None, dialect=csv.excel):
    with open(filename, 'w', encoding='utf-8') as f:
        if fieldnames is not None:
            writer = csv.DictWriter(f, fieldnames=fieldnames, dialect=dialect)
        else:
            writer = csv.writer(f, dialect=dialect)
        yield writer


def pickle_load(filename, *, fix_imports=True, encoding="ASCII", errors="strict"):
    with open(filename, 'rb') as f:
        return pickle.load(f, fix_imports=fix_imports, encoding=encoding, errors=errors)


def pickle_dump(obj, filename, protocol=None, *, fix_imports=True):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol=protocol, fix_imports=fix_imports)


def copyfile_if_not_exist(src, dst):
    if not os.path.exists(src):
        print(f'| {src} does not exist.')
        return
    if os.path.exists(dst):
        print(f'| {dst} already exists.')
        return
    shutil.copyfile(src, dst)
    print(f'| Copy {src} to {dst}.')
