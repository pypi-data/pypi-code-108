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
Raw Permission Views
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model

from tailbone.views import MasterView


class PermissionView(MasterView):
    """
    Master view for the permissions model.
    """
    model_class = model.Permission
    model_title = "Raw Permission"
    editable = False
    bulk_deletable = True

    grid_columns = [
        'role',
        'permission',
    ]

    def query(self, session):
        model = self.model
        query = super(PermissionView, self).query(session)
        query = query.options(orm.joinedload(model.Permission.role))
        return query


def includeme(config):
    PermissionView.defaults(config)
