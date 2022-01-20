#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of PyZenKit package.
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2015 Honza Mach <honza.mach.ml@gmail.com>
# Use of this package is governed by the MIT license, see LICENSE file.
#
# This project was initially written for personal use of the original author. Later
# it was developed much further and used for project of author`s employer.
#-------------------------------------------------------------------------------


"""
This module contains various handy utilities.
"""

__author__  = "Honza Mach <honza.mach.ml@gmail.com>"


import os

try:
    import dotenv
except ImportError:
    dotenv = None


def load_dotenv(path = None):
    """
    Load "dotenv" files in order of precedence to set environment variables.
    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files.

    Changes the current working directory to the location of the first file
    found, with the assumption that it is in the top level project directory
    and will be where the Python path should import local packages from.
    This is a no-op if ``python-dotenv`` is not installed.

    :param str path: Load the file at this location instead of searching.
    :return: ``True`` if a file was loaded.
    :rtype: bool
    """
    if dotenv is None:
        if path or os.path.isfile('.env.local') or os.path.isfile('.env'):
            print(
                ' * Tip: There are ".env.local" or ".env" files present.'
                ' Do "pip install python-dotenv" to use them.'
            )
        return False

    if path is not None:
        return dotenv.load_dotenv(path)

    new_dir = None

    for name in ('.env.local', '.env'):
        path = dotenv.find_dotenv(name, usecwd = True)

        if not path:
            continue

        if new_dir is None:
            new_dir = os.path.dirname(path)

        dotenv.load_dotenv(path)

    if new_dir and os.getcwd() != new_dir:
        os.chdir(new_dir)

    return new_dir is not None  # at least one file was located and loaded


def load_dotenv_cwd():
    """
    Load "dotenv" files in order of precedence to set environment variables.
    If an env var is already set it is not overwritten, so earlier files in the
    list are preferred over later files. This method attempts to load ``.env.local``
    and ``.env`` files, if present in current directory.

    This is a no-op if ``python-dotenv`` is not installed.
    """
    if dotenv is None:
        if os.path.isfile('.env.local') or os.path.isfile('.env'):
            print(
                ' * Tip: There are ".env.local" or ".env" files present.'
                ' Do "pip install python-dotenv" to use them.'
            )
        return

    for name in ('.env.local', '.env'):
        if os.path.isfile(name):
            dotenv.load_dotenv(name)


#-------------------------------------------------------------------------------


def get_resource_path(fs_path, *more_chunks):
    """
    Return filesystem path to application resource with ``APP_ROOT_PATH`` taken
    into consideration. If ``fs_path`` is absolute the ``APP_ROOT_PATH`` will
    be ignored as usual.
    """
    return os.path.join(os.getenv('APP_ROOT_PATH', '/'), fs_path, *more_chunks)

def get_resource_path_fr(fs_path, *more_chunks):
    """
    Force given application filesystem path to be relative to ``APP_ROOT_PATH``.
    """
    return os.path.join(os.getenv('APP_ROOT_PATH', '/'), fs_path.strip(os.sep), *more_chunks)
