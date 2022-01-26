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
Tailbone Web API - Ordering Batches

These views expose the basic CRUD interface to "ordering" batches, for the web
API.
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.core import Object
from rattail.db import model
from rattail.util import pretty_quantity

from cornice import Service

from tailbone.api.batch import APIBatchView, APIBatchRowView


class OrderingBatchViews(APIBatchView):

    model_class = model.PurchaseBatch
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    route_prefix = 'orderingbatchviews'
    permission_prefix = 'ordering'
    collection_url_prefix = '/ordering-batches'
    object_url_prefix = '/ordering-batch'
    supports_toggle_complete = True
    supports_execute = True

    def base_query(self):
        """
        Modifies the default logic as follows:

        Adds a condition to the query, to ensure only purchase batches with
        "ordering" mode are returned.
        """
        query = super(OrderingBatchViews, self).base_query()
        query = query.filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING)
        return query

    def normalize(self, batch):
        data = super(OrderingBatchViews, self).normalize(batch)

        data['vendor_uuid'] = batch.vendor.uuid
        data['vendor_display'] = six.text_type(batch.vendor)

        data['department_uuid'] = batch.department_uuid
        data['department_display'] = six.text_type(batch.department) if batch.department else None

        data['po_total_calculated_display'] = "${:0.2f}".format(batch.po_total_calculated or 0)
        data['ship_method'] = batch.ship_method
        data['notes_to_vendor'] = batch.notes_to_vendor
        return data

    def create_object(self, data):
        """
        Modifies the default logic as follows:

        Sets the mode to "ordering" for the new batch.
        """
        data = dict(data)
        data['mode'] = self.enum.PURCHASE_BATCH_MODE_ORDERING
        batch = super(OrderingBatchViews, self).create_object(data)
        return batch

    def worksheet(self):
        """
        Returns primary data for the Ordering Worksheet view.
        """
        batch = self.get_object()
        if batch.executed:
            raise self.forbidden()

        # TODO: much of the logic below was copied from the traditional master
        # view for ordering batches.  should maybe let them share it somehow?

        # organize existing batch rows by product
        order_items = {}
        for row in batch.active_rows():
            order_items[row.product_uuid] = row

        # organize vendor catalog costs by dept / subdept
        departments = {}
        costs = self.handler.get_order_form_costs(self.Session(), batch.vendor)
        costs = self.handler.sort_order_form_costs(costs)
        costs = list(costs)   # we must have a stable list for the rest of this
        self.handler.decorate_order_form_costs(batch, costs)
        for cost in costs:

            department = cost.product.department
            if department:
                department_dict = departments.setdefault(department.uuid, {
                    'uuid': department.uuid,
                    'number': department.number,
                    'name': department.name,
                })
            else:
                if None not in departments:
                    departments[None] = {
                        'uuid': None,
                        'number': None,
                        'name': "",
                    }
                department_dict = departments[None]

            subdepartments = department_dict.setdefault('subdepartments', {})

            subdepartment = cost.product.subdepartment
            if subdepartment:
                subdepartment_dict = subdepartments.setdefault(subdepartment.uuid, {
                    'uuid': subdepartment.uuid,
                    'number': subdepartment.number,
                    'name': subdepartment.name,
                })
            else:
                if None not in subdepartments:
                    subdepartments[None] = {
                        'uuid': None,
                        'number': None,
                        'name': "",
                    }
                subdepartment_dict = subdepartments[None]

            subdept_costs = subdepartment_dict.setdefault('costs', [])
            product = cost.product
            subdept_costs.append({
                'uuid': cost.uuid,
                'upc': six.text_type(product.upc),
                'upc_pretty': product.upc.pretty() if product.upc else None,
                'brand_name': product.brand.name if product.brand else None,
                'description': product.description,
                'size': product.size,
                'case_size': cost.case_size,
                'uom_display': "LB" if product.weighed else "EA",
                'vendor_item_code': cost.code,
                'preference': cost.preference,
                'preferred': cost.preference == 1,
                'unit_cost': cost.unit_cost,
                'unit_cost_display': "${:0.2f}".format(cost.unit_cost) if cost.unit_cost is not None else "",
                # TODO
                # 'cases_ordered': None,
                # 'units_ordered': None,
                # 'po_total': None,
                # 'po_total_display': None,
            })

        # sort the (sub)department groupings
        sorted_departments = []
        for dept in sorted(six.itervalues(departments), key=lambda d: d['name']):
            dept['subdepartments'] = sorted(six.itervalues(dept['subdepartments']),
                                            key=lambda s: s['name'])
            sorted_departments.append(dept)

        # fetch recent purchase history, sort/pad for template convenience
        history = self.handler.get_order_form_history(batch, costs, 6)
        for i in range(6 - len(history)):
            history.append(None)
        history = list(reversed(history))

        return {
            'batch': self.normalize(batch),
            'departments': departments,
            'sorted_departments': sorted_departments,
            'history': history,
        }

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._batch_defaults(config)
        cls._ordering_batch_defaults(config)

    @classmethod
    def _ordering_batch_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        object_url_prefix = cls.get_object_url_prefix()

        # worksheet
        worksheet = Service(name='{}.worksheet'.format(route_prefix),
                            path='{}/{{uuid}}/worksheet'.format(object_url_prefix))
        worksheet.add_view('GET', 'worksheet', klass=cls,
                           permission='{}.worksheet'.format(permission_prefix))
        config.add_cornice_service(worksheet)


