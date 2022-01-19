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
Views for 'ordering' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import os
import json

import six
import openpyxl
from sqlalchemy import orm

from rattail.db import model, api
from rattail.core import Object
from rattail.time import localtime

from webhelpers2.html import tags

from tailbone.views.purchasing import PurchasingBatchView


class OrderingBatchView(PurchasingBatchView):
    """
    Master view for "ordering" batches.
    """
    route_prefix = 'ordering'
    url_prefix = '/ordering'
    model_title = "Ordering Batch"
    model_title_plural = "Ordering Batches"
    index_title = "Ordering"
    rows_editable = True
    has_worksheet = True

    labels = {
        'po_total_calculated': "PO Total",
    }

    form_fields = [
        'id',
        'store',
        'buyer',
        'vendor',
        'department',
        'purchase',
        'vendor_email',
        'vendor_fax',
        'vendor_contact',
        'vendor_phone',
        'date_ordered',
        'po_number',
        'po_total_calculated',
        'notes',
        'created',
        'created_by',
        'status_code',
        'complete',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'po_total_calculated': "PO Total",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        # 'item_id',
        'brand_name',
        'description',
        'size',
        'cases_ordered',
        'units_ordered',
        # 'cases_received',
        # 'units_received',
        'po_total_calculated',
        # 'invoice_total',
        # 'credits',
        'status_code',
    ]

    row_form_fields = [
        'item_entry',
        'item_id',
        'upc',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'po_line_number',
        'po_unit_cost',
        'po_total_calculated',
        'status_code',
    ]

    order_form_header_columns = [
        "UPC",
        "Brand",
        "Description",
        "Case",
        "Vend. Code",
        "Pref.",
        "Unit Cost",
    ]

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_ORDERING

    def configure_form(self, f):
        super(OrderingBatchView, self).configure_form(f)
        batch = f.model_instance

        # purchase
        if self.creating or not batch.executed or not batch.purchase:
            f.remove_field('purchase')

    def get_batch_kwargs(self, batch, **kwargs):
        kwargs = super(OrderingBatchView, self).get_batch_kwargs(batch, **kwargs)
        kwargs['ship_method'] = batch.ship_method
        kwargs['notes_to_vendor'] = batch.notes_to_vendor
        return kwargs

    def configure_row_form(self, f):
        """
        Supplements the default logic as follows:

        When editing, only these fields allow changes; all others are made
        read-only:

        * ``cases_ordered``
        * ``units_ordered``
        """
        super(OrderingBatchView, self).configure_row_form(f)

        # when editing, only certain fields should allow changes
        if self.editing:
            editable_fields = [
                'cases_ordered',
                'units_ordered',
            ]
            for field in f.fields:
                if field not in editable_fields:
                    f.set_readonly(field)

    def scanning_entry(self):
        """
        AJAX view to handle user entry/fetch input for "scanning" feature.
        """
        data = self.request.json_body
        app = self.get_rattail_app()
        prodder = app.get_products_handler()

        batch = self.get_instance()
        entry = data['entry']
        row = self.handler.quick_entry(self.Session(), batch, entry)

        uom = self.enum.UNIT_OF_MEASURE_EACH
        if row.product and row.product.weighed:
            uom = self.enum.UNIT_OF_MEASURE_POUND

        cases_ordered = None
        if row.cases_ordered:
            cases_ordered = float(row.cases_ordered)

        units_ordered = None
        if row.units_ordered:
            units_ordered = float(row.units_ordered)

        po_case_cost = None
        if row.po_unit_cost is not None:
            po_case_cost = row.po_unit_cost * (row.case_quantity or 1)

        product_url = None
        if row.product_uuid:
            product_url = self.request.route_url('products.view', uuid=row.product_uuid)

        product_price = None
        if row.product and row.product.regular_price:
            product_price = row.product.regular_price.price

        product_price_display = None
        if product_price is not None:
            product_price_display = app.render_currency(product_price)

        return {
            'ok': True,
            'entry': entry,
            'row': {
                'uuid': row.uuid,
                'item_id': row.item_id,
                'upc_display': row.upc.pretty() if row.upc else None,
                'brand_name': row.brand_name,
                'description': row.description,
                'size': row.size,
                'unit_of_measure_display': self.enum.UNIT_OF_MEASURE[uom],
                'case_quantity': float(row.case_quantity) if row.case_quantity is not None else None,
                'cases_ordered': cases_ordered,
                'units_ordered': units_ordered,
                'po_unit_cost': float(row.po_unit_cost) if row.po_unit_cost is not None else None,
                'po_unit_cost_display': app.render_currency(row.po_unit_cost),
                'po_case_cost': float(po_case_cost) if po_case_cost is not None else None,
                'po_case_cost_display': app.render_currency(po_case_cost),
                'image_url': prodder.get_image_url(upc=row.upc),
                'product_url': product_url,
                'product_price_display': product_price_display,
            },
        }

    def scanning_update(self):
        """
        AJAX view to handle row data updates for "scanning" feature.
        """
        data = self.request.json_body
        batch = self.get_instance()
        assert batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING
        assert not (batch.executed or batch.complete)

        uuid = data.get('row_uuid')
        row = self.Session.query(self.model_row_class).get(uuid) if uuid else None
        if not row:
            return {'error': "Row not found"}
        if row.batch is not batch or row.removed:
            return {'error': "Row is not active for batch"}

        self.handler.update_row_quantity(row, **data)
        return {'ok': True}

    def worksheet(self):
        """
        View for editing batch row data as an order form worksheet.
        """
        batch = self.get_instance()
        if batch.executed:
            return self.redirect(self.get_action_url('view', batch))

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
                departments.setdefault(department.uuid, department)
            else:
                if None not in departments:
                    department = Object(name='', number=None)
                    departments[None] = department
                department = departments[None]
            
            subdepartments = getattr(department, '_order_subdepartments', None)
            if subdepartments is None:
                subdepartments = department._order_subdepartments = {}

            subdepartment = cost.product.subdepartment
            if subdepartment:
                subdepartments.setdefault(subdepartment.uuid, subdepartment)
            else:
                if None not in subdepartments:
                    subdepartment = Object(name=None, number=None)
                    subdepartments[None] = subdepartment
                subdepartment = subdepartments[None]

            subdept_costs = getattr(subdepartment, '_order_costs', None)
            if subdept_costs is None:
                subdept_costs = subdepartment._order_costs = []
            subdept_costs.append(cost)
            cost._batchrow = order_items.get(cost.product_uuid)

        # fetch recent purchase history, sort/pad for template convenience
        history = self.handler.get_order_form_history(batch, costs, 6)
        for i in range(6 - len(history)):
            history.append(None)
        history = list(reversed(history))

        title = self.get_instance_title(batch)
        order_date = batch.date_ordered
        if not order_date:
            order_date = localtime(self.rattail_config).date()

        buefy_data = None
        if self.get_use_buefy():
            buefy_data = self.get_worksheet_buefy_data(departments)

        return self.render_to_response('worksheet', {
            'batch': batch,
            'order_date': order_date,
            'instance': batch,
            'instance_title': title,
            'instance_url': self.get_action_url('view', batch),
            'vendor': batch.vendor,
            'departments': departments,
            'history': history,
            'get_upc': lambda p: p.upc.pretty() if p.upc else '',
            'header_columns': self.order_form_header_columns,
            'ignore_cases': not self.handler.allow_cases(),
            'worksheet_data': buefy_data,
        })

    def get_worksheet_buefy_data(self, departments):
        data = {}
        for department in six.itervalues(departments):
            for subdepartment in six.itervalues(department._order_subdepartments):
                for i, cost in enumerate(subdepartment._order_costs, 1):
                    cases = int(cost._batchrow.cases_ordered or 0) if cost._batchrow else None
                    units = int(cost._batchrow.units_ordered or 0) if cost._batchrow else None
                    key = 'cost_{}'.format(cost.uuid)
                    data['{}_cases'.format(key)] = cases
                    data['{}_units'.format(key)] = units

                    total = 0
                    row = cost._batchrow
                    if row:
                        total = row.po_total_calculated or row.po_total or 0
                    if not (total or cases or units):
                        display = ''
                    else:
                        display = '${:0,.2f}'.format(total)
                    data['{}_total_display'.format(key)] = display

        return data

    def worksheet_update(self):
        """
        Handles AJAX requests to update the order quantities for some row
        within the current batch, from the worksheet view.  POST data should
        include:

        * ``product_uuid``
        * ``cases_ordered``
        * ``units_ordered``

        If a row already exists for the given product, it will be updated;
        otherwise a new row is created for the product and then that is
        updated.  The handler's
        :meth:`~rattail:rattail.batch.purchase.PurchaseBatchHandler.update_row_quantity()`
        method is invoked to update the row.

        However, if both of the quantities given are empty, and a row exists
        for the given product, then that row is removed from the batch, instead
        of being updated.  If a matching row is not found, it will not be
        created.
        """
        batch = self.get_instance()

        try:
            data = self.request.json_body
        except json.JSONDecodeError:
            data = self.request.POST

        cases_ordered = data.get('cases_ordered')
        if cases_ordered is None:
            cases_ordered = 0
        elif not isinstance(cases_ordered, int):
            if cases_ordered == '':
                cases_ordered = 0
            else:
                cases_ordered = int(cases_ordered)
        if cases_ordered >= 100000: # TODO: really this depends on underlying column
            return {'error': "Invalid value for cases ordered: {}".format(cases_ordered)}

        units_ordered = data.get('units_ordered')
        if units_ordered is None:
            units_ordered = 0
        elif not isinstance(units_ordered, int):
            if units_ordered == '':
                units_ordered = 0
            else:
                units_ordered = int(units_ordered)
        if units_ordered >= 100000: # TODO: really this depends on underlying column
            return {'error': "Invalid value for units ordered: {}".format(units_ordered)}

        uuid = data.get('product_uuid')
        product = self.Session.query(model.Product).get(uuid) if uuid else None
        if not product:
            return {'error': "Product not found"}

        # first we find out which existing row(s) match the given product
        matches = [row for row in batch.active_rows()
                   if row.product_uuid == product.uuid]
        if matches and len(matches) != 1:
            raise RuntimeError("found too many ({}) matches for product {} in batch {}".format(
                len(matches), product.uuid, batch.uuid))

        row = None
        if cases_ordered or units_ordered:

            # make a new row if necessary
            if matches:
                row = matches[0]
            else:
                row = self.handler.make_row()
                row.product = product
                self.handler.add_row(batch, row)

            # update row quantities
            try:
                self.handler.update_row_quantity(row, cases_ordered=cases_ordered,
                                                 units_ordered=units_ordered)
            except Exception as error:
                return {'error': six.text_type(error)}

        else: # empty order quantities

            # remove row if present
            if matches:
                row = matches[0]
                self.handler.do_remove_row(row)
                row = None

        return {
            'row_cases_ordered': int(row.cases_ordered or 0) if row else None,
            'row_units_ordered': int(row.units_ordered or 0) if row else None,
            'row_po_total': '${:0,.2f}'.format(row.po_total or 0) if row else None,
            'row_po_total_calculated': '${:0,.2f}'.format(row.po_total_calculated or 0) if row else None,
            'row_po_total_display': '${:0,.2f}'.format(row.po_total_calculated or row.po_total or 0) if row else None,
            'batch_po_total': '${:0,.2f}'.format(batch.po_total or 0),
            'batch_po_total_calculated': '${:0,.2f}'.format(batch.po_total_calculated or 0),
            'batch_po_total_display': '${:0,.2f}'.format(batch.po_total_calculated or batch.po_total or 0),
        }

    def download_excel(self):
        """
        Download ordering batch as Excel spreadsheet.
        """
        batch = self.get_instance()

        # populate Excel worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Purchase Order"
        worksheet.append(["Store", "Vendor", "Date ordered"])
        worksheet.append([batch.store.name, batch.vendor.name, batch.date_ordered.strftime('%m/%d/%Y')])
        worksheet.append([])
        worksheet.append(['vendor_code', 'upc', 'brand_name', 'description', 'cases_ordered', 'units_ordered'])
        for row in batch.active_rows():
            worksheet.append([row.vendor_code, six.text_type(row.upc), row.brand_name,
                              '{} {}'.format(row.description, row.size),
                              row.cases_ordered, row.units_ordered])

        # write Excel file to batch data dir
        filedir = batch.filedir(self.rattail_config)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        filename = 'PO.{}.xlsx'.format(batch.id_str)
        path = batch.filepath(self.rattail_config, filename)
        workbook.save(path)

        return self.file_response(path)

    def get_execute_success_url(self, batch, result, **kwargs):
        if isinstance(result, model.Purchase):
            return self.request.route_url('purchases.view', uuid=result.uuid)
        return super(OrderingBatchView, self).get_execute_success_url(batch, result, **kwargs)

    @classmethod
    def defaults(cls, config):
        cls._ordering_defaults(config)
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)

    @classmethod
    def _ordering_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix permission group label
        config.add_tailbone_permission_group(permission_prefix, model_title_plural,
                                             overwrite=False)

        # scanning entry
        config.add_route('{}.scanning_entry'.format(route_prefix), '{}/scanning-entry'.format(instance_url_prefix))
        config.add_view(cls, attr='scanning_entry', route_name='{}.scanning_entry'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix),
                        renderer='json')

        # scanning update
        config.add_route('{}.scanning_update'.format(route_prefix), '{}/scanning-update'.format(instance_url_prefix))
        config.add_view(cls, attr='scanning_update', route_name='{}.scanning_update'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix),
                        renderer='json')

        # download as Excel
        config.add_route('{}.download_excel'.format(route_prefix), '{}/excel'.format(instance_url_prefix))
        config.add_view(cls, attr='download_excel', route_name='{}.download_excel'.format(route_prefix),
                        permission='{}.download_excel'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{}.download_excel'.format(permission_prefix),
                                       "Download {} as Excel".format(model_title))


def includeme(config):
    OrderingBatchView.defaults(config)
