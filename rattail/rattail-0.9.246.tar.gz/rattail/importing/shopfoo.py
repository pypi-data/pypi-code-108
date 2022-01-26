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
Rattail -> Rattail "local" data import, for sake of Shopfoo pattern data
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model
from rattail.core import get_uuid


class ShopfooProductImporterMixin(object):
    """
    Product -> ShopfooProduct
    """
    host_model_class = model.Product
    key = 'uuid'

    def setup(self):
        super(ShopfooProductImporterMixin, self).setup()
        self.cache_shopfoo_products()

    def cache_shopfoo_products(self):
        self.shopfoo_products = self.cache_model(self.model_class,
                                                 key='product_uuid')

    def query(self):
        return self.host_session.query(model.Product)\
                                .options(orm.joinedload(model.Product.brand))\
                                .options(orm.joinedload(model.Product.regular_price))

    def identify_shopfoo_product(self, product):
        if hasattr(self, 'shopfoo_products'):
            return self.shopfoo_products.get(product.uuid)

        try:
            return self.session.query(self.model_class)\
                               .filter(self.model_class.product == product)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def identify_shopfoo_product_uuid(self, product):

        # if we can identify the existing shopfoo product, use its uuid
        shopfoo_product = self.identify_shopfoo_product(product)
        if shopfoo_product:
            return shopfoo_product.uuid

        # otherwise we must make a new one, which means a new record
        return get_uuid()

    def normalize_host_object(self, product):

        # first get the primary data values
        data = self.normalize_base_product_data(product)

        # mark as "unwanted" if we no longer want this product
        unwanted = self.product_is_unwanted(product, data)
        if unwanted:
            data = self.mark_unwanted(product, data)

        data['uuid'] = self.identify_shopfoo_product_uuid(product)
        return data

    def normalize_base_product_data(self, product):
        """
        This method should return a dictionary with *all* primary data field
        values set, for the given product.  Note that a return value is always
        expected from this method; we have separate logic for dealing with
        "unwanted" products, so you should *not* return ``None`` here.
        """
        return {
            'product_uuid': product.uuid,
        }

    def product_is_unwanted(self, product, data):
        """
        Must return a boolean indicating if the product is *unwanted*.  If a
        product is deemed unwanted, and it does not yet exist in Shopfoo, it
        will not be added.  However if it does already exist in Shopfoo, we
        will continue to update it.
        """
        if product.deleted:
            return True
        if product.discontinued:
            return True
        if product.not_for_sale:
            return True
        return False

    def mark_unwanted(self, product, data):
        """
        This method should mark the *data* such that it indicates the product
        is unwanted.  It should not actually try to modify the product.
        """
        data['_deleted_'] = True
        return data
