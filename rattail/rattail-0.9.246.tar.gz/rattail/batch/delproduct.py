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
Handler for "delete product" batches
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model
from rattail.batch import BatchHandler
from rattail.time import localtime


class DeleteProductBatchHandler(BatchHandler):
    """
    Handler for delete product batches.
    """
    batch_model_class = model.DeleteProductBatch

    def should_populate(self, batch):
        if hasattr(batch, 'products'):
            return True
        return False

    def setup_delproduct_common(self, batch, progress=None):
        self.today = localtime(self.config).date()

        self.department_must_allow_delete = self.config.getbool(
            'rattail.batch', 'delproduct.department_must_allow_delete',
            default=False)

        if self.department_must_allow_delete:
            session = orm.object_session(batch)
            model = self.model
            query = session.query(model.Department)\
                           .filter(model.Department.number != None)
            self.departments = self.cache_model(session, model.Department,
                                                query=query, key='number')

    def teardown_delproduct_common(self, batch, progress=None):
        if self.department_must_allow_delete:
            del self.departments
        del self.department_must_allow_delete
        del self.today

    def setup_populate(self, batch, progress=None):
        self.setup_delproduct_common(batch, progress=progress)

    def teardown_populate(self, batch, progress=None):
        self.teardown_delproduct_common(batch, progress=progress)

    def populate(self, batch, progress=None):
        if hasattr(batch, 'products'):
            return self.populate_from_query(batch, progress=progress)

    def populate_from_query(self, batch, progress=None):
        session = orm.object_session(batch)
        units_added = set()

        def add_item(product):
             row = self.make_row()
             row.item_entry = product.uuid
             row.product = product
             self.add_row(batch, row)

        def append(product, i):
            unit = product.get_unit_item()
            if unit.uuid not in units_added:
                add_item(unit)
                for pack in unit.packs:
                    add_item(pack)
                units_added.add(unit.uuid)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(append, batch.products, progress,
                           message="Adding products to batch")

    def setup_refresh(self, batch, progress=None):
        self.setup_delproduct_common(batch, progress=progress)

    def teardown_refresh(self, batch, progress=None):
        self.teardown_delproduct_common(batch, progress=progress)

    def refresh_row(self, row):
        if not row.product:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND
            return

        self.refresh_product_basics(row)

        row.pack_size = row.product.pack_size

        # flag if item is present in scale(s)
        row.present_in_scale = self.is_scale_item(row)

        # maybe don't allow delete for certain departments
        if self.department_must_allow_delete:
            if not self.department_allows_delete(row):
                row.status_code = row.STATUS_DELETE_NOT_ALLOWED
                row.status_text = "dept. #{} does not allow delete".format(
                    row.department_number)
                return

        # flag items with recent activity
        activity = self.find_recent_activity(row)
        if activity:
            row.status_code = row.STATUS_RECENT_ACTIVITY
            row.status_text = activity
            return

        # flag items with inventory
        inventory = self.find_inventory(row)
        if inventory:
            row.status_code = row.STATUS_HAS_INVENTORY
            row.status_text = inventory
            return

        row.status_code = row.STATUS_OK

    def is_scale_item(self, row):
        # TODO: we should know this, but for now we do not have a way
        return False

    def department_allows_delete(self, row):
        department = self.get_department(row)
        if department and department.allow_product_deletions:
            return True
        return False

    def get_department(self, row):
        if not row.department_number:
            return

        if hasattr(self, 'departments'):
            return self.departments.get(row.department_number)

        session = orm.object_session(row)
        model = self.model
        try:
            return session.query(model.Department)\
                          .filter(model.Department.number == row.department_number)\
                          .one()
        except orm.exc.NoResultFound:
            pass

    def find_recent_activity(self, row):
        # TODO: how to check?  i'm assuming this should return things like:
        # - None
        # - "last sold on 2020-04-20
        # - "last purchased on 2020-04-20"
        pass

    def find_inventory(self, row):
        # TODO: how to check?  i'm assuming this should return things like:
        # - None
        # - X on hand at Y stores
        pass
