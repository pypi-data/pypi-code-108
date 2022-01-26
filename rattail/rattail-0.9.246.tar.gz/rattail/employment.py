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
Employment Handler
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.util import load_object
from rattail.app import GenericHandler


class EmploymentHandler(GenericHandler):
    """
    Base class and default implementation for employment handlers.
    """

    def begin_employment(self, person, start_date, **kwargs):
        """
        Begin employment for the given person.
        """
        session = self.get_session(person)

        # make sure we have an employee record
        employee = self.ensure_employee(person)
        session.flush()

        # employee status is now *current*
        employee.status = self.enum.EMPLOYEE_STATUS_CURRENT

        # maybe assign/update ID
        employee_id = kwargs.get('employee_id')
        if employee_id and employee.id != employee_id:
            employee.id = employee_id

        # create new history record, with start date
        history = self.make_employee_history(employee, start_date)
        session.flush()

        return employee

    def end_employment(self, employee, end_date, **kwargs):
        """
        End employment for the given employee.
        """
        session = self.get_session(employee)

        # employee status is now *former*
        employee.status = self.enum.EMPLOYEE_STATUS_FORMER

        # set end date for current history record, if present
        history = [h for h in employee.history if not h.end_date]
        if history:
            history = sorted(history, key=lambda h: h.start_date, reverse=True)
            history[0].end_date = end_date

    def ensure_employee(self, person):
        """
        Returns the employee record associated with the given person, creating
        it first if necessary.
        """
        employee = self.get_employee(person)
        if employee:
            return employee

        session = self.get_session(person)
        employee = self.make_employee(person)
        session.flush()
        return employee

    def get_employee(self, person):
        """
        Returns the employee associated with the given person, if there is one.
        """
        return person.employee

    def make_employee(self, person):
        """
        Create and return a new employee record.
        """
        employee = self.model.Employee()
        employee.person = person
        return employee

    def make_employee_history(self, employee, start_date):
        """
        Create and return a new employee history record.
        """
        history = self.model.EmployeeHistory()
        history.start_date = start_date
        employee.history.append(history)
        return history

    def why_not_begin_employment(self, person):
        """
        Inspect the given person and if they should not be made a current
        employee for any reason, return that reason as text.  If it's okay for
        the person to be made an employee, returns ``None``.
        """
        employee = self.get_employee(person)
        if employee and employee.status == self.enum.EMPLOYEE_STATUS_CURRENT:
            return "This person is already an employee"

    def why_not_end_employment(self, person):
        """
        Inspect the given person and if their current employment should not be
        ended for any reason, return that reason as text.  If it's okay for the
        person to stop being an employee, returns ``None``.
        """
        employee = self.get_employee(person)
        if not employee or employee.status != self.enum.EMPLOYEE_STATUS_CURRENT:
            return {'error': "This person is not currently an employee"}

    def get_context_employee(self, employee):
        """
        Return a dict of context data for the given employee.
        """
        status_display = None
        if employee.status is not None:
            status_display = self.enum.EMPLOYEE_STATUS.get(employee.status, "??")

        history = employee.sorted_history(reverse=True)
        if history:
            history = history[0]

        return {
            'uuid': employee.uuid,
            'id': employee.id,
            'status': employee.status,
            'status_display': status_display,
            'current': employee.status == self.enum.EMPLOYEE_STATUS_CURRENT,
            'start_date': six.text_type(history.start_date) if history else None,
            'end_date': six.text_type(history.end_date) if history and history.end_date else None,
        }


def get_employment_handler(config, **kwargs):
    """
    Create and return the configured :class:`EmploymentHandler` instance.
    """
    spec = config.get('rattail', 'employment.handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = EmploymentHandler
    return factory(config, **kwargs)
