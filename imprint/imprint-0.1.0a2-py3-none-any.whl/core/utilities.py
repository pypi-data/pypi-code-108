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
:py:mod:`imprint.core.utilities` containins general utilities to help
the engine create and process docx files.

The configuration loaders in this module are potentially suitable for
inclusion in the `haggis`_ library.


.. include:: /link-defs.rst
"""

__all__ = [
    'aggressive_strip', 'check_fail_state', 'trigger_fail_state',
    'get_handler', 'load_callable', 'substitute_headers_and_footers',
]


from datetime import datetime
from inspect import isclass, ismodule
import logging
import re
from warnings import warn
from zipfile import ZipFile

from haggis import logs, Sentinel
from haggis.files.zip import filter as filter_zip

from . import encoding


#: Private logger for this module
_logger = logging.getLogger(__name__)


#: A list of the valid options for :py:func:`check_fail_state` and
#: :py:func:`trigger_fail_state`.
_fail_options = ('raise', 'warn', 'ignore')


logs.add_logging_level('XTRACE', 2, exc_info=True)


def check_fail_state(fail):
    """
    Verify that `fail` is one of the valid options ``{'raise', 'warn',
    'ignore'}``.

    Raise a :py:exc:`ValueError` if it is not.
    """
    if fail not in _fail_options:
        raise ValueError(f'fail mode must be in {_fail_options}')


def trigger_fail_state(fail, msg,
                       error_class=ValueError, warn_class=UserWarning):
    """
    React to a failure according to the value of ``fail``:

      - ``'ignore'``: Do nothing
      - ``'warn'``: Raise a warning with message `msg` and class
        `warn_class` (:py:exc:`UserWarning` by default).
      - ``'raise'``: Raise an error with message `msg` and class
        `error_class` (:py:exc:`ValueError` by default).

    Any other value of `fail` triggers a :py:exc:`ValueError`.
    """
    check_fail_state(fail)
    if fail == 'raise':
        raise error_class(msg)
    elif fail == 'warn':
        warn(msg, warn_class, stacklevel=2)
    else:  # Make ignore explicit
        pass


def get_handler(handler_name):
    """
    Load the named :ref:`plugin handler <plugins-handlers>`.

    Handlers are callables that take an object ID and configuration
    dictionary and generate content for a specific tag like
    :ref:`xml-spec-tags-figure`, :ref:`xml-spec-tags-table` or
    :ref:`xml-spec-tags-string`.

    If the handler is not found as-is, the :py:mod:`imprint.handlers`
    package is prefixed to `handler_name` since that is where all
    built-in handlers live.
    """
    return load_callable(handler_name, 'imprint.handlers')


def load_callable(name, package_prefix=None, magic_module_attribute=Sentinel,
                  instantiate_class=False):
    """
    Retrieve an arbitrary callable from a module

    The input may be one of six things:

     1. A module with a `magic_module_attribute` that contains the
        callable.
     2. A callable that implements the correct interface.
     3. The name of a module containing the `magic_module_attribute`.
     4. The name of a callable.
     5. The name of a module in the `package_prefix` package.
     6. The name of a callable in the `package_prefix` package.

    The correct thing is identified as leniently as possible and
    returned. The returned object is not guaranteed to be the correct
    thing, just to pass very cursory inspection (e.g., modules must have
    the magic attribute and any other objects must be callable)

    Items 1, 3, 5 are not possible if `magic_module_attribute` is not
    specified. Items 5, 6 are not possible if `package_prefix` is not
    specified.

    This method has one special case. If the object found is a class with a
    no-arg `__init__` method and a `__call__` method, an instance rather than
    the class object is returned. Note that class objects themselves are
    callable, so if you specify a class without a no-arg `__init__` method or
    without a `__call__` method, make sure that `__init__` has the signature
    you require and returns the object that you expect.
    """
    def check_callable(candidate):
        """
        Check if an object is callable and return it if it is.

        If `candidate` is not callable, return :py:obj:`None`. If
        `instantiate_class` is set and `candidate` is a class object
        with a no-arg `__init__` method that initializes callable
        instances, an instance will be returned instead of the class.
        """
        if instantiate_class and isclass(candidate):
            try:
                instance = candidate()
            except TypeError:
                _logger.debug(
                    'Importing "%s.%s" as class: does not have a no-arg '
                    'constructor', candidate.__module__, candidate.__qualname__
                )
            else:
                if callable(instance):
                    _logger.debug('Importing callable instance of "%s.%s"',
                                  candidate.__module__, candidate.__qualname__)
                    candidate = instance
                else:
                    _logger.debug(
                        'Importing "%s.%s" as class: instance obtained, but '
                        'is not callable', candidate.__module__,
                        candidate.__qualname__
                    )
        elif callable(candidate):
            _logger.debug(
                'Importing "%s" as regular callable', candidate.__name__
                    if hasattr(candidate, '__name__') else repr(candidate)
            )
        else:
            candidate = None
        return candidate

    def load_candidate(modname, callname=None):
        if not callname and callname is not magic_module_attribute:
            modpath = modname.split('.')
            if len(modpath) == 1:
                callname = ''
                modpath = modname
            else:
                callname = modpath[-1]
                modpath = '.'.join(modpath[:-1])

        if callname:
            try:
                mod = __import__(modpath, None, None, callname)
            except ModuleNotFoundError as e:
                _logger.trace(
                    'Unable to import "%s" no such module: %s', modname, e
                )
            except ImportError as e:
                _logger.trace(
                    'Unable to import "%s" due to non-syntax error in module: '
                    '%s', modname, e
                )
            except SyntaxError as e:
                _logger.trace(
                    'Unable to import "%s" due to syntax error: %s', modname, e
                )
            else:
                if hasattr(mod, callname):
                    return check_candidate(mod, callname)
                else:
                    _logger.trace('Unable to import "%s": module has no '
                                  'such attribute', modname)

        return None

    load_module = lambda modname: load_candidate(modname,
                                                 magic_module_attribute)

    def check_candidate(mod, attr):
        candidate = getattr(mod, attr)  # Raises AttributeError
        if check_callable(candidate) is None:
            raise TypeError(f'{mod.__name__}.{attr} found but is not callable')
        return candidate

    # 1: Actual module containing callable `magic_module_attribute`
    if ismodule(name):
        if magic_module_attribute:
            return check_candidate(name, magic_module_attribute)
        else:
            raise ValueError('Magic attribute name not specified for module')

    # 2: Callable object
    if check_callable(name) is not None:
        return name

    # All following operations done on strings
    if not isinstance(name, str):
        raise TypeError('requested object must be module, callable or string')

    prefixed_name = package_prefix + '.' + name
    for item in (name, prefixed_name):
        for loader in (load_module, load_candidate):
            candidate = loader(item)
            if candidate is not None:
                return candidate

    raise TypeError(f'{name} ({type(name)}) does not correspond '
                    'to a known object')


def substitute_headers_and_footers(doc_file_name, keywords):
    """
    Perform a keyword replacement on all valid newstyle format strings
    in the header and footer XML of a word document.

    This operation is currently done by treating the XML as if it was a
    giant string. The assumption is valid but hacky, since format-like
    strings delimited by '{}' are unlikely to appear anywhere outside
    ``<w:t>`` tags.
    """
    with ZipFile(doc_file_name, 'r') as z:
        file_list = [name for name in z.namelist()
                            if name.startswith('word/footer') or
                               name.startswith('word/header')]

    _logger.debug('Replacing keywords in the following '
                  'headers and footers: %s', file_list)

    if 'date' in keywords:
        formatter = str.format
    else:
        formatter = lambda fmt, **kwds: str.format(fmt, date=datetime.now(),
                                                   **kwds)

    def kwd_replace(string):
        """
        Accept a string of bytes or characters and replace every
        apparent occurrence of a keyword.

        Failed replacements are left alone in the string.

        .. todo::

           The correct way to implement this is to parse the XML and
           only accept replacements between ``<w:t>`` tags. The issue is
           of course that there are too many breaks between ``<w:t>``
           tags.
        """
        if not isinstance(string, str):
            string = string.decode(encoding)

        def try_replace(matcher):
            format_string = matcher.group()
            try:
                replacement = formatter(format_string, **keywords)
            except Exception as e:
                replacement = format_string
                _logger.trace('Failed to replace "%s": Most likely caused by '
                              'no matches in keywords.', format_string)
            else:
                _logger.trace('Replacing "%s" with "%s"',
                              format_string, replacement)

            return replacement

        return re.sub('{[^}]*}', try_replace, string)

    filter_zip(doc_file_name, *file_list, filter=kwd_replace)


def aggressive_strip(string):
    """
    Split a string along newlines, strip surrounding whitespace on
    each line, and recombine with a single space in place of the
    newlines.
    """
    return ' '.join(filter(None, map(str.strip, string.splitlines())))
