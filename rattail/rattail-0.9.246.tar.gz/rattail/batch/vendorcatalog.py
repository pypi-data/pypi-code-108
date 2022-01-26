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
Handler for Vendor Catalog batches
"""

from __future__ import unicode_literals, absolute_import

import decimal

from sqlalchemy import orm

from rattail.db import model
from rattail.batch import BatchHandler


class VendorCatalogHandler(BatchHandler):
    """
    Handler for vendor catalog batches.
    """
    batch_model_class = model.VendorCatalogBatch

    # make sure web app knows to employ versioning workarounds
    # TODO: i am actually not sure why these *always* seem to be needed for
    # this batch?  maybe the product relationships are too "tight" somehow?
    populate_with_versioning = False
    refresh_with_versioning = False
    execute_with_versioning = False

    version_catchup_execute = [
        'ProductCost',
    ]

    # can set these to e.g. Decimal('0.01') to "ignore" cost diffs below that
    case_cost_diff_threshold = None
    unit_cost_diff_threshold = None

    def allow_future(self):
        """
        Returns boolean indicating whether "future" cost changes
        should be allowed.

        :returns: ``True`` if future cost changes allowed; else ``False``.
        """
        return self.config.getbool('rattail.batch', 'vendor_catalog.allow_future',
                                   default=False)

    def should_populate(self, batch):
        # all vendor catalogs must come from data file
        return True

    def setup(self, batch, progress=None):
        self.vendor = batch.vendor
        self.products = {'upc': {}, 'vendor_code': {}}
        session = self.app.get_session(batch)
        products = session.query(model.Product)\
                          .options(orm.joinedload(model.Product.brand))\
                          .options(orm.joinedload(model.Product.costs))

        def cache(product, i):
            if product.upc:
                self.products['upc'][product.upc] = product
            cost = product.cost_for_vendor(self.vendor)
            product.vendor_cost = cost
            if cost and cost.code:
                self.products['vendor_code'][cost.code] = product

        assert self.progress_loop(cache, products.all(), progress,
                                  message="Caching products by UPC and vendor code")

    setup_populate = setup
    setup_refresh = setup

    def populate(self, batch, progress=None):
        """
        Default logic just invokes :meth:`populate_from_file()`.
        """
        return self.populate_from_file(batch, progress=progress)

    def populate_from_file(self, batch, progress=None):
        """
        Populate the given batch using data from its input file.  A
        catalog parser will be instantiated and asked to read row data
        from the file.  Each row is then added to the batch.

        The batch must have valid
        :attr:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatch.filename`
        and
        :attr:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatch.parser_key`
        attributes.  The path to the input file will be determined by
        invoking the
        :meth:`~rattail.db.model.batch.core.BatchMixin.filepath()`
        method on the batch.

        :param batch: The batch to be populated.

        :param progress: Optional progress factory.
        """
        if not batch.filename:
            raise ValueError("batch does not have a filename: {}".format(batch))
        if not batch.parser_key:
            raise ValueError("batch does not have a parser_key: {}".format(batch))

        session = self.app.get_session(batch)
        path = batch.filepath(self.config)
        vendor_handler = self.app.get_vendor_handler()
        parser = vendor_handler.get_catalog_parser(batch.parser_key,
                                                   require=True)
        parser.session = session
        parser.vendor = batch.vendor
        if not batch.effective:
            batch.effective = parser.parse_effective_date(path)

        def append(row, i):
            self.add_row(batch, row)
            if i % 500 == 0: # pragma: no cover
                session.flush()

        data = list(parser.parse_rows(path, progress=progress))
        self.progress_loop(append, data, progress,
                           message="Adding initial rows to batch")

    def identify_product(self, row):
        """
        Try to locate the product represented by the given row.
        Lookups are done using either the ``upc`` or ``vendor_code``
        attributes of the row.

        Under normal circumstances the batch handler will have
        pre-cached all existing products, for quicker lookup.  For
        instance this is the case for the full populate and refresh
        actions.  But this logic is able to do its own slower lookups
        if there is no cache available.

        :param row: A
           :class:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatchRow`
           instance.

        :returns: A :class:`~rattail.db.model.products.Product`
           instance, or ``None`` if no match could be found.
        """
        products_handler = self.app.get_products_handler()
        session = self.app.get_session(row)
        product = None

        if row.upc:
            if hasattr(self, 'products'):
                product = self.products['upc'].get(row.upc)
            else:
                product = products_handler.locate_product_for_gpc(
                    session, row.upc)

        if not product and row.vendor_code:
            if hasattr(self, 'products'):
                product = self.products['vendor_code'].get(row.vendor_code)
            else:
                product = products_handler.locate_product_for_entry(
                    session, row.vendor_code, product_key='ignore',
                    lookup_vendor_code=True, vendor=row.batch.vendor)

        return product

    def refresh_row(self, row):
        """
        Refresh data attributes and status for the given row.

        For a vendor catalog, the typical thing is done for basic
        product attributes.

        If case cost is known but unit cost is not, the latter will be
        calculated if possible.

        "Old" (i.e. "current" prior to batch execution) values will
        all be re-fetched from the main database(s), and "diff" values
        will be re-calculated.

        :param row: A
           :class:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatchRow`
           instance.
        """
        batch = row.batch

        # clear this first in case it's set
        row.status_text = None

        if not row.product:
            row.product = self.identify_product(row)
            if not row.product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        product = row.product

        row.upc = row.product.upc
        row.item_id = row.product.item_id
        row.brand_name = row.product.brand.name if row.product.brand else None
        row.description = row.product.description
        row.size = row.product.size

        # maybe calculate unit cost from case cost
        if row.unit_cost is None and row.case_cost is not None:
            if row.case_size is not None:
                # nb. sometimes both case size and cost are integers,
                # and simple division yields a float!  this approach
                # should hopefully work regardless, to get a decimal.
                row.unit_cost = decimal.Decimal('{:0.4f}'.format(
                    row.case_cost / row.case_size))

        if hasattr(product, 'vendor_cost'):
            old_cost = product.vendor_cost
        else:
            old_cost = product.cost_for_vendor(batch.vendor)
        if not old_cost:
            row.status_code = row.STATUS_NEW_COST
            return

        row.cost = old_cost
        row.old_vendor_code = old_cost.code
        row.old_case_size = old_cost.case_size
        row.old_case_cost = old_cost.case_cost
        row.old_unit_cost = old_cost.unit_cost

        # only consider vendor match if product does in fact have a vendor
        # TODO: at least i assume that's a reasonable idea?
        if row.product.costs:
            row.is_preferred_vendor = row.product.costs[0].vendor is row.batch.vendor

        self.refresh_cost_diffs(row)
        self.set_status_per_diffs(row)

    def refresh_cost_diffs(self, row):

        # old_case_cost
        if row.case_cost is not None and row.old_case_cost is not None:
            row.case_cost_diff = row.case_cost - row.old_case_cost

        # old_unit_cost
        if row.unit_cost is not None and row.old_unit_cost is not None:
            row.unit_cost_diff = row.unit_cost - row.old_unit_cost
            if row.old_unit_cost:
                row.unit_cost_diff_percent = row.unit_cost_diff / row.old_unit_cost
            else:
                row.unit_cost_diff_percent = 1

    def set_status_per_diffs(self, row):

        if row.vendor_code != row.old_vendor_code:
            row.status_code = row.STATUS_CHANGE_VENDOR_ITEM_CODE
            row.status_text = "new vendor item code {} differs from old code {}".format(
                repr(row.vendor_code), repr(row.old_vendor_code))
            return

        if row.case_size != row.old_case_size:
            row.status_code = row.STATUS_CHANGE_CASE_SIZE
            row.status_text = "new case size {} differs from old case size {}".format(
                repr(row.case_size), repr(row.old_case_size))
            return

        if row.case_cost != row.old_case_cost:
            diff_meets_threshold = True
            if self.case_cost_diff_threshold and self.case_cost_diff_threshold > abs(
                    row.case_cost - row.old_case_cost):
                diff_meets_threshold = False
            if diff_meets_threshold:
                row.status_code = row.STATUS_CHANGE_COST
                row.status_text = "new case cost {} differs from old cost {}".format(
                    repr(row.case_cost), repr(row.old_case_cost))
                return

        if row.unit_cost != row.old_unit_cost:
            diff_meets_threshold = True
            if (self.unit_cost_diff_threshold
                and row.unit_cost is not None and row.old_unit_cost is not None
                and self.unit_cost_diff_threshold > abs(
                    row.unit_cost - row.old_unit_cost)):
                diff_meets_threshold = False
            if diff_meets_threshold:
                row.status_code = row.STATUS_CHANGE_COST
                row.status_text = "new unit cost {} differs from old cost {}".format(
                    repr(row.unit_cost), repr(row.old_unit_cost))
                return

        row.status_code = row.STATUS_NO_CHANGE

    # TODO: who uses this..?
    def cost_differs(self, row, cost):
        """
        Compare a batch row with a cost record to determine whether they match
        or differ.
        """
        if row.vendor_code is not None and row.vendor_code != cost.code:
            return "new vendor code {} differs from old code {}".format(
                repr(row.vendor_code), repr(cost.code))
        if row.case_cost is not None and row.case_cost != cost.case_cost:
            return "new case cost {} differs from old cost {}".format(
                row.case_cost, cost.case_cost)
        if row.unit_cost is not None and row.unit_cost != cost.unit_cost:
            return "new unit cost {} differs from old cost {}".format(
                row.unit_cost, cost.unit_cost)
