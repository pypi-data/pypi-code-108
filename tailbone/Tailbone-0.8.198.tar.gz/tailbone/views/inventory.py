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
Views for inventory batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import colander

from tailbone.views import MasterView


class InventoryAdjustmentReasonView(MasterView):
    """
    Master view for inventory adjustment reasons.
    """
    model_class = model.InventoryAdjustmentReason
    route_prefix = 'invadjust_reasons'
    url_prefix = '/inventory-adjustment-reasons'

    grid_columns = [
        'code',
        'description',
        'hidden',
    ]

    def configure_grid(self, g):
        super(InventoryAdjustmentReasonView, self).configure_grid(g)
        g.set_sort_defaults('code')

    def configure_form(self, f):
        super(InventoryAdjustmentReasonView, self).configure_form(f)

        # code
        f.set_validator('code', self.unique_code)

    def unique_code(self, node, value):
        query = self.Session.query(model.InventoryAdjustmentReason)\
                            .filter(model.InventoryAdjustmentReason.code == value)
        if self.editing:
            reason = self.get_instance()
            query = query.filter(model.InventoryAdjustmentReason.uuid != reason.uuid)
        if query.count():
            raise colander.Invalid(node, "Code must be unique")

# TODO: deprecate / remove this
InventoryAdjustmentReasonsView = InventoryAdjustmentReasonView


def includeme(config):
    InventoryAdjustmentReasonView.defaults(config)
