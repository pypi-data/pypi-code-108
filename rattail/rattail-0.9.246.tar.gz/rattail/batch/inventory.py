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
Handler for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import decimal
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import api, model
from rattail.gpc import GPC
from rattail.batch import BatchHandler


log = logging.getLogger(__name__)


class InventoryBatchHandler(BatchHandler):
    """
    Handler for inventory batches.
    """
    batch_model_class = model.InventoryBatch

    # set to False to disable "variance" batch count mode
    allow_variance = True

    # set to False to disable "zero all" batch count mode
    allow_zero_all = True

    # when user scans unknown product, warn but do not create row
    unknown_product_creates_row = False

    # set to False to prevent exposing case fields for user input,
    # when the batch count mode is "adjust only"
    allow_adjustment_cases = True

    def init_batch(self, batch, **kwargs):
        if batch.total_cost is None:
            batch.total_cost = 0

    def allow_cases(self, batch):
        """
        Must return a boolean to indicate whether "case counts" may be entered
        for the batch (in addition to "unit counts"), as opposed to unit counts
        only.
        """
        if batch.mode == self.enum.INVENTORY_MODE_ADJUST:
            return self.allow_adjustment_cases
        return True

    def get_count_modes(self):
        """
        Should return a list of "count modes" from which a user might select
        when creating a new inventory batch, for instance.  Each mode should be
        represented as a JSON-serializable dict.

        Note that this method should return *all* possible modes; per-user
        restrictions etc. are handled elsewhere.
        """
        code_names = {}
        for name in dir(self.enum):
            if name.startswith('INVENTORY_MODE_'):
                code_names[getattr(self.enum, name)] = name

        modes = []
        for key, label in self.enum.INVENTORY_MODE.items():
            name = code_names[key]

            if name == 'INVENTORY_MODE_ZERO_ALL':
                if not self.allow_zero_all:
                    continue

            if name == 'INVENTORY_MODE_VARIANCE':
                if not self.allow_variance:
                    continue

            modes.append({
                'code': key,
                'code_name': name,
                'label': label,
            })

        return modes

    def get_allowed_count_modes(self, session, user,
                                permission_prefix='inventory'):
        """
        Should return a list of "count modes" from which the given user can
        select when creating a new inventory batch.  Each mode should be
        represented as a JSON-serializable dict.

        Note that this method should return only those modes which are the
        given user is *allowed* to create, according to permissions.
        """
        auth = self.app.get_auth_handler()
        all_modes = self.get_count_modes()
        modes = []

        def has_perm(name):
            name = '{}.{}'.format(permission_prefix, name)
            return auth.has_permission(session, user, name)

        for mode in all_modes:

            # "replace" modes
            if mode['code_name'] in ('INVENTORY_MODE_REPLACE',
                                     'INVENTORY_MODE_REPLACE_ADJUST'):
                if not has_perm('create.replace'):
                    continue

            # "zero all" mode
            if mode['code_name'] == 'INVENTORY_MODE_ZERO_ALL':
                if not has_perm('create.zero'):
                    continue

            # "variance" mode
            if mode['code_name'] == 'INVENTORY_MODE_VARIANCE':
                if not has_perm('create.variance'):
                    continue

            # user is allowed to create this mode
            modes.append(mode)

        return modes

    def get_adjustment_reasons(self, session):
        """
        Returns the full list of Inventory Adjustment Reasons from the database.
        """
        reasons = session.query(model.InventoryAdjustmentReason)\
                         .filter(sa.or_(
                             model.InventoryAdjustmentReason.hidden == None,
                             model.InventoryAdjustmentReason.hidden == False))\
                         .order_by(model.InventoryAdjustmentReason.code)\
                         .all()
        return reasons

    def should_populate(self, batch):
        if batch.handheld_batches:
            return True
        if batch.mode == self.enum.INVENTORY_MODE_ZERO_ALL:
            return True

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from an input data file, parsed according
        to the batch device type.
        """
        if batch.handheld_batches:
            self.populate_from_handheld(batch, progress=progress)
        elif batch.mode == self.enum.INVENTORY_MODE_ZERO_ALL:
            self.populate_zero_all(batch, progress=progress)

    def populate_from_handheld(self, batch, progress=None):

        def append(hh, i):
            row = model.InventoryBatchRow()
            row.upc = hh.upc
            if hh.cases is not None:
                row.cases = hh.cases
            if hh.units is not None:
                row.units = hh.units
            self.add_row(batch, row)

        data = []
        for handheld in batch.handheld_batches:
            data.extend(handheld.active_rows())
        self.progress_loop(append, data, progress,
                           message="Adding initial rows to batch")

    def populate_zero_all(self, batch, progress=None):
        session = orm.object_session(batch)
        products = session.query(model.Product)\
                          .join(model.ProductInventory)\
                          .filter(model.ProductInventory.on_hand != None)\
                          .filter(model.ProductInventory.on_hand != 0)

        def append(product, i):
            row = model.InventoryBatchRow()
            row.product = product
            row.units = 0
            self.add_row(batch, row)

        self.progress_loop(append, products, progress,
                           message="Adding initial rows to batch")

    def should_aggregate_products(self, batch):
        """
        Must return a boolean indicating whether rows should be aggregated by
        product for the given batch.

        If rows *should* be aggregated, what this means is, when a user enters
        a barcode, which is already contained within the batch, then that row
        should be "added to" as opposed to creating a new row.
        """
        if batch.mode == self.enum.INVENTORY_MODE_VARIANCE:
            return True
        return False

    def find_row_for_product(self, session, batch, product):
        """
        Locate and return the batch row which matches the given product, if one
        exists.  Otherwise returns ``None``.
        """
        session = orm.object_session(batch)
        rows = session.query(model.InventoryBatchRow)\
                      .filter(model.InventoryBatchRow.batch == batch)\
                      .filter(model.InventoryBatchRow.product == product)\
                      .filter(model.InventoryBatchRow.removed == False)\
                      .all()
        if rows:
            if len(rows) > 1:
                log.warning("inventory batch %s has %s rows for product %s: %s",
                            batch.id_str, len(rows), product.uuid, product)
            return rows[0]

    def get_type2_product_info(self, session, entry):
        """
        Try to locate the product for the given "Type 2" UPC.  This method
        should do basic validation on the UPC and will only attempt the product
        lookup if it does appear to be a proper Type 2 UPC.

        Note that this logic is *not* implemented by default; you must override
        with your own logic if you need to support this use case.

        :param entry: Should be a "raw" UPC as text, i.e. as entered by the user.

        :returns: If product is found, this method should return a 2-tuple
           containing the product, and the (decimal) "price" embedded in the
           UPC.  But if no product could be found, this returns ``None``.
        """

    def quick_entry(self, session, batch, entry):
        """
        Quick entry is assumed to be a UPC scan or similar user input.  Product
        lookup will be based on this.

        Behavior of this method may vary according to config, but in general
        the idea is, either locate an existing batch row, or add a new one,
        based on the user input.  The row will be returned, if found/created.
        """
        if len(entry) > 14:
            raise ValueError("UPC has too many ({}) digits: {}".format(
                len(entry), entry))

        # first we try to locate the product, either by interpreting a "type 2"
        # barcode, or else assuming a normal UPC / ID
        type2 = self.get_type2_product_info(session, entry)
        if type2:
            product, embedded_price = type2
        else:
            product = self.locate_product_for_entry(session, entry,
                                                    lookup_by_code=True)

        if product:
            if product.is_pack_item():
                # TODO: should rename this setting
                force_unit_item = self.config.getbool(
                    'tailbone', 'inventory.force_unit_item', default=False)
                if force_unit_item:
                    product = product.unit
                    # set a flag so caller can inspect/know what happened here
                    product.__forced_unit_item__ = True

            aggregate = self.should_aggregate_products(batch)
            if aggregate:
                row = self.find_row_for_product(session, batch, product)
                if row:
                    # set flag so caller can inspect/know what happened here
                    row.__existing_reused__ = True
                    return row

            row = self.make_row()
            row.item_entry = entry
            row.product = product
            self.capture_current_units(row)
            if type2 and not aggregate: # TODO: what if aggregating?
                if embedded_price is None:
                    row.units = 1
                else:
                    regprice = product.regular_price.price if product.regular_price else None
                    if regprice:
                        row.units = (embedded_price / regprice).quantize(
                            decimal.Decimal('0.01'))
                    else:
                        row.units = 1
            self.add_row(batch, row)
            return row

        if self.unknown_product_creates_row:
            row = self.make_row()
            row.item_entry = entry
            if entry.isdigit():
                # TODO: why not calc check digit?
                row.upc = GPC(entry, calc_check_digit=False)
            row.description = "(unknown product)"
            self.add_row(batch, row)
            return row

        # if we made it this far, then we did not find the product,
        # *and* we did not add the unknown product to batch.  so just
        # throw an error so caller logic can handle that
        raise ValueError("Product not found!")

    def refresh(self, batch, progress=None):
        batch.total_cost = 0

        # destroy and re-create data rows if batch is zero-all
        if batch.mode == self.enum.INVENTORY_MODE_ZERO_ALL:
            del batch.data_rows[:]
            batch.rowcount = 0
            self.populate_zero_all(batch, progress=progress)
            return True

        return super(InventoryBatchHandler, self).refresh(batch, progress=progress)

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        product = row.product
        if not product:
            if row.upc:
                session = orm.object_session(row)
                product = api.get_product_by_upc(session, row.upc)
            if not product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        # current / static attributes
        row.product = product
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        row.status_code = row.STATUS_OK
        row.case_quantity = (product.cost.case_size or 1) if product.cost else 1

        if row.previous_units_on_hand is not None:
            row.variance = self.total_units(row) - row.previous_units_on_hand

        # TODO: is this a sufficient check?  need to avoid overwriting a cost
        # value which has been manually set, but this also means the first
        # value that lands will stick, and e.g. new cost would be ignored
        if row.unit_cost is None:
            row.unit_cost = self.get_unit_cost(row)

        self.refresh_totals(row)

    def total_units(self, row):
        return (row.cases or 0) * (row.case_quantity or 1) + (row.units or 0)

    def capture_current_units(self, row):
        """
        Capture the "current" (aka. "previous") unit count for the row, if
        applicable.
        """
        product = row.product
        if product and product.inventory:
            row.previous_units_on_hand = product.inventory.on_hand

    def refresh_totals(self, row):
        batch = row.batch

        if row.unit_cost is not None:
            row.total_cost = row.unit_cost * (row.full_unit_quantity or 0)
            batch.total_cost = (batch.total_cost or 0) + row.total_cost
        else:
            row.total_cost = None

    def get_unit_cost(self, row):
        if row.product and row.product.cost:
            return row.product.cost.unit_cost

    def execute(self, batch, progress=None, **kwargs):
        rows = batch.active_rows()
        self.update_rattail_inventory(batch, rows, progress=progress)
        return True

    def update_rattail_inventory(self, batch, rows, progress=None):

        def update(row, i):
            product = row.product
            inventory = product.inventory
            if not inventory:
                inventory = product.inventory = model.ProductInventory()
            inventory.on_hand = row.units

        self.progress_loop(update, rows, progress,
                           message="Updating local inventory")
