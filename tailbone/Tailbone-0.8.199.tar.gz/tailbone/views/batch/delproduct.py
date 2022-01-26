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
Views for "delete product" batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views.batch import BatchMasterView


class DeleteProductBatchView(BatchMasterView):
    """
    Master view for delete product batches.
    """
    model_class = model.DeleteProductBatch
    model_row_class = model.DeleteProductBatchRow
    default_handler_spec = 'rattail.batch.delproduct:DeleteProductBatchHandler'
    route_prefix = 'batch.delproduct'
    url_prefix = '/batches/delproduct'
    template_prefix = '/batch/delproduct'
    creatable = False
    bulk_deletable = True
    rows_bulk_deletable = True

    form_fields = [
        'id',
        'description',
        'notes',
        'inactivity_months',
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'pack_size',
        'department_name',
        'subdepartment_name',
        'present_in_scale',
        'date_created',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'product',
        'upc',
        'brand_name',
        'description',
        'size',
        'pack_size',
        'department_number',
        'department_name',
        'subdepartment_number',
        'subdepartment_name',
        'present_in_scale',
        'date_created',
        'status_code',
        'status_text',
    ]

    def template_kwargs_view(self, **kwargs):
        kwargs = super(DeleteProductBatchView, self).template_kwargs_view(**kwargs)
        batch = kwargs['batch']

        kwargs['rows_with_inventory'] = [row for row in batch.active_rows()
                                         if row.status_code == row.STATUS_HAS_INVENTORY]

        return kwargs

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'
        if row.status_code in (row.STATUS_DELETE_NOT_ALLOWED,
                               row.STATUS_HAS_INVENTORY,
                               row.STATUS_PENDING_CUSTOMER_ORDERS):
            return 'notice'

    def configure_row_grid(self, g):
        super(DeleteProductBatchView, self).configure_row_grid(g)

        # pack_size
        g.set_type('pack_size', 'quantity')

    def configure_row_form(self, f):
        super(DeleteProductBatchView, self).configure_row_form(f)
        row = f.model_instance

        # upc
        f.set_renderer('upc', self.render_upc)

        # pack_size
        f.set_type('pack_size', 'quantity')


def includeme(config):
    DeleteProductBatchView.defaults(config)
