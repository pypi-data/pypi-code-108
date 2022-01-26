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
Rattail -> Rattail "local" data import
"""

from __future__ import unicode_literals, absolute_import

from rattail import importing


class FromRattailLocalToRattail(importing.FromRattailHandler, importing.ToSQLAlchemyHandler):
    """
    Common base class for import handlers which read data from the Rattail DB
    for the sake of updating misc. other tables in that same DB.
    """
    host_title = "Rattail (default)"
    local_title = "Rattail (default)"

    def begin_local_transaction(self):
        self.session = self.host_session

        # ToRattailHandler would do this for us, but alas..we copy/pasted this
        if hasattr(self, 'runas_username') and self.runas_username:
            self.session.set_continuum_user(self.runas_username)

    def rollback_transaction(self):
        self.rollback_host_transaction()

    def commit_transaction(self):
        self.commit_host_transaction()


class FromRattailLocal(importing.FromSQLAlchemy):
    """
    Common base class for the "host" side of importers which read data from the
    Rattail DB for the sake of updating misc. other tables in that same DB.
    """
