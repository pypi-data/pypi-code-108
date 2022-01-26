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
Base data model for "shopfoo" pattern
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db import model
from rattail.db.core import filename_column


class ShopfooProductBase(object):
    """
    Product cache table, specific to the target system.  Each record in this
    table *should* match exactly, what is in the actual target system.
    """
    @declared_attr
    def __table_args__(cls):
        return cls.__product_table_args__()

    @classmethod
    def __product_table_args__(cls):
        table_name = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='{}_fk_product'.format(table_name)),
        )

    uuid = model.uuid_column()

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(cls):
        backref_name = cls.__tablename__
        return orm.relationship(
            model.Product,
            doc="""
            Reference to the actual product record, with which this cache
            record is associated.
            """,
            backref=orm.backref(
                backref_name,
                uselist=False,
                doc="""
                Reference to the local/cached {} record for this product.
                """.format(backref_name)))


@six.python_2_unicode_compatible
class ShopfooProductExportBase(model.ExportMixin):
    """
    Product export table, specific to the target system.  Each record in this
    table will correspond to a single export of product data to the target
    system.
    """
    filename = filename_column(nullable=True, doc="""
    Base filename for the export.  This name should be the same as is used for
    the final upload, if applicable.
    """)

    uploaded = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag to indicate whether the export has been successfully uploaded to the
    target system's server.
    """)

    def set_filename(self, config):
        """
        Set the export's official filename, per config.
        """
        table_name = self.__tablename__
        self.filename = "{}.{}.csv".format(table_name, self.id_str)

    def __str__(self):
        return self.id_str
