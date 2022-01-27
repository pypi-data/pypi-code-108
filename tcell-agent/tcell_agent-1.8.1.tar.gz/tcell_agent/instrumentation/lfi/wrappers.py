# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
from tcell_agent.instrumentation.lfi import utils
from os.path import abspath


def _base_wrapper(func, _file_path, _mode, *args, **kwargs):
    if utils.should_block_file_open(
        file_path=abspath(_file_path),
        mode=_mode,
        opener_class="{}.{}".format(func.__module__, func.__name__)
    ):
        raise IOError("Opening file '{}' blocked".format(_file_path))
    return func(*args, **kwargs)


def _base_open_wrapper(func, _file_path, *args, **kwargs):
    try:
        mode = kwargs.get('mode') or args[1]
    except IndexError:
        mode = 'r'
    mode = utils.get_native_file_mode(mode)
    return _base_wrapper(func, _file_path, mode, *args, **kwargs)


def _base_os_open_wrapper(func, _file_path, _mode, *args, **kwargs):
    mode = utils.get_native_file_mode(_mode)
    return _base_wrapper(func, _file_path, mode, *args, **kwargs)


def py2_file_wrapper(func, *args, **kwargs):
    """ file(name[, mode[, buffering]]) """
    return py2_open_wrapper(func, *args, **kwargs)


def py2_open_wrapper(func, *args, **kwargs):
    """ open(name[, mode[, buffering]]) """
    file_path = kwargs.get('name') or args[0]
    return _base_open_wrapper(func, file_path, *args, **kwargs)


def py2_os_open_wrapper(func, *args, **kwargs):
    """ os.open(file, flags[, mode]) """
    # os.open takes no kwargs
    return _base_os_open_wrapper(func, args[0], args[1], *args, **kwargs)


def py2_io_open_wrapper(func, *args, **kwargs):
    """ io.open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None,
            closefd=True) """
    return py3_open_wrapper(func, *args, **kwargs)


def py3_open_wrapper(func, *args, **kwargs):
    """ open(file, mode='r', buffering=-1, encoding=None, errors=None,
            newline=None, closefd=True, opener=None) """
    file_path = str(kwargs.get('file') or args[0])
    return _base_open_wrapper(func, file_path, *args, **kwargs)


def py3_os_open_wrapper(func, *args, **kwargs):
    """ os.open(path, flags, mode=0o777, *, dir_fd=None) """
    return py2_os_open_wrapper(func, *args, **kwargs)


def py3_io_open_wrapper(func, *args, **kwargs):
    """ io.open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None,
            closefd=True, opener=None)
        also used by `Pathlib.open`
    """
    return py3_open_wrapper(func, *args, **kwargs)


def py3_pathlib_normalaccessor_open_wrapper(func, *args, **kwargs):
    """ os.open(path, flags, mode=0o777, *, dir_fd=None) """
    # since `pathlib._NormalAccessor.open` is called as an instance method the
    # first argument will be the instance it self, so lets just omit it
    file_path, mode = str(args[1]), args[2]
    return _base_os_open_wrapper(func, file_path, mode, *args[1:], **kwargs)
