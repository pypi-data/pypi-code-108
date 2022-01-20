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
The :py:mod:`imprint.core` package contains the Imprint
:ref:`introduction-layers-engine`. The :py:mod:`~imprint.core.tags` and
:py:mod:`~imprint.core.state` modules implement most of the
functionality useful to end-users through the public :ref:`tag-api`. The
:py:mod:`~imprint.core.parsers` and :py:mod:`~imprint.core.utilities`
contain the :ref:`internals`.
"""

__all__ = [
    'parsers', 'state', 'tags', 'utilities',
    'root_tag', 'encoding', 'KnownError'
]


#: Name of the root tag expected in XML documents.
root_tag = 'imprint-template'


#: The expected encoding of XML documents
encoding = 'utf-8'


class KnownError(Exception):
    """
    A custom exception class that is used by the engine to indicate that
    a tag or plugin handler exited for a known reason.

    In cases where this exception is logged, the message is printed
    without a stack trace.
    """
    pass
