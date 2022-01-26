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
Data Models for Customer Orders
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, uuid_column
from rattail.db.model import (Store, Customer, PendingCustomer, Person,
                              Product, PendingProduct, User, Note)
from rattail.db.types import GPCType


class CustomerOrderBase(object):
    """
    Base class for customer orders; defines common fields.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_table_args__()

    @classmethod
    def __customer_order_table_args__(cls):
        table_name = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'],
                                    name='{}_fk_store'.format(table_name)),
            sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'],
                                    name='{}_fk_customer'.format(table_name)),
            sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'],
                                    name='{}_fk_person'.format(table_name)),
            sa.ForeignKeyConstraint(['pending_customer_uuid'], ['pending_customer.uuid'],
                                    name='{}_fk_pending_customer'.format(table_name)),
        )

    store_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def store(cls):
        return orm.relationship(
            Store,
            doc="""
            Reference to the store to which the order applies.
            """)

    customer_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def customer(cls):
        return orm.relationship(
            Customer,
            doc="""
            Reference to the customer account for which the order exists.
            """)

    person_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def person(cls):
        return orm.relationship(
            Person,
            doc="""
            Reference to the person to whom the order applies.
            """)

    pending_customer_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def pending_customer(cls):
        tablename = cls.__tablename__
        return orm.relationship(
            PendingCustomer,
            doc="""
            Reference to the *pending* customer account for the order,
            if applicable.
            """,
            backref='{}_records'.format(tablename))

    contact_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Cached display name for the contact (customer).
    """)

    phone_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    Customer contact phone number for sake of this order.
    """)

    email_address = sa.Column(sa.String(length=255), nullable=True, doc="""
    Customer contact email address for sake of this order.
    """)

    total_price = sa.Column(sa.Numeric(precision=10, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) for all items on the order.
    """)


@six.python_2_unicode_compatible
class CustomerOrder(CustomerOrderBase, Base):
    """
    Represents an order placed by the customer.
    """
    __tablename__ = 'custorder'

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_table_args__() + (
            sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'],
                                    name='custorder_fk_created_by'),
        )

    uuid = uuid_column()

    id = sa.Column(sa.Integer(), doc="""
    Numeric, auto-increment ID for the order.
    """)

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the order/batch was first created.
    """)

    created_by_uuid = sa.Column(sa.String(length=32), nullable=True)
    created_by = orm.relationship(
        User,
        doc="""
        Reference to the user who initially created the order/batch.
        """)

    status_code = sa.Column(sa.Integer(), nullable=False)

    items = orm.relationship(
        'CustomerOrderItem',
        back_populates='order',
        collection_class=ordering_list('sequence', count_from=1),
        cascade='all, delete-orphan',
        doc="""
        Sequence of :class:`CustomerOrderItem` instances which belong to the order.
        """)

    def __str__(self):
        if self.id:
            return "#{}".format(self.id)
        return "(pending)"


@six.python_2_unicode_compatible
class CustomerOrderItemBase(object):
    """
    Base class for customer order line items.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_item_table_args__()

    @classmethod
    def __customer_order_item_table_args__(cls):
        table_name = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='{}_fk_product'.format(table_name)),
            sa.ForeignKeyConstraint(['pending_product_uuid'], ['pending_product.uuid'],
                                    name='{}_fk_pending_product'.format(table_name)),
        )

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(cls):
        return orm.relationship(
            Product,
            doc="""
            Reference to the master product record for the line item.
            """)

    pending_product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def pending_product(cls):
        tablename = cls.__tablename__
        return orm.relationship(
            PendingProduct,
            doc="""
            Reference to the *pending* product record for the order
            item, if applicable.
            """,
            backref='{}_records'.format(tablename))

    product_upc = sa.Column(GPCType(), nullable=True, doc="""
    UPC for the product associated with the row.
    """)

    product_scancode = sa.Column(sa.String(length=14), nullable=True, doc="""
    Scancode for the product, if applicable.
    """)

    product_item_id = sa.Column(sa.String(length=50), nullable=True, doc="""
    Item ID for the product, if applicable.
    """)

    product_brand = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name for the product being ordered.  This should be a cache of the
    relevant :attr:`Brand.name`.
    """)

    product_description = sa.Column(sa.String(length=60), nullable=True, doc="""
    Primary description for the product being ordered.  This should be a cache
    of :attr:`Product.description`.
    """)

    product_size = sa.Column(sa.String(length=30), nullable=True, doc="""
    Size of the product being ordered.  This should be a cache of
    :attr:`Product.size`.
    """)

    product_weighed = sa.Column(sa.String(length=4), nullable=True, doc="""
    Flag indicating whether the product is sold by weight.  This should be a
    cache of :attr:`Product.weighed`.
    """)

    # TODO: probably should get rid of this, i can't think of why it's needed.
    # for now we just make sure it is nullable, since that wasn't the case.
    product_unit_of_measure = sa.Column(sa.String(length=4), nullable=True, doc="""
    Code indicating the unit of measure for the product.  This should be a
    cache of :attr:`Product.unit_of_measure`.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    case_quantity = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Case pack count for the product being ordered.  This should be a cache of
    :attr:`Product.case_size`.
    """)

    # TODO: i now think that cases_ordered and units_ordered should go away.
    # but will wait until that idea has proven itself before removing.  am
    # pretty sure they are obviated by order_quantity and order_uom.

    cases_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of cases of product which were initially ordered.
    """)

    units_ordered = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Number of units of product which were initially ordered.
    """)

    order_quantity = sa.Column(sa.Numeric(precision=10, scale=4), nullable=True, doc="""
    Quantity being ordered by the customer.
    """)

    order_uom = sa.Column(sa.String(length=4), nullable=True, doc="""
    Code indicating the unit of measure for the order itself.  Does not
    directly reflect the :attr:`~rattail.db.model.Product.unit_of_measure`.
    """)

    product_unit_cost = sa.Column(sa.Numeric(precision=9, scale=5), nullable=True, doc="""
    Unit cost of the product being ordered.  This should be a cache of the
    relevant :attr:`rattail.db.model.ProductCost.unit_cost`.
    """)

    unit_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Unit price for the product being ordered.  This is the price which is
    quoted to the customer and/or charged to the customer, but for a unit only
    and *before* any discounts are applied.  It generally will be a cache of
    the relevant :attr:`ProductPrice.price`.
    """)

    unit_regular_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Regular price for the item unit.  Note that if a sale price is in
    effect, then this may differ from :attr:`unit_price`.
    """)

    unit_sale_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Sale price for the item unit, if applicable.
    """)

    sale_ends = sa.Column(sa.DateTime(), nullable=True, doc="""
    End date/time for the sale in effect, if any.
    """)

    discount_percent = sa.Column(sa.Numeric(precision=5, scale=3), nullable=False, default=0, doc="""
    Discount percentage which will be applied to the product's price as part of
    calculating the :attr:`total_price` for the item.
    """)

    total_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Full price (not including tax etc.) which the customer is asked to pay for the item.
    """)

    price_needs_confirmation = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating that the price for this item should be confirmed
    by someone, before the order advances to the procurement phase.

    Items/rows with this flag set will probably indicate that also via
    their status.

    When the price is eventually confirmed by someone, this flag
    should be cleared and probably the status will update as well.
    """)

    paid_amount = sa.Column(sa.Numeric(precision=8, scale=3), nullable=False, default=0, doc="""
    Amount which the customer has paid toward the :attr:`total_price` of theitem.
    """)

    payment_transaction_number = sa.Column(sa.String(length=8), nullable=True, doc="""
    Transaction number in which payment for the order was taken, if applicable.
    """)

    def __str__(self):
        return str(self.product or "(no product)")


