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
Tailbone Web API - Product Views
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model

from tailbone.api import APIMasterView2 as APIMasterView


class ProductView(APIMasterView):
    """
    API views for Product data
    """
    model_class = model.Product
    collection_url_prefix = '/products'
    object_url_prefix = '/product'
    supports_autocomplete = True

    def normalize(self, product):
        cost = product.cost
        return {
            'uuid': product.uuid,
            '_str': six.text_type(product),
            'upc': six.text_type(product.upc),
            'scancode': product.scancode,
            'item_id': product.item_id,
            'item_type': product.item_type,
            'description': product.description,
            'status_code': product.status_code,
            'default_unit_cost': cost.unit_cost if cost else None,
            'default_unit_cost_display': "${:0.2f}".format(cost.unit_cost) if cost and cost.unit_cost is not None else None,
        }

    def make_autocomplete_query(self, term):
        query = self.Session.query(model.Product)\
                            .outerjoin(model.Brand)\
                            .filter(sa.or_(
                                model.Brand.name.ilike('%{}%'.format(term)),
                                model.Product.description.ilike('%{}%'.format(term))))

        if not self.request.has_perm('products.view_deleted'):
            query = query.filter(model.Product.deleted == False)

        query = query.order_by(model.Brand.name,
                               model.Product.description)\
                     .options(orm.joinedload(model.Product.brand))
        return query

    def autocomplete_display(self, product):
        return product.full_description


def includeme(config):
    ProductView.defaults(config)
