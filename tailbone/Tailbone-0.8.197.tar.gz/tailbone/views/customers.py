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
Customer Views
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

import colander
from pyramid.httpexceptions import HTTPNotFound
from webhelpers2.html import HTML, tags

from tailbone import grids
from tailbone.db import Session
from tailbone.views import MasterView

from rattail.db import model


class CustomerView(MasterView):
    """
    Master view for the Customer class.
    """
    model_class = model.Customer
    is_contact = True
    has_versions = True
    people_detachable = True
    touchable = True
    supports_autocomplete = True

    # whether to show "view full profile" helper for customer view
    show_profiles_helper = True

    labels = {
        'id': "ID",
        'default_phone': "Phone Number",
        'default_email': "Email Address",
        'default_address': "Physical Address",
        'active_in_pos': "Active in POS",
        'active_in_pos_sticky': "Always Active in POS",
    }

    grid_columns = [
        'id',
        'number',
        'name',
        'phone',
        'email',
    ]

    form_fields = [
        'id',
        'number',
        'name',
        'default_phone',
        'default_address',
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
        'default_email',
        'email_preference',
        'wholesale',
        'active_in_pos',
        'active_in_pos_sticky',
        'people',
        'groups',
        'members',
    ]

    def configure_grid(self, g):
        super(CustomerView, self).configure_grid(g)

        # name
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.set_sort_defaults('name')

        # phone
        g.set_joiner('phone', lambda q: q.outerjoin(model.CustomerPhoneNumber, sa.and_(
            model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid,
            model.CustomerPhoneNumber.preference == 1)))
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.CustomerPhoneNumber.number, d)())
        g.set_filter('phone', model.CustomerPhoneNumber.number,
                     # label="Phone Number",
                     factory=grids.filters.AlchemyPhoneNumberFilter)
        g.set_label('phone', "Phone Number")

        # email
        g.set_joiner('email', lambda q: q.outerjoin(model.CustomerEmailAddress, sa.and_(
            model.CustomerEmailAddress.parent_uuid == model.Customer.uuid,
            model.CustomerEmailAddress.preference == 1)))
        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.CustomerEmailAddress.address, d)())
        g.set_filter('email', model.CustomerEmailAddress.address)#, label="Email Address")
        g.set_label('email', "Email Address")

        # email_preference
        g.set_enum('email_preference', self.enum.EMAIL_PREFERENCE)

        # person
        g.set_joiner('person', lambda q:
                     q.outerjoin(model.CustomerPerson,
                                 sa.and_(
                                     model.CustomerPerson.customer_uuid == model.Customer.uuid,
                                     model.CustomerPerson.ordinal == 1))\
                     .outerjoin(model.Person))
        g.set_sorter('person', model.Person.display_name)
        g.set_renderer('person', self.grid_render_person)

        g.set_link('id')
        g.set_link('number')
        g.set_link('name')
        g.set_link('person')
        g.set_link('email')

    def get_instance(self):
        try:
            instance = super(CustomerView, self).get_instance()
        except HTTPNotFound:
            pass
        else:
            if instance:
                return instance

        key = self.request.matchdict['uuid']

        # search by Customer.id
        instance = self.Session.query(model.Customer)\
                               .filter(model.Customer.id == key)\
                               .first()
        if instance:
            return instance

        # search by CustomerPerson.uuid
        instance = self.Session.query(model.CustomerPerson).get(key)
        if instance:
            return instance.customer

        # search by CustomerGroupAssignment.uuid
        instance = self.Session.query(model.CustomerGroupAssignment).get(key)
        if instance:
            return instance.customer

        raise HTTPNotFound

    def configure_common_form(self, f):
        super(CustomerView, self).configure_common_form(f)
        customer = f.model_instance
        permission_prefix = self.get_permission_prefix()
        use_buefy = self.get_use_buefy()

        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and customer.emails:
            f.set_default('default_email', customer.emails[0].address)

        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and customer.phones:
            f.set_default('default_phone', customer.phones[0].number)

        # default_address
        if self.creating or self.editing:
            f.remove_field('default_address')
        else:
            f.set_renderer('default_address', self.render_default_address)
            f.set_readonly('default_address')

        # address_*
        if not (self.creating or self.editing):
            f.remove_fields('address_street',
                            'address_street2',
                            'address_city',
                            'address_state',
                            'address_zipcode')
        elif self.editing and customer.addresses:
            addr = customer.addresses[0]
            f.set_default('address_street', addr.street)
            f.set_default('address_street2', addr.street2)
            f.set_default('address_city', addr.city)
            f.set_default('address_state', addr.state)
            f.set_default('address_zipcode', addr.zipcode)

        f.set_enum('email_preference', self.enum.EMAIL_PREFERENCE)
        preferences = list(self.enum.EMAIL_PREFERENCE.items())
        preferences.insert(0, ('', "(no preference)"))
        f.widgets['email_preference'].values = preferences

        # person
        if self.creating:
            f.remove_field('person')
        else:
            f.set_readonly('person')
            f.set_renderer('person', self.form_render_person)

        # people
        if self.viewing:
            if use_buefy:
                f.set_renderer('people', self.render_people_buefy)
            elif self.people_detachable and self.has_perm('detach_person'):
                f.set_renderer('people', self.render_people_removable)
            else:
                f.set_renderer('people', self.render_people)
        else:
            f.remove('people')

        # groups
        if self.creating:
            f.remove_field('groups')
        else:
            f.set_renderer('groups', self.render_groups)
            f.set_readonly('groups')

    def configure_form(self, f):
        super(CustomerView, self).configure_form(f)
        customer = f.model_instance
        permission_prefix = self.get_permission_prefix()

        # members
        if self.creating:
            f.remove_field('members')
        else:
            f.set_renderer('members', self.render_members)
            f.set_readonly('members')

    def template_kwargs_view(self, **kwargs):
        kwargs = super(CustomerView, self).template_kwargs_view(**kwargs)

        kwargs['show_profiles_helper'] = self.show_profiles_helper

        use_buefy = self.get_use_buefy()
        if use_buefy:
            customer = kwargs['instance']
            people = []
            for person in customer.people:
                data = {
                    'uuid': person.uuid,
                    'full_name': person.display_name,
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    '_action_url_view': self.request.route_url('people.view',
                                                               uuid=person.uuid),
                }
                if self.editable and self.request.has_perm('people.edit'):
                    data['_action_url_edit'] = self.request.route_url(
                        'people.edit',
                        uuid=person.uuid)
                if self.people_detachable and self.has_perm('detach_person'):
                    data['_action_url_detach'] = self.request.route_url(
                        'customers.detach_person',
                        uuid=customer.uuid,
                        person_uuid=person.uuid)
                people.append(data)
            kwargs['people_data'] = people

        return kwargs

    def unique_id(self, node, value):
        query = self.Session.query(model.Customer)\
                            .filter(model.Customer.id == value)
        if self.editing:
            customer = self.get_instance()
            query = query.filter(model.Customer.uuid != customer.uuid)
        if query.count():
            raise colander.Invalid(node, "Customer ID must be unique")

    def render_default_address(self, customer, field):
        if customer.addresses:
            return six.text_type(customer.addresses[0])

    def grid_render_person(self, customer, field):
        person = getattr(customer, field)
        if not person:
            return ""
        return six.text_type(person)

    def form_render_person(self, customer, field):
        person = getattr(customer, field)
        if not person:
            return ""

        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_people(self, customer, field):
        people = customer.people
        if not people:
            return ""

        items = []
        for person in people:
            text = six.text_type(person)
            url = self.request.route_url('people.view', uuid=person.uuid)
            link = tags.link_to(text, url)
            items.append(HTML.tag('li', c=[link]))
        return HTML.tag('ul', c=items)

    def render_people_removable(self, customer, field):
        people = customer.people
        if not people:
            return ""

        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        view_url = lambda p, i: self.request.route_url('people.view', uuid=p.uuid)
        actions = [
            grids.GridAction('view', icon='zoomin', url=view_url),
        ]
        if self.people_detachable and self.request.has_perm('{}.detach_person'.format(permission_prefix)):
            url = lambda p, i: self.request.route_url('{}.detach_person'.format(route_prefix),
                                                      uuid=customer.uuid, person_uuid=p.uuid)
            actions.append(
                grids.GridAction('detach', icon='trash', url=url))

        columns = ['first_name', 'last_name', 'display_name']
        g = grids.Grid(
            key='{}.people'.format(route_prefix),
            data=customer.people,
            columns=columns,
            labels={'display_name': "Full Name"},
            url=lambda p: self.request.route_url('people.view', uuid=p.uuid),
            linked_columns=columns,
            main_actions=actions)
        return HTML.literal(g.render_grid())

    def render_people_buefy(self, customer, field):
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        factory = self.get_grid_factory()
        g = factory(
            key='{}.people'.format(route_prefix),
            data=[],
            columns=[
                'full_name',
                'first_name',
                'last_name',
            ],
            sortable=True,
            sorters={'full_name': True, 'first_name': True, 'last_name': True},
        )

        if self.request.has_perm('people.view'):
            g.main_actions.append(self.make_action('view', icon='eye'))
        if self.request.has_perm('people.edit'):
            g.main_actions.append(self.make_action('edit', icon='edit'))
        if self.people_detachable and self.has_perm('detach_person'):
            g.main_actions.append(self.make_action('detach', icon='minus-circle',
                                                   link_class='has-text-warning',
                                                   click_handler="$emit('detach-person', props.row._action_url_detach)"))

        return HTML.literal(
            g.render_buefy_table_element(data_prop='peopleData'))

    def render_groups(self, customer, field):
        groups = customer.groups
        if not groups:
            return ""
        items = []
        for group in groups:
            text = "({}) {}".format(group.id, group.name)
            url = self.request.route_url('customergroups.view', uuid=group.uuid)
            items.append(HTML.tag('li', tags.link_to(text, url)))
        return HTML.tag('ul', HTML.literal('').join(items))

    def render_members(self, customer, field):
        members = customer.members
        if not members:
            return ""
        items = []
        for member in members:
            text = six.text_type(member)
            url = self.request.route_url('members.view', uuid=member.uuid)
            items.append(HTML.tag('li', tags.link_to(text, url)))
        return HTML.tag('ul', HTML.literal('').join(items))

    def get_version_child_classes(self):
        return [
            (model.CustomerPhoneNumber, 'parent_uuid'),
            (model.CustomerEmailAddress, 'parent_uuid'),
            (model.CustomerMailingAddress, 'parent_uuid'),
            (model.CustomerPerson, 'customer_uuid'),
            (model.CustomerNote, 'parent_uuid'),
        ]

    def detach_person(self):
        customer = self.get_instance()
        person = self.Session.query(model.Person).get(self.request.matchdict['person_uuid'])
        if not person:
            return self.notfound()

        if person in customer.people:
            customer.people.remove(person)
        else:
            self.request.session.flash("No change; person \"{}\" not attached to customer \"{}\"".format(
                person, customer))

        return self.redirect(self.request.get_referrer())

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._customer_defaults(config)

    @classmethod
    def _customer_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # detach person
        if cls.people_detachable:
            config.add_tailbone_permission(permission_prefix,
                                           '{}.detach_person'.format(permission_prefix),
                                           "Detach a Person from a {}".format(model_title))
            # TODO: this should require POST, but we'll add that once
            # we can assume a Buefy theme is present, to avoid having
            # to implement the logic in old jquery...
            config.add_route('{}.detach_person'.format(route_prefix),
                             '{}/detach-person/{{person_uuid}}'.format(instance_url_prefix),
                             # request_method='POST',
            )
            config.add_view(cls, attr='detach_person',
                            route_name='{}.detach_person'.format(route_prefix),
                            permission='{}.detach_person'.format(permission_prefix))


