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
Master view for version tables
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy_continuum as continuum

from tailbone.views import MasterView
from tailbone.util import raw_datetime


class VersionMasterView(MasterView):
    """
    Base class for version master views
    """
    creatable = False
    editable = False
    deletable = False

    labels = {
        'transaction_issued_at': "Changed",
        'transaction_user': "Changed by",
        'transaction_id': "Transaction ID",
    }

    grid_columns = [
        'transaction_issued_at',
        'transaction_user',
        'version_parent',
        'transaction_id',
    ]

    def query(self, session):
        Transaction = continuum.transaction_class(self.true_model_class)

        query = session.query(self.model_class)\
                       .join(Transaction,
                             Transaction.id == self.model_class.transaction_id)

        return query

    def configure_grid(self, g):
        super(VersionMasterView, self).configure_grid(g)
        Transaction = continuum.transaction_class(self.true_model_class)

        g.set_sorter('transaction_issued_at', Transaction.issued_at)
        g.set_sorter('transaction_id', Transaction.id)
        g.set_sort_defaults('transaction_issued_at', 'desc')

        g.set_renderer('transaction_issued_at', self.render_transaction_issued_at)
        g.set_renderer('transaction_user', self.render_transaction_user)
        g.set_renderer('transaction_id', self.render_transaction_id)

        g.set_link('transaction_issued_at')
        g.set_link('transaction_user')
        g.set_link('version_parent')

    def render_transaction_issued_at(self, version, field):
        value = version.transaction.issued_at
        return raw_datetime(self.rattail_config, value)

    def render_transaction_user(self, version, field):
        return version.transaction.user

    def render_transaction_id(self, version, field):
        return version.transaction.id
