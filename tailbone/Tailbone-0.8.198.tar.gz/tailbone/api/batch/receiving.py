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
Tailbone Web API - Receiving Batches
"""

from __future__ import unicode_literals, absolute_import

import logging

import six
import humanize

from rattail.db import model
from rattail.time import make_utc
from rattail.util import pretty_quantity

from deform import widget as dfwidget

from tailbone import forms
from tailbone.api.batch import APIBatchView, APIBatchRowView
from tailbone.forms.receiving import ReceiveRow


log = logging.getLogger(__name__)


class ReceivingBatchViews(APIBatchView):

    model_class = model.PurchaseBatch
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    route_prefix = 'receivingbatchviews'
    permission_prefix = 'receiving'
    collection_url_prefix = '/receiving-batches'
    object_url_prefix = '/receiving-batch'
    supports_toggle_complete = True
    supports_execute = True

    def base_query(self):
        query = super(ReceivingBatchViews, self).base_query()
        query = query.filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)
        return query

    def normalize(self, batch):
        data = super(ReceivingBatchViews, self).normalize(batch)

        data['vendor_uuid'] = batch.vendor.uuid
        data['vendor_display'] = six.text_type(batch.vendor)

        data['department_uuid'] = batch.department_uuid
        data['department_display'] = six.text_type(batch.department) if batch.department else None

        data['po_total'] = batch.po_total
        data['invoice_total'] = batch.invoice_total
        data['invoice_total_calculated'] = batch.invoice_total_calculated

        return data

    def create_object(self, data):
        data = dict(data)
        data['mode'] = self.enum.PURCHASE_BATCH_MODE_RECEIVING
        batch = super(ReceivingBatchViews, self).create_object(data)
        return batch

    def mark_receiving_complete(self):
        """
        Mark the given batch as "receiving complete".
        """
        batch = self.get_object()

        if batch.executed:
            return {'error': "Batch {} has already been executed: {}".format(
                batch.id_str, batch.description)}

        if batch.complete:
            return {'error': "Batch {} is already marked complete: {}".format(
                batch.id_str, batch.description)}

        if batch.receiving_complete:
            return {'error': "Receiving is already complete for batch {}: {}".format(
                batch.id_str, batch.description)}

        batch.receiving_complete = True
        return self._get(obj=batch)

    def eligible_purchases(self):
        uuid = self.request.params.get('vendor_uuid')
        vendor = self.Session.query(model.Vendor).get(uuid) if uuid else None
        if not vendor:
            return {'error': "Vendor not found"}

        purchases = self.handler.get_eligible_purchases(
            vendor, self.enum.PURCHASE_BATCH_MODE_RECEIVING)

        purchases = [self.normalize_eligible_purchase(p)
                     for p in purchases]

        return {'purchases': purchases}

    def normalize_eligible_purchase(self, purchase):
        return self.handler.normalize_eligible_purchase(purchase)

    def render_eligible_purchase(self, purchase):
        return self.handler.render_eligible_purchase(purchase)

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._batch_defaults(config)
        cls._receiving_batch_defaults(config)

    @classmethod
    def _receiving_batch_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        collection_url_prefix = cls.get_collection_url_prefix()
        object_url_prefix = cls.get_object_url_prefix()

        # mark receiving complete
        config.add_route('{}.mark_receiving_complete'.format(route_prefix), '{}/{{uuid}}/mark-receiving-complete'.format(object_url_prefix))
        config.add_view(cls, attr='mark_receiving_complete', route_name='{}.mark_receiving_complete'.format(route_prefix),
                        permission='{}.edit'.format(permission_prefix),
                        renderer='json')

        # eligible purchases
        config.add_route('{}.eligible_purchases'.format(route_prefix), '{}/eligible-purchases'.format(collection_url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='eligible_purchases', route_name='{}.eligible_purchases'.format(route_prefix),
                        permission='{}.create'.format(permission_prefix),
                        renderer='json')


class ReceivingBatchRowViews(APIBatchRowView):

    model_class = model.PurchaseBatchRow
    default_handler_spec = 'rattail.batch.purchase:PurchaseBatchHandler'
    route_prefix = 'receiving.rows'
    permission_prefix = 'receiving'
    collection_url_prefix = '/receiving-batch-rows'
    object_url_prefix = '/receiving-batch-row'
    supports_quick_entry = True

    def make_filter_spec(self):
        filters = super(ReceivingBatchRowViews, self).make_filter_spec()
        if filters:

            # must translate certain convenience filters
            orig_filters, filters = filters, []
            for filtr in orig_filters:

                # # is_received
                # # NOTE: this is only relevant for truck dump or "from scratch"
                # if filtr['field'] == 'is_received' and filtr['op'] == 'eq' and filtr['value'] is True:
                #     filters.extend([
                #         {'or': [
                #             {'field': 'cases_received', 'op': '!=', 'value': 0},
                #             {'field': 'units_received', 'op': '!=', 'value': 0},
                #         ]},
                #     ])

                # is_incomplete
                if filtr['field'] == 'is_incomplete' and filtr['op'] == 'eq' and filtr['value'] is True:
                    # looking for any rows with "ordered" quantity, but where the
                    # status does *not* signify a "settled" row so to speak
                    # TODO: would be nice if we had a simple flag to leverage?
                    filters.extend([
                        {'or': [
                            {'field': 'cases_ordered', 'op': '!=', 'value': 0},
                            {'field': 'units_ordered', 'op': '!=', 'value': 0},
                        ]},
                        {'field': 'status_code', 'op': 'not_in', 'value': [
                            model.PurchaseBatchRow.STATUS_OK,
                            model.PurchaseBatchRow.STATUS_PRODUCT_NOT_FOUND,
                            model.PurchaseBatchRow.STATUS_CASE_QUANTITY_DIFFERS,
                        ]},
                    ])

                # is_invalid
                elif filtr['field'] == 'is_invalid' and filtr['op'] == 'eq' and filtr['value'] is True:
                    filters.extend([
                        {'field': 'status_code', 'op': 'in', 'value': [
                            model.PurchaseBatchRow.STATUS_PRODUCT_NOT_FOUND,
                            model.PurchaseBatchRow.STATUS_COST_NOT_FOUND,
                            model.PurchaseBatchRow.STATUS_CASE_QUANTITY_UNKNOWN,
                            model.PurchaseBatchRow.STATUS_CASE_QUANTITY_DIFFERS,
                        ]},
                    ])

                # is_unexpected
                elif filtr['field'] == 'is_unexpected' and filtr['op'] == 'eq' and filtr['value'] is True:
                    # looking for any rows which do *not* have "ordered/shipped" quantity
                    filters.extend([
                        {'and': [
                            {'or': [
                                {'field': 'cases_ordered', 'op': 'is_null'},
                                {'field': 'cases_ordered', 'op': '==', 'value': 0},
                            ]},
                            {'or': [
                                {'field': 'units_ordered', 'op': 'is_null'},
                                {'field': 'units_ordered', 'op': '==', 'value': 0},
                            ]},
                            {'or': [
                                {'field': 'cases_shipped', 'op': 'is_null'},
                                {'field': 'cases_shipped', 'op': '==', 'value': 0},
                            ]},
                            {'or': [
                                {'field': 'units_shipped', 'op': 'is_null'},
                                {'field': 'units_shipped', 'op': '==', 'value': 0},
                            ]},
                            {'or': [
                                # but "unexpected" also implies we have some confirmed amount(s)
                                {'field': 'cases_received', 'op': '!=', 'value': 0},
                                {'field': 'units_received', 'op': '!=', 'value': 0},
                                {'field': 'cases_damaged', 'op': '!=', 'value': 0},
                                {'field': 'units_damaged', 'op': '!=', 'value': 0},
                                {'field': 'cases_expired', 'op': '!=', 'value': 0},
                                {'field': 'units_expired', 'op': '!=', 'value': 0},
                            ]},
                        ]},
                    ])

                # is_damaged
                elif filtr['field'] == 'is_damaged' and filtr['op'] == 'eq' and filtr['value'] is True:
                    filters.extend([
                        {'or': [
                            {'field': 'cases_damaged', 'op': '!=', 'value': 0},
                            {'field': 'units_damaged', 'op': '!=', 'value': 0},
                        ]},
                    ])

                # is_expired
                elif filtr['field'] == 'is_expired' and filtr['op'] == 'eq' and filtr['value'] is True:
                    filters.extend([
                        {'or': [
                            {'field': 'cases_expired', 'op': '!=', 'value': 0},
                            {'field': 'units_expired', 'op': '!=', 'value': 0},
                        ]},
                    ])

                else: # just some filter, use as-is
                    filters.append(filtr)

        return filters

    def normalize(self, row):
        data = super(ReceivingBatchRowViews, self).normalize(row)

        batch = row.batch
        app = self.get_rattail_app()
        prodder = app.get_products_handler()

        data['product_uuid'] = row.product_uuid
        data['item_id'] = row.item_id
        data['upc'] = six.text_type(row.upc)
        data['upc_pretty'] = row.upc.pretty() if row.upc else None
        data['brand_name'] = row.brand_name
        data['description'] = row.description
        data['size'] = row.size
        data['full_description'] = row.product.full_description if row.product else row.description

        # only provide image url if so configured
        if self.rattail_config.getbool('rattail.batch', 'purchase.mobile_images', default=True):
            data['image_url'] = prodder.get_image_url(product=row.product, upc=row.upc)

        # unit_uom can vary by product
        data['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'

        data['case_quantity'] = row.case_quantity
        data['order_quantities_known'] = batch.order_quantities_known

        data['cases_ordered'] = row.cases_ordered
        data['units_ordered'] = row.units_ordered

        data['cases_shipped'] = row.cases_shipped
        data['units_shipped'] = row.units_shipped

        data['cases_received'] = row.cases_received
        data['units_received'] = row.units_received

        data['cases_damaged'] = row.cases_damaged
        data['units_damaged'] = row.units_damaged

        data['cases_expired'] = row.cases_expired
        data['units_expired'] = row.units_expired

        data['po_unit_cost'] = row.po_unit_cost
        data['po_total'] = row.po_total

        data['invoice_unit_cost'] = row.invoice_unit_cost
        data['invoice_total'] = row.invoice_total
        data['invoice_total_calculated'] = row.invoice_total_calculated

        data['allow_cases'] = self.handler.allow_cases()

        data['quick_receive'] = self.rattail_config.getbool(
            'rattail.batch', 'purchase.mobile_quick_receive',
            default=True)

        if batch.order_quantities_known:
            data['quick_receive_all'] = self.rattail_config.getbool(
                'rattail.batch', 'purchase.mobile_quick_receive_all',
                default=False)

        # TODO: this was copied from regular view receive_row() method; should merge
        if data['quick_receive'] and data.get('quick_receive_all'):
            if data['allow_cases']:
                data['quick_receive_uom'] = 'CS'
                raise NotImplementedError("TODO: add CS support for quick_receive_all")
            else:
                data['quick_receive_uom'] = data['unit_uom']
                accounted_for = self.handler.get_units_accounted_for(row)
                remainder = self.handler.get_units_ordered(row) - accounted_for

                if accounted_for:
                    # some product accounted for; button should receive "remainder" only
                    if remainder:
                        remainder = pretty_quantity(remainder)
                        data['quick_receive_quantity'] = remainder
                        data['quick_receive_text'] = "Receive Remainder ({} {})".format(
                            remainder, data['unit_uom'])
                    else:
                        # unless there is no remainder, in which case disable it
                        data['quick_receive'] = False

                else: # nothing yet accounted for, button should receive "all"
                    if not remainder:
                        log.warning("quick receive remainder is empty for row %s", row.uuid)
                    remainder = pretty_quantity(remainder)
                    data['quick_receive_quantity'] = remainder
                    data['quick_receive_text'] = "Receive ALL ({} {})".format(
                        remainder, data['unit_uom'])

        data['unexpected_alert'] = None
        if batch.order_quantities_known and not row.cases_ordered and not row.units_ordered:
            warn = True
            if batch.is_truck_dump_parent() and row.product:
                uuids = [child.uuid for child in batch.truck_dump_children]
                if uuids:
                    count = self.Session.query(model.PurchaseBatchRow)\
                                        .filter(model.PurchaseBatchRow.batch_uuid.in_(uuids))\
                                        .filter(model.PurchaseBatchRow.product == row.product)\
                                        .count()
                    if count:
                        warn = False
            if warn:
                data['unexpected_alert'] = "This item was NOT on the original purchase order."

        # TODO: surely the caller of API should determine this flag?
        # maybe alert user if they've already received some of this product
        alert_received = self.rattail_config.getbool('tailbone', 'receiving.alert_already_received',
                                                     default=False)
        if alert_received:
            data['received_alert'] = None
            if self.handler.get_units_confirmed(row):
                msg = "You have already received some of this product; last update was {}.".format(
                    humanize.naturaltime(make_utc() - row.modified))
                data['received_alert'] = msg

        return data

    def receive(self):
        """
        View which handles "receiving" against a particular batch row.
        """
        # first do basic input validation
        schema = ReceiveRow().bind(session=self.Session())
        form = forms.Form(schema=schema, request=self.request)
        # TODO: this seems hacky, but avoids "complex" date value parsing
        form.set_widget('expiration_date', dfwidget.TextInputWidget())
        if not form.validate(newstyle=True):
            log.debug("form did not validate: %s",
                      form.make_deform_form().error)
            return {'error': "Form did not validate"}

        # fetch / validate row object
        row = self.Session.query(model.PurchaseBatchRow).get(form.validated['row'])
        if row is not self.get_object():
            return {'error': "Specified row does not match the route!"}

        # handler takes care of the row receiving logic for us
        kwargs = dict(form.validated)
        del kwargs['row']
        self.handler.receive_row(row, **kwargs)

        self.Session.flush()
        return self._get(obj=row)

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._batch_row_defaults(config)
        cls._receiving_batch_row_defaults(config)

    @classmethod
    def _receiving_batch_row_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        object_url_prefix = cls.get_object_url_prefix()

        # receive (row)
        config.add_route('{}.receive'.format(route_prefix), '{}/{{uuid}}/receive'.format(object_url_prefix),
                         request_method=('OPTIONS', 'POST'))
        config.add_view(cls, attr='receive', route_name='{}.receive'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix),
                        renderer='json')


def includeme(config):
    ReceivingBatchViews.defaults(config)
    ReceivingBatchRowViews.defaults(config)
