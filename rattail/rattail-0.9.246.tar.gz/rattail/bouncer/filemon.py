# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
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
FileMon logic for Bouncer
"""

from __future__ import unicode_literals, absolute_import

from rattail.filemon import Action


class HandleBounceFile(Action):
    """
    Fully "handle" the given email message file, acting on it as
    needed, depending on whether or not it is actually considered
    to be a bounce etc.
    """
    
    def __call__(self, path, key='default', **kwargs):
        handler = self.app.get_bounce_handler(key)
        handler.handle_bounce_file(path)
