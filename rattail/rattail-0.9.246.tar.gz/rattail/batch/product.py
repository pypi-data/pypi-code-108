# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Handler for generic product batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.batch import BatchHandler


class ProductBatchHandler(BatchHandler):
    """
    Handler for generic product batches.
    """
    batch_model_class = model.ProductBatch

    def should_populate(self, batch):
        if batch.input_filename:
            return True
        return False

    def populate(self, batch, progress=None):
        if batch.input_filename:
            return self.populate_from_file(batch, progress=progress)

    def populate_from_file(self, batch, progress=None):
        raise NotImplementedError

    def refresh_row(self, row):
        if not row.product:
            if not row.item_entry:
                row.status_code = row.STATUS_MISSING_KEY
                return

            session = self.app.get_session(row)
            # nb. we prefer a GPC lookup if one is present
            row.product = self.locate_product_for_entry(session,
                                                        row.upc or row.item_entry)
            if not row.product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        self.refresh_product_basics(row)
        product = row.product

        row.department = product.department
        row.subdepartment = product.subdepartment
        row.category = product.category
        row.family = product.family
        row.reportcode = product.report_code

        cost = product.cost
        row.vendor = cost.vendor if cost else None
        row.vendor_item_code = cost.code if cost else None
        row.regular_cost = cost.unit_cost if cost else None
        row.current_cost = cost.discount_cost if cost else None
        row.current_cost_starts = cost.discount_starts if row.current_cost else None
        row.current_cost_ends = cost.discount_ends if row.current_cost else None

        regprice = product.regular_price
        curprice = product.current_price
        sugprice = product.suggested_price
        row.regular_price = regprice.price if regprice else None
        row.current_price = curprice.price if curprice else None
        row.current_price_starts = curprice.starts if curprice else None
        row.current_price_ends = curprice.ends if curprice else None
        row.suggested_price = sugprice.price if sugprice else None

        row.status_code = row.STATUS_OK

    def describe_execution(self, batch, **kwargs):
        return ("A new batch will be created, using the items from this one.  "
                "Type of the new batch depends on your choice of action.")

    def execute(self, batch, user=None, action='make_label_batch', progress=None, **kwargs):

        if action == 'make_label_batch':
            result = self.make_label_batch(batch, user, progress=progress)

        elif action == 'make_pricing_batch':
            result = self.make_pricing_batch(batch, user, progress=progress)

        else:
            raise RuntimeError("Batch execution action is not supported: {}".format(action))

        return result

    def make_label_batch(self, product_batch, user, progress=None,
                         **kwargs):
        """
        Make a new Label Batch from the given Product Batch.

        :param product_batch: Reference to a
           :class:`~rattail.db.model.batch.product.ProductBatch`
           instance from which a new label batch should be made.

        :param user: :class:`~rattail.db.model.users.User` who is
           responsible for this action.

        :returns: A new
           :class:`~rattail.db.model.batch.labels.LabelBatch`
           instance, populated from the given product batch.
        """
        handler = self.app.get_batch_handler(
            'labels', default='rattail.batch.labels:LabelBatchHandler')
        session = self.app.get_session(product_batch)
        kwargs.setdefault('description', product_batch.description)
        kwargs.setdefault('notes', product_batch.notes)
        label_batch = handler.make_batch(session, created_by=user,
                                         **kwargs)
        label_batch.product_batch = product_batch
        handler.do_populate(label_batch, user, progress=progress)
        return label_batch

    def make_pricing_batch(self, product_batch, user, progress=None,
                           **kwargs):
        """
        Make a new Pricing Batch from the given Product Batch.

        :param product_batch: Reference to a
           :class:`~rattail.db.model.batch.product.ProductBatch`
           instance from which a new pricing batch should be made.

        :param user: :class:`~rattail.db.model.users.User` who is
           responsible for this action.

        :returns: A new
           :class:`~rattail.db.model.batch.pricing.PricingBatch`
           instance, populated from the given product batch.
        """
        handler = self.app.get_batch_handler(
            'pricing', default='rattail.batch.pricing:PricingBatchHandler')
        session = self.app.get_session(product_batch)
        kwargs.setdefault('description', product_batch.description)
        kwargs.setdefault('notes', product_batch.notes)
        pricing_batch = handler.make_batch(session, created_by=user,
                                           **kwargs)
        pricing_batch.product_batch = product_batch
        handler.do_populate(pricing_batch, user, progress=progress)
        return pricing_batch
