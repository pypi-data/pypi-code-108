# -*- coding: utf-8 -*-
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
Autocomplete Handler for Products
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.autocomplete import Autocompleter
from rattail.db import model


class ProductAutocompleter(Autocompleter):
    """
    Autocompleter for Products.

    Actually this will search both the
    :attr:`~rattail.db.model.products.Brand.name` and
    :attr:`~rattail.db.model.products.Product.description` fields.

    Note that this will *not* include products marked as "deleted" -
    see :class:`ProductAllAutocompleter` if you need those too for
    some reason.
    """
    autocompleter_key = 'products'
    model_class = model.Product
    autocomplete_fieldname = 'description'

    def make_base_query(self, session):
        model = self.model
        return session.query(model.Product)\
                      .outerjoin(model.Brand)\
                      .options(orm.joinedload(model.Product.brand))

    def restrict_autocomplete_query(self, session, query, **kwargs):
        model = self.model

        # do not show "deleted" items by default
        query = query.filter(model.Product.deleted == False)

        return query

    def filter_autocomplete_query(self, session, query, term):
        model = self.model

        # filter by user-provided term
        criteria = []
        for word in term.split():
            criteria.append(sa.or_(
                model.Brand.name.ilike('%{}%'.format(word)),
                model.Product.description.ilike('%{}%'.format(word))))
        query = query.filter(sa.and_(*criteria))

        return query

    def sort_autocomplete_query(self, session, query):
        model = self.model
        return query.order_by(model.Brand.name,
                              model.Product.description)

    def autocomplete_display(self, product):
        return product.full_description


class ProductAllAutocompleter(ProductAutocompleter):
    """
    Autocompleter for Products, which shows *all* results, including
    "deleted" items etc.
    """

    def restrict_autocomplete_query(self, session, query, **kwargs):
        return query


class ProductNewOrderAutocompleter(ProductAutocompleter):
    """
    Special "new order" autocompleter for products.

    We set it apart with a different key (``'products.neworder'``) so
    that you can override it independently of other product
    autocompleters.

    But the default logic for this one is a bit special too, in that
    it will try to search for *both* UPC (or whatever your "key" is)
    *and* product brand, description etc.  The UPC (key) must match
    "exactly" whereas the description etc. uses wildcard search.

    .. attribute:: lookup_only_keys

       You can set this to an explicit list of product "keys" to
       restrict which types of lookups are performed for that.

     """
    autocompleter_key = 'products.neworder'
    model_class = model.Product
    autocomplete_fieldname = 'description'
    lookup_only_keys = []

    def get_autocomplete_data(self, session, term, **kwargs):
        """
        Collect data for all matching results.  This will run two
        queries, one for product "key" (e.g. UPC) and another to
        search brand, description etc.

        Note that this still honors :attr:`max_results` and will run
        the product "key" query first, without limit since it will
        have very few results.  Then the wildcard search query runs
        and will be limited.
        """
        # first run the product "key" query, and save matches for later
        self.key_matches = self.find_product_key_matches(session, term,
                                                         include_keys=True)

        # then run the "normal" upstream query to get data from the
        # wildcard search.  note that this will be results-limited
        data = super(ProductNewOrderAutocompleter, self).get_autocomplete_data(
            session, term, **kwargs)

        return data

    def get_autocomplete_results(self, data):
        """
        Format the data into a final results set for return to the
        caller.
        """
        # first get normal "search" results
        data = super(ProductNewOrderAutocompleter, self).get_autocomplete_results(data)

        # then inject key matches at the beginning
        for i, match in enumerate(self.key_matches):
            key, product = match
            data.insert(i, {'label': self.autocomplete_display(product),
                            'value': self.autocomplete_value(product)})

        return data

    def find_product_key_matches(self, session, term, **kwargs):
        """
        Find the products where the "key" matches the given term.

        Usually this just means finding a UPC match.
        """
        handler = self.app.get_products_handler()
        if 'only' not in kwargs and self.lookup_only_keys:
            kwargs['only'] = self.lookup_only_keys
        products = handler.find_products_by_key(session, term, **kwargs)
        return products
