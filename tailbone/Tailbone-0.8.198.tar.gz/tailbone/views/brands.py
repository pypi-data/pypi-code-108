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
Brand Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView


class BrandView(MasterView):
    """
    Master view for the Brand class.
    """
    model_class = model.Brand
    has_versions = True
    bulk_deletable = True
    supports_autocomplete = True

    mergeable = True
    merge_additive_fields = [
        'product_count',
    ]
    merge_fields = merge_additive_fields + [
        'uuid',
        'name',
    ]

    grid_columns = [
        'name',
        'confirmed',
    ]

    form_fields = [
        'name',
        'confirmed',
    ]

    has_rows = True
    model_row_class = model.Product

    row_labels = {
        'upc': "UPC",
    }

    row_grid_columns = [
        'upc',
        'description',
        'size',
        'department',
        'vendor',
        'regular_price',
        'current_price',
    ]

    def configure_grid(self, g):
        super(BrandView, self).configure_grid(g)

        # name
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')
        g.set_link('name')

        # confirmed
        g.set_type('confirmed', 'boolean')

    def get_row_data(self, brand):
        return self.Session.query(model.Product)\
                           .filter(model.Product.brand == brand)

    def get_parent(self, product):
        return product.brand

    def configure_row_grid(self, g):
        super(BrandView, self).configure_row_grid(g)

        app = self.get_rattail_app()
        self.handler = app.get_products_handler()
        g.set_renderer('regular_price', self.render_price)
        g.set_renderer('current_price', self.render_price)

        g.set_sort_defaults('upc')

    def render_price(self, product, field):
        if not product.not_for_sale:
            price = product[field]
            if price:
                return self.handler.render_price(price)

    def row_view_action_url(self, product, i):
        return self.request.route_url('products.view', uuid=product.uuid)

    def get_merge_data(self, brand):
        product_count = self.Session.query(model.Product)\
                                    .filter(model.Product.brand == brand)\
                                    .count()
        return {
            'uuid': brand.uuid,
            'name': brand.name,
            'product_count': product_count,
        }

    def merge_objects(self, removing, keeping):
        products = self.Session.query(model.Product)\
                               .filter(model.Product.brand == removing)\
                               .all()
        for product in products:
            product.brand = keeping

        self.Session.flush()
        self.Session.delete(removing)


def includeme(config):
    BrandView.defaults(config)