class PendingCustomerView(MasterView):
    """
    Master view for the Pending Customer class.
    """
    model_class = model.PendingCustomer
    route_prefix = 'pending_customers'
    url_prefix = '/customers/pending'

    labels = {
        'id': "ID",
        'status_code': "Status",
    }

    grid_columns = [
        'id',
        'display_name',
        'first_name',
        'last_name',
        'phone_number',
        'email_address',
        'status_code',
    ]

    form_fields = [
        'id',
        'display_name',
        'first_name',
        'middle_name',
        'last_name',
        'phone_number',
        'phone_type',
        'email_address',
        'email_type',
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
        'address_type',
        'status_code',
        'created',
        'user',
    ]

    def configure_grid(self, g):
        super(PendingCustomerView, self).configure_grid(g)

        g.set_enum('status_code', self.enum.PENDING_CUSTOMER_STATUS)
        g.filters['status_code'].default_active = True
        g.filters['status_code'].default_verb = 'not_equal'
        g.filters['status_code'].default_value = six.text_type(self.enum.PENDING_CUSTOMER_STATUS_RESOLVED)

        g.set_sort_defaults('display_name')
        g.set_link('id')
        g.set_link('display_name')

    def configure_form(self, f):
        super(PendingCustomerView, self).configure_form(f)

        f.set_enum('status_code', self.enum.PENDING_CUSTOMER_STATUS)

        # created
        if self.creating:
            f.remove('created')
        else:
            f.set_readonly('created')

        # user
        if self.creating:
            f.remove('user')
        else:
            f.set_readonly('user')
            f.set_renderer('user', self.render_user)

    def editable_instance(self, pending):
        if pending.status_code == self.enum.PENDING_CUSTOMER_STATUS_RESOLVED:
            return False
        return True

    def resolve_person(self):
        model = self.model
        pending = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', pending))

        uuid = self.request.POST['person_uuid']
        person = self.Session.query(model.Person).get(uuid)
        if not person:
            self.request.session.flash("Person not found!", 'error')
            return redirect

        app = self.get_rattail_app()
        people_handler = app.get_people_handler()
        people_handler.resolve_person(pending, person, self.request.user)
        self.Session.flush()
        return redirect

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._pending_customer_defaults(config)

    @classmethod
    def _pending_customer_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()

        # resolve person
        config.add_tailbone_permission(permission_prefix,
                                       '{}.resolve_person'.format(permission_prefix),
                                       "Resolve a {} as a Person".format(model_title))
        config.add_route('{}.resolve_person'.format(route_prefix),
                         '{}/resolve-person'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='resolve_person',
                        route_name='{}.resolve_person'.format(route_prefix),
                        permission='{}.resolve_person'.format(permission_prefix))


