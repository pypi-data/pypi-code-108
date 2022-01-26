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
Customer Order Batch Handler

Please note this is different from the Customer Order Handler.
"""

from __future__ import unicode_literals, absolute_import, division

import re
import decimal

import six
import sqlalchemy as sa

from rattail.db import model
from rattail.batch import BatchHandler
from rattail.util import OrderedDict
from rattail.time import localtime


class CustomerOrderBatchHandler(BatchHandler):
    """
    Handler for all "customer order" batches, regardless of "mode".  The
    handler must inspect the
    :attr:`~rattail.db.model.batch.custorder.CustomerOrderBatch.mode` attribute
    of each batch it deals with, in order to determine which logic to apply.

    .. attribute:: has_custom_product_autocomplete

       If true, this flag indicates that the handler provides custom
       autocomplete logic for use when selecting a product while
       creating a new order.
    """
    batch_model_class = model.CustomerOrderBatch
    has_custom_product_autocomplete = False
    nondigits_pattern = re.compile(r'\D')

    def init_batch(self, batch, progress=None, **kwargs):
        """
        Assign the "local" store to the batch, if applicable.
        """
        session = self.app.get_session(batch)
        batch.store = self.config.get_store(session)

    def new_order_requires_customer(self):
        """
        Returns a boolean indicating whether a *new* "customer order"
        in fact requires a proper customer account, or not.  Note that
        in all cases a new order requires a *person* to associate
        with, but technically the customer is optional, unless this
        returns true.
        """
        return self.config.getbool('rattail.custorders',
                                   'new_order_requires_customer',
                                   default=False)

    def allow_contact_info_choice(self):
        """
        Returns a boolean indicating whether the user is allowed at
        all, to choose from existing contact info options for the
        customer, vs. they just have to go with whatever the handler
        auto-provides.
        """
        return self.config.getbool('rattail.custorders',
                                   'new_orders.allow_contact_info_choice',
                                   default=False)

    def allow_contact_info_creation(self):
        """
        Returns a boolean indicating whether the user is allowed to
        enter *new* contact info for the customer.  This setting
        should only be honored if :meth:`allow_contact_info_choice()`
        also returns true.
        """
        return self.config.getbool('rattail.custorders',
                                   'new_orders.allow_contact_info_create',
                                   default=False)

    def allow_unknown_product(self):
        """
        Returns a boolean indicating whether "unknown" products are
        allowed on new orders.
        """
        return self.config.getbool('rattail.custorders',
                                   'allow_unknown_product',
                                   default=False)

    def product_price_may_be_questionable(self):
        """
        Returns a boolean indicating whether "any" product's price may
        be questionable.  So this isn't saying that a price *is*
        questionable but rather that it *may* be, if the user
        indicates it.  (That checkbox is only shown for the user if
        this flag is true.)
        """
        return self.config.getbool('rattail.custorders',
                                   'product_price_may_be_questionable',
                                   default=False)

    def assign_contact(self, batch, customer=None, person=None, **kwargs):
        """
        Assign the customer and/or person "contact" for the order.
        """
        clientele = self.app.get_clientele_handler()
        customer_required = self.new_order_requires_customer()

        # nb. person is always required
        if customer and not person:
            person = clientele.get_person(customer)
        if not person:
            raise ValueError("Must specify a person")

        # customer may or may not be optional
        if person and not customer:
            customer = clientele.get_customer(person)
        if customer_required and not customer:
            raise ValueError("Must specify a customer account")

        # assign contact
        batch.customer = customer
        batch.person = person

        # cache contact name
        batch.contact_name = self.get_contact_display(batch)

        # update phone/email per new contact
        batch.phone_number = None
        batch.email_address = None
        if customer_required:
            batch.phone_number = clientele.get_first_phone_number(customer)
            batch.email_address = clientele.get_first_email_address(customer)
        else:
            batch.phone_number = person.first_phone_number()
            batch.email_address = person.first_email_address()

        # always reset "add to customer" flags
        batch.clear_param('add_phone_number')
        batch.clear_param('add_email_address')

        session = self.app.get_session(batch)
        session.flush()

    def get_contact(self, batch):
        """
        Should return the contact record (i.e. Customer or Person) for
        the batch.
        """
        customer_required = self.new_order_requires_customer()

        if customer_required:
            return batch.customer
        else:
            return batch.person

    def get_contact_id(self, batch):
        """
        Should return contact ID for the batch, i.e. customer ID.
        """
        contact = self.get_contact(batch)
        if isinstance(contact, model.Customer):
            return contact.id

    def get_contact_display(self, batch):
        """
        Should return contact display text for the batch,
        i.e. customer name.
        """
        contact = self.get_contact(batch)
        if contact:
            return six.text_type(contact)

        pending = batch.pending_customer
        if pending:
            return six.text_type(pending)

    def get_contact_phones(self, batch):
        """
        Retrieve all phone records on file for the batch contact, to
        be presented as options for user to choose from when making a
        new order.
        """
        phones = []
        contact = self.get_contact(batch)
        if contact:
            phones = contact.phones

        return [self.normalize_phone(phone)
                for phone in phones]

    def normalize_phone(self, phone):
        """
        Normalize the given phone record to simple data dict, for
        passing around via JSON etc.
        """
        return {
            'uuid': phone.uuid,
            'type': phone.type,
            'number': phone.number,
            'preference': phone.preference,
            'preferred': phone.preference == 1,
        }

    def get_contact_emails(self, batch):
        """
        Retrieve all email records on file for the batch contact, to
        be presented as options for user to choose from when making a
        new order.

        Note that the default logic will exclude invalid email addresses.
        """
        emails = []
        contact = self.get_contact(batch)
        if contact:
            emails = contact.emails

        # exclude invalid
        emails = [email for email in emails
                  if not email.invalid]

        return [self.normalize_email(email)
                for email in emails]

    def normalize_email(self, email):
        """
        Normalize the given email record to simple data dict, for
        passing around via JSON etc.
        """
        return {
            'uuid': email.uuid,
            'type': email.type,
            'address': email.address,
            'invalid': email.invalid,
            'preference': email.preference,
            'preferred': email.preference == 1,
        }

    def get_contact_notes(self, batch):
        """
        Get extra "contact notes" which should be made visible to the
        user who is entering the new order.
        """
        notes = []

        invalid = False
        contact = self.get_contact(batch)
        if contact:
            invalid = [email for email in contact.emails
                       if email.invalid]
        if invalid:
            notes.append("Customer has one or more invalid email addresses on file.")

        return notes

    def unassign_contact(self, batch, **kwargs):
        """
        Unassign the customer and/or person "contact" for the order.
        """
        batch.customer = None
        batch.person = None

        # note that if batch already has a "pending" customer on file,
        # we will "restore" it as the contact info for the batch
        pending = batch.pending_customer
        if pending:
            batch.contact_name = pending.display_name
            batch.phone_number = pending.phone_number
            batch.email_address = pending.email_address
        else:
            batch.contact_name = None
            batch.phone_number = None
            batch.email_address = None

        # always reset "add to customer" flags
        batch.clear_param('add_phone_number')
        batch.clear_param('add_email_address')

        session = self.app.get_session(batch)
        session.flush()
        session.refresh(batch)

    def validate_pending_customer_data(self, batch, user, data):
        pass

    def update_pending_customer(self, batch, user, data):
        model = self.model
        people = self.app.get_people_handler()

        # first validate all data
        self.validate_pending_customer_data(batch, user, data)

        # clear out any contact it may have
        self.unassign_contact(batch)

        # create pending customer if needed
        pending = batch.pending_customer
        if not pending:
            pending = model.PendingCustomer()
            pending.user = user
            pending.status_code = self.enum.PENDING_CUSTOMER_STATUS_PENDING
            batch.pending_customer = pending

        # update pending customer info
        if 'first_name' in data:
            pending.first_name = data['first_name']
        if 'last_name' in data:
            pending.last_name = data['last_name']
        if 'display_name' in data:
            pending.display_name = data['display_name']
        else:
            pending.display_name = people.normalize_full_name(pending.first_name,
                                                              pending.last_name)
        if 'phone_number' in data:
            pending.phone_number = self.app.format_phone_number(data['phone_number'])
        if 'email_address' in data:
            pending.email_address = data['email_address']

        # also update the batch w/ contact info
        batch.contact_name = pending.display_name
        batch.phone_number = pending.phone_number
        batch.email_address = pending.email_address

    def get_case_size_for_product(self, product):
        if product.case_size:
            return product.case_size

        cost = product.cost
        if cost:
            return cost.case_size

    def get_case_price_for_row(self, row):
        """
        Calculate and return the per-case price for the given row.

        NB. we do not store case price, only unit price.  maybe that
        should change some day..
        """
        if row.unit_price is not None:
            case_price = row.unit_price * (row.case_quantity or 1)
            return case_price.quantize(decimal.Decimal('0.01'))

    # TODO: this method should maybe not exist?  and caller just
    # invokes the handler directly instead?
    def customer_autocomplete(self, session, term, **kwargs):
        """
        Override the Customer autocomplete, to search by phone number
        as well as name.
        """
        autocompleter = self.app.get_autocompleter('customers.neworder')
        return autocompleter.autocomplete(session, term, **kwargs)

    # TODO: this method should maybe not exist?  and caller just
    # invokes the handler directly instead?
    def person_autocomplete(self, session, term, **kwargs):
        """
        Override the Person autocomplete, to search by phone number as
        well as name.
        """
        autocompleter = self.app.get_autocompleter('people.neworder')
        return autocompleter.autocomplete(session, term, **kwargs)

    def get_customer_info(self, batch, **kwargs):
        """
        Return a data dict containing misc. info pertaining to the
        customer/person for the order batch.
        """
        info = {
            'customer_uuid': None,
            'person_uuid': None,
            'phone_number': None,
            'email_address': None,
        }

        if batch.customer:
            info['customer_uuid'] = batch.customer.uuid
            phone = batch.customer.first_phone()
            if phone:
                info['phone_number'] = phone.number
            email = batch.customer.first_email()
            if email:
                info['email_address'] = email.address

        if batch.person:
            info['person_uuid'] = batch.person.uuid
            if not info['phone_number']:
                phone = batch.person.first_phone()
                if phone:
                    info['phone_number'] = phone.number
                email = batch.person.first_email()
                if email:
                    info['email_address'] = email.address

        return info

    def custom_product_autocomplete(self, session, term, **kwargs):
        """
        For the given term, this should return a (possibly empty) list
        of products which "match" the term.  Each element in the list
        should be a dict with "label" and "value" keys.
        """
        raise NotImplementedError("Please define the "
                                  "{}.custom_product_autocomplete() "
                                  "method.".format(__class__.__name__))

    def get_past_orders(self, batch, **kwargs):
        """
        Retrieve a list of past orders for the batch contact.
        """
        session = self.app.get_session(batch)
        model = self.model
        orders = session.query(model.CustomerOrder)

        contact = self.get_contact(batch)
        if isinstance(contact, model.Customer):
            orders = orders.filter(model.CustomerOrder.customer == contact)
        else:
            orders = orders.filter(model.CustomerOrder.person == contact)

        orders = orders.order_by(model.CustomerOrder.created.desc())
        return orders.all()

    def get_past_products(self, batch, **kwargs):
        """
        Should return a (possibly empty) list of products which have
        been ordered in the past by the customer who is associated
        with the given batch.
        """
        session = self.app.get_session(batch)
        model = self.model
        products = OrderedDict()

        # track down all order items for batch contact
        orders = self.get_past_orders(batch)
        for order in orders:
            for item in order.items:
                product = item.product
                if product:
                    # we only want the first match for each product
                    products.setdefault(product.uuid, product)

        return list(products.values())

    def get_product_info(self, batch, product, **kwargs):
        """
        Return a data dict containing misc. info pertaining to the
        given product, for the order batch.
        """
        products = self.app.get_products_handler()
        vendor = product.cost.vendor if product.cost else None
        info = {
            'uuid': product.uuid,
            'upc': six.text_type(product.upc),
            'item_id': product.item_id,
            'scancode': product.scancode,
            'upc_pretty': product.upc.pretty(),
            'brand_name': product.brand.name if product.brand else None,
            'description': product.description,
            'size': product.size,
            'full_description': product.full_description,
            'case_quantity': self.app.render_quantity(self.get_case_size_for_product(product)),
            'unit_price': float(product.regular_price.price) if product.regular_price and product.regular_price.price is not None else None,
            'unit_price_display': products.render_price(product.regular_price),
            'department_name': product.department.name if product.department else None,
            'vendor_name': vendor.name if vendor else None,
            'url': products.get_url(product),
            'image_url': products.get_image_url(product),
            'uom_choices': self.uom_choices_for_product(product),
        }

        # TODO: this was somewhat copied from
        # tailbone.views.products.render_price() - should make it part
        # of the products handler instead?
        sale_price = None
        if not product.not_for_sale:
            sale_price = product.current_price
            if sale_price:
                if sale_price.price:
                    info['sale_price'] = float(sale_price.price)
                info['sale_price_display'] = products.render_price(sale_price)
                sale_ends = sale_price.ends
                if sale_ends:
                    sale_ends = localtime(self.config, sale_ends, from_utc=True).date()
                    info['sale_ends'] = six.text_type(sale_ends)
                    info['sale_ends_display'] = self.app.render_date(sale_ends)

        case_price = None
        if product.regular_price and product.regular_price is not None:
            case_size = self.get_case_size_for_product(product)
            # use sale price if there is one, else normal unit price
            unit_price = product.regular_price.price
            if sale_price:
                unit_price = sale_price.price
            case_price = (case_size or 1) * unit_price
            case_price = case_price.quantize(decimal.Decimal('0.01'))
        info['case_price'] = six.text_type(case_price) if case_price is not None else None
        info['case_price_display'] = self.app.render_currency(case_price)

        key = self.config.product_key()
        if key == 'upc':
            info['key'] = info['upc_pretty']
        else:
            info['key'] = getattr(product, key, info['upc_pretty'])

        return info

    def uom_choices_for_row(self, row):
        """
        Return a list of UOM choices for the given batch row.
        """
        if row.product:
            return self.uom_choices_for_product(row.product)

        choices = []

        # Each
        unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_EACH]
        choices.append({'key': self.enum.UNIT_OF_MEASURE_EACH,
                        'value': unit_name})

        # Case
        case_text = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE]
        if case_text:
            choices.append({'key': self.enum.UNIT_OF_MEASURE_CASE,
                            'value': case_text})

        return choices

    def uom_choices_for_product(self, product):
        """
        Return a list of UOM choices for the given product.
        """
        choices = []

        # Each
        if not product or not product.weighed:
            unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_EACH]
            choices.append({'key': self.enum.UNIT_OF_MEASURE_EACH,
                            'value': unit_name})

        # Pound
        if not product or product.weighed:
            unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_POUND]
            choices.append({
                'key': self.enum.UNIT_OF_MEASURE_POUND,
                'value': unit_name,
            })

        # Case
        case_text = None
        case_size = self.get_case_size_for_product(product)
        if case_size is None:
            case_text = "{} (&times; ?? {})".format(
                self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                unit_name)
        elif case_size > 1:
            case_text = "{} (&times; {} {})".format(
                self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                self.app.render_quantity(case_size),
                unit_name)
        if case_text:
            choices.append({'key': self.enum.UNIT_OF_MEASURE_CASE,
                            'value': case_text})

        return choices

    def why_not_add_product(self, product, batch):
        """
        This method can inspect the given product, and batch, to
        determine if the product may be added to the batch as a new
        row.  Useful to e.g. prevent one customer from ordering too
        many things, etc.

        :returns: If there is a reason not to add the product, should
           return that reason as a string; otherwise ``None``.
        """

    def add_product(self, batch, product, order_quantity, order_uom,
                    **kwargs):
        """
        Add a new row to the batch, for the given product and order
        quantity.
        """
        row = self.make_row()
        row.item_entry = product.uuid
        row.product = product
        row.order_quantity = order_quantity
        row.order_uom = order_uom
        if 'price_needs_confirmation' in kwargs:
            row.price_needs_confirmation = kwargs['price_needs_confirmation']
        self.add_row(batch, row)
        return row

    def add_pending_product(self, batch, pending_info,
                            order_quantity, order_uom,
                            **kwargs):
        """
        Add a new row to the batch, for the given "pending" product
        and order quantity.

        :param batch: Reference to the current order batch.

        :param pending_info: Dict of information about a new pending product.

        :param order_quantity: Quantity of the item to be added to the order.

        :param order_uom: Unit of measure for the order quantity.
        """
        session = self.app.get_session(batch)

        # make a new pending product
        pending_product = self.make_pending_product(**pending_info)
        session.add(pending_product)
        session.flush()

        # TODO: seems like make_pending_product() should do this?
        if pending_product.department and not pending_product.department_name:
            pending_product.department_name = pending_product.department.name

        # make a new row, w/ pending product
        row = self.make_row()
        row.pending_product = pending_product
        row.order_quantity = order_quantity
        row.order_uom = order_uom
        self.add_row(batch, row)
        return row

    def make_pending_product(self, **kwargs):
        products_handler = self.app.get_products_handler()
        if 'status_code' not in kwargs:
            kwargs['status_code'] = self.enum.PENDING_PRODUCT_STATUS_PENDING
        return products_handler.make_pending_product(**kwargs)

    def update_pending_product(self, row, data):
        """
        Update the pending product data for the given batch row.
        """
        # create pending product if needed
        pending = row.pending_product
        if not pending:
            pending = self.make_pending_product(**data)

        simple_fields = [
            'scancode',
            'item_id',
            'item_type',
            'department_name',
            'department_uuid',
            'brand_name',
            'brand_uuid',
            'description',
            'size',
            'vendor_name',
            'vendor_uuid',
            'vendor_item_code',
            'special_order',
            'notes',
        ]

        decimal_fields = [
            'unit_cost',
            'case_size',
            'case_cost',
            'regular_price_amount',
        ]

        # update pending product info
        if 'upc' in data:
            pending.upc = self.app.make_gpc(data['upc']) if data['upc'] else None
        for field in simple_fields:
            if field in data:
                setattr(pending, field, data[field])
        for field in decimal_fields:
            if field in data:
                value = data[field]
                value = decimal.Decimal(value) if value is not None else None
                setattr(pending, field, value)

        # refresh the row per new pending product info
        self.refresh_row(row)

    def refresh_row(self, row):
        if not row.product:
            if row.item_entry:
                session = self.app.get_session(row)
                product = self.locate_product_for_entry(session, row.item_entry)
                if product:
                    row.product = product
            if not row.product and not row.pending_product:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        product = row.product
        if product:

            row.product_upc = product.upc
            row.product_item_id = product.item_id
            row.product_scancode = product.scancode
            row.product_brand = six.text_type(product.brand or "")
            row.product_description = product.description
            row.product_size = product.size
            row.product_weighed = product.weighed
            row.case_quantity = self.get_case_size_for_product(product)

            department = product.department
            row.department_number = department.number if department else None
            row.department_name = department.name if department else None

            cost = product.cost
            row.product_unit_cost = cost.unit_cost if cost else None

            regprice = product.regular_price
            row.unit_regular_price = regprice.price if regprice else None

            curprice = product.current_price
            row.unit_sale_price = curprice.price if curprice else None
            row.sale_ends = curprice.ends if curprice else None

            row.unit_price = row.unit_sale_price or row.unit_regular_price

        else:
            self.refresh_row_from_pending_product(row)

        # we need to know if total price is updated
        old_total = row.total_price

        # maybe update total price
        if row.unit_price is None:
            row.total_price = None
        elif not row.unit_price:
            row.total_price = 0
        else:
            row.total_price = row.unit_price * row.order_quantity
            if row.order_uom == self.enum.UNIT_OF_MEASURE_CASE:
                row.total_price *= (row.case_quantity or 1)

        # update total price for batch too, if it changed
        if row.total_price != old_total:
            batch = row.batch
            batch.total_price = ((batch.total_price or 0)
                                 + (row.total_price or 0)
                                 - (old_total or 0))

        if not row.product and row.pending_product:
            row.status_code = row.STATUS_PENDING_PRODUCT
        else:
            row.status_code = row.STATUS_OK

    def refresh_row_from_pending_product(self, row):
        """
        Refresh basic row attributes from its pending product.
        """
        pending = row.pending_product
        if not pending:
            return

        row.product_upc = pending.upc
        row.product_item_id = pending.item_id
        row.product_scancode = pending.scancode
        row.product_brand = six.text_type(pending.brand or pending.brand_name or '')
        row.product_description = pending.description
        row.product_size = pending.size
        # TODO: is this even important?  pending does not have it
        # row.product_weighed = pending.weighed
        row.case_quantity = pending.case_size

        if pending.department:
            row.department = pending.department
            row.department_number = pending.department.number
            row.department_name = pending.department.name
        elif pending.department_name:
            row.department = None
            row.department_number = None
            row.department_name = pending.department_name
        else:
            row.department = None
            row.department_number = None
            row.department_name = None

        row.product_unit_cost = pending.unit_cost
        row.unit_regular_price = pending.regular_price_amount
        row.unit_price = row.unit_regular_price
        row.unit_sale_price = None
        row.sale_ends = None

    def remove_row(self, row):
        batch = row.batch

        if not row.removed:
            row.removed = True

            if row.total_price:
                batch.total_price = (batch.total_price or 0) - row.total_price

        self.refresh_batch_status(batch)

    def delete_extra_data(self, batch, progress=None, **kwargs):

        # do the normal stuff (e.g. delete input files)
        super(CustomerOrderBatchHandler, self).delete_extra_data(
            batch, progress=progress, **kwargs)

        session = self.app.get_session(batch)

        # delete pending customer if present
        pending = batch.pending_customer
        if pending:
            batch.pending_customer = None
            session.delete(pending)

        # delete any pending products if present
        for row in batch.data_rows:
            pending = row.pending_product
            if pending:
                row.pending_product = None
                session.delete(pending)

    def execute(self, batch, user=None, progress=None, **kwargs):
        """
        Default behavior here will create and return a new rattail
        Customer Order.  It also may "add contact info" e.g. to the
        customer record.  Override as needed.
        """
        rows = batch.active_rows()
        order = self.make_new_order(batch, user=user, progress=progress, **kwargs)
        self.update_contact_info(batch, user)
        self.mark_pending_things_ready(batch, rows)
        return order

    def mark_pending_things_ready(self, batch, rows):
        if batch.pending_customer:
            batch.pending_customer.status = self.enum.PENDING_CUSTOMER_STATUS_READY
        for row in rows:
            if row.pending_product:
                row.pending_product.status = self.enum.PENDING_PRODUCT_STATUS_READY

    def update_contact_info(self, batch, user, **kwargs):
        """
        Update contact info from the batch, onto the customer record.
        """
        if batch.get_param('add_phone_number'):
            self.add_phone_number(batch, user)
        if batch.get_param('add_email_address'):
            self.add_email_address(batch, user)

    def add_phone_number(self, batch, user, **kwargs):
        """
        Add phone number from the batch to the customer record.

        Note that the default behavior does *not* do that, but instead
        will send an email alert to configured recipient(s) with the
        update request.
        """
        self.app.send_email('new_phone_requested', {
            'user': user,
            'user_display': user.display_name if user else "(unknown user)",
            'contact': self.get_contact(batch),
            'contact_id': self.get_contact_id(batch),
            'phone_number': batch.phone_number,
        })

    def add_email_address(self, batch, user, **kwargs):
        """
        Add email address from the batch to the customer record.

        Note that the default behavior does *not* do that, but instead
        will send an email alert to configured recipient(s) with the
        update request.
        """
        self.app.send_email('new_email_requested', {
            'user': user,
            'user_display': user.display_name if user else "(unknown user)",
            'contact': self.get_contact(batch),
            'contact_id': self.get_contact_id(batch),
            'email_address': batch.email_address,
        })

    def make_new_order(self, batch, user=None, progress=None, **kwargs):
        """
        Create and return a new rattail Customer Order based on the
        batch contents.
        """
        batch_fields = [
            'store',
            'id',
            'customer',
            'person',
            'pending_customer',
            'phone_number',
            'email_address',
            'total_price',
        ]

        order = model.CustomerOrder()
        order.created_by = user
        order.status_code = self.enum.CUSTORDER_STATUS_ORDERED
        for field in batch_fields:
            setattr(order, field, getattr(batch, field))

        session = self.app.get_session(batch)
        session.add(order)
        session.flush()

        row_fields = [
            'product',
            'pending_product_uuid',
            'product_upc',
            'product_brand',
            'product_description',
            'product_size',
            'product_weighed',
            'department_number',
            'department_name',
            'case_quantity',
            'order_quantity',
            'order_uom',
            'product_unit_cost',
            'unit_price',
            'discount_percent',
            'total_price',
            'price_needs_confirmation',
            'paid_amount',
            'payment_transaction_number',
        ]

        def convert(row, i):

            # add new order item
            item = model.CustomerOrderItem()
            item.sequence = i
            for field in row_fields:
                setattr(item, field, getattr(row, field))
            order.items.append(item)

            # set initial status and attach events
            self.set_initial_item_status(item, user)

        self.progress_loop(convert, batch.active_rows(), progress,
                           message="Converting batch rows to order items")

        session.flush()
        return order

    def set_initial_item_status(self, item, user, **kwargs):
        """
        Set the initial status for the given order item, and attach
        any events.

        The first logical status is ``CUSTORDER_ITEM_STATUS_INITIATED``
        and an item may stay there if there is some other step(s)
        which must occur before the item is ready to proceed.  For
        instance the default logic will leave it there if the price
        needs to be confirmed, but you can override as needed, for
        instance if you require payment up-front.

        The second status is ``CUSTORDER_ITEM_STATUS_READY`` which
        indicates the item is ready to proceed.  The default logic
        will auto-advance the item to this status if the price does
        *not* need to be confirmed.  Again you may need to override
        e.g. to prevent this until up-front payment is received.
        """
        # set "initiated" status
        item.status_code = self.enum.CUSTORDER_ITEM_STATUS_INITIATED
        item.add_event(self.enum.CUSTORDER_ITEM_EVENT_INITIATED, user)

        # but if the price is good...
        if not item.price_needs_confirmation:

            # then we set "ready" status
            item.status_code = self.enum.CUSTORDER_ITEM_STATUS_READY
            item.status_text = "everything looks normal"

            item.add_event(self.enum.CUSTORDER_ITEM_EVENT_READY, user,
                           note=item.status_text)
