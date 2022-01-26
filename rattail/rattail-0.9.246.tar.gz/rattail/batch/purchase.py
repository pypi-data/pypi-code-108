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
Handler for "purchasing" batches
"""

from __future__ import unicode_literals, absolute_import, division

import decimal
import logging

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.db.util import maxlen
from rattail.gpc import GPC
from rattail.batch import BatchHandler
from rattail.time import localtime, make_utc
from rattail.vendors.invoices import require_invoice_parser, iter_invoice_parsers
from rattail.exceptions import BatchAlreadyExecuted


log = logging.getLogger(__name__)


class PurchaseBatchHandler(BatchHandler):
    """
    Handler for all "purchasing" batches, regardless of "mode".  The handler
    must inspect the
    :attr:`~rattail.db.model.batch.purchase.PurchaseBatch.mode` attribute of
    each batch it deals with, in order to determine which logic to apply.
    Possible mode values are:

    * ``rattail.enum.PURCHASE_BATCH_MODE_ORDERING``
    * ``rattail.enum.PURCHASE_BATCH_MODE_RECEIVING``
    * ``rattail.enum.PURCHASE_BATCH_MODE_COSTING``
    """
    batch_model_class = model.PurchaseBatch
    penny = decimal.Decimal('0.01')

    def allow_cases(self):
        """
        Must return boolean indicating whether "cases" should be generally
        allowed, for sake of quantity input etc.
        """
        return self.config.getbool('rattail.batch', 'purchase.allow_cases',
                                   default=False)

    def allow_receiving_from_scratch(self, **kwargs):
        """
        Return boolean indicating whether receiving "from scratch" is allowed.
        """
        return self.config.getbool('rattail.batch',
                                   'purchase.allow_receiving_from_scratch',
                                   default=False)

    def allow_receiving_from_invoice(self, **kwargs):
        """
        Return boolean indicating whether receiving "from invoice" is allowed.
        """
        return self.config.getbool('rattail.batch',
                                   'purchase.allow_receiving_from_invoice',
                                   default=False)

    def allow_receiving_from_purchase_order(self, **kwargs):
        """
        Return boolean indicating whether receiving "from PO" is allowed.
        """
        return self.config.getbool('rattail.batch',
                                   'purchase.allow_receiving_from_purchase_order',
                                   default=False)

    def allow_receiving_from_purchase_order_with_invoice(self, **kwargs):
        """
        Return boolean indicating whether receiving "from PO with
        invoice" is allowed.
        """
        return self.config.getbool('rattail.batch',
                                   'purchase.allow_receiving_from_purchase_order_with_invoice',
                                   default=False)

    def allow_truck_dump_receiving(self, **kwargs):
        """
        Return boolean indicating whether "truck dump receiving" is allowed.
        """
        return self.config.getbool('rattail.batch',
                                   'purchase.allow_truck_dump_receiving',
                                   default=False)

    def possible_receiving_workflows(self, **kwargs):
        """
        Returns a list representing all "receiving workflows" which are
        *possible* when making a new batch.  Note that possible != supported.
        See :meth:`supported_receiving_workflows()` for the latter.

        Each element of the list will be a dict with 3 items; keys of which
        are: ``'workflow_key'``, ``'display'`` and ``'description'``.

        Maybe these "creation type key" strings should be defined within the
        ``enum`` module, but for now they're sort of just magical hard-coded
        values I guess:

        * ``'from_scratch'``
        * ``'from_invoice'``
        * ``'from_po'``
        * ``'truck_dump_children_first'``
        * ``'truck_dump_children_last'``
        """
        return [
            {
                'workflow_key': 'from_scratch',
                'display': "From Scratch",
                'description': "Create a new empty batch and start scanning!",
            },
            {
                'workflow_key': 'from_invoice',
                'display': "From Invoice File",
                'description': "Upload an invoice file, and receive \"against\" it.",
            },
            {
                'workflow_key': 'from_po',
                'display': "From Purchase Order",
                'description': "Select an existing PO, and receive \"against\" it.",
            },
            {
                'workflow_key': 'from_po_with_invoice',
                'display': "From Purchase Order, with Invoice File",
                'description': "Select an existing PO, and provide its invoice file.",
            },
            {
                'workflow_key': 'truck_dump_children_first',
                'display': "Truck Dump (invoices FIRST)",
                'description': "Upload all invoice files and then receive against the whole lot at once.",
            },
            {
                'workflow_key': 'truck_dump_children_last',
                'display': "Truck Dump (invoices LAST)",
                'description': "Create a new empty truck dump batch, and start scanning; upload invoices later.",
            },
        ]

    def supported_receiving_workflows(self, **kwargs):
        """
        Returns a list representing which "creation types" are *supported* by
        the app, when making a new receiving batch.  Elements of this list will
        be of the same type as returned by :meth:`possible_receiving_workflows()`.
        """
        possible = self.possible_receiving_workflows()
        possible = dict([(item['workflow_key'], item)
                         for item in possible])

        workflows = []
        if self.allow_receiving_from_scratch():
            workflows.append(possible['from_scratch'])
        if self.allow_receiving_from_invoice():
            workflows.append(possible['from_invoice'])
        if self.allow_receiving_from_purchase_order():
            workflows.append(possible['from_po'])
        if self.allow_receiving_from_purchase_order_with_invoice():
            workflows.append(possible['from_po_with_invoice'])
        if self.allow_truck_dump_receiving():
            workflows.append(possible['truck_dump_children_first'])
            workflows.append(possible['truck_dump_children_last'])
        return workflows

    def receiving_workflow_info(self, workflow_key):
        """
        Returns the info dict for the given "creation type" key.  The dict will
        be one of those as returned by :meth:`possible_receiving_workflows()`.
        """
        for typ in self.possible_receiving_workflows():
            if typ['workflow_key'] == workflow_key:
                return typ

    def possible_costing_workflows(self, **kwargs):
        """
        Returns a list representing all "costing workflows" which are
        *possible* when making a new batch.  Note that possible != supported.
        See :meth:`supported_costing_workflows()` for the latter.

        Each element of the list will be a dict with 3 items; keys of which
        are: ``'workflow_key'``, ``'display'`` and ``'description'``.

        Maybe these "creation type key" strings should be defined within the
        ``enum`` module, but for now they're sort of just magical hard-coded
        values I guess:

        * ``'invoice_only'``
        * ``'invoice_with_po'``
        """
        return [
            {
                'workflow_key': 'invoice_only',
                'display': "Invoice Only",
                'description': "Create a new batch from invoice file only.",
            },
            {
                'workflow_key': 'invoice_with_po',
                'display': "Invoice with PO",
                'description': "Select an existing PO, and provide its invoice file.",
            },
        ]

    def supported_costing_workflows(self, **kwargs):
        """
        Returns a list representing which "creation types" are *supported* by
        the app, when making a new costing batch.  Elements of this list will
        be of the same type as returned by :meth:`possible_costing_workflows()`.
        """
        # TODO: for now we only support 'invoice_with_po' just to keep it simple
        return [workflow for workflow in self.possible_costing_workflows()
                if workflow['workflow_key'] == 'invoice_with_po']

    def costing_workflow_info(self, workflow_key):
        """
        Returns the info dict for the given "creation type" key.  The
        dict will be one of those as returned by
        :meth:`possible_costing_workflows()`.
        """
        for typ in self.possible_costing_workflows():
            if typ['workflow_key'] == workflow_key:
                return typ

    def allow_expired_credits(self):
        """
        Must return boolean indicating whether "expired" credits should be
        tracked.  In practice, this should either en- or dis-able various UI
        elements which involves expired product.
        """
        return self.config.getbool('rattail.batch', 'purchase.allow_expired_credits',
                                   default=False)

    def make_basic_batch(self, session, **kwargs):
        """
        Create a "bare minimum" batch object.

        Here we'll set the default store, if none is provided.
        """
        # try to assign store for new batch
        if 'store_uuid' not in kwargs and 'store' not in kwargs:
            store = self.config.get_store(session)
            if store:
                kwargs['store'] = store

        # remove the purchase_key kwarg, if present.  that comes into play
        # later in `init_batch()` but original kwargs will be used so we're not
        # harming those by removing it here
        kwargs.pop('purchase_key', None)

        # continue with usual logic
        batch = super(PurchaseBatchHandler, self).make_basic_batch(session, **kwargs)
        return batch

    def init_batch(self, batch, progress=None, **kwargs):
        """
        If this is a receiving batch, try to assign the original PO for it, by
        invoking :meth:`assign_purchase_order()`.
        """
        purchase_key = kwargs.get('purchase_key')
        if purchase_key:
            self.assign_purchase_order(batch, purchase_key,
                                       session=kwargs.get('session'))

    def assign_purchase_order(self, batch, purchase_key, session=None):
        """
        Assign the original PO for the given batch.  This will first obtain the
        PO via :meth:`get_purchase_order()` and if one is found, will try to
        assign it to the batch.

        Note that by default this will only try to assign
        ``batch.purchase_uuid``, but this will only happen if the PO object is
        a :class:`~rattail.db.model.purchase.Purchase` instance.

        :returns: The PO object if found, or ``None``.
        """
        if not session:
            session = orm.object_session(batch)
        purchase = self.get_purchase_order(session, purchase_key)
        if isinstance(purchase, model.Purchase):
            batch.purchase_uuid = purchase.uuid

        return purchase

    def should_populate(self, batch):
        """
        Must populate when e.g. making new receiving batch from PO or invoice,
        but otherwise not, e.g. receiving from scratch.
        """
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if self.has_purchase_order(batch):
                return True
            if self.has_invoice_file(batch):
                return True

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            if self.has_purchase_order(batch):
                return True
            if self.has_invoice_file(batch):
                return True

        return False

    def get_purchase_order(self, session, purchase_key, **kwargs):
        """
        Retrieve the PO object represented by ``purchase_key``.  The default
        logic assumes the key is a UUID, and will try to locate the
        corresponding :class:`~rattail.db.model.purchase.Purchase` instance.
        """
        return session.query(model.Purchase).get(purchase_key)

    def get_purchase_key(self, purchase, **kwargs):
        """
        Returns the "key" for the given purchase order object.

        Default logic here assumes that ``purchase`` is a Rattail
        Purchase object, so you may need to override.
        """
        return purchase.uuid

    def get_purchase_department(self, purchase, **kwargs):
        """
        Returns the :class:`~rattail.db.model.org.Department` record
        to which the purchase should be attributed, if
        applicable/known.
        """
        return getattr(purchase, 'department', None)

    def normalize_eligible_purchase(self, purchase):
        department = self.get_purchase_department(purchase)
        return {
            'key': self.get_purchase_key(purchase),
            'department_uuid': department.uuid if department else None,
            'display': self.render_eligible_purchase(purchase),
        }

    def get_eligible_purchases(self, vendor, mode):
        """
        This method should return a list of "eligible purchases" for the given
        vendor and batch mode.  Generally speaking, this list will be presented
        to the user so they can choose which PO to receive against, etc.

        Note that the only "real" requirement for the return value, is that it
        be a sequence of some type, e.g. list.  The actual purchase objects can
        be of whatever type your handler and other app logic require.
        """
        session = orm.object_session(vendor)
        model = self.config.get_model()

        purchases = session.query(model.Purchase)\
                           .filter(model.Purchase.vendor == vendor)

        if mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_ORDERED)\
                                 .order_by(model.Purchase.date_ordered.desc(),
                                           model.Purchase.created.desc())

        elif mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            purchases = purchases.filter(model.Purchase.status == self.enum.PURCHASE_STATUS_RECEIVED)\
                                 .order_by(model.Purchase.date_received, model.Purchase.created)

        return purchases.all()

    def render_eligible_purchase(self, purchase):
        """
        Render the purchase as a simple string, e.g. for use within a dropdown
        when user must select one from a list.
        """
        if purchase.status == self.enum.PURCHASE_STATUS_ORDERED:
            date = purchase.date_ordered
            total = purchase.po_total
        elif purchase.status == self.enum.PURCHASE_STATUS_RECEIVED:
            date = purchase.date_received
            total = purchase.invoice_total
        distinction = purchase.department or purchase.buyer
        return "{} for ${:0,.2f} ({})".format(date, total or 0, distinction)

    def populate(self, batch, progress=None):
        """
        Fill the batch with initial data, e.g. from data file or existing PO.

        A receiving batch which is populated from PO/file will also have its
        :attr:`~rattail.db.model.batch.purchase.PurchaseBatch.order_quantities_known`
        attribute set to ``True``.

        If the batch is a "truck dump child" and does not yet have a receiving
        date, it is given the same one as the parent batch.
        """
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            if batch.is_truck_dump_parent():
                pass            # TODO?

            elif batch.is_truck_dump_child():

                # copy receiving date from parent
                if not batch.date_received:
                    batch.date_received = batch.truck_dump_batch.date_received

                if batch.invoice_file:
                    self.populate_from_truck_dump_invoice(batch, progress=progress)
                    return

            else: # "normal" (no truck dump)

                if self.has_purchase_order(batch) and self.has_invoice_file(batch):
                    self.populate_from_invoice_with_po(batch, progress=progress)
                    return

                if self.has_invoice_file(batch):
                    self.populate_from_invoice(batch, progress=progress)
                    return

                if self.has_purchase_order(batch):
                    self.populate_from_purchase_order(batch, progress=progress)
                    return

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:

            if self.has_purchase_order(batch) and self.has_invoice_file(batch):
                self.populate_from_invoice_with_po(batch, progress=progress)
                return

            if self.has_invoice_file(batch):
                self.populate_from_invoice(batch, progress=progress)
                return

        raise NotImplementedError("Don't know how to populate batch: {}".format(batch))

    def has_purchase_order(self, batch, **kwargs):
        """
        Should inspect the batch and return ``True`` if there is a
        "purchase order" associated with it, or ``False`` if not.
        """
        return bool(batch.purchase)

    def has_invoice_file(self, batch, **kwargs):
        """
        Should inspect the batch and return ``True`` if there is an
        "invoice file" associated with it, or ``False`` if not.
        """
        return bool(batch.invoice_file)

    def get_supported_invoice_parsers(self, vendor=None, **kwargs):
        """
        Should return a list of invoice parsers which are *supported*
        and should be exposed to the user.

        :param vendor: Vendor for whom the parser is needed, if known.
           If you specify a vendor then parsers which indicate support
           for a *different* vendor will be excluded from the list.
        """
        parsers = sorted(iter_invoice_parsers(), key=lambda p: p.display)

        result = []
        if vendor:
            session = self.app.get_session(vendor)
            for Parser in parsers:
                if Parser.vendor_key:
                    # parser declares a vendor, so only add if it's a match
                    parser = Parser(self.config)
                    pvendor = parser.get_vendor(session)
                    if pvendor and pvendor is vendor:
                        result.append(parser)
                else: # parser is vendor-neutral; always add
                    result.append(parser)

        else: # no vendor specified, so show all parsers
            result = parsers

        return result

    def require_invoice_parser(self, batch):
        """
        Returns the appropriate invoice parser for the given batch, or
        raises an error if one can't be found.
        """
        return require_invoice_parser(self.config, batch.invoice_parser_key)

    def get_vendor_for_parser(self, batch, parser):
        """
        Returns the "configured" vendor for the given invoice parser.
        """
        session = self.app.get_session(batch)
        vendor = api.get_vendor(session, parser.vendor_key)
        if vendor is not batch.vendor:
            raise RuntimeError("Parser is for vendor '{}' "
                               "but batch is for: {}".format(
                                   parser.vendor_key, batch.vendor))
        return vendor

    def populate_from_invoice(self, batch, progress=None):
        """
        Populate a batch from vendor invoice file.
        """
        session = self.app.get_session(batch)
        parser = self.require_invoice_parser(batch)
        parser.session = session
        parser.vendor = self.get_vendor_for_parser(batch, parser)

        path = batch.filepath(self.config, batch.invoice_file)
        batch.invoice_date = parser.parse_invoice_date(path)
        batch.invoice_number = parser.parse_invoice_number(path)
        batch.order_quantities_known = True

        def append(invrow, i):
            row = self.make_row_from_invoice(batch, invrow)
            self.add_row(batch, row)

        self.progress_loop(append, list(parser.parse_rows(path)), progress,
                           message="Adding initial rows to batch")

        # pretty sure batch.invoice_total is set by way of adding rows
        # to the batch, so technically "calculated" but should be a
        # simple sum of amounts taken from invoice parser.  at any
        # rate some parsers can grab the total directly; if so we
        # prefer that
        total = parser.parse_invoice_total(path)
        if total is not None:
            batch.invoice_total = total
        else:
            batch.invoice_total = sum([row.invoice_total or 0
                                       for row in batch.active_rows()])

        self.refresh_batch_status(batch)

    def populate_from_purchase_order(self, batch, progress=None):
        """
        Populate a batch from existing purchase order.
        """
        assert batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                              self.enum.PURCHASE_BATCH_MODE_COSTING)
        assert batch.purchase
        session = orm.object_session(batch)
        batch.order_quantities_known = True

        # maybe copy total from PO
        if not batch.po_total:
            batch.po_total = batch.purchase.po_total

        # maybe copy receiving date from parent
        if batch.is_truck_dump_child() and not batch.date_received:
            batch.date_received = batch.truck_dump_batch.date_received

        def append(item, i):
            row = self.make_row_from_po_item( batch, item)

            # TODO: some of this probably should be moved into
            # make_row_for_po_item() ..?

            # since we're *receiving* from a PO (i.e. not an invoice), we can
            # assume "shipped" quantities were same as "ordered" quantities
            # TODO: does this still seem like a good idea..?
            if row.cases_ordered:
                row.cases_shipped = row.cases_ordered
            if row.units_ordered:
                row.units_shipped = row.units_ordered

            row.po_unit_cost = item.po_unit_cost
            row.po_total = item.po_total
            if not row.po_total and row.po_unit_cost:
                units = self.get_units_shipped(row)
                if units:
                    row.po_total = units * row.po_unit_cost

            if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
                row.invoice_unit_cost = item.invoice_unit_cost
                row.invoice_total = item.invoice_total

            self.add_row(batch, row)

        self.progress_loop(append, batch.purchase.items, progress,
                           message="Adding initial rows to batch")

        session.flush()
        self.refresh_batch_status(batch)

    def populate_from_invoice_with_po(self, batch, progress=None):
        """
        Populate a batch from existing SMS PO *and* invoice file.
        """
        # first we populate from PO, "per usual"
        self.populate_from_purchase_order(batch, progress=progress)

        # next we "overlay" the invoice onto the batch
        session = self.app.get_session(batch)
        parser = self.require_invoice_parser(batch)
        parser.session = session
        parser.vendor = self.get_vendor_for_parser(batch, parser)
        path = batch.filepath(self.config, batch.invoice_file)
        batch.invoice_date = parser.parse_invoice_date(path)
        batch.invoice_number = parser.parse_invoice_number(path)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            self.assume_shipped_is_received = self.config.getbool(
                'rattail.batch', 'purchase.receiving.assume_shipped_is_received')

        def overlay(invrow, i):
            row = self.find_batch_row_for_invoice_row(batch, invrow)
            if row:
                self.update_batch_row_from_invoice_row(row, invrow)
                self.refresh_row(row)
            else:
                row = self.make_row_from_invoice(batch, invrow)

                # if we are in "receiving" mode then we *may* go ahead and
                # assume that the shipped quantity, is what we are receiving
                # as well.  if config says so that is.
                if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                    if self.assume_shipped_is_received:
                        row.cases_received = row.cases_shipped
                        row.units_received = row.units_shipped

                self.add_row(batch, row)

        self.progress_loop(overlay, list(parser.parse_rows(path)), progress,
                           message="Overlaying invoice data onto PO")

        # set the "original" invoice total
        total = parser.parse_invoice_total(path)
        if total is not None:
            batch.invoice_total = total
        else:
            batch.invoice_total = sum([row.invoice_total or 0
                                       for row in batch.active_rows()])

        # finally update batch status, in case of new products not found etc.
        self.refresh_batch_status(batch)

    def update_batch_row_from_invoice_row(self, row, invrow):
        """
        Update an existing batch row, with a line item row parsed from
        an invoice.
        """
        batch = row.batch

        row.invoice_line_number = invrow.line_number

        # here we want the "best" case quantity we can get.  we will
        # use the one from invoice if present; otherwise keep using
        # what the row already had on file
        case_quantity = row.case_quantity

        # nb. we always replace the batch row's case quantity from the
        # invoice row, although if that's empty, then refresh_row()
        # may apply case quantity from product cost record
        row.case_quantity = invrow.case_quantity
        if row.case_quantity:
            case_quantity = row.case_quantity

        row.cases_shipped = invrow.shipped_cases
        row.units_shipped = invrow.shipped_units

        # if we are in "receiving" mode then we *may* go ahead and
        # assume that the shipped quantity, is what we are receiving
        # as well.  if config says so that is.
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if self.assume_shipped_is_received:
                row.cases_received = row.cases_shipped
                row.units_received = row.units_shipped

        row.invoice_unit_cost = invrow.unit_cost
        row.invoice_case_cost = invrow.case_cost

        # now about that case quantity..we may need to use it to
        # calculate unit or case cost
        if case_quantity:
            case_quantity = decimal.Decimal(six.text_type(case_quantity))
            if row.invoice_unit_cost and not row.invoice_case_cost:
                row.invoice_case_cost = row.invoice_unit_cost * case_quantity
            elif row.invoice_case_cost and not row.invoice_unit_cost:
                row.invoice_unit_cost = row.invoice_case_cost / case_quantity

        row.invoice_total = invrow.total_cost
        row.out_of_stock = invrow.out_of_stock

    def find_batch_row_for_invoice_row(self, batch, invrow):
        """
        For a given invoice row (line item), locate and return the
        "matching" batch row.
        """
        session = self.app.get_session(batch)

        # first try to locate the rattail product, and match on that
        product = self.locate_product_for_entry(session, invrow.item_entry,
                                                lookup_vendor_code=True,
                                                vendor=batch.vendor)
        if product:
            for row in batch.data_rows:
                if row.product is product:
                    return row

    def populate_from_truck_dump_invoice(self, batch, progress=None):
        """
        Logic for populating a "truck dump child" batch, from a vendor invoice
        data file.
        """
        child_batch = batch
        parent_batch = child_batch.truck_dump_batch
        session = orm.object_session(child_batch)

        parser = self.require_invoice_parser(batch)
        parser.session = session

        parser.vendor = api.get_vendor(session, parser.vendor_key)
        if parser.vendor is not child_batch.vendor:
            raise RuntimeError("Parser is for vendor '{}' but batch is for: {}".format(
                parser.vendor_key, child_batch.vendor))

        path = child_batch.filepath(self.config, child_batch.invoice_file)
        child_batch.invoice_date = parser.parse_invoice_date(path)
        child_batch.order_quantities_known = True

        def append(invoice_row, i):
            row = self.make_row_from_invoice(child_batch, invoice_row)
            self.add_row(child_batch, row)

        self.progress_loop(append, list(parser.parse_rows(path)), progress,
                           message="Adding initial rows to batch")

        if parent_batch.truck_dump_children_first:
            # children first, so should add rows to parent batch now
            session.flush()

            def append(child_row, i):
                if not child_row.out_of_stock:

                    # if row for this product already exists in parent, must aggregate
                    parent_row = self.locate_parent_row_for_child(parent_batch, child_row)
                    if parent_row:

                        # confirm 'case_quantity' matches
                        if parent_row.case_quantity != child_row.case_quantity:
                            raise ValueError("differing 'case_quantity' for item {}: {}".format(
                                child_row.item_entry, child_row.description))

                        # confirm 'out_of_stock' matches
                        if parent_row.out_of_stock != child_row.out_of_stock:
                            raise ValueError("differing 'out_of_stock' for item {}: {}".format(
                                cihld_row.item_entry, child_row.description))

                        # confirm 'invoice_unit_cost' matches
                        if parent_row.invoice_unit_cost != child_row.invoice_unit_cost:
                            raise ValueError("differing 'invoice_unit_cost' for item {}: {}".format(
                                cihld_row.item_entry, child_row.description))

                        # confirm 'invoice_case_cost' matches
                        if parent_row.invoice_case_cost != child_row.invoice_case_cost:
                            raise ValueError("differing 'invoice_case_cost' for item {}: {}".format(
                                cihld_row.item_entry, child_row.description))

                        # add 'ordered' quantities
                        if child_row.cases_ordered:
                            parent_row.cases_ordered = (parent_row.cases_ordered or 0) + child_row.cases_ordered
                        if child_row.units_ordered:
                            parent_row.units_ordered = (parent_row.units_ordered or 0) + child_row.units_ordered

                        # add 'shipped' quantities
                        if child_row.cases_shipped:
                            parent_row.cases_shipped = (parent_row.cases_shipped or 0) + child_row.cases_shipped
                        if child_row.units_shipped:
                            parent_row.units_shipped = (parent_row.units_shipped or 0) + child_row.units_shipped

                        # add 'invoice_total' quantities
                        if child_row.invoice_total:
                            parent_row.invoice_total = (parent_row.invoice_total or 0) + child_row.invoice_total
                            parent_batch.invoice_total = (parent_batch.invoice_total or 0) + child_row.invoice_total
                        if child_row.invoice_total_calculated:
                            parent_row.invoice_total_calculated = (parent_row.invoice_total_calculated or 0) + child_row.invoice_total_calculated
                            parent_batch.invoice_total_calculated = (parent_batch.invoice_total_calculated or 0) + child_row.invoice_total_calculated

                    else: # new product; simply add new row to parent
                        parent_row = self.make_parent_row_from_child(child_row)
                        self.add_row(parent_batch, parent_row)

            self.progress_loop(append, child_batch.active_rows(), progress,
                               message="Adding rows to parent batch")

        else: # children last, so should make parent claims now
            self.make_truck_dump_claims_for_child_batch(child_batch, progress=progress)

        self.refresh_batch_status(parent_batch)

    def locate_parent_row_for_child(self, parent_batch, child_row):
        """
        Locate a row within parent batch, which "matches" given row from child
        batch.  May return ``None`` if no match found.
        """
        if child_row.product_uuid:
            rows = [row for row in parent_batch.active_rows()
                    if row.product_uuid == child_row.product_uuid]
            if rows:
                return rows[0]

        elif child_row.item_entry:
            rows = [row for row in parent_batch.active_rows()
                    if row.product_uuid is None
                    and row.item_entry == child_row.item_entry]
            if rows:
                return rows[0]

    def make_row_from_po_item(self, batch, item):
        """
        Create a new batch row, from the given ``po_item`` object,
        which is assumed to be a purchase order line item of some
        sort.  Default implementation specifically assumes it is a
        `PurchaseItem` instance, but subclasses may assume something
        else.
        """
        row = self.make_row()
        row.po_line_number = item.sequence
        product = item.product
        row.item = item
        row.product = product
        if product:
            row.upc = product.upc
            row.item_id = product.item_id
        else:
            row.upc = item.upc
            row.item_id = item.item_id

        # we set the case size according to PO, but we also set the
        # "official" case size for the row, to match.  later on when
        # the row is refreshed that may be updated from product record.
        row.po_case_size = item.case_quantity
        row.case_quantity = row.po_case_size

        row.cases_ordered = item.cases_ordered
        row.units_ordered = item.units_ordered

        # TODO: previous logic did not do this..?
        row.cases_shipped = item.cases_shipped
        row.units_shipped = item.units_shipped

        row.cases_received = item.cases_received
        row.units_received = item.units_received
        return row

    def make_row_from_invoice(self, batch, invoice_row):
        """
        Create a new batch row, from the given ``invoice_row`` object, which is
        assumed to be a
        :class:`~rattail.db.model.batch.vendorinvoice.VendorInvoiceBatchRow`
        object as obtained from an invoice parser.
        """
        row = model.PurchaseBatchRow()
        if invoice_row.line_number:
            row.invoice_line_number = invoice_row.line_number
        row.item_entry = invoice_row.item_entry
        row.upc = invoice_row.upc
        row.vendor_code = invoice_row.vendor_code
        row.brand_name = invoice_row.brand_name
        row.description = invoice_row.description
        row.size = invoice_row.size
        row.invoice_case_size = invoice_row.case_quantity
        row.case_quantity = row.invoice_case_size
        row.cases_ordered = invoice_row.ordered_cases
        row.units_ordered = invoice_row.ordered_units
        row.cases_shipped = invoice_row.shipped_cases
        row.units_shipped = invoice_row.shipped_units
        row.out_of_stock = invoice_row.out_of_stock
        row.invoice_unit_cost = invoice_row.unit_cost
        row.invoice_total = invoice_row.total_cost
        row.invoice_case_cost = invoice_row.case_cost
        return row

    def make_parent_row_from_child(self, child_row):
        row = model.PurchaseBatchRow()
        row.item_entry = child_row.item_entry
        row.upc = child_row.upc
        row.vendor_code = child_row.vendor_code
        row.brand_name = child_row.brand_name
        row.description = child_row.description
        row.size = child_row.size
        row.case_quantity = child_row.case_quantity
        row.cases_ordered = child_row.cases_ordered
        row.units_ordered = child_row.units_ordered
        row.cases_shipped = child_row.cases_shipped
        row.units_shipped = child_row.units_shipped
        row.out_of_stock = child_row.out_of_stock
        row.invoice_unit_cost = child_row.invoice_unit_cost
        row.invoice_total = child_row.invoice_total
        row.invoice_case_cost = child_row.invoice_case_cost
        return row

    def make_truck_dump_claims_for_child_batch(self, batch, progress=None):
        """
        Make all "claims" against a truck dump, for the given child batch.
        This assumes no claims exist for the child batch at time of calling,
        and that the truck dump batch is complete and not yet executed.
        """
        session = orm.object_session(batch)
        truck_dump_rows = batch.truck_dump_batch.active_rows()
        child_rows = batch.active_rows()

        # organize truck dump by product and UPC
        truck_dump_by_product = {}
        truck_dump_by_upc = {}

        def organize_parent(row, i):
            if row.product:
                truck_dump_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                truck_dump_by_upc.setdefault(row.upc, []).append(row)

        self.progress_loop(organize_parent, truck_dump_rows, progress,
                           message="Organizing truck dump parent rows")

        # organize child batch by product and UPC
        child_by_product = {}
        child_by_upc = {}

        def organize_child(row, i):
            if row.product:
                child_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                child_by_upc.setdefault(row.upc, []).append(row)

        self.progress_loop(organize_child, child_rows, progress,
                           message="Organizing truck dump child rows")

        # okay then, let's go through all our organized rows, and make claims

        def make_claims(child_product, i):
            uuid, child_product_rows = child_product
            if uuid in truck_dump_by_product:
                truck_dump_product_rows = truck_dump_by_product[uuid]
                for truck_dump_row in truck_dump_product_rows:
                    self.make_truck_dump_claims(truck_dump_row, child_product_rows)

        self.progress_loop(make_claims, child_by_product.items(), progress,
                           count=len(child_by_product),
                           message="Claiming parent rows for child") # (pass #1)

    def make_truck_dump_claims(self, truck_dump_row, child_rows):

        # first we go through the truck dump parent row, and calculate all
        # "present", and "claimed" vs. "pending" product quantities

        # cases_received
        cases_received = truck_dump_row.cases_received or 0
        cases_received_claimed = sum([claim.cases_received or 0
                                      for claim in truck_dump_row.claims])
        cases_received_pending = cases_received - cases_received_claimed

        # units_received
        units_received = truck_dump_row.units_received or 0
        units_received_claimed = sum([claim.units_received or 0
                                      for claim in truck_dump_row.claims])
        units_received_pending = units_received - units_received_claimed

        # cases_damaged
        cases_damaged = truck_dump_row.cases_damaged or 0
        cases_damaged_claimed = sum([claim.cases_damaged or 0
                                     for claim in truck_dump_row.claims])
        cases_damaged_pending = cases_damaged - cases_damaged_claimed

        # units_damaged
        units_damaged = truck_dump_row.units_damaged or 0
        units_damaged_claimed = sum([claim.units_damaged or 0
                                     for claim in truck_dump_row.claims])
        units_damaged_pending = units_damaged - units_damaged_claimed

        # cases_expired
        cases_expired = truck_dump_row.cases_expired or 0
        cases_expired_claimed = sum([claim.cases_expired or 0
                                     for claim in truck_dump_row.claims])
        cases_expired_pending = cases_expired - cases_expired_claimed

        # units_expired
        units_expired = truck_dump_row.units_expired or 0
        units_expired_claimed = sum([claim.units_expired or 0
                                     for claim in truck_dump_row.claims])
        units_expired_pending = units_expired - units_expired_claimed

        # TODO: should be calculating mispicks here too, right?

        def make_claim(child_row):
            c = model.PurchaseBatchRowClaim()
            c.claiming_row = child_row
            truck_dump_row.claims.append(c)
            return c

        for child_row in child_rows:

            # stop now if everything in this parent row is accounted for
            if not (cases_received_pending or units_received_pending
                    or cases_damaged_pending or units_damaged_pending
                    or cases_expired_pending or units_expired_pending):
                break

            # for each child row we also calculate all "present", and "claimed"
            # vs. "pending" product quantities

            # cases_shipped
            cases_shipped = child_row.cases_shipped or 0
            cases_shipped_claimed = sum([(claim.cases_received or 0)
                                         + (claim.cases_damaged or 0)
                                         + (claim.cases_expired or 0)
                                         for claim in child_row.truck_dump_claims])
            cases_shipped_pending = cases_shipped - cases_shipped_claimed

            # units_shipped
            units_shipped = child_row.units_shipped or 0
            units_shipped_claimed = sum([(claim.units_received or 0)
                                         + (claim.units_damaged or 0)
                                         + (claim.units_expired or 0)
                                         for claim in child_row.truck_dump_claims])
            units_shipped_pending = units_shipped - units_shipped_claimed

            # skip this child row if everything in it is accounted for
            if not (cases_shipped_pending or units_shipped_pending):
                continue

            # there should only be one claim for this parent/child combo
            claim = None

            # let's cache this
            case_quantity = child_row.case_quantity

            # make case claims
            if cases_shipped_pending and cases_received_pending:
                claim = claim or make_claim(child_row)
                if cases_received_pending >= cases_shipped_pending:
                    claim.cases_received = (claim.cases_received or 0) + cases_shipped_pending
                    child_row.cases_received = (child_row.cases_received or 0) + cases_shipped_pending
                    cases_received_pending -= cases_shipped_pending
                    cases_shipped_pending = 0
                else: # shipped > received
                    claim.cases_received = (claim.cases_received or 0) + cases_received_pending
                    child_row.cases_received = (child_row.cases_received or 0) + cases_received_pending
                    cases_shipped_pending -= cases_received_pending
                    cases_received_pending = 0
                self.refresh_row(child_row)
            if cases_shipped_pending and cases_damaged_pending:
                claim = claim or make_claim(child_row)
                if cases_damaged_pending >= cases_shipped_pending:
                    claim.cases_damaged = (claim.cases_damaged or 0) + cases_shipped_pending
                    child_row.cases_damaged = (child_row.cases_damaged or 0) + cases_shipped_pending
                    cases_damaged_pending -= cases_shipped_pending
                    cases_shipped_pending = 0
                else: # shipped > damaged
                    claim.cases_damaged = (claim.cases_damaged or 0) + cases_damaged_pending
                    child_row.cases_damaged = (child_row.cases_damaged or 0) + cases_damaged_pending
                    cases_shipped_pending -= cases_damaged_pending
                    cases_damaged_pending = 0
                self.refresh_row(child_row)
            if cases_shipped_pending and cases_expired_pending:
                claim = claim or make_claim(child_row)
                if cases_expired_pending >= cases_shipped_pending:
                    claim.cases_expired = (claim.cases_expired or 0) + cases_shipped_pending
                    child_row.cases_expired = (child_row.cases_expired or 0) + cases_shipped_pending
                    cases_expired_pending -= cases_shipped_pending
                    cases_shipped_pending = 0
                else: # shipped > expired
                    claim.cases_expired = (claim.cases_expired or 0) + cases_expired_pending
                    child_row.cases_expired = (child_row.cases_expired or 0) + cases_expired_pending
                    cases_shipped_pending -= cases_expired_pending
                    cases_expired_pending = 0
                self.refresh_row(child_row)

            # make unit claims
            if units_shipped_pending and units_received_pending:
                claim = claim or make_claim(child_row)
                if units_received_pending >= units_shipped_pending:
                    claim.units_received = (claim.units_received or 0) + units_shipped_pending
                    child_row.units_received = (child_row.units_received or 0) + units_shipped_pending
                    units_received_pending -= units_shipped_pending
                    units_shipped_pending = 0
                else: # shipped > received
                    claim.units_received = (claim.units_received or 0) + units_received_pending
                    child_row.units_received = (child_row.units_received or 0) + units_received_pending
                    units_shipped_pending -= units_received_pending
                    units_received_pending = 0
                self.refresh_row(child_row)
            if units_shipped_pending and units_damaged_pending:
                claim = claim or make_claim(child_row)
                if units_damaged_pending >= units_shipped_pending:
                    claim.units_damaged = (claim.units_damaged or 0) + units_shipped_pending
                    child_row.units_damaged = (child_row.units_damaged or 0) + units_shipped_pending
                    units_damaged_pending -= units_shipped_pending
                    units_shipped_pending = 0
                else: # shipped > damaged
                    claim.units_damaged = (claim.units_damaged or 0) + units_damaged_pending
                    child_row.units_damaged = (child_row.units_damaged or 0) + units_damaged_pending
                    units_shipped_pending -= units_damaged_pending
                    units_damaged_pending = 0
                self.refresh_row(child_row)
            if units_shipped_pending and units_expired_pending:
                claim = claim or make_claim(child_row)
                if units_expired_pending >= units_shipped_pending:
                    claim.units_expired = (claim.units_expired or 0) + units_shipped_pending
                    child_row.units_expired = (child_row.units_expired or 0) + units_shipped_pending
                    units_expired_pending -= units_shipped_pending
                    units_shipped_pending = 0
                else: # shipped > expired
                    claim.units_expired = (claim.units_expired or 0) + units_expired_pending
                    child_row.units_expired = (child_row.units_expired or 0) + units_expired_pending
                    units_shipped_pending -= units_expired_pending
                    units_expired_pending = 0
                self.refresh_row(child_row)

            # claim units from parent, as cases for child.  note that this
            # crosses the case/unit boundary, but is considered "safe" because
            # we assume the child row has correct case quantity even if parent
            # row has a different one.
            if cases_shipped_pending and units_received_pending:
                received = units_received_pending // case_quantity
                if received:
                    claim = claim or make_claim(child_row)
                    if received >= cases_shipped_pending:
                        claim.cases_received = (claim.cases_received or 0) + cases_shipped_pending
                        child_row.cases_received = (child_row.units_received or 0) + cases_shipped_pending
                        units_received_pending -= (cases_shipped_pending * case_quantity)
                        cases_shipped_pending = 0
                    else: # shipped > received
                        claim.cases_received = (claim.cases_received or 0) + received
                        child_row.cases_received = (child_row.units_received or 0) + received
                        cases_shipped_pending -= received
                        units_received_pending -= (received * case_quantity)
                    self.refresh_row(child_row)
            if cases_shipped_pending and units_damaged_pending:
                damaged = units_damaged_pending // case_quantity
                if damaged:
                    claim = claim or make_claim(child_row)
                    if damaged >= cases_shipped_pending:
                        claim.cases_damaged = (claim.cases_damaged or 0) + cases_shipped_pending
                        child_row.cases_damaged = (child_row.units_damaged or 0) + cases_shipped_pending
                        units_damaged_pending -= (cases_shipped_pending * case_quantity)
                        cases_shipped_pending = 0
                    else: # shipped > damaged
                        claim.cases_damaged = (claim.cases_damaged or 0) + damaged
                        child_row.cases_damaged = (child_row.units_damaged or 0) + damaged
                        cases_shipped_pending -= damaged
                        units_damaged_pending -= (damaged * case_quantity)
                    self.refresh_row(child_row)
            if cases_shipped_pending and units_expired_pending:
                expired = units_expired_pending // case_quantity
                if expired:
                    claim = claim or make_claim(child_row)
                    if expired >= cases_shipped_pending:
                        claim.cases_expired = (claim.cases_expired or 0) + cases_shipped_pending
                        child_row.cases_expired = (child_row.units_expired or 0) + cases_shipped_pending
                        units_expired_pending -= (cases_shipped_pending * case_quantity)
                        cases_shipped_pending = 0
                    else: # shipped > expired
                        claim.cases_expired = (claim.cases_expired or 0) + expired
                        child_row.cases_expired = (child_row.units_expired or 0) + expired
                        cases_shipped_pending -= expired
                        units_expired_pending -= (expired * case_quantity)
                    self.refresh_row(child_row)

            # if necessary, try to claim cases from parent, as units for child.
            # this also crosses the case/unit boundary but is considered safe
            # only if the case quantity matches between child and parent rows.
            # (otherwise who knows what could go wrong.)
            if case_quantity == truck_dump_row.case_quantity:
                if units_shipped_pending and cases_received_pending:
                    received = cases_received_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if received >= units_shipped_pending:
                        claim.units_received = (claim.units_received or 0) + units_shipped_pending
                        child_row.units_received = (child_row.units_received or 0) + units_shipped_pending
                        leftover = received % units_shipped_pending
                        if leftover == 0:
                            cases_received_pending -= (received // units_shipped_pending)
                        else:
                            cases_received_pending -= (received // units_shipped_pending) - 1
                            units_received_pending += leftover
                        units_shipped_pending = 0
                    else: # shipped > received
                        claim.units_received = (claim.units_received or 0) + received
                        child_row.units_received = (child_row.units_received or 0) + received
                        units_shipped_pending -= received
                        cases_received_pending = 0
                    self.refresh_row(child_row)
                if units_shipped_pending and cases_damaged_pending:
                    damaged = cases_damaged_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if damaged >= units_shipped_pending:
                        claim.units_damaged = (claim.units_damaged or 0) + units_shipped_pending
                        child_row.units_damaged = (child_row.units_damaged or 0) + units_shipped_pending
                        leftover = damaged % units_shipped_pending
                        if leftover == 0:
                            cases_damaged_pending -= (damaged // units_shipped_pending)
                        else:
                            cases_damaged_pending -= (damaged // units_shipped_pending) - 1
                            units_damaged_pending += leftover
                        units_shipped_pending = 0
                    else: # shipped > damaged
                        claim.units_damaged = (claim.units_damaged or 0) + damaged
                        child_row.units_damaged = (child_row.units_damaged or 0) + damaged
                        units_shipped_pending -= damaged
                        cases_damaged_pending = 0
                    self.refresh_row(child_row)
                if units_shipped_pending and cases_expired_pending:
                    expired = cases_expired_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if expired >= units_shipped_pending:
                        claim.units_expired = (claim.units_expired or 0) + units_shipped_pending
                        child_row.units_expired = (child_row.units_expired or 0) + units_shipped_pending
                        leftover = expired % units_shipped_pending
                        if leftover == 0:
                            cases_expired_pending -= (expired // units_shipped_pending)
                        else:
                            cases_expired_pending -= (expired // units_shipped_pending) - 1
                            units_expired_pending += leftover
                        units_shipped_pending = 0
                    else: # shipped > expired
                        claim.units_expired = (claim.units_expired or 0) + expired
                        child_row.units_expired = (child_row.units_expired or 0) + expired
                        units_shipped_pending -= expired
                        cases_expired_pending = 0
                    self.refresh_row(child_row)

            # refresh the parent row, to reflect any new claim(s) made
            self.refresh_row(truck_dump_row)

    # TODO: surely this should live elsewhere
    def calc_best_fit(self, units, case_quantity):
        case_quantity = case_quantity or 1
        if case_quantity == 1:
            return 0, units
        cases = units // case_quantity
        if cases:
            return cases, units - (cases * case_quantity)
        return 0, units

    def refresh(self, batch, progress=None):
        """
        Supplements the default logic as follows:

        First, the default refresh logic runs.  And if the batch is *not* part
        of a truck dump, nothing more happens.  But if it *is* truck dump...

        Basically whether the given batch is a truck dump parent, or truck dump
        child batch, the goal here is the same.  We must locate any rows in the
        given batch which are not yet "fully claimed / complete" with regard to
        the "other" (parent/child) batch.

        For any rows which are not yet fully resolved between parent and child,
        an attempt is then made to add new row "claims" where possible, to
        eliminate the gap.

        The status of the given batch is then updated.  If the batch is a truck
        dump child then the status of its parent batch will also be updated.
        If the given batch is truck dump parent, then status for *each* of its
        children will also be updated.  See :meth:`refresh_batch_status()` for
        more on that.
        """
        # refresh all rows etc. per usual
        result = super(PurchaseBatchHandler, self).refresh(batch, progress=progress)
        if result:

            # here begins some extra magic for truck dump receiving batches
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                session = orm.object_session(batch)
                session.flush()

                if batch.is_truck_dump_parent():

                    # will try to establish new claims against the parent
                    # batch, where possible
                    unclaimed = [row for row in batch.active_rows()
                                 if row.status_code in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                                        row.STATUS_TRUCKDUMP_PARTCLAIMED)]
                    for row in unclaimed:
                        if row.product_uuid: # only support rows with product for now
                            self.make_truck_dump_claims_for_parent_row(row)

                    # all rows should be refreshed now, but batch status still needs it
                    self.refresh_batch_status(batch)
                    for child in batch.truck_dump_children:
                        self.refresh_batch_status(child)

                elif batch.is_truck_dump_child():

                    # will try to establish claims against the parent batch,
                    # for each "incomplete" row (i.e. those with unclaimed
                    # order quantities)
                    incomplete = [row for row in batch.active_rows()
                                  if row.status_code in (row.STATUS_INCOMPLETE,
                                                         row.STATUS_ORDERED_RECEIVED_DIFFER)]
                    for row in incomplete:
                        if row.product_uuid: # only support rows with product for now
                            parent_rows = [parent_row for parent_row in batch.truck_dump_batch.active_rows()
                                           if parent_row.product_uuid == row.product_uuid]
                            for parent_row in parent_rows:
                                self.make_truck_dump_claims(parent_row, [row])
                                if row.status_code not in (row.STATUS_INCOMPLETE,
                                                           row.STATUS_ORDERED_RECEIVED_DIFFER):
                                    break

                    # all rows should be refreshed now, but batch status still needs it
                    self.refresh_batch_status(batch.truck_dump_batch)
                    self.refresh_batch_status(batch)

        return result

    def refresh_batch_status(self, batch):
        """
        Logic for updating the status attribute(s) for the given batch.

        This primarily tries to see if there are any "unknown" items in the batch,
        and set status accordingly if some are found.

        But it also is responsible for setting "truck dump" status, for a truck
        dump parent batch, based on whether or not its children have fully
        claimed all of its items etc.
        """
        rows = batch.active_rows()

        # "unknown product" is the most egregious status; we'll "prefer" it
        # over all others in order to bring it to user's attention
        if any([row.status_code == row.STATUS_PRODUCT_NOT_FOUND for row in rows]):
            batch.status_code = batch.STATUS_UNKNOWN_PRODUCT

        # for now anything else is considered ok
        else:
            batch.status_code = batch.STATUS_OK

        # truck dump parent batch gets status to reflect how much is (un)claimed
        if batch.is_truck_dump_parent():

            # batch is "claimed" only if all rows are "settled" so to speak
            if all([row.truck_dump_status == row.STATUS_TRUCKDUMP_CLAIMED
                    for row in rows]):
                batch.truck_dump_status = batch.STATUS_TRUCKDUMP_CLAIMED

            # otherwise just call it "unclaimed"
            else:
                batch.truck_dump_status = batch.STATUS_TRUCKDUMP_UNCLAIMED

    def locate_product(self, row, session=None, vendor=None):
        """
        Try to locate the product represented by the given row.  Default
        behavior here, is to do a simple lookup on either ``Product.upc`` or
        ``Product.item_id``, depending on which is configured as your product
        key field.
        """
        if not session:
            session = self.app.get_session(row)

        if row.item_entry:
            product = self.locate_product_for_entry(session, row.item_entry)
            if product:
                return product

        # TODO: is the rest of this really needed?  maybe so if there are
        # some handlers out there assuming its behavior..

        product_key = self.config.product_key()

        if product_key == 'upc':
            if row.upc:
                product = self.locate_product_for_entry(session, row.upc)
            if product:
                return product

        elif product_key == 'item_id':
            if row.item_id:
                product = self.locate_product_for_entry(session, row.item_id,
                                                        product_key='item_id')

        # product key didn't work, but vendor item code just might
        if row.vendor_code:
            product = self.locate_product_for_entry(session, row.vendor_code,
                                                    product_key='NONE', # TODO
                                                    lookup_vendor_code=True,
                                                    vendor=vendor or row.batch.vendor)
            if product:
                return product

        # before giving up, let's do a lookup on alt codes too
        if row.item_entry:
            product = self.locate_product_for_entry(session, row.item_entry,
                                                    product_key='NONE', # TODO
                                                    lookup_by_code=True)
            if product:
                return product

    def transform_pack_to_unit(self, row):
        """
        Transform the given row, which is assumed to associate with a "pack"
        item, such that it associates with the "unit" item instead.
        """
        if not row.product:
            return
        if not row.product.is_pack_item():
            return

        assert row.batch.is_truck_dump_parent()

        # remove any existing claims for this (parent) row
        if row.claims:
            session = orm.object_session(row)
            del row.claims[:]
            # set temporary status for the row, if needed.  this is to help
            # with claiming logic below
            if row.status_code in (row.STATUS_TRUCKDUMP_PARTCLAIMED,
                                   row.STATUS_TRUCKDUMP_CLAIMED,
                                   row.STATUS_TRUCKDUMP_OVERCLAIMED):
                row.status_code = row.STATUS_TRUCKDUMP_UNCLAIMED
            session.flush()
            session.refresh(row)

        # pretty sure this is the only status we're expecting at this point...
        assert row.status_code == row.STATUS_TRUCKDUMP_UNCLAIMED

        # replace the row's product association
        pack = row.product
        unit = pack.unit
        row.product = unit
        row.item_id = unit.item_id
        row.upc = unit.upc

        # set new case quantity, per preferred cost
        cost = unit.cost_for_vendor(row.batch.vendor)
        row.case_quantity = (cost.case_size or 1) if cost else 1

        # must recalculate "units received" since those were for the pack item
        if row.units_received:
            row.units_received *= pack.pack_size

        # try to establish "claims" between parent and child(ren)
        self.make_truck_dump_claims_for_parent_row(row)

        # refresh the row itself, so product attributes will be updated
        self.refresh_row(row)

        # refresh status for the batch(es) proper, just in case this changed things
        self.refresh_batch_status(row.batch)
        for child in row.batch.truck_dump_children:
            self.refresh_batch_status(child)

    def make_truck_dump_claims_for_parent_row(self, row):
        """
        Try to establish all "truck dump claims" between parent and children,
        for the given parent row.
        """
        for child in row.batch.truck_dump_children:
            child_rows = [child_row for child_row in child.active_rows()
                          if child_row.product_uuid == row.product.uuid]
            if child_rows:
                self.make_truck_dump_claims(row, child_rows)
                if row.status_code not in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                           row.STATUS_TRUCKDUMP_PARTCLAIMED):
                    break

    def quick_entry(self, session, batch, entry):
        """
        Quick entry is assumed to be a UPC scan or similar user input.  Product
        lookup will be based on this.

        If the product cannot be found, an error is raised.

        If the batch already contains a row matching the relevant product, that
        row will be returned.

        Otherwise, a new row will be added to the batch, and returned.
        """
        # first try to locate the product based on quick entry
        product = self.quick_locate_product(session, batch, entry)

        # then try to locate existing row(s) which match product/entry
        rows = self.quick_locate_rows(batch, entry, product)
        if rows:

            # if aggregating, just re-use matching row
            prefer_existing = True # TODO: make configurable
            if prefer_existing:
                if len(rows) > 1:
                    log.warning("found multiple row matches for '%s' in batch %s: %s",
                                entry, batch.uuid, batch)
                return rows[0]

            else: # borrow product from matching row, but make new row
                other_row = rows[0]
                row = self.make_row()
                row.item_entry = entry
                row.product = other_row.product
                self.add_row(batch, row)
                session.flush()
                self.refresh_batch_status(batch)
                return row

        # matching row(s) not found; add new row if product was identified
        # TODO: probably should be smarter about how we handle deleted?
        if product and not product.deleted:
            row = self.make_row()
            row.item_entry = entry
            row.product = product
            self.add_row(batch, row)
            session.flush()
            self.refresh_batch_status(batch)
            return row

        # at this point a true product could not be found, but we can still add
        # a new row with just the quick entry, stored in product "key" field
        key = self.config.product_key()
        if key == 'upc':

            # check for "bad" upc
            if len(entry) > 14:
                return

            if not entry.isdigit():
                return

            provided = GPC(entry, calc_check_digit=False)
            checked = GPC(entry, calc_check_digit='upc')

            # product not in system, but presumably sane upc, so add to batch anyway
            row = self.make_row()
            row.item_entry = entry
            add_check_digit = True # TODO: make this dynamic, of course
            if add_check_digit:
                row.upc = checked
            else:
                row.upc = provided
            row.item_id = entry
            row.description = "(unknown product)"
            self.add_row(batch, row)
            session.flush()
            self.refresh_batch_status(batch)
            return row

        elif key == 'item_id':

            # check for "too long" item_id
            if len(entry) > maxlen(model.PurchaseBatchRow.item_id):
                return

            # product not in system, but presumably sane item_id, so add to batch anyway
            row = self.make_row()
            row.item_entry = entry
            row.item_id = entry
            row.description = "(unknown product)"
            self.add_row(batch, row)
            session.flush()
            self.refresh_batch_status(batch)
            return row

        else:
            raise NotImplementedError("don't know how to handle product key: {}".format(key))

    def quick_locate_product(self, session, batch, entry):
        """
        Slightly customized logic for locating a product from quick entry.

        This will attempt a "normal" product lookup first, except it will skip
        the "alternate code" lookup logic for this phase.  Effectively then,
        the lookup would work on either UUID or product "key" field only.

        If product not yet found, logic will then try to locate a cost record
        based on the entry and whichever vendor is associated with the batch.

        If product still not found, the "alternate code" lookup will be tried.
        """
        # first attempt lookup on product key (only)
        product = self.locate_product_for_entry(session, entry,
                                                lookup_by_code=False)
        if product:
            return product

        # now we'll attempt lookup by vendor item code
        product = api.get_product_by_vendor_code(session, entry,
                                                 vendor=batch.vendor)
        if product:
            return product

        # okay then, let's attempt lookup by "alternate" code
        product = api.get_product_by_code(session, entry)
        if product:
            return product

    def quick_locate_rows(self, batch, entry, product):
        """
        Locate and return all rows in the given batch, which match the given
        product and/or quick entry.

        This logic will prefer rows which match on product UUID, and if any of
        these are found then that's all that will be returned.

        Otherwise, it will attempt to match the quick entry, against the
        product "key" field for each row.
        """
        active_rows = batch.active_rows()
        rows = []

        # try to locate rows by product uuid match before other key
        if product:
            rows = [row for row in active_rows
                    if row.product_uuid == product.uuid]
            if rows:
                return rows

        key = self.config.product_key()
        if key == 'upc':

            if entry.isdigit():

                # we prefer "exact" UPC matches, i.e. those which assumed the
                # entry already contained the check digit.
                provided = GPC(entry, calc_check_digit=False)
                rows = [row for row in active_rows
                        if row.upc == provided]
                if rows:
                    return rows

                # if no "exact" UPC matches, we'll settle for those (UPC matches)
                # which assume the entry lacked a check digit.
                checked = GPC(entry, calc_check_digit='upc')
                rows = [row for row in active_rows
                        if row.upc == checked]
                return rows

        elif key == 'item_id':
            rows = [row for row in active_rows
                    if row.item_id == entry]
            return rows

    def after_add_row(self, batch, row):
        """
        Implements an event hook with the following logic:

        If the batch is for "receiving" then various invoice totals are updated,
        both for the row and batch.  In particular:

        * :attr:`rattail.db.model.batch.purchase.PurchaseBatch.invoice_total`
        * :attr:`rattail.db.model.batch.purchase.PurchaseBatch.invoice_total_calculated`
        * :attr:`rattail.db.model.batch.purchase.PurchaseBatchRow.invoice_total_calculated`
        """
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            # update "original" invoice total for batch
            if row.invoice_total is not None:
                batch.invoice_total = (batch.invoice_total or 0) + row.invoice_total

            # update "calculated" invoice totals for row, batch
            if row.invoice_unit_cost is None:
                row.invoice_total_calculated = None
            else:
                row.invoice_total_calculated = row.invoice_unit_cost * self.get_units_accounted_for(row)
            if row.invoice_total_calculated is not None:
                batch.invoice_total_calculated = (batch.invoice_total_calculated or 0) + row.invoice_total_calculated

    def refresh_row(self, row, **kwargs):
        """
        Refreshing a row will A) assume that ``row.product`` is already set to
        a valid product, or else will attempt to locate the product, and B)
        update various other fields on the row (description, size, etc.)  to
        reflect the current product data.  It also will adjust the batch PO
        total per the row PO total.
        """
        batch = row.batch

        # always reset status first thing
        row.status_code = None
        row.status_text = None

        # first identify the product, or else we have nothing more to do
        product = row.product
        if not product:
            product = self.locate_product(row)
            if product:
                row.product = product
            else:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        # update various (cached) product attributes for the row
        cost = product.cost_for_vendor(batch.vendor)
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        if product.department:
            row.department_number = product.department.number
            row.department_name = product.department.name
        else:
            row.department_number = None
            row.department_name = None
        row.vendor_code = cost.code if cost else None
        if not row.catalog_cost_confirmed:
            row.catalog_unit_cost = cost.unit_cost if cost else None

        # figure out the effective case quantity, and whether it differs with
        # what we previously had on file
        case_quantity_differs = False
        if cost and cost.case_size:
            if not row.case_quantity:
                row.case_quantity = cost.case_size
            elif row.case_quantity != cost.case_size:
                if batch.is_truck_dump_parent():
                    if batch.truck_dump_children_first:
                        # supposedly our case quantity came from a truck dump
                        # child row, which we assume to be authoritative
                        case_quantity_differs = True
                    else:
                        # truck dump has no children yet, which means we have
                        # no special authority for case quantity; therefore
                        # should treat master cost record as authority
                        row.case_quantity = cost.case_size
                else:
                    case_quantity_differs = True

        # determine PO / invoice unit cost if necessary
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING and row.po_unit_cost is None:
            row.po_unit_cost = self.get_unit_cost(row.product, batch.vendor)
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING and row.invoice_unit_cost is None:
            if row.invoice_case_cost is not None and row.case_quantity:
                row.invoice_unit_cost = (row.invoice_case_cost / row.case_quantity)\
                   .quantize(decimal.Decimal('0.00001'))
            else:
                row.invoice_unit_cost = row.po_unit_cost or (
                    cost.unit_cost if cost else None)

        # all that's left should be setting status for the row...and that logic
        # will primarily depend on the 'mode' for this purchase batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.status_code = row.STATUS_OK

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            # first check to see if we have *any* confirmed items
            if not (row.cases_received or row.units_received or
                    row.cases_damaged or row.units_damaged or
                    row.cases_expired or row.units_expired or
                    row.cases_mispick or row.units_mispick or
                    row.cases_missing or row.units_missing):

                # no, we do not have any confirmed items...

                # TODO: is this right? should row which ordered nothing just be removed?
                if batch.order_quantities_known and not (row.cases_ordered or row.units_ordered):
                    row.status_code = row.STATUS_OK
                # TODO: is this right? should out of stock just be a filter for
                # the user to specify, or should it affect status?
                elif row.out_of_stock:
                    row.status_code = row.STATUS_OUT_OF_STOCK
                else:
                    row.status_code = row.STATUS_INCOMPLETE

                # truck dump parent rows are also given status for that, which
                # reflects claimed vs. pending, i.e. child reconciliation
                if batch.is_truck_dump_parent():
                    row.truck_dump_status = row.STATUS_TRUCKDUMP_CLAIMED

            else: # we do have some confirmed items

                # primary status code for row should ideally reflect ordered
                # vs. received, although there are some exceptions
                # TODO: this used to prefer "case qty differs" and now i'm not
                # sure what the priority should be..perhaps config should say?
                if batch.order_quantities_known and (
                        self.get_units_shipped(row) != self.get_units_accounted_for(row)):
                    row.status_code = row.STATUS_ORDERED_RECEIVED_DIFFER
                elif case_quantity_differs:
                    row.status_code = row.STATUS_CASE_QUANTITY_DIFFERS
                    row.status_text = "batch has {} but master cost has {}".format(
                        repr(row.case_quantity), repr(cost.case_size))
                # TODO: is this right? should out of stock just be a filter for
                # the user to specify, or should it affect status?
                elif row.out_of_stock:
                    row.status_code = row.STATUS_OUT_OF_STOCK
                else:
                    row.status_code = row.STATUS_OK

                # truck dump parent rows are also given status for that, which
                # reflects claimed vs. pending, i.e. child reconciliation
                if batch.is_truck_dump_parent():
                    confirmed = self.get_units_confirmed(row)
                    claimed = self.get_units_claimed(row)
                    if claimed == confirmed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_CLAIMED
                    elif not claimed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_UNCLAIMED
                    elif claimed < confirmed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_PARTCLAIMED
                    elif claimed > confirmed:
                        row.truck_dump_status = row.STATUS_TRUCKDUMP_OVERCLAIMED
                    else:
                        raise NotImplementedError

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:

            if row.po_line_number and not row.invoice_line_number:
                row.status_code = row.STATUS_ON_PO_NOT_INVOICE

            elif row.invoice_line_number and not row.po_line_number:
                row.status_code = row.STATUS_ON_INVOICE_NOT_PO

            elif not self.get_units_received(row):
                row.status_code = row.STATUS_DID_NOT_RECEIVE

            elif (row.invoice_unit_cost and row.catalog_unit_cost
                  and (row.invoice_unit_cost - row.catalog_unit_cost) > self.penny):
                row.status_code = row.STATUS_COST_INCREASE

            else:
                row.status_code = row.STATUS_OK

        else:
            raise NotImplementedError("can't refresh row for batch of mode: {}".format(
                self.enum.PURCHASE_BATCH_MODE.get(batch.mode, "unknown ({})".format(batch.mode))))

    def can_declare_credit(self, row, credit_type='received', cases=None, units=None, **kwargs):
        """
        This method should be used to validate a potential declaration of
        credit, i.e. call this before calling :meth:`declare_credit()`.  See
        the latter for call signature documentation, as they are the same.

        This method will use similar logic to confirm the proposed credit is
        valid, i.e. there is sufficient "received" quantity in place for it.
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("Must provide amount for cases *or* units.")
        if cases and units:
            raise ValueError("Must provide amount for cases *or* units (but not both).")
        if cases and cases < 0:
            raise ValueError("Must provide *positive* amount for cases.")
        if units and units < 0:
            raise ValueError("Must provide *positive* amount for units.")

        # make sure we have a (non-executed) receiving batch
        if row.batch.mode != self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            raise NotImplementedError("receive_row() is only for receiving batches")
        if row.batch.executed:
            raise NotImplementedError("receive_row() is only for *non-executed* batches")

        if cases:
            if row.cases_received and row.cases_received >= cases:
                return True

            if row.units_received:
                units = cases * row.case_quantity
                if row.units_received >= units:
                    return True

        if units:
            if row.units_received and row.units_received >= units:
                return True

            if row.cases_received:
                cases = units // row.case_quantity
                if units % row.case_quantity:
                    cases += 1
                if row.cases_received >= cases:
                    return True

        raise ValueError("Credit amount cannot be more than the \"Received\" amount.")

    def declare_credit(self, row, credit_type='received', cases=None, units=None, **kwargs):
        """
        This method is similar in nature to :meth:`receive_row()`, although its
        goal is different.  Whereas ``receive_row()`` is concerned with "adding
        confirmed quantities" to the row, ``declare_credit()`` will instead
        "convert" some quantity which was previously "received" into one of the
        possible credit types.

        In other words if you have "received" 2 CS of a given product, but then
        while stocking it you discover 3 EA are damaged, then you would use
        this method to declare a credit like so::

           handler.declare_credit(row, credit_type='damaged', units=3)

        The received quantity for the row would go down by 3 EA, and its
        damaged quantity would go up by 3 EA.  The logic is able to handle
        "splitting" a case as necessary to accomplish this.

        Note that each call must specify *either* a (non-empty) ``cases`` or
        ``units`` value, but *not* both!

        :param rattail.db.model.batch.purchase.PurchaseBatchRow row: Batch row
           which is to be updated with the given receiving data.  The row must
           exist, i.e. this method will not create a new row for you.

        :param str credit_type: Must be one of the credit types which are
           "supported" according to the handler.  Possible types include:

           * ``'damaged'``
           * ``'expired'``
           * ``'mispick'``
           * ``'missing'``

        :param decimal.Decimal cases: Case quantity for the credit, if applicable.

        :param decimal.Decimal units: Unit quantity for the credit, if applicable.

        :param datetime.date expiration_date: Expiration date for the credit,
           if applicable.  Only used if ``credit_type='expired'``.
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("Must provide amount for cases *or* units.")
        if cases and units:
            raise ValueError("Must provide amount for cases *or* units (but not both).")
        if cases and cases < 0:
            raise ValueError("Must provide *positive* amount for cases.")
        if units and units < 0:
            raise ValueError("Must provide *positive* amount for units.")

        # make sure we have a (non-executed) receiving batch
        if row.batch.mode != self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            raise NotImplementedError("receive_row() is only for receiving batches")
        if row.batch.executed:
            raise NotImplementedError("receive_row() is only for *non-executed* batches")

        if cases:
            if row.cases_received and row.cases_received >= cases:
                self.receive_row(row, mode='received', cases=-cases)
                self.receive_row(row, mode=credit_type, cases=cases, **kwargs)
                return

            if row.units_received:
                units = cases * row.case_quantity
                if row.units_received >= units:
                    self.receive_row(row, mode='received', units=-units)
                    self.receive_row(row, mode=credit_type, units=units, **kwargs)
                    return

        if units:
            if row.units_received and row.units_received >= units:
                self.receive_row(row, mode='received', units=-units)
                self.receive_row(row, mode=credit_type, units=units, **kwargs)
                return

            if row.cases_received:
                cases = units // row.case_quantity
                if units % row.case_quantity:
                    cases += 1
                if row.cases_received >= cases:
                    self.receive_row(row, mode='received', cases=-cases)
                    if (cases * row.case_quantity) > units:
                        self.receive_row(row, mode='received', units=cases * row.case_quantity - units)
                    self.receive_row(row, mode=credit_type, units=units, **kwargs)
                    return

        raise ValueError("credit amount must be <= 'received' amount for the row")

    def undeclare_credit(self, row, credit, **kwargs):
        """
        This does the opposite of :meth:`declare_credit()` basically.

        Here you must provide a credit that has previously been
        declared, and this method will move the case/unit amounts for
        the credit back into the "received" tally for the row.  It
        then will remove the credit; that will no longer exist.
        """
        if credit.cases_shorted:
            self.receive_row(row, mode=credit.credit_type,
                             cases=-credit.cases_shorted,
                             update_credits=False)
            self.receive_row(row, mode='received',
                             cases=credit.cases_shorted)

        if credit.units_shorted:
            self.receive_row(row, mode=credit.credit_type,
                             units=-credit.units_shorted,
                             update_credits=False)
            self.receive_row(row, mode='received',
                             units=credit.units_shorted)

        session = self.app.get_session(row)
        session.delete(credit)

    def receive_row(self, row, mode='received', cases=None, units=None,
                    update_credits=True, **kwargs):
        """
        This method is arguably the workhorse of the whole process. Callers
        should invoke it as they receive input from the user during the
        receiving workflow.

        Each call to this method must include the row to be updated, as well as
        the details of the update.  These details should reflect "changes"
        which are to be made, as opposed to "final values" for the row.  In
        other words if a row already has ``cases_received == 1`` and the user
        is receiving a second case, this method should be called like so::

           handler.receive_row(row, mode='received', cases=1)

        The row will be updated such that ``cases_received == 2``; the main
        point here is that the caller should *not* specify ``cases=2`` because
        it is the handler's job to "apply changes" from the caller.  (If the
        caller speficies ``cases=2`` then the row would end up with
        ``cases_received == 3``.)

        For "undo" type adjustments, caller can just send a negative amount,
        and the handler will apply the changes as expected::

           handler.receive_row(row, mode='received', cases=-1)

        Note that each call must specify *either* a (non-empty) ``cases`` or
        ``units`` value, but *not* both!  If you need to adjust both then you
        must make two separate calls.

        :param ~rattail.db.model.batch.purchase.PurchaseBatchRow row: Batch row
           which is to be updated with the given receiving data.  The row must
           exist, i.e. this method will not create a new row for you.

        :param str mode: Must be one of the receiving modes which are
           "supported" according to the handler.  Possible modes include:

           * ``'received'``
           * ``'damaged'``
           * ``'expired'``
           * ``'mispick'``
           * ``'missing'``

        :param ~decimal.Decimal cases: Case quantity for the update, if applicable.

        :param ~decimal.Decimal units: Unit quantity for the update, if applicable.

        :param ~datetime.date expiration_date: Expiration date for the update,
           if applicable.  Only used if ``mode='expired'``.

        This method exists mostly to consolidate the various logical steps which
        must be taken for each new receiving input from the user.  Under the hood
        it delegates to a few other methods:

        * :meth:`receiving_update_row_attrs()`
        * :meth:`receiving_update_row_credits()`
        * :meth:`receiving_update_row_children()`
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("Must provide amount for cases *or* units.")
        if cases and units:
            raise ValueError("Must provide amount for cases *or* units (but not both).")

        # make sure we have a (non-executed) receiving batch
        if row.batch.mode != self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            raise NotImplementedError("receive_row() is only for receiving batches")
        if row.batch.executed:
            raise NotImplementedError("receive_row() is only for *non-executed* batches")

        # update the given row
        self.receiving_update_row_attrs(row, mode, cases, units)

        # update the given row's credits
        if update_credits:
            self.receiving_update_row_credits(row, mode, cases, units, **kwargs)

        # update the given row's "children" (if this is truck dump parent)
        self.receiving_update_row_children(row, mode, cases, units, **kwargs)

    def receiving_update_row_attrs(self, row, mode, cases, units):
        """
        Apply a receiving update to the row's attributes.

        Note that this should not be called directly; it is invoked as part of
        :meth:`receive_row()`.
        """
        batch = row.batch

        # add values as-is to existing case/unit amounts.  note
        # that this can sometimes give us negative values!  e.g. if
        # user scans 1 CS and then subtracts 2 EA, then we would
        # have 1 / -2 for our counts.  but we consider that to be
        # expected, and other logic must allow for the possibility
        if cases:
            setattr(row, 'cases_{}'.format(mode),
                    (getattr(row, 'cases_{}'.format(mode)) or 0) + cases)
        if units:
            setattr(row, 'units_{}'.format(mode),
                    (getattr(row, 'units_{}'.format(mode)) or 0) + units)

        # refresh row status etc.
        self.refresh_row(row)

        # update calculated invoice totals if normal received amounts
        if mode == 'received':
            # TODO: should round invoice amount to 2 places here?
            invoice_amount = 0
            if cases:
                invoice_amount += cases * (row.case_quantity or 0) * (row.invoice_unit_cost or 0)
            if units:
                invoice_amount += units * (row.invoice_unit_cost or 0)
            row.invoice_total_calculated = (row.invoice_total_calculated or 0) + invoice_amount
            batch.invoice_total_calculated = (batch.invoice_total_calculated or 0) + invoice_amount

    def receiving_update_row_credits(self, row, mode, cases, units, **kwargs):
        """
        Apply a receiving update to the row's credits, if applicable.

        Note that this should not be called directly; it is invoked as part of
        :meth:`receive_row()`.
        """
        batch = row.batch

        # only certain modes should involve credits
        if mode not in ('damaged', 'expired', 'mispick', 'missing'):
            return

        # TODO: need to add mispick support obviously
        if mode == 'mispick':
            raise NotImplementedError("mispick credits not yet supported")

        # TODO: must account for negative values here! i.e. remove credit in
        # some scenarios, perhaps using `kwargs` to find the match?
        if (cases and cases > 0) or (units and units > 0):
            positive = True
        else:
            positive = False
            raise NotImplementedError("TODO: add support for negative values when updating credits")

        # always make new credit; never aggregate
        credit = model.PurchaseBatchCredit()
        self.populate_credit(credit, row)
        credit.credit_type = mode
        credit.cases_shorted = cases or None
        credit.units_shorted = units or None

        # calculate credit total
        # TODO: should this leverage case cost if present?
        credit_units = self.get_units(credit.cases_shorted,
                                      credit.units_shorted,
                                      credit.case_quantity)
        credit.credit_total = credit_units * (credit.invoice_unit_cost or 0)

        # apply other attributes to credit, per caller kwargs
        credit.product_discarded = kwargs.get('discarded')
        if mode == 'expired':
            credit.expiration_date = kwargs.get('expiration_date')
        elif mode == 'mispick' and kwargs.get('mispick_product'):
            mispick_product = kwargs['mispick_product']
            credit.mispick_product = mispick_product
            credit.mispick_upc = mispick_product.upc
            if mispick_product.brand:
                credit.mispick_brand_name = mispick_product.brand.name
            credit.mispick_description = mispick_product.description
            credit.mispick_size = mispick_product.size

        # attach credit to row
        row.credits.append(credit)

    def update_row_cost(self, row, **kwargs):
        """
        Update the cost value(s) for the given row, and calculate new totals
        accordingly.  This will handle updating the row as well as the batch,
        as necessary.

        Note that thus far, it is assumed the given row is for a "receiving"
        batch, and the logic does not provide special handling for truck dump.
        The only cost kwargs supported are:

        * ``catalog_unit_cost``
        * ``invoice_unit_cost``
        """
        session = orm.object_session(row)
        batch = row.batch

        # cache original values for comparison
        old_invoice_total_calculated = row.invoice_total_calculated

        # update catalog_unit_cost for row
        if 'catalog_unit_cost' in kwargs:
            row.catalog_unit_cost = kwargs['catalog_unit_cost']
            row.catalog_cost_confirmed = True

        # update invoice_unit_cost for row, and totals for row/batch
        if 'invoice_unit_cost' in kwargs:
            row.invoice_unit_cost = kwargs['invoice_unit_cost']
            row.invoice_cost_confirmed = True
            row.invoice_total_calculated = (
                row.invoice_unit_cost * self.get_units_accounted_for(row))
            batch.invoice_total_calculated += (
                row.invoice_total_calculated - old_invoice_total_calculated)

        session.flush()
        self.refresh_row(row)

    def update_row_quantity(self, row, **kwargs):
        """
        Update quantity value(s) for the given row, and calculate new totals
        accordingly.  This will handle updating the row as well as the batch,
        as necessary.  Which kwargs this method accepts, and which values are
        updated, will depend on the batch mode.

        *Ordering Mode*

        Possible kwargs are:

        * ``cases_ordered``
        * ``units_ordered``

        Logic will figure out the "diff" between the given quantites, and the
        row's existing values at the time.  It then invokes :meth:`order_row()`
        with the diff values.
        """
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            cases_ordered = kwargs.get('cases_ordered')
            if cases_ordered is not None:
                if isinstance(cases_ordered, six.string_types):
                    cases_ordered = decimal.Decimal(cases_ordered or '0')
                cases_diff = cases_ordered - (row.cases_ordered or 0)
                if cases_diff:
                    self.order_row(row, cases=cases_diff)
            units_ordered = kwargs.get('units_ordered')
            if units_ordered is not None:
                if isinstance(units_ordered, six.string_types):
                    units_ordered = decimal.Decimal(units_ordered or '0')
                units_diff = units_ordered - (row.units_ordered or 0)
                if units_diff:
                    self.order_row(row, units=units_diff)

    def order_row(self, row, cases=None, units=None, **kwargs):
        """
        This method is conceptually similar to :meth:`receive_row()` and, while
        the latter is more "necessary" than this one is, this method tries to
        match its style just for consistency.  Callers may or may not need this
        method directly, but are welcome to use it.

        Each call to this method must include the row to be updated, as well as
        the details of the update.  These details should reflect "changes"
        which are to be made, as opposed to "final values" for the row.  In
        other words if a row already has ``cases_ordered == 1`` and the user
        is ordering a second case, this method should be called like so::

           handler.order_row(row, cases=1)

        The row will be updated such that ``cases_ordered == 2``; the main
        point here is that the caller should *not* specify ``cases=2`` because
        it is the handler's job to "apply changes" from the caller.  (If the
        caller speficies ``cases=2`` then the row would end up with
        ``cases_ordered == 3``.)

        See also :meth:`update_row_quantity()` which allows the caller to
        specify the final values instead.

        For "undo" type adjustments, caller can just send a negative amount,
        and the handler will apply the changes as expected::

           handler.order_row(row, cases=-1)

        Note that each call must specify *either* a (non-empty) ``cases`` or
        ``units`` value, but *not* both!  If you need to adjust both then you
        must make two separate calls.

        :param ~rattail.db.model.batch.purchase.PurchaseBatchRow row: Batch row
           which is to be updated with the given order data.  The row must
           exist, i.e. this method will not create a new row for you.

        :param ~decimal.Decimal cases: Case quantity for the update, if applicable.

        :param ~decimal.Decimal units: Unit quantity for the update, if applicable.
        """
        # make sure we have cases *or* units
        if not (cases or units):
            raise ValueError("must provide amount for cases *or* units")
        if cases and units:
            raise ValueError("must provide amount for cases *or* units (but not both)")

        batch = row.batch

        # make sure we have a (non-executed) ordering batch
        if batch.mode != self.enum.PURCHASE_BATCH_MODE_ORDERING:
            raise NotImplementedError("order_row() is only for ordering batches")
        if batch.executed:
            raise BatchAlreadyExecuted(batch)

        # add values as-is to existing case/unit amounts.
        # TODO: what if this gives us negative values?
        if cases:
            row.cases_ordered = (row.cases_ordered or 0) + cases
        if units:
            row.units_ordered = (row.units_ordered or 0) + units

        # TODO: pretty sure this isn't needed?
        # # refresh row status etc.
        # self.refresh_row(row)

        # update calculated PO totals
        po_amount = 0
        if cases:
            po_amount += cases * (row.case_quantity or 1) * (row.po_unit_cost or 0)
        if units:
            po_amount += units * (row.po_unit_cost or 0)
        row.po_total_calculated = (row.po_total_calculated or 0) + po_amount
        batch.po_total_calculated = (batch.po_total_calculated or 0) + po_amount

    def get_order_form_costs(self, session, vendor):
        """
        This method should return an iterable sequence of "cost" records, each
        of which corresponds to a single (unique) product, and which should be
        displayed on an "order form" for a buyer.  Note that this need not sort
        the list, as that is done in :meth:`sort_order_form_costs()`.

        Default logic will return
        :class:`~rattail.db.model.product.ProductCost` records.  It should
        ideally be possible to return any "other" type of cost records, but
        probably other code will need some tweaks to allow for that.

        Default logic also will try to filter out certain "undesirable"
        products, e.g. those which are discontinued, deleted etc.
        """
        # note that the joinedload() usage is for efficiency when displaying
        # the final record within the order form worksheet
        return session.query(model.ProductCost)\
                      .join(model.Product)\
                      .outerjoin(model.Brand)\
                      .filter(model.ProductCost.vendor == vendor)\
                      .filter(model.Product.deleted == False)\
                      .filter(model.Product.discontinued == False)\
                      .filter(model.Product.not_for_sale == False)\
                      .options(orm.joinedload(model.ProductCost.product)\
                               .joinedload(model.Product.department))\
                      .options(orm.joinedload(model.ProductCost.product)\
                               .joinedload(model.Product.subdepartment))

    def sort_order_form_costs(self, costs):
        """
        Sort the given sequence of "cost" records, for display on the Order
        Form worksheet.
        """
        return costs.order_by(model.Brand.name,
                              model.Product.description,
                              model.Product.size)

    def decorate_order_form_costs(self, batch, costs):
        """
        Decorate the given sequence of "cost" records, to add any additional
        context data needed for display on Order Form worksheet.
        """

    def get_order_form_history(self, batch, costs, count):
        """
        This method should return relevant purchase history, for display within
        the Order Form worksheet.

        :param batch: Reference to the current batch, for which the Order Form
           worksheet is to be displayed.

        :param costs: Sequence of "cost" records for the current worksheet.

        :param count: Number of recent purchases for which history should be
           returned.  May depend on the caller generating the worksheet, but
           default number for this is probably 6.
        """
        session = orm.object_session(batch)

        # fetch last X purchases for this vendor, organize line items by product
        history = []
        purchases = session.query(model.Purchase)\
                           .filter(model.Purchase.vendor == batch.vendor)\
                           .filter(model.Purchase.status >= self.enum.PURCHASE_STATUS_ORDERED)\
                           .order_by(model.Purchase.date_ordered.desc(),
                                     model.Purchase.created.desc())\
                           .options(orm.joinedload(model.Purchase.items))
        for purchase in purchases[:count]:
            items = {}
            for item in purchase.items:
                items[item.product_uuid] = item
            history.append({'purchase': purchase, 'items': items})

        return history

    def populate_credit(self, credit, row):
        """
        Populate all basic attributes for the given credit, from the given row.
        """
        batch = row.batch

        credit.store = batch.store
        credit.vendor = batch.vendor
        credit.date_ordered = batch.date_ordered
        credit.date_shipped = batch.date_shipped
        credit.date_received = batch.date_received
        credit.invoice_number = batch.invoice_number
        credit.invoice_date = batch.invoice_date
        credit.product = row.product
        credit.upc = row.upc
        credit.vendor_item_code = row.vendor_code
        credit.brand_name = row.brand_name
        credit.description = row.description
        credit.size = row.size
        credit.department_number = row.department_number
        credit.department_name = row.department_name
        credit.case_quantity = row.case_quantity
        credit.invoice_line_number = row.invoice_line_number
        credit.invoice_case_cost = row.invoice_case_cost
        credit.invoice_unit_cost = row.invoice_unit_cost
        credit.invoice_total = row.invoice_total_calculated

    def receiving_update_row_children(self, row, mode, cases, units, **kwargs):
        """
        Apply a receiving update to the row's "children", if applicable.

        Note that this should not be called directly; it is invoked as part of
        :meth:`receive_row()`.

        This logic only applies to a "truck dump parent" row, since that is the
        only type which can have "children".  Also this logic is assumed only
        to apply if using the "children first" workflow.  If these criteria are
        not met then nothing is done.

        This method is ultimately responsible for updating "everything"
        (relevant) about the children of the given parent row.  This includes
        updating the child row(s) as well as the "claim" records used for
        reconciliation, as well as any child credit(s).  However most of the
        heavy lifting is done by :meth:`receiving_update_row_child()`.
        """
        batch = row.batch

        # updating row children is only applicable for truck dump parent, and
        # even then only if "children first" workflow
        if not batch.is_truck_dump_parent():
            return
        # TODO: maybe should just check for `batch.truck_dump_children` instead?
        if not batch.truck_dump_children_first:
            return

        # apply changes to child row(s) until we exhaust update quantities
        while cases or units:

            # find the "best match" child per current quantities, or quit if we
            # can no longer find any child match at all
            child_row = self.receiving_find_best_child_row(row, mode, cases, units)
            if not child_row:
                break

            # apply update to child, which should reduce our quantities
            before = cases, units
            cases, units = self.receiving_update_row_child(row, child_row, mode, cases, units, **kwargs)
            if (cases, units) == before:
                raise RuntimeError("infinite loop detected; aborting")

        # refresh parent row status
        self.refresh_row(row)

    def receiving_update_row_child(self, parent_row, child_row, mode, cases, units, **kwargs):
        """
        Update the given child row attributes, as well as the "claim" record
        which ties it to the parent, as well as any credit(s) which may apply.

        Ideally the child row can accommodate the "full" case/unit amounts
        given, but if not then it must do as much as it can.  Note that the
        child row should have been located via :meth:`receiving_find_best_child_row()`
        and therefore should be able to accommodate *something* at least.

        This method returns a 2-tuple of ``(cases, units)`` which reflect the
        amounts it was *not* able to claim (or relinquish, if incoming amounts
        are negative).  In other words these are the "leftovers" which still
        need to be dealt with somehow.
        """
        # were we given positive or negative values for the update?
        if (cases and cases > 0) or (units and units > 0):
            positive = True
        else:
            positive = False

        ##############################

        def update(cases, units):

            # update child claim
            claim = get_claim()
            if cases:
                setattr(claim, 'cases_{}'.format(mode),
                        (getattr(claim, 'cases_{}'.format(mode)) or 0) + cases)
            if units:
                setattr(claim, 'units_{}'.format(mode),
                        (getattr(claim, 'units_{}'.format(mode)) or 0) + units)
            # remove claim if now empty (should only happen if negative values?)
            if claim.is_empty():
                parent_row.claims.remove(claim)

            # update child row
            self.receiving_update_row_attrs(child_row, mode, cases, units)
            if cases:
                child_row.cases_shipped_claimed += cases
                child_row.cases_shipped_pending -= cases
            if units:
                child_row.units_shipped_claimed += units
                child_row.units_shipped_pending -= units

            # update child credit, if applicable
            self.receiving_update_row_credits(child_row, mode, cases, units, **kwargs)

        def get_claim():
            claims = [claim for claim in parent_row.claims
                      if claim.claiming_row is child_row]
            if claims:
                if len(claims) > 1:
                    raise ValueError("child row has too many claims on parent!")
                return claims[0]
            claim = model.PurchaseBatchRowClaim()
            claim.claiming_row = child_row
            parent_row.claims.append(claim)
            return claim

        ##############################

        # first we try to accommodate the full "as-is" amounts, if possible
        if positive:
            if cases and units:
                if child_row.cases_shipped_pending >= cases and child_row.units_shipped_pending >= units:
                    update(cases, units)
                    return 0, 0
            elif cases:
                if child_row.cases_shipped_pending >= cases:
                    update(cases, 0)
                    return 0, 0
            else: # units
                if child_row.units_shipped_pending >= units:
                    update(0, units)
                    return 0, 0
        else: # negative
            if cases and units:
                if child_row.cases_shipped_claimed >= -cases and child_row.units_shipped_claimed >= -units:
                    update(cases, units)
                    return 0, 0
            elif cases:
                if child_row.cases_shipped_claimed >= -cases:
                    update(cases, 0)
                    return 0, 0
            else: # units
                if child_row.units_shipped_claimed >= -units:
                    update(0, units)
                    return 0, 0

        # next we try a couple more variations on that theme, aiming for "as
        # much as possible, as simply as possible"
        if cases and units:
            if positive:
                if child_row.cases_shipped_pending >= cases:
                    update(cases, 0)
                    return 0, units
                if child_row.units_shipped_pending >= units:
                    update(0, units)
                    return cases, 0
            else: # negative
                if child_row.cases_shipped_claimed >= -cases:
                    update(cases, 0)
                    return 0, units
                if child_row.units_shipped_claimed >= -units:
                    update(0, units)
                    return cases, 0

        # okay then, try to (simply) use up any "child" quantities
        if positive:
            if cases and units and (child_row.cases_shipped_pending
                                    and child_row.units_shipped_pending):
                pending = (child_row.cases_shipped_pending,
                           child_row.units_shipped_pending)
                update(pending[0], pending[1])
                return cases - pending[0], units - pending[1]
            if cases and child_row.cases_shipped_pending:
                pending = child_row.cases_shipped_pending
                update(pending, 0)
                return cases - pending, 0
            if units and child_row.units_shipped_pending:
                pending = child_row.units_shipped_pending
                update(0, pending)
                return 0, units - pending
        else: # negative
            if cases and units and (child_row.cases_shipped_claimed
                                    and child_row.units_shipped_claimed):
                claimed = (child_row.cases_shipped_claimed,
                           child_row.units_shipped_claimed)
                update(-claimed[0], -claimed[1])
                return cases + claimed[0], units + claimed[1]
            if cases and child_row.cases_shipped_claimed:
                claimed = child_row.cases_shipped_claimed
                update(-claimed, 0)
                return cases + claimed, 0
            if units and child_row.units_shipped_claimed:
                claimed = child_row.units_shipped_claimed
                update(0, -claimed)
                return 0, units + claimed

        # looks like we're gonna have to split some cases, one way or another
        if parent_row.case_quantity != child_row.case_quantity:
            raise NotImplementedError("cannot split case when parent/child disagree about size")
        if positive:
            if cases and child_row.units_shipped_pending:
                if child_row.units_shipped_pending >= parent_row.case_quantity:
                    unit_cases = child_row.units_shipped_pending // parent_row.case_quantity
                    if unit_cases >= cases:
                        update(0, cases * parent_row.case_quantity)
                        return 0, units
                    else: # unit_cases < cases
                        update(0, unit_cases * parent_row.case_quantity)
                        return cases - unit_cases, units
                else: # units_pending < case_size
                    pending = child_row.units_shipped_pending
                    update(0, pending)
                    return (cases - 1,
                            (units or 0) + parent_row.case_quantity - pending)
            if units and child_row.cases_shipped_pending:
                if units >= parent_row.case_quantity:
                    unit_cases = units // parent_row.case_quantity
                    if unit_cases <= child_row.cases_shipped_pending:
                        update(unit_cases, 0)
                        return 0, units - (unit_cases * parent_row.case_quantity)
                    else: # unit_cases > cases_pending
                        pending = child_row.cases_shipped_pending
                        update(pending, 0)
                        return 0, units - (pending * parent_row.case_quantity)
                else: # units < case_size
                    update(0, units)
                    return 0, 0
        else: # negative
            if cases and child_row.units_shipped_claimed:
                if child_row.units_shipped_claimed >= parent_row.case_quantity:
                    unit_cases = child_row.units_shipped_claimed // parent_row.case_quantity
                    if unit_cases >= -cases:
                        update(0, cases * parent_row.case_quantity)
                        return 0, units
                    else: # unit_cases < -cases
                        update(0, -unit_cases * parent_row.case_quantity)
                        return cases + unit_cases, units
                else: # units_claimed < case_size
                    claimed = child_row.units_shipped_claimed
                    update(0, -claimed)
                    return (cases + 1,
                            (units or 0) - parent_row.case_quantity + claimed)
            if units and child_row.cases_shipped_claimed:
                if -units >= parent_row.case_quantity:
                    unit_cases = -units // parent_row.case_quantity
                    if unit_cases <= child_row.cases_shipped_claimed:
                        update(-unit_cases, 0)
                        return 0, units + (unit_cases * parent_row.case_quantity)
                    else: # unit_cases > cases_claimed
                        claimed = child_row.cases_shipped_claimed
                        update(-claimed, 0)
                        return 0, units + (claimed * parent_row.case_quantity)
                else: # -units < case_size
                    update(0, units)
                    return 0, 0

        # TODO: this should theoretically never happen; should log/raise error?
        log.warning("unable to claim/relinquish any case/unit amounts for child row: %s", child_row)
        return cases, units

    def receiving_find_best_child_row(self, row, mode, cases, units):
        """
        Locate and return the "best match" child row, for the given parent row
        and receiving update details.  The idea here is that the parent row
        will represent the "receiving" side of things, whereas the child row
        will be the "ordering" side.

        For instance if the update is for say, "received 2 CS" and there are
        two child rows, one of which is for 1 CS and the other 2 CS, the latter
        will be returned.  This logic is capable of "splitting" a case where
        necessary, in order to find a partial match etc.
        """
        parent_row = row
        parent_batch = parent_row.batch

        if not (cases or units):
            raise ValueError("must provide amount for cases and/or units")

        if cases and units and (
                (cases > 0 and units < 0) or (cases < 0 and units > 0)):
            raise NotImplementedError("not sure how to handle mixed pos/neg for case/unit amounts")

        # were we given positive or negative values for the update?
        if (cases and cases > 0) or (units and units > 0):
            positive = True
        else:
            positive = False

        # first we collect all potential child rows
        all_child_rows = []
        for child_batch in parent_batch.truck_dump_children:

            # match on exact product if possible, otherwise must match on upc etc.
            if parent_row.product:
                child_rows = [child_row for child_row in child_batch.active_rows()
                              if child_row.product_uuid == parent_row.product.uuid]
            else:
                # note that we only want to match child rows which have *no* product ref
                # TODO: should consult config to determine which product key to match on
                child_rows = [child_row for child_row in child_batch.active_rows()
                              if not child_row.product_uuid and child_row.upc == parent_row.upc]

            for child_row in child_rows:

                # for each child row we also calculate "claimed" vs. "pending" amounts

                # cases_ordered
                child_row.cases_shipped_claimed = sum([(claim.cases_received or 0)
                                                       + (claim.cases_damaged or 0)
                                                       + (claim.cases_expired or 0)
                                                       for claim in child_row.truck_dump_claims])
                child_row.cases_shipped_pending = (child_row.cases_ordered or 0) - child_row.cases_shipped_claimed

                # units_ordered
                child_row.units_shipped_claimed = sum([(claim.units_received or 0)
                                                       + (claim.units_damaged or 0)
                                                       + (claim.units_expired or 0)
                                                       for claim in child_row.truck_dump_claims])
                child_row.units_shipped_pending = (child_row.units_ordered or 0) - child_row.units_shipped_claimed

                # maybe account for split cases
                if child_row.units_shipped_pending < 0:
                    split_cases = -child_row.units_shipped_pending // child_row.case_quantity
                    if -child_row.units_shipped_pending % child_row.case_quantity:
                        split_cases += 1
                    if split_cases > child_row.cases_shipped_pending:
                        raise ValueError("too many cases have been split?")
                    child_row.cases_shipped_pending -= split_cases
                    child_row.units_shipped_pending += split_cases * child_row.case_quantity

                all_child_rows.append(child_row)

        def sortkey(row):
            if positive:
                return self.get_units(row.cases_shipped_pending,
                                      row.units_shipped_pending,
                                      row.case_quantity)
            else: # negative
                return self.get_units(row.cases_shipped_claimed,
                                      row.units_shipped_claimed,
                                      row.case_quantity)

        # sort child rows such that smallest (relevant) quantities come first;
        # idea being we would prefer the "least common denominator" to match
        all_child_rows.sort(key=sortkey)

        # first try to find an exact match
        for child_row in all_child_rows:
            if cases and units:
                if positive:
                    if child_row.cases_shipped_pending == cases and child_row.units_shipped_pending == units:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed == cases and child_row.units_shipped_claimed == units:
                        return child_row
            elif cases:
                if positive:
                    if child_row.cases_shipped_pending == cases:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed == cases:
                        return child_row
            else: # units
                if positive:
                    if child_row.units_shipped_pending == units:
                        return child_row
                else: # negative
                    if child_row.units_shipped_claimed == units:
                        return child_row

        # next we try to find the "first" (smallest) match which satisfies, but
        # which does so *without* having to split up any cases
        for child_row in all_child_rows:
            if cases and units:
                if positive:
                    if child_row.cases_shipped_pending >= cases and child_row.units_shipped_pending >= units:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed >= -cases and child_row.units_shipped_claimed >= -units:
                        return child_row
            elif cases:
                if positive:
                    if child_row.cases_shipped_pending >= cases:
                        return child_row
                else: # negative
                    if child_row.cases_shipped_claimed >= -cases:
                        return child_row
            else: # units
                if positive:
                    if child_row.units_shipped_pending >= units:
                        return child_row
                else: # negative
                    if child_row.units_shipped_claimed >= -units:
                        return child_row

        # okay, we're getting desperate now; let's start splitting cases and
        # may the first possible match (which fully satisfies) win...
        incoming_units = self.get_units(cases, units, parent_row.case_quantity)
        for child_row in all_child_rows:
            if positive:
                pending_units = self.get_units(child_row.cases_shipped_pending,
                                               child_row.units_shipped_pending,
                                               child_row.case_quantity)
                if pending_units >= incoming_units:
                    return child_row
            else: # negative
                claimed_units = self.get_units(child_row.cases_shipped_claimed,
                                               child_row.units_shipped_claimed,
                                               child_row.case_quantity)
                if claimed_units >= -incoming_units:
                    return child_row

        # and now we're even more desperate.  at this point no child row can
        # fully (by itself) accommodate the update at hand, which means we must
        # look for the first child which can accommodate anything at all, and
        # settle for the partial match.  note that we traverse the child row
        # list *backwards* here, hoping for the "biggest" match
        for child_row in reversed(all_child_rows):
            if positive:
                if child_row.cases_shipped_pending or child_row.units_shipped_pending:
                    return child_row
            else: # negative
                if child_row.cases_shipped_claimed or child_row.units_shipped_claimed:
                    return child_row

    def remove_row(self, row):
        """
        Overrides the default logic as follows:

        In all cases, the row is deleted outright from the batch, instead of
        simply marking its ``removed`` flag.  Then
        :meth:`refresh_batch_status()` is invoked.

        However, *before* those things happen, we may do some other steps based
        on the batch mode:

        *Ordering Mode*

        If the row has a
        :attr:`~rattail.db.model.batch.purchase.PurchaseBatchRow.po_total_calculated`
        amount, then the batch's
        :attr:`~rattail.db.model.batch.purchase.PurchaseBatch.po_total_calculated`
        is decreased by that amount.

        *Receiving Mode*

        If the row has a
        :attr:`~rattail.db.model.batch.purchase.PurchaseBatchRow.invoice_total_calculated`
        amount, then the batch's
        :attr:`~rattail.db.model.batch.purchase.PurchaseBatch.invoice_total_calculated`
        is decreased by that amount.
        """
        session = orm.object_session(row)
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            if row.po_total_calculated:
                batch.po_total_calculated -= row.po_total_calculated

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if row.invoice_total_calculated:
                batch.invoice_total_calculated -= row.invoice_total_calculated

        session.delete(row)
        session.flush()
        self.refresh_batch_status(batch)

    def get_unit_cost(self, product, vendor):
        """
        Must return the PO unit cost for the given product, from the given vendor.
        """
        cost = product.cost_for_vendor(vendor) or product.cost
        if cost:
            return cost.unit_cost

    def get_units(self, cases, units, case_quantity):
        case_quantity = case_quantity or 1
        return (units or 0) + case_quantity * (cases or 0)

    def get_units_ordered(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_ordered, row.units_ordered, case_quantity)

    def get_units_shipped(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_shipped, row.units_shipped, case_quantity)

    def get_units_received(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_received, row.units_received, case_quantity)

    def get_units_damaged(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_damaged, row.units_damaged, case_quantity)

    def get_units_expired(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_expired, row.units_expired, case_quantity)

    def get_units_confirmed(self, row, case_quantity=None):
        received = self.get_units_received(row, case_quantity=case_quantity)
        damaged = self.get_units_damaged(row, case_quantity=case_quantity)
        expired = self.get_units_expired(row, case_quantity=case_quantity)
        return received + damaged + expired

    def get_units_mispick(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_mispick, row.units_mispick, case_quantity)

    def get_units_missing(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_missing, row.units_missing, case_quantity)

    def get_units_accounted_for(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        mispick = self.get_units_mispick(row, case_quantity=case_quantity)
        missing = self.get_units_missing(row, case_quantity=case_quantity)
        return confirmed + mispick + missing

    def get_units_shorted(self, obj, case_quantity=None):
        case_quantity = case_quantity or obj.case_quantity or 1
        if hasattr(obj, 'cases_shorted'):
            # obj is really a credit
            return self.get_units(obj.cases_shorted, obj.units_shorted, case_quantity)
        else:
            # obj is a row, so sum the credits
            return sum([self.get_units(credit.cases_shorted, credit.units_shorted, case_quantity)
                        for credit in obj.credits])

    def get_units_claimed(self, row, case_quantity=None):
        """
        Returns the total number of units which are "claimed" by child rows,
        for the given truck dump parent row.
        """
        claimed = 0
        for claim in row.claims:
            # prefer child row's notion of case quantity, over parent row
            case_qty = case_quantity or claim.claiming_row.case_quantity or row.case_quantity
            claimed += self.get_units_confirmed(claim, case_quantity=case_qty)
        return claimed

    def get_units_claimed_received(self, row, case_quantity=None):
        return sum([self.get_units_received(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_damaged(self, row, case_quantity=None):
        return sum([self.get_units_damaged(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_expired(self, row, case_quantity=None):
        return sum([self.get_units_expired(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_available(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        claimed = self.get_units_claimed(row, case_quantity=case_quantity)
        return confirmed - claimed

    def auto_receive_all_items(self, batch, progress=None):
        """
        Automatically "receive" all items for the given batch.  Meant for
        development purposes only!
        """
        def receive(row, i):
            # only do this for rows which have product identified
            if row.product:

                # auto-receive whatever is left
                cases, units = self.calculate_pending(row, unconfirmed='shipped')
                if cases:
                    self.receive_row(row, mode='received', cases=cases)
                if units:
                    self.receive_row(row, mode='received', units=units)

        self.progress_loop(receive, batch.active_rows(), progress,
                           message="Marking all items as \"received\"")

        batch.set_param('auto_received', True)
        self.refresh(batch, progress=progress)

    def update_order_counts(self, purchase, progress=None):
        """
        Update the "on order" counts for all items on the given purchase.
        Obviously this assumes that the purchase was just "ordered" from the
        vendor.
        """

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                inventory.on_order = (inventory.on_order or 0) + (item.units_ordered or 0) + (
                    (item.cases_ordered or 0) * (item.case_quantity or 1))

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def update_receiving_inventory(self, purchase, consume_on_order=True, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                count = (item.units_received or 0) + (item.cases_received or 0) * (item.case_quantity or 1)
                if count:
                    if consume_on_order:
                        if (inventory.on_order or 0) < count:
                            log.error("received %s units for %s but it only had %s on order",
                                      count, item.product, inventory.on_order or 0)
                            inventory.on_order = 0
                        else:
                            inventory.on_order -= count
                    inventory.on_hand = (inventory.on_hand or 0) + count

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def why_not_execute(self, batch):
        """
        This makes the following checks, but only for "receiving" batches:

        If it is a truck dump parent batch, then its
        :attr:`~rattail.db.model.batch.purchase.PurchaseBatch.truck_dump_status`
        must be "claimed" or else execution is not allowed.  This is for
        simplicity, to require the truck dump parent and child batches to be
        "fully" on the same page, and nothing accidentally left behind.

        If it is a truck dump child, then execution is "never" allowed.  (At
        least, that's what we want to tell the user, so they're forced to
        execute the parent batch.  Technically the handler *does* know how to
        execute a child batch; see :meth:`execute()` and
        :meth:`execute_truck_dump()` for more info.)
        """
        # not all receiving batches are executable
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            if batch.is_truck_dump_parent() and batch.truck_dump_status != batch.STATUS_TRUCKDUMP_CLAIMED:
                return ("Can't execute a Truck Dump (parent) batch until "
                        "it has been fully claimed by children")

            if batch.is_truck_dump_child():
                return ("Can't directly execute batch which is child of a truck dump "
                        "(must execute truck dump instead)")

    def describe_execution(self, batch, html_allowed=False, **kwargs):
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            return ("A new \"Purchase\" is created, from the contents of this "
                    "batch.  Also, the \"On Order\" counts for each product "
                    "will be updated accordingly.  You will be redirected to "
                    "the new Purchase.")

    def execute(self, batch, user, progress=None):
        """
        Performs execution logic for the batch, as follows:

        *Ordering Mode*

        A new purchase is created via :meth:`make_purchase()`, and then
        :meth:`update_order_counts()` is invoked to keep the numbers straight.
        The new purchase is then returned.

        *Receiving Mode*

        If the batch does not yet have a receiving date, that is set to the
        current date.

        If the batch is a truck dump parent, then :meth:`execute_truck_dump()`
        is invoked.

        Otherwise, either a "traditional" receiving, or truck dump child batch
        is assumed, and :meth:`receive_purchase()` is invoked.

        *Costing Mode*

        This assumes an original purchase is attached to the batch.  The
        invoice date for that purchase is updated according to the value in the
        batch, and the status for the purchase is set to "costed".  The
        purchase object is returned.

        .. note::
           Execution for a "costing" batch has yet to be fully implemented.
        """
        session = orm.object_session(batch)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            purchase = self.make_purchase(batch, user, progress=progress)
            self.update_order_counts(purchase, progress=progress)
            return purchase

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if not batch.date_received:
                batch.date_received = localtime(self.config).date()
            if self.allow_truck_dump_receiving() and batch.is_truck_dump_parent():
                self.execute_truck_dump(batch, user, progress=progress)
                return True
            else:
                with session.no_autoflush:
                    return self.receive_purchase(batch, progress=progress)

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            # TODO: finish this...
            # with session.no_autoflush:
            #     return self.cost_purchase(batch, progress=progress)
            purchase = batch.purchase
            purchase.invoice_date = batch.invoice_date
            purchase.status = self.enum.PURCHASE_STATUS_COSTED
            return purchase

        assert False

    def execute_truck_dump(self, batch, user, progress=None):
        """
        Fully executes a truck dump parent batch.  In reality nothing is done
        with the data from the parent; instead, each truck dump child batch is
        simply executed in sequence.
        """
        now = make_utc()
        for child in batch.truck_dump_children:
            if not self.execute(child, user, progress=progress):
                raise RuntimeError("Failed to execute child batch: {}".format(child))
            child.executed = now
            child.executed_by = user

    def make_credits(self, batch, progress=None):
        """
        Make all final credit records for the given batch.  Meant to be called
        as part of the batch execution process.
        """
        session = orm.object_session(batch)
        mapper = orm.class_mapper(model.PurchaseBatchCredit)
        date_received = batch.date_received
        if not date_received:
            date_received = localtime(self.config).date()

        def add_credits(row, i):

            # basically "clone" existing credits from batch row
            for batch_credit in row.credits:
                credit = model.PurchaseCredit()
                for prop in mapper.iterate_properties:
                    if isinstance(prop, orm.ColumnProperty) and hasattr(credit, prop.key):
                        setattr(credit, prop.key, getattr(batch_credit, prop.key))
                credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                if not credit.date_received:
                    credit.date_received = date_received
                session.add(credit)

            # maybe create "missing" credits for items not accounted for
            if not row.out_of_stock:
                cases, units = self.calculate_pending(row)
                if cases or units:
                    credit = model.PurchaseCredit()
                    self.populate_credit(credit, row)
                    credit.credit_type = 'missing'
                    credit.cases_shorted = cases or None
                    credit.units_shorted = units or None

                    # calculate credit total
                    # TODO: should this leverage case cost if present?
                    credit_units = self.get_units(credit.cases_shorted,
                                                  credit.units_shorted,
                                                  credit.case_quantity)
                    credit.credit_total = credit_units * (credit.invoice_unit_cost or 0)

                    credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                    if not credit.date_received:
                        credit.date_received = date_received
                    session.add(credit)

        return self.progress_loop(add_credits, batch.active_rows(), progress,
                                  message="Creating purchase credits")

    def calculate_pending(self, row, unconfirmed='ordered'):
        """
        Calculate the "pending" case and unit amounts for the given row.  This
        essentially is the difference between "ordered" and "confirmed",
        e.g. if a row has ``cases_ordered == 2`` and ``cases_received == 1``
        then it is considered to have "1 pending case".

        Note that this method *is* aware of the "split cases" problem, and will
        adjust the pending amounts if any split cases are detected.

        :param row: The row for which pending amounts should be calculated.

        :param unconfirmed: The type of quantities which are to be
           considered as "unconfirmed" for the sake of pending
           calculation.  The default for this is ``'ordered'``
           although it probably should be ``'shipped'`` instead.

        :returns: A 2-tuple of ``(cases, units)`` pending amounts.
        """
        # calculate remaining cases, units
        cases_confirmed = ((row.cases_received or 0)
                           + (row.cases_damaged or 0)
                           + (row.cases_expired or 0))
        cases_unconfirmed = getattr(row, 'cases_{}'.format(unconfirmed)) or 0
        cases_pending = cases_unconfirmed - cases_confirmed
        units_confirmed = ((row.units_received or 0)
                           + (row.units_damaged or 0)
                           + (row.units_expired or 0))
        units_unconfirmed = getattr(row, 'units_{}'.format(unconfirmed)) or 0
        units_pending = units_unconfirmed - units_confirmed

        # maybe account for split cases
        if units_pending < 0:
            # TODO: should this check involve case_quantity? or just cases_pending?
            if row.case_quantity == 1 and cases_pending == 0:
                # in this scenario, we have "confirmed" more units than were
                # "ordered" but it is not the result of a split case, so will
                # consider 0 units pending
                units_pending = 0
            else:
                split_cases = -units_pending // row.case_quantity
                if -units_pending % row.case_quantity:
                    split_cases += 1
                if split_cases > cases_pending:
                    raise ValueError("too many cases have been split?")
                cases_pending -= split_cases
                units_pending += split_cases * row.case_quantity

        return cases_pending, units_pending

    def make_purchase(self, batch, user, progress=None):
        """
        Effectively clones the given batch, creating a new Purchase in the
        Rattail system.
        """
        session = orm.object_session(batch)
        purchase = model.Purchase()

        # TODO: should be smarter and only copy certain fields here
        skip_fields = [
            'id',
            'date_received',
            'po_total',
        ]
        for prop in orm.object_mapper(batch).iterate_properties:
            if prop.key in skip_fields:
                continue
            if hasattr(purchase, prop.key):
                setattr(purchase, prop.key, getattr(batch, prop.key))
        purchase.po_total = batch.po_total_calculated

        def clone(row, i):
            item = model.PurchaseItem()
            # TODO: should be smarter and only copy certain fields here
            for prop in orm.object_mapper(row).iterate_properties:
                if hasattr(item, prop.key):
                    setattr(item, prop.key, getattr(row, prop.key))
            item.po_total = row.po_total_calculated
            purchase.items.append(item)

        with session.no_autoflush:
            self.progress_loop(clone, batch.active_rows(), progress,
                               message="Creating purchase items")

        purchase.created = make_utc()
        purchase.created_by = user
        purchase.status = self.enum.PURCHASE_STATUS_ORDERED
        session.add(purchase)
        batch.purchase = purchase
        return purchase

    def receive_purchase(self, batch, progress=None):
        """
        Update the purchase for the given batch, to indicate received status.
        """
        session = orm.object_session(batch)
        purchase = batch.purchase
        if not purchase:
            batch.purchase = purchase = model.Purchase()

            # TODO: should be smarter and only copy certain fields here
            skip_fields = [
                'uuid',
                'date_received',
            ]
            with session.no_autoflush:
                for prop in orm.object_mapper(batch).iterate_properties:
                    if prop.key in skip_fields:
                        continue
                    if hasattr(purchase, prop.key):
                        setattr(purchase, prop.key, getattr(batch, prop.key))

        purchase.invoice_number = batch.invoice_number
        purchase.invoice_date = batch.invoice_date
        purchase.invoice_total = batch.invoice_total_calculated
        purchase.date_received = batch.date_received

        # determine which fields we'll copy when creating new purchase item
        copy_fields = []
        for prop in orm.class_mapper(model.PurchaseItem).iterate_properties:
            if hasattr(model.PurchaseBatchRow, prop.key):
                copy_fields.append(prop.key)

        def update(row, i):
            item = row.item
            if not item:
                row.item = item = model.PurchaseItem()
                for field in copy_fields:
                    setattr(item, field, getattr(row, field))
                purchase.items.append(item)

            item.cases_received = row.cases_received
            item.units_received = row.units_received
            item.cases_damaged = row.cases_damaged
            item.units_damaged = row.units_damaged
            item.cases_expired = row.cases_expired
            item.units_expired = row.units_expired
            item.invoice_line_number = row.invoice_line_number
            item.invoice_case_cost = row.invoice_case_cost
            item.invoice_unit_cost = row.invoice_unit_cost
            item.invoice_total = row.invoice_total_calculated

        with session.no_autoflush:
            self.progress_loop(update, batch.active_rows(), progress,
                               message="Updating purchase line items")

        purchase.status = self.enum.PURCHASE_STATUS_RECEIVED
        return purchase

    def clone_row(self, oldrow):
        newrow = super(PurchaseBatchHandler, self).clone_row(oldrow)

        for oldcredit in oldrow.credits:
            newcredit = model.PurchaseBatchCredit()
            self.copy_credit_attributes(oldcredit, newcredit)
            newrow.credits.append(newcredit)

        return newrow

    def copy_credit_attributes(self, source_credit, target_credit):
        mapper = orm.class_mapper(model.PurchaseBatchCredit)
        for prop in mapper.iterate_properties:
            if prop.key not in ('uuid', 'row_uuid'):
                if isinstance(prop, orm.ColumnProperty):
                    setattr(target_credit, prop.key, getattr(source_credit, prop.key))
