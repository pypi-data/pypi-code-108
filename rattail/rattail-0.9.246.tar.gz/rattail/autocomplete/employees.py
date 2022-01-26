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
Autocomplete Handler for Employees
"""

from __future__ import unicode_literals, absolute_import

from rattail.autocomplete import Autocompleter
from rattail.db import model


class EmployeeAutocompleter(Autocompleter):
    """
    Autocompleter for Employees
    """
    autocompleter_key = 'employees'
    model_class = model.Person
    autocomplete_fieldname = 'display_name'

    def restrict_autocomplete_query(self, session, query, **kwargs):
        model = self.model
        query = query.join(model.Employee)\
                     .filter(model.Employee.status == self.enum.EMPLOYEE_STATUS_CURRENT)
        return query

    def autocomplete_value(self, person):
        return person.employee.uuid