class OrderingBatchRowViews(APIBatchRowView):

    model_class = model.PurchaseBatchRow
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    route_prefix = 'ordering.rows'
    permission_prefix = 'ordering'
    collection_url_prefix = '/ordering-batch-rows'
    object_url_prefix = '/ordering-batch-row'
    supports_quick_entry = True
    editable = True

    def normalize(self, row):
        batch = row.batch
        data = super(OrderingBatchRowViews, self).normalize(row)

        data['item_id'] = row.item_id
        data['upc'] = six.text_type(row.upc)
        data['upc_pretty'] = row.upc.pretty() if row.upc else None
        data['brand_name'] = row.brand_name
        data['description'] = row.description
        data['size'] = row.size
        data['full_description'] = row.product.full_description if row.product else row.description

        # # only provide image url if so configured
        # if self.rattail_config.getbool('rattail.batch', 'purchase.mobile_images', default=True):
        #     data['image_url'] = pod.get_image_url(self.rattail_config, row.upc) if row.upc else None

        # unit_uom can vary by product
        data['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'

        data['case_quantity'] = row.case_quantity
        data['cases_ordered'] = row.cases_ordered
        data['units_ordered'] = row.units_ordered
        data['cases_ordered_display'] = pretty_quantity(row.cases_ordered or 0, empty_zero=False)
        data['units_ordered_display'] = pretty_quantity(row.units_ordered or 0, empty_zero=False)

        data['po_unit_cost'] = row.po_unit_cost
        data['po_unit_cost_display'] = "${:0.2f}".format(row.po_unit_cost) if row.po_unit_cost is not None else None
        data['po_total_calculated'] = row.po_total_calculated
        data['po_total_calculated_display'] = "${:0.2f}".format(row.po_total_calculated) if row.po_total_calculated is not None else None
        data['status_code'] = row.status_code
        data['status_display'] = row.STATUS.get(row.status_code, six.text_type(row.status_code))

        return data

    def update_object(self, row, data):
        """
        Overrides the default logic as follows:

        So far, we only allow updating the ``cases_ordered`` and/or
        ``units_ordered`` quantities; therefore ``data`` should have one or
        both of those keys.

        This data is then passed to the
        :meth:`~rattail:rattail.batch.purchase.PurchaseBatchHandler.update_row_quantity()`
        method of the batch handler.

        Note that the "normal" logic for this method is not invoked at all.
        """
        if not self.handler.is_mutable(row.batch):
            return {'error': "Batch is not mutable"}

        self.handler.update_row_quantity(row, **data)
        return row


def includeme(config):
    OrderingBatchViews.defaults(config)
    OrderingBatchRowViews.defaults(config)
