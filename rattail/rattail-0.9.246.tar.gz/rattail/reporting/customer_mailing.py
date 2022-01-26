# -*- coding: utf-8; -*-
"""
"Customer Mailing" report
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.reporting import ExcelReport


class CustomerMailing(ExcelReport):
    """
    Generates a customer mailing address list.
    """
    type_key = 'customer_mailing'
    name = "Customer Mailing"

    output_fields = [
        'first_name',
        'last_name',
        'street',
        'street2',
        'city',
        'state',
        'zipcode',
        'address_invalid',
    ]

    def make_data(self, session, params, progress=None, **kwargs):
        model = self.model

        # looking for all customers with a person associated
        customers = session.query(model.Customer)\
                           .join(model.CustomerPerson)\
                           .join(model.Person)\
                           .order_by(model.Person.first_name,
                                     model.Person.last_name)
        rows = []

        def add_row(customer, i):
            person = customer.first_person()
            address = customer.address or person.address
            rows.append({
                'first_name': person.first_name,
                'last_name': person.last_name,
                'street': address.street if address else None,
                'street2': address.street2 if address else None,
                'city': address.city if address else None,
                'state': address.state if address else None,
                'zipcode': address.zipcode if address else None,
                'address_invalid': address.invalid if address else None,
            })

        self.progress_loop(add_row, customers, progress,
                           message="Fetching data for report")
        return rows
