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
Autocomplete Handler for People
"""

from __future__ import unicode_literals, absolute_import

from rattail.autocomplete import Autocompleter
from rattail.autocomplete.base import PhoneMagicMixin
from rattail.db import model


class PersonAutocompleter(Autocompleter):
    """
    Autocompleter for People
    """
    autocompleter_key = 'people'
    model_class = model.Person
    autocomplete_fieldname = 'display_name'


class PersonEmployeeAutocompleter(Autocompleter):
    """
    Autocompleter for People, but restricted to return only results
    for people who are (or have been) an employee.
    """
    autocompleter_key = 'people.employees'
    model_class = model.Person
    autocomplete_fieldname = 'display_name'

    def restrict_autocomplete_query(self, session, query, **kwargs):
        model = self.model
        query = query.join(model.Employee)
        return query


class PersonNewOrderAutocompleter(PhoneMagicMixin, Autocompleter):
    """
    Special "new order" autocompleter for people.

    We set it apart with a different key (``'people.neworder'``) so
    that you can override it independently of other person
    autocompleters.

    But the default logic for this one is a bit special too, in that
    it will try to search for *either* phone number *or* person name.
    If the search term includes at least 4 digits then it is
    considered to be a phone number search; otherwise it will be
    considered a name search.
    """
    autocompleter_key = 'people.neworder'
    model_class = model.Person
    autocomplete_fieldname = 'display_name'
    phone_model_class = model.PersonPhoneNumber
