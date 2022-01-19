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
Department Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from webhelpers2.html import HTML

from tailbone import grids
from tailbone.views import MasterView


class DepartmentView(MasterView):
    """
    Master view for the Department class.
    """
    model_class = model.Department
    touchable = True
    has_versions = True
    supports_autocomplete = True

    grid_columns = [
        'number',
        'name',
        'product',
        'personnel',
        'exempt_from_gross_sales',
    ]

    form_fields = [
        'number',
        'name',
        'product',
        'personnel',
        'exempt_from_gross_sales',
        'allow_product_deletions',
        'employees',
    ]

    has_rows = True
    model_row_class = model.Product

    row_labels = {
        'upc': "UPC",
    }

    row_grid_columns = [
        'upc',
        'brand',
        'description',
        'size',
        'vendor',
        'regular_price',
        'current_price',
    ]

    def configure_grid(self, g):
        super(DepartmentView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('number')
        g.set_type('product', 'boolean')
        g.set_type('personnel', 'boolean')
        g.set_link('number')
        g.set_link('name')

    def configure_form(self, f):
        super(DepartmentView, self).configure_form(f)
        use_buefy = self.get_use_buefy()

        f.remove_field('subdepartments')

        if not use_buefy or self.creating or self.editing:
            f.remove('employees')
        else:
            f.set_renderer('employees', self.render_employees)

        f.set_type('product', 'boolean')
        f.set_type('personnel', 'boolean')

    def render_employees(self, department, field):
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        factory = self.get_grid_factory()
        g = factory(
            key='{}.employees'.format(route_prefix),
            data=[],
            columns=[
                'first_name',
                'last_name',
            ],
            sortable=True,
            sorters={'first_name': True, 'last_name': True},
        )

        if self.request.has_perm('employees.view'):
            g.main_actions.append(self.make_action('view', icon='eye'))
        if self.request.has_perm('employees.edit'):
            g.main_actions.append(self.make_action('edit', icon='edit'))

        return HTML.literal(
            g.render_buefy_table_element(data_prop='employeesData'))

    def template_kwargs_view(self, **kwargs):
        kwargs = super(DepartmentView, self).template_kwargs_view(**kwargs)
        use_buefy = self.get_use_buefy()
        department = kwargs['instance']
        department_employees = sorted(department.employees, key=six.text_type)

        if use_buefy:
            employees = []
            for employee in department_employees:
                person = employee.person
                employees.append({
                    'uuid': employee.uuid,
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    '_action_url_view': self.request.route_url('employees.view', uuid=employee.uuid),
                    '_action_url_edit': self.request.route_url('employees.edit', uuid=employee.uuid),
                })
            kwargs['employees_data'] = employees

        else: # not buefy
            if department.employees:
                actions = [
                    grids.GridAction('view', icon='zoomin',
                                     url=lambda r, i: self.request.route_url('employees.view', uuid=r.uuid))
                ]
                kwargs['employees'] = grids.Grid(None, department_employees, ['display_name'], request=self.request,
                                                 model_class=model.Employee, main_actions=actions)
            else:
                kwargs['employees'] = None

        return kwargs

    def before_delete(self, department):
        """
        Check to see if there are any products which belong to the department;
        if there are then we do not allow delete and redirect the user.
        """
        count = self.Session.query(model.Product)\
                            .filter(model.Product.department == department)\
                            .count()
        if count:
            self.request.session.flash("Will not delete department which still has {} products: {}".format(
                count, department), 'error')
            raise self.redirect(self.get_action_url('view', department))

    def get_row_data(self, department):
        return self.Session.query(model.Product)\
                           .filter(model.Product.department == department)

    def get_parent(self, product):
        return product.department

    def configure_row_grid(self, g):
        super(DepartmentView, self).configure_row_grid(g)

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

    def list_by_vendor(self):
        """
        View list of departments by vendor
        """
        data = self.Session.query(model.Department)\
                           .outerjoin(model.Product)\
                           .join(model.ProductCost)\
                           .join(model.Vendor)\
                           .filter(model.Vendor.uuid == self.request.params['uuid'])\
                           .distinct()\
                           .order_by(model.Department.name)

        def configure(g):
            g.configure(include=[
                g.name,
            ], readonly=True)

        def row_attrs(row, i):
            return {'data-uuid': row.uuid}

        grid = self.make_grid(data=data, sortable=False, filterable=False, pageable=False,
                              configure=configure, width=None, checkboxes=True,
                              row_attrs=row_attrs, main_actions=[], more_actions=[])
        self.request.response.content_type = str('text/html')
        self.request.response.text = grid.render_grid()
        return self.request.response

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # list by vendor
        config.add_route('{}.by_vendor'.format(route_prefix), '{}/by-vendor'.format(url_prefix))
        config.add_view(cls, attr='list_by_vendor', route_name='{}.by_vendor'.format(route_prefix),
                        permission='{}.list'.format(permission_prefix))

        cls._defaults(config)


def includeme(config):
    DepartmentView.defaults(config)