class CustomerOrderItem(CustomerOrderItemBase, Base):
    """
    Represents a particular line item (product) within a customer order.
    """
    __tablename__ = 'custorder_item'

    @declared_attr
    def __table_args__(cls):
        return cls.__customer_order_item_table_args__() + (
            sa.ForeignKeyConstraint(['order_uuid'], ['custorder.uuid'],
                                    name='custorder_item_fk_order'),
        )

    uuid = uuid_column()

    order_uuid = sa.Column(sa.String(length=32), nullable=False)
    order = orm.relationship(CustomerOrder, back_populates='items', doc="""
    Reference to the :class:`CustomerOrder` instance to which the item belongs.
    """)

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric sequence for the item, i.e. its "line number".  These values should
    obviously increment in sequence and be unique within the context of a
    single order.
    """)

    status_code = sa.Column(sa.Integer(), nullable=False)

    status_text = sa.Column(sa.String(length=255), nullable=True, doc="""
    Text which may briefly explain the batch status code, if needed.
    """)

    def add_event(self, type_code, user, **kwargs):
        """
        Convenience method to add an event for the order item.
        """
        self.events.append(CustomerOrderItemEvent(type_code=type_code,
                                                  user=user,
                                                  **kwargs))


class CustomerOrderItemEvent(Base):
    """
    An event in the life of a customer order item
    """
    __tablename__ = 'custorder_item_event'
    __table_args__ = (
        sa.ForeignKeyConstraint(['item_uuid'], ['custorder_item.uuid'], name='custorder_item_event_fk_item'),
        sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], name='custorder_item_event_fk_user'),
    )

    uuid = uuid_column()

    item_uuid = sa.Column(sa.String(length=32), nullable=False)

    item = orm.relationship(
        CustomerOrderItem,
        doc="""
        Reference to the :class:`CustomerOrder` instance to which the item belongs.
        """,
        backref=orm.backref(
            'events',
            order_by='CustomerOrderItemEvent.occurred',
            cascade='all, delete-orphan'))

    type_code = sa.Column(sa.Integer, nullable=False)

    occurred = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
    Date and time when the event occurred.
    """)

    user_uuid = sa.Column(sa.String(length=32), nullable=False)

    user = orm.relationship(
        User,
        doc="""
        User who was the "actor" for the event.
        """)

    note = sa.Column(sa.Text(), nullable=True, doc="""
    Optional note recorded for the event.
    """)


class CustomerOrderItemNote(Note):
    """
    Represents a note attached to an order item.
    """
    __mapper_args__ = {'polymorphic_identity': 'CustomerOrderItem'}

CustomerOrderItem.notes = orm.relationship(
    CustomerOrderItemNote,
    primaryjoin=CustomerOrderItemNote.parent_uuid == CustomerOrderItem.uuid,
    foreign_keys=[CustomerOrderItemNote.parent_uuid],
    order_by=CustomerOrderItemNote.created,
    cascade='all, delete-orphan',
    doc="""
    Sequence of notes attached to the order item.
    """,
    backref=orm.backref(
        'person',
        doc="""
        Reference to the order item to which the note is attached.
        """))
