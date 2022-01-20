# -*- coding: utf-8 -*-

# imprint: a program for creating documents from data and content templates
#
# Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
# Version: 13 Apr 2019: Initial Coding


"""
:py:mod:`imprint.handlers.utilities` contains common utilities for
handlers. Users wishing to write their own handlers may want to use
these functions to facilitate a uniform interface. Existing handlers in
this package use these functions as well.
"""

from collections.abc import Mapping


__all__ = ['get_key', 'get_file', 'normalize_descriptor']


def get_key(config, kwds, key, default=None,
            formatted='formatted', missing_ok=True):
    """
    Retreive the value of `key` from the mapping `config`.

    If `key` does not exist in `config`, return `default` instead.

    If `formatted` is a string, it determines the key name that
    determines whether `key` is a format string or not (default is
    yes). Otherwise, it is interpreted as a boolean directly.

    Parameters
    ----------
    config : dict
        The :ref:`plugins-data-configuration` dictionary to search.
    kwds : dict
        The :ref:`keywords` dictionary to use for replacements if
        `formatted` turns out to be truthy.
    key : str
        The name of the key in `config` containing the required value.
    default :
        The value to return if `key` is missing from `config`.
    formatted : str or bool
        Either the name of the key to get the formatted flag from (if a
        string), or the flag itself. In either case, ignored if the
        value is not a string.
    missing_ok : bool
        If truthy, missing values are replaced by `default`. Otherwise
        a :py:exc:`KeyError` is raised.

    Return
    ------
    The value in `config` associated with `key`, optionally formatted
    with `kwds`.
    """
    if missing_ok:
        value = config.get(key, default)
    else:
        value = config[key]
    if isinstance(value, str) and config.get(formatted, True):
        value = value.format(**kwds)
    return value


def get_file(config, kwds, key='file', default=None,
             formatted='formatted', missing_ok=False):
    """
    A wrapper around :py:func:`get_key` that sets the default key to
    ``'file'`` and forbids missing keys.
    """
    return get_key(config, kwds, key, default, formatted, missing_ok)


def normalize_descriptor(descriptor, key, copy=False):
    """
    If `descriptor` is a mapping, return it as-is; otherwise, turn it
    into a value in a mapping keyed by `key`.

    If the descriptor is returned as-is, it can optionally be copied by
    setting `copy` to :py:obj:`True`.
    """
    if isinstance(descriptor, Mapping):
        return descriptor.copy() if copy else descriptor
    return {key: descriptor}
