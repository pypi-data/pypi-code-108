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
Root package of :py:mod:`imprint`.

This package contains the following sub-packages:

  - :py:mod:`~imprint.core`:
      The code that generates the documents. This includes all XML
      parsers and implementations of the :ref:`tag-api-builtins`.
  - :py:mod:`~imprint.handlers`:
      A package implementing common :ref:`plugins-handlers` for the
      built-in tags that accept them.
  - :py:mod:`~imprint.tests`:
      While woefully incomplete, this package contains the beginnings of 
      unit tests for imprint.

The public driver script for the :py:mod:`imprint` package is
:program:`imprint`, implemented in the module
:py:mod:`imprint.driver`.
"""


__all__ = ['__version__']



from .version import __version__
"""
The current version of the software. Individual components, especially in the
configuration, may have different version numbers.
"""
