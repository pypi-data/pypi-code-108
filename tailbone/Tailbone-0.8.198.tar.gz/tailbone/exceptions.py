# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tailbone Exceptions
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.exceptions import RattailError


class TailboneError(RattailError):
    """
    Base class for all Tailbone exceptions.
    """


@six.python_2_unicode_compatible
class TailboneJSONFieldError(TailboneError):
    """
    Error raised when JSON serialization of a form field results in an error.
    This is just a simple wrapper, to make the error message more helpful for
    the developer.
    """

    def __init__(self, field, error):
        self.field = field
        self.error = error

    def __str__(self):
        return ("Failed to serialize field '{}' as JSON!  "
                "Original error was: {}".format(self.field, self.error))
