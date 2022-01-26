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
Handler for pricing batches
"""

from __future__ import unicode_literals, absolute_import

import decimal

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.gpc import GPC
from rattail.batch import BatchHandler
from rattail.excel import ExcelReader


class PricingBatchHandler(BatchHandler):
    """
    Handler for pricing batches.
    """
    batch_model_class = model.PricingBatch

    # cached decimal object used for rounding percentages, below
    percent_decimal = decimal.Decimal('.001')

    def should_populate(self, batch):
        if batch.params and batch.params.get('auto_generate_from_srp_breach'):
            return True
        if batch.input_filename:
            return True
        if hasattr(batch, 'products'):
            return True
        return False

    def populate(self, batch, progress=None):
        """
        Batch row data comes from product query.
        """
        # maybe populate with products which have an SRP breach
        if batch.params and batch.params.get('auto_generate_from_srp_breach'):
            self.populate_from_srp_breach(batch, progress=progress)
            return

        if batch.input_filename:
            return self.populate_from_file(batch, progress=progress)

        if hasattr(batch, 'product_batch') and batch.product_batch:
            self.populate_from_product_batch(batch, progress=progress)
            return

        assert batch.products
        session = orm.object_session(batch)

        def append(item, i):
            row = model.PricingBatchRow()
            row.product = item
            row.upc = row.product.upc
            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(append, batch.products, progress,
                           message="Adding initial rows to batch")

    def populate_from_file(self, batch, progress=None):
        """
        Batch row data comes from input data file.
        """
        path = batch.filepath(self.config, filename=batch.input_filename)
        reader = ExcelReader(path)
        excel_rows = reader.read_rows(progress=progress)
        session = orm.object_session(batch)

        def append(excel, i):
            row = model.PricingBatchRow()

            if 'upc' in excel:
                item_entry = excel['upc']
            else:
                item_entry = excel.get('UPC')
            if isinstance(item_entry, float):
                item_entry = six.text_type(int(item_entry))
            row.item_entry = item_entry

            row.product = self.locate_product_for_entry(session, row.item_entry)
            if row.product:
                row.upc = row.product.upc
            elif row.item_entry:
                row.upc = GPC(row.item_entry, calc_check_digit='upc')

            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(append, excel_rows, progress,
                           message="Adding initial rows to batch")

    def populate_from_product_batch(self, batch, progress=None):
        """
        Populate pricing batch from product batch.
        """
        session = orm.object_session(batch)
        product_batch = batch.product_batch

        def add(prow, i):
            row = model.PricingBatchRow()
            row.item_entry = prow.item_entry
            with session.no_autoflush:
                row.product = prow.product
            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(add, product_batch.active_rows(), progress,
                           message="Adding initial rows to batch")

    def populate_from_srp_breach(self, batch, progress=None):
        session = orm.object_session(batch)
        products = self.find_products_with_srp_breach(session, progress=progress)

        def append(product, i):
            row = self.make_row()
            row.product = product
            self.add_row(batch, row)

        self.progress_loop(append, products, progress,
                           message="Adding rows to batch")

    def find_products_with_srp_breach(self, session, progress=None):
        """
        Find and return a list of all products whose "regular price" is greater
        than "suggested price" (SRP).
        """
        query = session.query(model.Product)\
                       .options(orm.joinedload(model.Product.regular_price))\
                       .options(orm.joinedload(model.Product.suggested_price))
                       # TODO: should add these filters? make configurable?
                       # .filter(model.Product.deleted == False)\
                       # .filter(model.Product.discontinued == False)\
        products = []

        def collect(product, i):
            regular = product.regular_price
            suggested = product.suggested_price
            if (regular and regular.price and suggested and suggested.price
                and regular.price > suggested.price):
                products.append(product)

        self.progress_loop(collect, query.all(), progress,
                           message="Collecting products with SRP breach")
        return products

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        product = row.product
        if not product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        row.item_id = product.item_id
        row.upc = product.upc
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size

        department = product.department
        row.department_number = department.number if department else None
        row.department_name = department.name if department else None

        subdept = product.subdepartment
        row.subdepartment_number = subdept.number if subdept else None
        row.subdepartment_name = subdept.name if subdept else None

        family = product.family
        row.family_code = family.code if family else None

        report = product.report_code
        row.report_code = report.code if report else None

        row.alternate_code = product.code

        cost = product.cost
        row.vendor = cost.vendor if cost else None
        row.vendor_item_code = cost.code if cost else None
        row.regular_unit_cost = cost.unit_cost if cost else None

        sugprice = product.suggested_price
        row.suggested_price = sugprice.price if sugprice else None

        curprice = product.current_price
        if curprice:
            row.current_price = curprice.price
            row.current_price_type = curprice.type
            row.current_price_starts = curprice.starts
            row.current_price_ends = curprice.ends
        else:
            row.current_price = None
            row.current_price_type = None
            row.current_price_starts = None
            row.current_price_ends = None

        regprice = product.regular_price
        row.old_price = regprice.price if regprice else None

    def set_status_per_diff(self, row):
        """
        Set the row's status code according to its price diff
        """
        # manually priced items are "special" unless batch says to re-calc
        if row.manually_priced and not row.batch.calculate_for_manual:
            row.status_code = row.STATUS_PRODUCT_MANUALLY_PRICED
            return

        # prefer "% Diff" if batch defines that
        threshold = row.batch.min_diff_percent
        if threshold:
            # force rounding of row's % diff, for comparison to threshold
            # (this is just to avoid unexpected surprises for the user)
            # (ideally we'd just flush() the session but this seems safer)
            if isinstance(row.price_diff_percent, decimal.Decimal):
                row.price_diff_percent = row.price_diff_percent.quantize(self.percent_decimal)
            # TODO: why don't we use price_diff_percent here again?
            minor = abs(row.margin_diff) < threshold

        else: # or, use "$ Diff" as fallback
            threshold = row.batch.min_diff_threshold
            minor = bool(threshold) and abs(row.price_diff) < threshold

        # unchanged?
        if row.price_diff == 0:
            row.status_code = row.STATUS_PRICE_UNCHANGED

        # new price > SRP?
        elif row.suggested_price and row.new_price > row.suggested_price:
            row.status_code = row.STATUS_PRICE_BREACHES_SRP

        # price increase?
        elif row.price_diff > 0:
            if minor:
                row.status_code = row.STATUS_PRICE_INCREASE_MINOR
            else:
                row.status_code = row.STATUS_PRICE_INCREASE

        # must be price decrease
        else: # row.price_diff < 0
            if minor:
                row.status_code = row.STATUS_PRICE_DECREASE_MINOR
            else:
                row.status_code = row.STATUS_PRICE_DECREASE
