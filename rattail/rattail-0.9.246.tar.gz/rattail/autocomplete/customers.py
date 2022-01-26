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
Autocomplete Handler for Customers
"""

from __future__ import unicode_literals, absolute_import

import re

import sqlalchemy as sa
from sqlalchemy import orm

from rattail.autocomplete import Autocompleter
from rattail.autocomplete.base import PhoneMagicMixin
from rattail.db import model


class CustomerAutocompleter(Autocompleter):
    """
    Autocompleter for Customers (by name)
    """
    autocompleter_key = 'customers'
    model_class = model.Customer
    autocomplete_fieldname = 'name'


class CustomerPhoneAutocompleter(Autocompleter):
    """
    Autocompleter for Customers (by phone)

    .. note::
       As currently implemented, this view will only work with a
       PostgreSQL database.  It normalizes the user's search term and
       the database values to numeric digits only (i.e. removes
       special characters from each) in order to be able to perform
       smarter matching.  However normalizing the database value
       currently uses the PG SQL ``regexp_replace()`` function.
    """
    autocompleter_key = 'customers.phone'
    invalid_pattern = re.compile(r'\D')

    def prepare_autocomplete_term(self, term, **kwargs):
        return self.invalid_pattern.sub('', term)

    def make_autocomplete_query(self, session, term, **kwargs):
        model = self.model
        return session.query(model.CustomerPhoneNumber)\
                      .filter(sa.func.regexp_replace(model.CustomerPhoneNumber.number, r'\D', '', 'g').like('%{}%'.format(term)))\
                      .order_by(model.CustomerPhoneNumber.number)\
                      .options(orm.joinedload(model.CustomerPhoneNumber.customer))

    def autocomplete_display(self, phone):
        return "{} {}".format(phone.number, phone.customer)

    def autocomplete_value(self, phone):
        return phone.customer.uuid


class CustomerNewOrderAutocompleter(PhoneMagicMixin, Autocompleter):
    """
    Special "new order" autocompleter for customers.

    We set it apart with a different key (``'customers.neworder'``) so
    that you can override it independently of other customer
    autocompleters.

    But the default logic for this one is a bit special too, in that
    it will try to search for *either* phone number *or* customer
    name.  If the search term includes at least 4 digits then it is
    considered to be a phone number search; otherwise it will be
    considered a name search.
    """
    autocompleter_key = 'customers.neworder'
    model_class = model.Customer
    autocomplete_fieldname = 'name'
    phone_model_class = model.CustomerPhoneNumber
