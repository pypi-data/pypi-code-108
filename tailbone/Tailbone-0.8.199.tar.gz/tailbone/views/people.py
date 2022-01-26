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
Person Views
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model, api
from rattail.db.util import maxlen
from rattail.time import localtime
from rattail.util import OrderedDict, simple_error

import colander
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from webhelpers2.html import HTML, tags

from tailbone import forms, grids
from tailbone.views import MasterView


log = logging.getLogger(__name__)


class PersonView(MasterView):
    """
    Master view for the Person class.
    """
    model_class = model.Person
    model_title_plural = "People"
    route_prefix = 'people'
    touchable = True
    has_versions = True
    bulk_deletable = True
    is_contact = True
    manage_notes_from_profile_view = False
    supports_autocomplete = True

    labels = {
        'default_phone': "Phone Number",
        'default_email': "Email Address",
    }

    grid_columns = [
        'display_name',
        'first_name',
        'last_name',
        'phone',
        'email',
        'merge_requested',
    ]

    form_fields = [
        'first_name',
        'middle_name',
        'last_name',
        'display_name',
        'default_phone',
        'default_email',
        'address',
        'employee',
        'customers',
        'members',
        'users',
    ]

    mergeable = True

    def __init__(self, request):
        super(PersonView, self).__init__(request)

        # always get a reference to the People Handler
        app = self.get_rattail_app()
        self.handler = app.get_people_handler()

    def make_grid_kwargs(self, **kwargs):
        kwargs = super(PersonView, self).make_grid_kwargs(**kwargs)

        # turn on checkboxes if user can create a merge reqeust
        if self.mergeable and self.has_perm('request_merge'):
            kwargs['checkboxes'] = True

        return kwargs

    def configure_grid(self, g):
        super(PersonView, self).configure_grid(g)

        g.joiners['email'] = lambda q: q.outerjoin(model.PersonEmailAddress, sa.and_(
            model.PersonEmailAddress.parent_uuid == model.Person.uuid,
            model.PersonEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.PersonPhoneNumber, sa.and_(
            model.PersonPhoneNumber.parent_uuid == model.Person.uuid,
            model.PersonPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.PersonEmailAddress.address)
        g.set_filter('phone', model.PersonPhoneNumber.number,
                     factory=grids.filters.AlchemyPhoneNumberFilter)

        g.joiners['customer_id'] = lambda q: q.outerjoin(model.CustomerPerson).outerjoin(model.Customer)
        g.filters['customer_id'] = g.make_filter('customer_id', model.Customer.id)

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.set_joiner('employee_status', lambda q: q.outerjoin(model.Employee))
        g.set_filter('employee_status', model.Employee.status,
                     value_enum=self.enum.EMPLOYEE_STATUS)

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.PersonEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.PersonPhoneNumber.number, d)())

        g.set_label('merge_requested', "MR")
        g.set_renderer('merge_requested', self.render_merge_requested)

        g.set_sort_defaults('display_name')

        g.set_label('display_name', "Full Name")
        g.set_label('phone', "Phone Number")
        g.set_label('email', "Email Address")
        g.set_label('customer_id', "Customer ID")

        g.set_link('display_name')
        g.set_link('first_name')
        g.set_link('last_name')

    def render_merge_requested(self, person, field):
        model = self.model
        merge_request = self.Session.query(model.MergePeopleRequest)\
                                    .filter(sa.or_(
                                        model.MergePeopleRequest.removing_uuid == person.uuid,
                                        model.MergePeopleRequest.keeping_uuid == person.uuid))\
                                    .filter(model.MergePeopleRequest.merged == None)\
                                    .first()
        if merge_request:
            use_buefy = self.get_use_buefy()
            if use_buefy:
                return HTML.tag('span',
                                class_='has-text-danger has-text-weight-bold',
                                title="A merge has been requested for this person.",
                                c="MR")
            return "MR"

    def get_instance(self):
        # TODO: I don't recall why this fallback check for a vendor contact
        # exists here, but leaving it intact for now.
        key = self.request.matchdict['uuid']
        instance = self.Session.query(model.Person).get(key)
        if instance:
            return instance
        instance = self.Session.query(model.VendorContact).get(key)
        if instance:
            return instance.person
        raise HTTPNotFound

    def is_person_protected(self, person):
        for user in person.users:
            if self.user_is_protected(user):
                return True
        return False

    def editable_instance(self, person):
        if self.request.is_root:
            return True
        return not self.is_person_protected(person)

    def deletable_instance(self, person):
        if self.request.is_root:
            return True
        return not self.is_person_protected(person)

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated

        # do normal create/update
        person = super(PersonView, self).objectify(form, data)

        # collect data from all name fields
        names = {}
        if 'first_name' in form:
            names['first'] = data['first_name']
        if 'middle_name' in form:
            names['middle'] = data['middle_name']
        if 'last_name' in form:
            names['last'] = data['last_name']
        if 'display_name' in form and 'display_name' not in form.readonly_fields:
            names['full'] = data['display_name']

        # TODO: why do we find colander.null values in data at this point?
        # ugh, for now we must convert them
        for key in names:
            if names[key] is colander.null:
                names[key] = None

        # do explicit name update w/ common handler logic
        self.handler.update_names(person, **names)

        return person

    def delete_instance(self, person):
        """
        Supplements the default logic as follows:

        Any customer associations are first deleted for the person.  Once that
        is complete, deletion continues as per usual.
        """
        session = orm.object_session(person)

        # must explicitly remove all CustomerPerson records
        for cp in list(person._customers):
            customer = cp.customer
            session.delete(cp)
            # session.flush()
            customer._people.reorder()

        # continue with normal logic
        super(PersonView, self).delete_instance(person)

    def touch_instance(self, person):
        """
        Supplements the default logic as follows:

        In addition to "touching" the person proper, we also "touch" each
        contact info record associated with them.
        """
        # touch person, as per usual
        super(PersonView, self).touch_instance(person)

        def touch(obj):
            change = model.Change()
            change.class_name = obj.__class__.__name__
            change.instance_uuid = obj.uuid
            change.deleted = False
            self.Session.add(change)

        # phone numbers
        for phone in person.phones:
            touch(phone)

        # email addresses
        for email in person.emails:
            touch(email)

        # mailing addresses
        for address in person.addresses:
            touch(address)

    def configure_common_form(self, f):
        super(PersonView, self).configure_common_form(f)
        person = f.model_instance

        f.set_label('display_name', "Full Name")

        # TODO: should remove this?
        f.set_readonly('phone')
        f.set_label('phone', "Phone Number")

        f.set_renderer('default_phone', self.render_default_phone)
        if not self.creating and person.phones:
            f.set_default('default_phone', person.phones[0].number)

        # TODO: should remove this?
        f.set_readonly('email')
        f.set_label('email', "Email Address")

        f.set_renderer('default_email', self.render_default_email)
        if not self.creating and person.emails:
            f.set_default('default_email', person.emails[0].address)

        f.set_readonly('address')
        f.set_label('address', "Mailing Address")

        # employee
        if self.creating:
            f.remove_field('employee')
        else:
            f.set_readonly('employee')
            f.set_renderer('employee', self.render_employee)

        # customers
        if self.creating:
            f.remove_field('customers')
        else:
            f.set_readonly('customers')
            f.set_renderer('customers', self.render_customers)

        # members
        if self.creating:
            f.remove_field('members')
        else:
            f.set_readonly('members')
            f.set_renderer('members', self.render_members)

        # users
        if self.creating:
            f.remove_field('users')
        else:
            f.set_readonly('users')
            f.set_renderer('users', self.render_users)

    def render_employee(self, person, field):
        employee = person.employee
        if not employee:
            return ""
        text = six.text_type(employee)
        url = self.request.route_url('employees.view', uuid=employee.uuid)
        return tags.link_to(text, url)

    def render_customers(self, person, field):
        customers = person._customers
        if not customers:
            return ""
        items = []
        for customer in customers:
            customer = customer.customer
            text = six.text_type(customer)
            if customer.number:
                text = "(#{}) {}".format(customer.number, text)
            elif customer.id:
                text = "({}) {}".format(customer.id, text)
            url = self.request.route_url('customers.view', uuid=customer.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def render_members(self, person, field):
        members = person.members
        if not members:
            return ""
        items = []
        for member in members:
            text = six.text_type(member)
            if member.number:
                text = "(#{}) {}".format(member.number, text)
            elif member.id:
                text = "({}) {}".format(member.id, text)
            url = self.request.route_url('members.view', uuid=member.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def render_users(self, person, field):
        use_buefy = self.get_use_buefy()
        users = person.users
        items = []
        for user in users:
            text = user.username
            url = self.request.route_url('users.view', uuid=user.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        if items:
            return HTML.tag('ul', c=items)
        elif self.viewing and self.request.has_perm('users.create'):
            if use_buefy:
                return HTML.tag('b-button', type='is-primary', c="Make User",
                                **{'@click': 'clickMakeUser()'})
            else:
                return HTML.tag('button', type='button', id='make-user', c="Make User")
        else:
            return ""

    def get_version_child_classes(self):
        return [
            (model.PersonPhoneNumber, 'parent_uuid'),
            (model.PersonEmailAddress, 'parent_uuid'),
            (model.PersonMailingAddress, 'parent_uuid'),
            (model.Employee, 'person_uuid'),
            (model.CustomerPerson, 'person_uuid'),
            (model.VendorContact, 'person_uuid'),
        ]

    def get_merge_fields(self):
        fields = self.handler.get_merge_preview_fields()
        return [field['name'] for field in fields]

    def get_merge_additive_fields(self):
        fields = self.handler.get_merge_preview_fields()
        return [field['name'] for field in fields
                if field.get('additive')]

    def get_merge_coalesce_fields(self):
        fields = self.handler.get_merge_preview_fields()
        return [field['name'] for field in fields
                if field.get('coalesce')]

    def get_merge_data(self, person):
        return self.handler.get_merge_preview_data(person)

    def validate_merge(self, removing, keeping):
        reason = self.handler.why_not_merge(removing, keeping)
        if reason:
            raise Exception(reason)

    def merge_objects(self, removing, keeping):
        self.handler.perform_merge(removing, keeping, user=self.request.user)

    def view_profile(self):
        """
        View which exposes the "full profile" for a given person, i.e. all
        related customer, employee, user info etc.
        """
        self.viewing = True
        person = self.get_instance()
        employee = person.employee
        context = {
            'person': person,
            'instance': person,
            'instance_title': self.get_instance_title(person),
            'today': localtime(self.rattail_config).date(),
            'person_data': self.get_context_person(person),
            'phone_type_options': self.get_phone_type_options(),
            'email_type_options': self.get_email_type_options(),
            'max_lengths': self.get_max_lengths(),
            'customers_data': self.get_context_customers(person),
            'members_data': self.get_context_members(person),
            'employee': employee,
            'employee_data': self.get_context_employee(employee) if employee else {},
            'employee_view_url': self.request.route_url('employees.view', uuid=employee.uuid) if employee else None,
            'employee_history': employee.get_current_history() if employee else None,
            'employee_history_data': self.get_context_employee_history(employee),
            'dynamic_content_title': self.get_context_content_title(person),
        }

        use_buefy = self.get_use_buefy()
        template = 'view_profile_buefy' if use_buefy else 'view_profile'
        return self.render_to_response(template, context)

    def template_kwargs_view_profile(self, **kwargs):
        """
        Stub method so subclass can call `super()` for it.
        """
        return kwargs

    def template_kwargs_view_profile_buefy(self, **kwargs):
        """
        Note that any subclass should not need to define this method.
        It by default invokes :meth:`template_kwargs_view_profile()`
        and returns that result.
        """
        return self.template_kwargs_view_profile(**kwargs)

    def get_max_lengths(self):
        model = self.model
        return {
            'address_street': maxlen(model.PersonMailingAddress.street),
            'address_street2': maxlen(model.PersonMailingAddress.street2),
            'address_city': maxlen(model.PersonMailingAddress.city),
            'address_state': maxlen(model.PersonMailingAddress.state),
            'address_zipcode': maxlen(model.PersonMailingAddress.zipcode),
        }

    def get_phone_type_options(self):
        """
        Returns a list of "phone type" options, for use in dropdown.
        """
        # TODO: should probably define this list somewhere else
        phone_types = [
            "Home",
            "Mobile",
            "Work",
            "Other",
            "Fax",
        ]
        return [{'value': typ, 'label': typ}
                for typ in phone_types]

    def get_email_type_options(self):
        """
        Returns a list of "email type" options, for use in dropdown.
        """
        # TODO: should probably define this list somewhere else
        email_types = [
            "Home",
            "Work",
            "Other",
        ]
        return [{'value': typ, 'label': typ}
                for typ in email_types]

    def get_context_person(self, person):

        context = {
            'uuid': person.uuid,
            'first_name': person.first_name,
            'middle_name': person.middle_name,
            'last_name': person.last_name,
            'display_name': person.display_name,
            'view_url': self.get_action_url('view', person),
            'view_profile_url': self.get_action_url('view_profile', person),
            'phones': self.get_context_phones(person),
            'emails': self.get_context_emails(person),
            'dynamic_content_title': self.get_context_content_title(person),
        }

        if person.address:
            context['address'] = self.get_context_address(person.address)

        return context

    def get_context_content_title(self, person):
        return six.text_type(person)

    def get_context_address(self, address):
        context = {
            'uuid': address.uuid,
            'street': address.street,
            'street2': address.street2,
            'city': address.city,
            'state': address.state,
            'zipcode': address.zipcode,
            'display': six.text_type(address),
        }

        model = self.model
        if isinstance(address, model.PersonMailingAddress):
            person = address.person
            context['invalid'] = self.handler.address_is_invalid(person, address)

        return context

    def get_context_customers(self, person):
        data = []
        for cp in person._customers:
            customer = cp.customer
            data.append({
                'uuid': customer.uuid,
                'ordinal': cp.ordinal,
                'id': customer.id,
                'number': customer.number,
                'name': customer.name,
                'view_url': self.request.route_url('customers.view',
                                                   uuid=customer.uuid),
                'people': [self.get_context_person(p)
                           for p in customer.people],
                'addresses': [self.get_context_address(a)
                              for a in customer.addresses],
            })
        return data

    def get_context_members(self, person):
        data = OrderedDict()

        for member in person.members:
            data[member.uuid] = self.get_context_member(member)

        for customer in person.customers:
            for member in customer.members:
                if member.uuid not in data:
                    data[member.uuid] = self.get_context_member(member)

        return list(data.values())

    def get_context_member(self, member):
        profile_url = None
        if member.person:
            profile_url = self.request.route_url('people.view_profile',
                                                 uuid=member.person_uuid)

        return {
            'uuid': member.uuid,
            'number': member.number,
            'id': member.id,
            'active': member.active,
            'joined': six.text_type(member.joined) if member.joined else None,
            'withdrew': six.text_type(member.withdrew) if member.withdrew else None,
            'customer_uuid': member.customer_uuid,
            'customer_name': member.customer.name if member.customer else None,
            'person_uuid': member.person_uuid,
            'display': six.text_type(member),
            'person_display_name': member.person.display_name if member.person else None,
            'view_url': self.request.route_url('members.view', uuid=member.uuid),
            'view_profile_url': profile_url,
        }

    def get_context_employee(self, employee):
        """
        Return a dict of context data for the given employee.
        """
        app = self.get_rattail_app()
        handler = app.get_employment_handler()
        context = handler.get_context_employee(employee)
        context['view_url'] = self.request.route_url('employees.view', uuid=employee.uuid)
        return context

    def get_context_employee_history(self, employee):
        data = []
        if employee:
            for history in employee.sorted_history(reverse=True):
                data.append({
                    'uuid': history.uuid,
                    'start_date': six.text_type(history.start_date),
                    'end_date': six.text_type(history.end_date or ''),
                })
        return data

    def ensure_customer(self, person):
        """
        Return the `Customer` record for the given person, establishing it
        first if necessary.
        """
        app = self.get_rattail_app()
        handler = app.get_clientele_handler()
        customer = handler.ensure_customer(person)
        return customer

    def profile_edit_name(self):
        """
        View which allows a person's name to be updated.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        self.handler.update_names(person,
                                  first=data['first_name'],
                                  middle=data['middle_name'],
                                  last=data['last_name'])

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
            'dynamic_content_title': self.get_context_content_title(person),
        }

    def get_context_phones(self, person):
        data = []
        for phone in person.phones:
            data.append({
                'uuid': phone.uuid,
                'type': phone.type,
                'number': phone.number,
                'preferred': phone.preferred,
                'preference': phone.preference,
            })
        return data

    def profile_add_phone(self):
        """
        View which adds a new phone number for the person.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        try:
            phone = self.handler.add_phone(person, data['phone_number'],
                                           type=data['phone_type'],
                                           preferred=data['phone_preferred'])
        except Exception as error:
            log.warning("failed to add phone", exc_info=True)
            return {'error': simple_error(error)}

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_update_phone(self):
        """
        View which updates a phone number for the person.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        phone = self.Session.query(model.PersonPhoneNumber).get(data['phone_uuid'])
        if not phone:
            return {'error': "Phone not found."}

        kwargs = {
            'number': data['phone_number'],
            'type': data['phone_type'],
        }
        if 'phone_preferred' in data:
            kwargs['preferred'] = data['phone_preferred']

        try:
            phone = self.handler.update_phone(person, phone, **kwargs)
        except Exception as error:
            log.warning("failed to update phone", exc_info=True)
            return {'error': simple_error(error)}

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_delete_phone(self):
        """
        View which allows a person's phone number to be deleted.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        # validate phone
        phone = self.Session.query(model.PersonPhoneNumber).get(data['phone_uuid'])
        if not phone:
            return {'error': "Phone not found."}
        if phone not in person.phones:
            return {'error': "Phone does not belong to this person."}

        # remove phone
        person.remove_phone(phone)

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_set_preferred_phone(self):
        """
        View which allows a person's "preferred" phone to be set.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        # validate phone
        phone = self.Session.query(model.PersonPhoneNumber).get(data['phone_uuid'])
        if not phone:
            return {'error': "Phone not found."}
        if phone not in person.phones:
            return {'error': "Phone does not belong to this person."}

        # update phone preference
        person.set_primary_phone(phone)

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def get_context_emails(self, person):
        data = []
        for email in person.emails:
            data.append({
                'uuid': email.uuid,
                'type': email.type,
                'address': email.address,
                'invalid': email.invalid,
                'preferred': email.preferred,
                'preference': email.preference,
            })
        return data

    def profile_add_email(self):
        """
        View which adds a new email address for the person.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        kwargs = {
            'type': data['email_type'],
            'invalid': False,
        }
        if 'email_preferred' in data:
            kwargs['preferred'] = data['email_preferred']

        try:
            email = self.handler.add_email(person, data['email_address'], **kwargs)
        except Exception as error:
            log.warning("failed to add email", exc_info=True)
            return {'error': simple_error(error)}

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_update_email(self):
        """
        View which updates an email address for the person.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        email = self.Session.query(model.PersonEmailAddress).get(data['email_uuid'])
        if not email:
            return {'error': "Email not found."}

        try:
            email = self.handler.update_email(person, email,
                                              address=data['email_address'],
                                              type=data['email_type'],
                                              invalid=data['email_invalid'])
        except Exception as error:
            log.warning("failed to add email", exc_info=True)
            return {'error': simple_error(error)}

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_delete_email(self):
        """
        View which allows a person's email address to be deleted.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        # validate email
        email = self.Session.query(model.PersonEmailAddress).get(data['email_uuid'])
        if not email:
            return {'error': "Email not found."}
        if email not in person.emails:
            return {'error': "Email does not belong to this person."}

        # remove email
        person.remove_email(email)

        self.Session.flush()

        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_set_preferred_email(self):
        """
        View which allows a person's "preferred" email to be set.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        # validate email
        email = self.Session.query(model.PersonEmailAddress).get(data['email_uuid'])
        if not email:
            return {'error': "Email not found."}
        if email not in person.emails:
            return {'error': "Email does not belong to this person."}

        # update email preference
        person.set_primary_email(email)

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_edit_address(self):
        """
        View which allows a person's mailing address to be updated.
        """
        person = self.get_instance()
        data = dict(self.request.json_body)

        # update person address
        address = person.address
        if not address:
            address = person.add_address()
        address.street = data['street']
        address.street2 = data['street2']
        address.city = data['city']
        address.state = data['state']
        address.zipcode = data['zipcode']

        self.handler.mark_address_invalid(person, address, data['invalid'])

        self.Session.flush()
        return {
            'success': True,
            'person': self.get_context_person(person),
        }

    def profile_start_employee(self):
        """
        View which will cause the person to start being an employee.
        """
        person = self.get_instance()
        app = self.get_rattail_app()
        handler = app.get_employment_handler()

        reason = handler.why_not_begin_employment(person)
        if reason:
            return {'error': reason}

        data = self.request.json_body
        start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        employee = handler.begin_employment(person, start_date,
                                            employee_id=data['id'])
        self.Session.flush()
        return self.profile_start_employee_result(employee, start_date)

    def profile_start_employee_result(self, employee, start_date):
        return {
            'success': True,
            'employee': self.get_context_employee(employee),
            'employee_view_url': self.request.route_url('employees.view', uuid=employee.uuid),
            'start_date': six.text_type(start_date),
            'employee_history_data': self.get_context_employee_history(employee),
        }

    def profile_end_employee(self):
        """
        View which will cause the person to stop being an employee.
        """
        person = self.get_instance()
        app = self.get_rattail_app()
        handler = app.get_employment_handler()

        reason = handler.why_not_end_employment(person)
        if reason:
            return {'error': reason}

        data = dict(self.request.json_body)
        end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        employee = handler.get_employee(person)
        handler.end_employment(employee, end_date,
                               revoke_access=data.get('revoke_access'))
        self.Session.flush()
        return self.profile_end_employee_result(employee, end_date)

    def profile_end_employee_result(self, employee, end_date):
        return {
            'success': True,
            'employee': self.get_context_employee(employee),
            'employee_view_url': self.request.route_url('employees.view', uuid=employee.uuid),
            'end_date': six.text_type(end_date),
            'employee_history_data': self.get_context_employee_history(employee),
        }

    def profile_edit_employee_history(self):
        """
        AJAX view for updating an employee history record.
        """
        person = self.get_instance()
        employee = person.employee

        uuid = self.request.json_body['uuid']
        history = self.Session.query(model.EmployeeHistory).get(uuid)
        if not history or history not in employee.history:
            return {'error': "Must specify a valid Employee History record for this Person."}

        # all history records have a start date, so always update that
        start_date = self.request.json_body['start_date']
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        history.start_date = start_date

        # only update end_date if history already had one
        if history.end_date:
            end_date = self.request.json_body['end_date']
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            history.end_date = end_date

        self.Session.flush()
        current_history = employee.get_current_history()
        return {
            'success': True,
            'employee': self.get_context_employee(employee),
            'start_date': six.text_type(current_history.start_date),
            'end_date': six.text_type(current_history.end_date or ''),
            'employee_history_data': self.get_context_employee_history(employee),
        }

    def profile_update_employee_id(self):
        """
        View to update an employee's ID value.
        """
        app = self.get_rattail_app()
        employment = app.get_employment_handler()

        person = self.get_instance()
        employee = employment.get_employee(person)

        data = self.request.json_body
        employee.id = data['employee_id']
        self.Session.flush()

        return {
            'success': True,
            'employee': self.get_context_employee(employee),
        }

    def make_note_form(self, mode, person):
        schema = NoteSchema().bind(session=self.Session(),
                                   person_uuid=person.uuid)
        if mode == 'create':
            del schema['uuid']
        form = forms.Form(schema=schema, request=self.request)
        return form

    def profile_add_note(self):
        person = self.get_instance()
        form = self.make_note_form('create', person)
        if form.validate(newstyle=True):
            note = self.create_note(person, form)
            self.Session.flush()
            return self.profile_add_note_success(note)
        else:
            return self.profile_add_note_failure(person, form)

    def create_note(self, person, form):
        note = model.PersonNote()
        note.type = form.validated['note_type']
        note.subject = form.validated['note_subject']
        note.text = form.validated['note_text']
        note.created_by = self.request.user
        person.notes.append(note)
        return note

    def profile_add_note_success(self, note):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_add_note_failure(self, person, form):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_edit_note(self):
        person = self.get_instance()
        form = self.make_note_form('edit', person)
        if form.validate(newstyle=True):
            note = self.update_note(person, form)
            self.Session.flush()
            return self.profile_edit_note_success(note)
        else:
            return self.profile_edit_note_failure(person, form)

    def update_note(self, person, form):
        note = self.Session.query(model.PersonNote).get(form.validated['uuid'])
        note.subject = form.validated['note_subject']
        note.text = form.validated['note_text']
        return note

    def profile_edit_note_success(self, note):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_edit_note_failure(self, person, form):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_delete_note(self):
        person = self.get_instance()
        form = self.make_note_form('delete', person)
        if form.validate(newstyle=True):
            self.delete_note(person, form)
            self.Session.flush()
            return self.profile_delete_note_success(person)
        else:
            return self.profile_delete_note_failure(person, form)

    def delete_note(self, person, form):
        note = self.Session.query(model.PersonNote).get(form.validated['uuid'])
        self.Session.delete(note)

    def profile_delete_note_success(self, person):
        return self.redirect(self.get_action_url('view_profile', person))

    def profile_delete_note_failure(self, person, form):
        return self.redirect(self.get_action_url('view_profile', person))

    def make_user(self):
        uuid = self.request.POST['person_uuid']
        person = self.Session.query(model.Person).get(uuid)
        if not person:
            return self.notfound()
        if person.users:
            raise RuntimeError("person {} already has {} user accounts: ".format(
                person.uuid, len(person.users), person))
        user = model.User()
        user.username = api.make_username(person)
        user.person = person
        user.active = False
        self.Session.add(user)
        self.Session.flush()
        self.request.session.flash("User has been created: {}".format(user.username))
        return self.redirect(self.request.route_url('users.view', uuid=user.uuid))

    def request_merge(self):
        """
        Create a new merge request for the given 2 people.
        """
        self.handler.request_merge(self.request.user,
                                   self.request.POST['removing_uuid'],
                                   self.request.POST['keeping_uuid'])
        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):
        cls._people_defaults(config)
        cls._defaults(config)

    @classmethod
    def _people_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # "profile" perms
        # TODO: should let view class (or config) determine which of these are available
        config.add_tailbone_permission_group('people_profile', "People Profile View")
        config.add_tailbone_permission('people_profile', 'people_profile.toggle_employee',
                                       "Toggle the person's Employee status")
        config.add_tailbone_permission('people_profile', 'people_profile.edit_employee_history',
                                       "Edit the person's Employee History records")

        # view profile
        config.add_tailbone_permission(permission_prefix, '{}.view_profile'.format(permission_prefix),
                                       "View full \"profile\" for {}".format(model_title))
        config.add_route('{}.view_profile'.format(route_prefix), '{}/{{{}}}/profile'.format(url_prefix, model_key),
                         request_method='GET')
        config.add_view(cls, attr='view_profile', route_name='{}.view_profile'.format(route_prefix),
                        permission='{}.view_profile'.format(permission_prefix))

        # profile - edit personal details
        config.add_tailbone_permission('people_profile',
                                       'people_profile.edit_person',
                                       "Edit the Personal details")

        # profile - edit name
        config.add_route('{}.profile_edit_name'.format(route_prefix),
                         '{}/profile/edit-name'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_edit_name',
                        route_name='{}.profile_edit_name'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - add phone
        config.add_route('{}.profile_add_phone'.format(route_prefix),
                         '{}/profile/add-phone'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_add_phone',
                        route_name='{}.profile_add_phone'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - update phone
        config.add_route('{}.profile_update_phone'.format(route_prefix),
                         '{}/profile/update-phone'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_update_phone',
                        route_name='{}.profile_update_phone'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - delete phone
        config.add_route('{}.profile_delete_phone'.format(route_prefix),
                         '{}/profile/delete-phone'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_delete_phone',
                        route_name='{}.profile_delete_phone'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - set preferred phone
        config.add_route('{}.profile_set_preferred_phone'.format(route_prefix),
                         '{}/profile/set-preferred-phone'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_set_preferred_phone',
                        route_name='{}.profile_set_preferred_phone'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - add email
        config.add_route('{}.profile_add_email'.format(route_prefix),
                         '{}/profile/add-email'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_add_email',
                        route_name='{}.profile_add_email'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - update email
        config.add_route('{}.profile_update_email'.format(route_prefix),
                         '{}/profile/update-email'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_update_email',
                        route_name='{}.profile_update_email'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - delete email
        config.add_route('{}.profile_delete_email'.format(route_prefix),
                         '{}/profile/delete-email'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_delete_email',
                        route_name='{}.profile_delete_email'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - set preferred email
        config.add_route('{}.profile_set_preferred_email'.format(route_prefix),
                         '{}/profile/set-preferred-email'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_set_preferred_email',
                        route_name='{}.profile_set_preferred_email'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - edit address
        config.add_route('{}.profile_edit_address'.format(route_prefix),
                         '{}/profile/edit-address'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_edit_address',
                        route_name='{}.profile_edit_address'.format(route_prefix),
                        renderer='json',
                        permission='people_profile.edit_person')

        # profile - start employee
        config.add_route('{}.profile_start_employee'.format(route_prefix), '{}/profile/start-employee'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_start_employee', route_name='{}.profile_start_employee'.format(route_prefix),
                        permission='people_profile.toggle_employee', renderer='json')

        # profile - end employee
        config.add_route('{}.profile_end_employee'.format(route_prefix), '{}/profile/end-employee'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_end_employee', route_name='{}.profile_end_employee'.format(route_prefix),
                        permission='people_profile.toggle_employee', renderer='json')

        # profile - edit employee history
        config.add_route('{}.profile_edit_employee_history'.format(route_prefix), '{}/profile/edit-employee-history'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_edit_employee_history', route_name='{}.profile_edit_employee_history'.format(route_prefix),
                        permission='people_profile.edit_employee_history', renderer='json')

        # profile - update employee ID
        config.add_route('{}.profile_update_employee_id'.format(route_prefix),
                         '{}/profile/update-employee-id'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='profile_update_employee_id',
                        route_name='{}.profile_update_employee_id'.format(route_prefix),
                        renderer='json',
                        permission='employees.edit')

        # manage notes from profile view
        if cls.manage_notes_from_profile_view:

            # add note
            config.add_tailbone_permission('people_profile', 'people_profile.add_note',
                                           "Add new {} Note records".format(model_title))
            config.add_route('{}.profile_add_note'.format(route_prefix), '{}/{{{}}}/profile/new-note'.format(url_prefix, model_key),
                             request_method='POST')
            config.add_view(cls, attr='profile_add_note', route_name='{}.profile_add_note'.format(route_prefix),
                            permission='people_profile.add_note')

            # edit note
            config.add_tailbone_permission('people_profile', 'people_profile.edit_note',
                                           "Edit {} Note records".format(model_title))
            config.add_route('{}.profile_edit_note'.format(route_prefix), '{}/{{{}}}/profile/edit-note'.format(url_prefix, model_key),
                             request_method='POST')
            config.add_view(cls, attr='profile_edit_note', route_name='{}.profile_edit_note'.format(route_prefix),
                            permission='people_profile.edit_note')

            # delete note
            config.add_tailbone_permission('people_profile', 'people_profile.delete_note',
                                           "Delete {} Note records".format(model_title))
            config.add_route('{}.profile_delete_note'.format(route_prefix), '{}/{{{}}}/profile/delete-note'.format(url_prefix, model_key),
                             request_method='POST')
            config.add_view(cls, attr='profile_delete_note', route_name='{}.profile_delete_note'.format(route_prefix),
                            permission='people_profile.delete_note')

        # make user for person
        config.add_route('{}.make_user'.format(route_prefix), '{}/make-user'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='make_user', route_name='{}.make_user'.format(route_prefix),
                        permission='users.create')

        # merge requests
        if cls.mergeable:
            config.add_tailbone_permission(permission_prefix, '{}.request_merge'.format(permission_prefix),
                                           "Request merge for 2 {}".format(model_title_plural))
            config.add_route('{}.request_merge'.format(route_prefix), '{}/request-merge'.format(url_prefix),
                             request_method='POST')
            config.add_view(cls, attr='request_merge', route_name='{}.request_merge'.format(route_prefix),
                            permission='{}.request_merge'.format(permission_prefix))


class PersonNoteView(MasterView):
    """
    Master view for the PersonNote class.
    """
    model_class = model.PersonNote
    route_prefix = 'person_notes'
    url_prefix = '/people/notes'
    has_versions = True

    grid_columns = [
        'person',
        'type',
        'subject',
        'created',
        'created_by',
    ]

    form_fields = [
        'person',
        'type',
        'subject',
        'text',
        'created',
        'created_by',
    ]

    def get_instance_title(self, note):
        return note.subject or "(no subject)"

    def configure_grid(self, g):
        super(PersonNoteView, self).configure_grid(g)

        # person
        g.set_joiner('person', lambda q: q.join(model.Person,
                                                model.Person.uuid == model.PersonNote.parent_uuid))
        g.set_sorter('person', model.Person.display_name)
        g.set_filter('person', model.Person.display_name, label="Person Name")

        # created_by
        CreatorPerson = orm.aliased(model.Person)
        g.set_joiner('created_by', lambda q: q.join(model.User).outerjoin(CreatorPerson,
                                                                          CreatorPerson.uuid == model.User.person_uuid))
        g.set_sorter('created_by', CreatorPerson.display_name)

        g.set_sort_defaults('created', 'desc')

        g.set_link('person')
        g.set_link('subject')
        g.set_link('created')

    def configure_form(self, f):
        super(PersonNoteView, self).configure_form(f)

        # person
        f.set_readonly('person')
        f.set_renderer('person', self.render_person)

        # created
        f.set_readonly('created')

        # created_by
        f.set_readonly('created_by')
        f.set_renderer('created_by', self.render_user)


@colander.deferred
def valid_note_uuid(node, kw):
    session = kw['session']
    person_uuid = kw['person_uuid']
    def validate(node, value):
        note = session.query(model.PersonNote).get(value)
        if not note:
            raise colander.Invalid(node, "Note not found")
        if note.person.uuid != person_uuid:
            raise colander.Invalid(node, "Note is for the wrong person")
        return note.uuid
    return validate


class NoteSchema(colander.Schema):

    uuid = colander.SchemaNode(colander.String(),
                               validator=valid_note_uuid)

    note_type = colander.SchemaNode(colander.String())

    note_subject = colander.SchemaNode(colander.String(), missing='')

    note_text = colander.SchemaNode(colander.String(), missing='')


class MergePeopleRequestView(MasterView):
    """
    Master view for the MergePeopleRequest class.
    """
    model_class = model.MergePeopleRequest
    route_prefix = 'people_merge_requests'
    url_prefix = '/people/merge-requests'
    creatable = False
    editable = False

    labels = {
        'removing_uuid': "Removing",
        'keeping_uuid': "Keeping",
    }

    grid_columns = [
        'removing_uuid',
        'keeping_uuid',
        'requested',
        'requested_by',
        'merged',
        'merged_by',
    ]

    form_fields = [
        'removing_uuid',
        'keeping_uuid',
        'requested',
        'requested_by',
        'merged',
        'merged_by',
    ]

    def configure_grid(self, g):
        super(MergePeopleRequestView, self).configure_grid(g)

        g.set_renderer('removing_uuid', self.render_referenced_person_name)
        g.set_renderer('keeping_uuid', self.render_referenced_person_name)

        g.filters['merged'].default_active = True
        g.filters['merged'].default_verb = 'is_null'

        g.set_sort_defaults('requested', 'desc')

        g.set_link('removing_uuid')
        g.set_link('keeping_uuid')

    def render_referenced_person_name(self, merge_request, field):
        uuid = getattr(merge_request, field)
        person = self.Session.query(self.model.Person).get(uuid)
        if person:
            return six.text_type(person)
        return "(person not found)"

    def get_instance_title(self, merge_request):
        model = self.model
        removing = self.Session.query(model.Person).get(merge_request.removing_uuid)
        keeping = self.Session.query(model.Person).get(merge_request.keeping_uuid)
        return "{} -> {}".format(
            removing or "(not found)",
            keeping or "(not found)")

    def configure_form(self, f):
        super(MergePeopleRequestView, self).configure_form(f)

        f.set_renderer('removing_uuid', self.render_referenced_person)
        f.set_renderer('keeping_uuid', self.render_referenced_person)

    def render_referenced_person(self, merge_request, field):
        uuid = getattr(merge_request, field)
        person = self.Session.query(self.model.Person).get(uuid)
        if person:
            text = six.text_type(person)
            url = self.request.route_url('people.view', uuid=person.uuid)
            return tags.link_to(text, url)
        return "(person not found)"


def includeme(config):
    PersonView.defaults(config)
    PersonNoteView.defaults(config)
    MergePeopleRequestView.defaults(config)
