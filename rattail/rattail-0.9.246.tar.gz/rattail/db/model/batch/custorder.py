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
Models for customer order batches
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import (Base, BatchMixin, BatchRowMixin,
                              CustomerOrderBase, CustomerOrderItemBase,
                              CustomerOrder, CustomerOrderItem)


class CustomerOrderBatch(BatchMixin, CustomerOrderBase, Base):
    """
    Hopefully generic batch used for entering new customer orders into the
    system, as well as fulfilling them along the way, etc.
    """
    batch_key = 'custorder'
    __tablename__ = 'batch_custorder'
    __batchrow_class__ = 'CustomerOrderBatchRow'
    model_title_plural = "Customer Order Batches"

    @declared_attr
    def __table_args__(cls):
        return cls.__batch_table_args__() + cls.__customer_order_table_args__() + (
            sa.ForeignKeyConstraint(['order_uuid'], ['custorder.uuid'],
                                    name='batch_custorder_fk_order'),
        )

    STATUS_OK                           = 1

    STATUS = {
        STATUS_OK                       : "ok",
    }

    order_uuid = sa.Column(sa.String(length=32), nullable=True)
    order = orm.relationship(
        CustomerOrder,
        doc="""
        Reference to the customer order with which the batch is associated.
        May be null, e.g. in the case of a "new order" batch.
        """,
        backref=orm.backref(
            'batches',
            order_by='CustomerOrderBatch.id',
            doc="""
            List of batches associated with the customer order.
            """))

    mode = sa.Column(sa.Integer(), nullable=False, doc="""
    Numeric "mode" for the customer order batch, to indicate new/fulfilling etc.
    """)


class CustomerOrderBatchRow(BatchRowMixin, CustomerOrderItemBase, Base):
    """
    Row of data within a customer order batch.
    """
    __tablename__ = 'batch_custorder_row'
    __batch_class__ = CustomerOrderBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__batchrow_table_args__() + cls.__customer_order_item_table_args__() + (
            sa.ForeignKeyConstraint(['item_uuid'], ['custorder_item.uuid'],
                                    name='batch_custorder_row_fk_item'),
        )

    STATUS_OK                           = 1
    STATUS_PRODUCT_NOT_FOUND            = 2
    # STATUS_PRICE_NEEDS_CONFIRMATION     = 3
    STATUS_PENDING_PRODUCT              = 4

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_PRODUCT_NOT_FOUND        : "product not found",
        # STATUS_PRICE_NEEDS_CONFIRMATION : "price needs to be confirmed",
        STATUS_PENDING_PRODUCT          : "has pending product",
    }

    item_entry = sa.Column(sa.String(length=32), nullable=True, doc="""
    Raw entry value, as obtained from the initial data source, and which is
    used to locate the product within the system.  This raw value is preserved
    in case the initial lookup fails and a refresh must attempt further
    lookup(s) later.  Only used by certain batch handlers in practice.
    """)

    item_uuid = sa.Column(sa.String(length=32), nullable=True)
    item = orm.relationship(
        CustomerOrderItem,
        doc="""
        Reference to the customer order line item with which the batch row is
        associated.  May be null, e.g. in the case of a "new order" batch.
        """)
