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
Views for 'creating' customer order batches

Note that this provides only the "direct" or "raw" table views for these
batches.  This does *not* provide a way to create a new batch; you should see
:meth:`tailbone.views.custorders.orders.CustomerOrdersView.create()` for that
logic.
"""

from __future__ import unicode_literals, absolute_import

from tailbone.views.custorders.batch import CustomerOrderBatchView


class CreateCustomerOrderBatchView(CustomerOrderBatchView):
    """
    Master view for "creating customer order" batches.
    """
    route_prefix = 'new_custorders'
    url_prefix = '/new-customer-orders'
    model_title = "New Customer Order"
    model_title_plural = "New Customer Orders"
    creatable = False


def includeme(config):
    CreateCustomerOrderBatchView.defaults(config)
