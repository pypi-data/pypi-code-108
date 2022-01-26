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
Handler for label batches
"""

from __future__ import unicode_literals, absolute_import

import csv
import decimal
import logging

import six
import json
import sqlalchemy as sa
from sqlalchemy import orm

from rattail import enum
from rattail.db import model, api
from rattail.gpc import GPC
from rattail.batch import BatchHandler
from rattail.csvutil import UnicodeDictReader
from rattail.time import make_utc
from rattail.config import parse_bool


log = logging.getLogger(__name__)


class LabelBatchHandler(BatchHandler):
    """
    Handler for Print Labels batches.
    """
    batch_model_class = model.LabelBatch

    def setup(self, batch, progress=None):
        self.now = make_utc()

    setup_populate = setup
    setup_refresh = setup
    setup_clone = setup

    def make_batch(self, session, progress=None, **kwargs):
        """
        Make a new batch, with initial rows if applicable.
        """
        self.skip_first_line = parse_bool(kwargs.pop('skip_first_line', False))
        self.calc_check_digit = kwargs.pop('calc_check_digit', False)
        if self.calc_check_digit != 'upc':
            self.calc_check_digit = parse_bool(self.calc_check_digit)
        file_has_options = parse_bool(kwargs.pop('file_has_options', False))
        batch = super(LabelBatchHandler, self).make_batch(session, progress, **kwargs)
        batch.file_has_options = file_has_options
        return batch

    def auto_executable(self, batch):
        """
        Must return a boolean indicating whether the given bath is eligible for
        "automatic" execution, i.e. immediately after batch is created.
        """
        if batch.filename and '.autoexecute.' in batch.filename:
            return True
        return False

    def populate(self, batch, progress=None):
        """
        Pre-fill batch with row data from handheld batch, etc.
        """
        session = orm.object_session(batch)
        if batch.label_profile:
            self.label_profile = batch.label_profile
        else:
            self.label_profile = self.get_label_profile(session)

        if hasattr(batch, 'product_batch') and batch.product_batch:
            self.populate_from_product_batch(batch, progress=progress)
            return

        assert batch.handheld_batch or batch.filename or batch.products
        label_code = self.label_profile.code if self.label_profile else None

        def append(item, i):
            row = model.LabelBatchRow()
            row.label_code = label_code
            row.label_profile = self.label_profile
            with session.no_autoflush:
                if isinstance(item, model.Product):
                    row.product = item
                    row.label_quantity = 1
                    if batch.static_prices and hasattr(item, '_batch_price'):
                        row.regular_price = item._batch_price
                else: # item is handheld batch row
                    row.product = item.product
                    row.label_quantity = item.units or 1
                    # copy these in case product is null
                    row.item_entry = item.item_entry
                    row.item_id = item.item_id
                    row.upc = item.upc
                    row.brand_name = item.brand_name
                    row.description = item.description
                    row.size = item.size
            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        if batch.handheld_batch:
            data = batch.handheld_batch.active_rows()
        elif batch.filename:
            if batch.file_has_options:
                self.set_options_from_file(batch)
                if batch.label_profile:
                    self.label_profile = batch.label_profile
            data = self.read_products_from_file(batch, progress=progress)
        elif batch.products:
            data = batch.products

        self.progress_loop(append, data, progress,
                           message="Adding initial rows to batch")

    def populate_from_product_batch(self, batch, progress=None):
        """
        Populate label batch from product batch.
        """
        session = orm.object_session(batch)
        product_batch = batch.product_batch
        label_code = self.label_profile.code if self.label_profile else None

        def add(prow, i):
            row = model.LabelBatchRow()
            row.label_code = label_code
            row.label_profile = self.label_profile
            row.label_quantity = 1
            with session.no_autoflush:
                row.product = prow.product
            self.add_row(batch, row)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(add, product_batch.active_rows(), progress,
                           message="Adding initial rows to batch")

    def set_options_from_file(self, batch):
        """
        Set various batch options, if any are present within the data file.
        """
        path = batch.filepath(self.config)
        with open(path, 'rt') as f:
            options = json.loads(f.readline())
        if 'description' in options and options['description']:
            batch.description = options['description']
        if 'notes' in options and options['notes']:
            batch.notes = options['notes']
        if 'static_prices' in options:
            batch.static_prices = options['static_prices']
        if 'label_code' in options:
            batch.label_code = options['label_code']
            if batch.label_code:
                session = orm.object_session(batch)
                batch.label_profile = session.query(model.LabelProfile)\
                                             .filter(model.LabelProfile.code == batch.label_code)\
                                             .one()

    def read_products_from_file(self, batch, progress=None):
        """
        Returns list of Product objects based on lookup from CSV file data.

        # TODO: should this actually happen here? vs refresh and just mark product not found?
        """
        path = batch.filepath(self.config)
        with open(path, 'rt') as f:
            if self.skip_first_line:
                f.readline()
                reader = csv.reader(f)
                data = [{'upc': row[0]} for row in reader]
            else:
                fields = None
                if batch.file_has_options:
                    f.readline()
                    reader = csv.reader(f)
                    fields = next(reader)
                    f.seek(0)
                    f.readline()
                    f.readline()
                reader = UnicodeDictReader(f, fieldnames=fields)
                data = list(reader)

        products = []
        session = orm.object_session(batch)

        def append(entry, i):
            upc = entry['upc'].strip()
            if upc:
                try:
                    upc = GPC(upc, calc_check_digit=self.calc_check_digit)
                except ValueError:
                    pass
                else:
                    product = api.get_product_by_upc(session, upc)
                    if product:
                        if batch.static_prices and entry['regular_price']:
                            product._batch_price = decimal.Decimal(entry['regular_price'])
                        products.append(product)
                    else:
                        log.warning("product not found: {}".format(upc))

        self.progress_loop(append, data, progress,
                           message="Reading data from CSV file")
        return products

    def get_label_profile(self, session):
        code = self.config.get('rattail.batch', 'labels.default_code')
        if code:
            return session.query(model.LabelProfile)\
                          .filter(model.LabelProfile.code == code)\
                          .one()
        else:
            return session.query(model.LabelProfile)\
                          .order_by(model.LabelProfile.ordinal)\
                          .first()

    def refresh_row(self, row):
        """
        Inspect a row from the source data and populate additional attributes
        for it, according to what we find in the database.
        """
        if not row.product:
            session = orm.object_session(row)
            if row.item_entry:
                row.product = self.locate_product_for_entry(session, row.item_entry)
            if not row.product and row.upc:
                row.product = api.get_product_by_upc(session, row.upc)
            if not row.product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        self.refresh_product_basics(row)

        product = row.product
        category = product.category
        row.category_code = category.code if category else None
        row.category_name = category.name if category else None

        if not row.batch.static_prices:
            regular_price = product.regular_price
            row.regular_price = regular_price.price if regular_price else None
            row.pack_quantity = regular_price.pack_multiple if regular_price else None
            row.pack_price = regular_price.pack_price if regular_price else None

            sale_price = product.sale_price
            if sale_price:
                now = getattr(self, 'now', None) or make_utc()
                if (sale_price.type == enum.PRICE_TYPE_SALE and
                    sale_price.starts and sale_price.starts <= now and
                    sale_price.ends and sale_price.ends >= now):
                    pass            # this is what we want
                else:
                    sale_price = None
            row.sale_price = sale_price.price if sale_price else None
            row.sale_start = sale_price.starts if sale_price else None
            row.sale_stop = sale_price.ends if sale_price else None

            tpr_price = product.tpr_price
            if tpr_price:
                now = getattr(self, 'now', None) or self.app.make_utc()
                if (tpr_price.type == self.enum.PRICE_TYPE_TPR and
                    tpr_price.starts and tpr_price.starts <= now and
                    tpr_price.ends and tpr_price.ends >= now):
                    pass            # this is what we want
                else:
                    tpr_price = None
            row.tpr_price = tpr_price.price if tpr_price else None
            row.tpr_starts = tpr_price.starts if tpr_price else None
            row.tpr_ends = tpr_price.ends if tpr_price else None

            current_price = product.current_price
            if current_price:
                now = getattr(self, 'now', None) or self.app.make_utc()
                if (current_price.type in (self.enum.PRICE_TYPE_SALE,
                                           self.enum.PRICE_TYPE_TPR) and
                    current_price.starts and current_price.starts <= now and
                    current_price.ends and current_price.ends >= now):
                    pass            # this is what we want
                else:
                    current_price = None
            row.current_price = current_price.price if current_price else None
            row.current_starts = current_price.starts if current_price else None
            row.current_ends = current_price.ends if current_price else None

        cost = product.cost
        vendor = cost.vendor if cost else None
        row.vendor_id = vendor.id if vendor else None
        row.vendor_name = vendor.name if vendor else None
        row.vendor_item_code = cost.code if cost else None
        row.case_quantity = cost.case_size if cost else None
        if row.regular_price:
            row.status_code = row.STATUS_OK
        else:
            row.status_code = row.STATUS_REGULAR_PRICE_UNKNOWN

    def quick_entry(self, session, batch, entry):
        """
        Quick entry is assumed to be a UPC scan or similar user input.  If a
        matching product can be found, this will add a new row for the batch;
        otherwise an error is raised.
        """
        product = self.locate_product_for_entry(session, entry)
        if not product:
            raise ValueError("Product not found: {}".format(entry))

        row = self.make_row()
        row.product = product
        self.add_row(batch, row)
        return row

    def get_effective_rows(self, batch):
        # filter out removed rows, and maybe inactive product rows
        rows = batch.active_rows()
        if self.config.getbool('rattail.batch',
                               'labels.exclude_inactive_products',
                               default=False):
            rows = [row for row in rows
                    if row.status_code not in (row.STATUS_PRODUCT_APPEARS_INACTIVE,
                                               row.STATUS_PRODUCT_NOT_FOUND)]
        return rows

    def execute(self, batch, progress=None, **kwargs):
        """
        Print some labels!
        """
        rows = self.get_effective_rows(batch)
        self.print_labels(batch, rows, progress=progress)
        return True

    def print_labels(self, batch, rows, progress=None):
        """
        Print all labels for the given batch.
        """
        label_handler = self.app.get_label_handler()
        profiles = {}

        def organize(row, i):
            profile = row.label_profile
            if not profile:
                return
            if profile.uuid not in profiles:
                profiles[profile.uuid] = profile
                profile.labels = []

            data = row.get_data_dict()

            # TODO: should rename these columns in the schema; for now
            # just copy values in the dict to make other logic happy
            data['sale_starts'] = data['sale_start']
            data['sale_ends'] = data['sale_end']

            # TODO: this flag seems dubious; not sure how best to
            # handle, but also not sure it's even useful.  in what
            # case would we want to print "dynamic" data from product
            # master when we have it all in the batch?
            if not batch.static_prices:
                data['product'] = row.product

            profile.labels.append((data, row.label_quantity))

        self.progress_loop(organize, rows, progress,
                           message="Organizing labels by type")

        # okay now print for real
        for profile in six.itervalues(profiles):
            printer = label_handler.get_printer(profile)
            printer.print_labels(profile.labels, progress=progress)
