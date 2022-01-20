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
:py:mod:`imprint.handlers.string.strings` contains the basic built-in
:ref:`plugins-handlers` for inserting strings into a document. All the
handlers in this module are compatible with the
:ref:`plugin interface <plugins-strings-signature>` used by the
:ref:`xml-spec-tags-string` tag.
"""

import logging

from ..utilities import get_file


__all__ = ['TextFile',]


#: Private logger for this module
_logger = logging.getLogger(__name__)


def TextFile(config, kwds):
    """
    Generate a string directly from the contents of a text file.

    Text files are inserted literally, with no styling information
    beyond that of the :ref:`xml-spec-tags-string` tag that triggered
    the plugin. Newlines are not preserved.

    The following :ref:`plugins-data-configuration` keys are used:

        file
            The (mandatory) file name.
        formatted
            Whether or not ``file`` is a format string that has keyword
            replacements in it. Defaults to truthy. Set to falsy if
            the name contains random opening braces.
    """
    input_path = get_file(config, kwds)
    _logger.trace('Loading string from %r', input_path)
    with open(input_path, 'rt') as file:
        return file.read()
