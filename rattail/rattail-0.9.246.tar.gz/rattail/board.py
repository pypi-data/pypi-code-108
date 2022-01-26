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
Board Handler
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import load_object
from rattail.app import GenericHandler


class BoardHandler(GenericHandler):
    """
    Base class and default implementation for board handlers.
    """

    def method_not_implemented(self, method):
        msg = "Please implement {}.{}()".format(
            self.__class__.__name__, method)
        return NotImplementedError(msg)

    def begin_board_membership(self, person, start_date, **kwargs):
        """
        Begin board membership for the given person.
        """
        raise self.method_not_implemented('begin_board_membership')

    def end_board_membership(self, person, end_date, **kwargs):
        """
        End board membership for the given person.
        """
        raise self.method_not_implemented('end_board_membership')

    def why_not_begin_board_membership(self, person):
        """
        Inspect the given person and if they should not be made a current board
        member for any reason, return that reason as text.  If it's okay for
        the person to be made a board member, returns ``None``.
        """
        raise self.method_not_implemented('why_not_begin_board_membership')

    def why_not_end_board_membership(self, person):
        """
        Inspect the given person and if their current board membership should
        not be ended for any reason, return that reason as text.  If it's okay
        for the person to stop being a board member, returns ``None``.
        """
        raise self.method_not_implemented('why_not_end_board_membership')


def get_board_handler(config, **kwargs):
    """
    Create and return the configured :class:`BoardHandler` instance.
    """
    spec = config.get('rattail', 'board.handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = BoardHandler
    return factory(config, **kwargs)
