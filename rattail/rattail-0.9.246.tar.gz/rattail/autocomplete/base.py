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
Autocomplete handlers - base class
"""

from __future__ import unicode_literals, absolute_import

import re

import sqlalchemy as sa
from sqlalchemy import orm


class Autocompleter(object):
    """
    Base class and partial default implementation for autocomplete
    handlers.  It is expected that all autocomplete handlers will
    ultimately inherit from this base class, therefore it defines the
    implementation "interface" loosely speaking.  Custom autocomplete
    handlers are welcome to supplement or override this as needed, and
    in fact must do so for certain aspects.

    .. attribute:: autocompleter_key

       The key indicates what "type" of autocompleter this is.  It
       should be a string, e.g. ``'products'``.  It will generally
       correspond to the route names used in Tailbone, though not
       always.  

    .. attribute:: max_results

       If set, should return no more than this many results.  The base
       default *is* set, to 100.  Set to ``None`` to disable limiting
       the number of results.

       The reason to limit results is to avoid situations where the
       query returns many thousands of records, so that's slow anyway,
       but then the browser may well freeze up trying to process it.

       Note that your query probably should be *sorted* somehow, so
       that the e.g. "first 100" results are more relevant.

       Any subclass is free to override this, but you an also set it
       directly on an instance, e.g.::

          autocompleter = app.get_autocompleter('products')
          autocompleter.max_results = 250
          results = autocompleter.autocomplete(session, "apple cider vinegar")
    """
    autocompleter_key = None
    max_results = 100

    def __init__(self, config):
        if not self.autocompleter_key:
            raise NotImplementedError("You must define `autocompleter_key` "
                                      "attribute for handler class: {}".format(
                                          self.__class__))
        self.config = config
        self.app = self.config.get_app()
        self.enum = config.get_enum()
        self.model = config.get_model()

    def get_model_class(self):
        return self.model_class

    @property
    def autocomplete_fieldname(self):
        raise NotImplementedError("You must define `autocomplete_fieldname` "
                                  "attribute for handler class: {}".format(
                                      self.__class__))

    def autocomplete(self, session, term, **kwargs):
        """
        The main reason this class exists.  This method accepts a
        ``term`` (string) argument and will return a sequence of
        matching results.
        """
        term = self.prepare_autocomplete_term(term)
        if not term:
            return []

        data = self.get_autocomplete_data(session, term)
        return self.get_autocomplete_results(data)

    def prepare_autocomplete_term(self, term, **kwargs):
        """
        If necessary, massage the incoming search term for use with
        the autocomplete query.
        """
        return term

    def get_autocomplete_data(self, session, term, **kwargs):
        """
        Collect data for matching results, based on the given search
        term.  This method basically does 2 things:

        First it calls :meth:`make_autocomplete_query()` to get the
        final query, then it invokes the query.

        When invoking the query it will "usually" limit the number of
        results, based on :attr:`max_results`.
        """
        query = self.make_autocomplete_query(session, term)

        # maybe limit number of results for efficiency's sake
        if self.max_results:
            return query[:self.max_results]

        # otherwise just return all of them
        return query.all()

    def make_autocomplete_query(self, session, term, **kwargs):
        """
        Build the complete query from which to obtain search results.
        """
        # we are querying one table (and column) by default
        query = self.make_base_query(session)

        # restrict according to business logic etc. if applicable
        query = self.restrict_autocomplete_query(session, query)

        # filter according to search term(s)
        query = self.filter_autocomplete_query(session, query, term)

        # sort results by something meaningful
        query = self.sort_autocomplete_query(session, query)
        return query

    def make_base_query(self, session):
        """
        Create and return the base ("unfiltered") query from which
        search results will ultimately be obtained.
        """
        model_class = self.get_model_class()
        query = session.query(model_class)
        return query

    def restrict_autocomplete_query(self, session, query, **kwargs):
        """
        Optionally restrict ("pre-filter") the query according to any
        applicable business logic.
        """
        return query

    def filter_autocomplete_query(self, session, query, term):
        """
        Apply the actual "search" filtering and return the query.
        """
        model_class = self.get_model_class()
        column = getattr(model_class, self.autocomplete_fieldname)
        criteria = [column.ilike('%{}%'.format(word))
                    for word in term.split()]
        query = query.filter(sa.and_(*criteria))
        return query

    def sort_autocomplete_query(self, session, query):
        model_class = self.get_model_class()
        column = getattr(model_class, self.autocomplete_fieldname)
        query = query.order_by(column)
        return query

    def get_autocomplete_results(self, data):
        """
        Format the data into a final results set for return to the
        caller.
        """
        return [{'label': self.autocomplete_display(rec),
                 'value': self.autocomplete_value(rec)}
                for rec in data]

    def autocomplete_display(self, obj):
        return getattr(obj, self.autocomplete_fieldname)

    def autocomplete_value(self, obj):
        return obj.uuid


class PhoneMagicMixin(object):
    """
    Mixin for adding "phone number magic" to an otherwise sort of
    normal autocompleter.

    The "magic" is that this will try to search for *either* phone
    number *or* contact name.  If the search term includes at least 4
    digits then it is considered to be a phone number search;
    otherwise it will be considered a name search.
    """
    nondigits_pattern = re.compile(r'\D')

    def make_autocomplete_query(self, session, term, **kwargs):
        """
        This is where the magic happens.  We override this to check if
        the search term resembles a phone number and if so, do a phone
        number search; otherwise a name search.
        """
        column = getattr(self.model_class, self.autocomplete_fieldname)

        # define the base query
        query = session.query(self.model_class)\
                       .options(orm.joinedload(self.model_class.phones))

        # does search term look like a phone number?
        phone_term = self.get_phone_search_term(term)
        if phone_term:

            # yep, so just search for the phone number
            query = query.join(self.phone_model_class,
                               self.phone_model_class.parent_uuid == self.model_class.uuid)
            query = query.filter(sa.func.regexp_replace(self.phone_model_class.number,
                                                        r'\D', '', 'g')\
                                 .like('%{}%'.format(phone_term)))

        else: # term does not look like a phone number

            # so just search by name
            criteria = [column.ilike('%{}%'.format(word))
                        for word in term.split()]
            query = query.filter(sa.and_(*criteria))

        # oh, and sort by something useful
        query = query.order_by(column)

        return query

    def get_phone_search_term(self, term):
        """
        Try to figure out if the given search term represents a whole
        or partial phone number, and if so return just the digits.
        """
        digits = self.nondigits_pattern.sub('', term)
        if digits and len(digits) >= 4:
            return digits

    def get_autocomplete_results(self, data):
        """
        We override the formatting of results, because we want the
        autocomplete results themselves, to appear as "<name> <phone>"
        in the dropdown user sees, but we also want to include the
        ``display`` key which contains just the name.

        The reason for this has to do with how the
        ``tailbone-autocomplete`` comonent works.  The ``display``
        (name only)` will be shown on the button after selection is
        made.
        """
        results = []
        for contact in data:
            phone = contact.first_phone()
            name = getattr(contact, self.autocomplete_fieldname)
            if phone:
                label = "{} {}".format(name, phone.number)
            else:
                label = name
            results.append({'value': contact.uuid,
                            'label': label,
                            'display': name})
        return results