# # TODO: this is referenced by some custom apps, but should be moved??
# def unique_id(value, field):
#     customer = field.parent.model
#     query = Session.query(model.Customer).filter(model.Customer.id == value)
#     if customer.uuid:
#         query = query.filter(model.Customer.uuid != customer.uuid)
#     if query.count():
#         raise fa.ValidationError("Customer ID must be unique")


# TODO: this only works when creating, need to add edit support?
# TODO: can this just go away? since we have unique_id() view method above
def unique_id(node, value):
    customers = Session.query(model.Customer).filter(model.Customer.id == value)
    if customers.count():
        raise colander.Invalid(node, "Customer ID must be unique")


def customer_info(request):
    """
    View which returns simple dictionary of info for a particular customer.
    """
    uuid = request.params.get('uuid')
    customer = Session.query(model.Customer).get(uuid) if uuid else None
    if not customer:
        return {}
    return {
        'uuid':                 customer.uuid,
        'name':                 customer.name,
        'phone_number':         customer.phone.number if customer.phone else '',
        }


def includeme(config):

    # info
    config.add_route('customer.info', '/customers/info')
    config.add_view(customer_info, route_name='customer.info',
                    renderer='json', permission='customers.view')

    CustomerView.defaults(config)
    PendingCustomerView.defaults(config)
