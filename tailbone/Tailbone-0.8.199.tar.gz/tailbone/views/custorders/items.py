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
Customer order item views
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
from sqlalchemy import orm

from rattail.db import model
from rattail.time import localtime

from webhelpers2.html import HTML, tags

from tailbone.views import MasterView
from tailbone.util import raw_datetime


class CustomerOrderItemView(MasterView):
    """
    Master view for customer order items
    """
    model_class = model.CustomerOrderItem
    route_prefix = 'custorders.items'
    url_prefix = '/custorders/items'
    creatable = False
    editable = False
    deletable = False

    labels = {
        'order': "Customer Order",
        'order_id': "Order ID",
        'order_uom': "Order UOM",
        'status_code': "Status",
    }

    grid_columns = [
        'order_id',
        'person',
        'product_brand',
        'product_description',
        'product_size',
        'order_quantity',
        'order_uom',
        'case_quantity',
        'order_created',
        'status_code',
    ]

    has_rows = True
    model_row_class = model.CustomerOrderItemEvent
    rows_title = "Event History"
    rows_filterable = False
    rows_sortable = False
    rows_pageable = False
    rows_viewable = False

    row_grid_columns = [
        'occurred',
        'type_code',
        'user',
        'note',
    ]

    form_fields = [
        'order',
        'sequence',
        'person',
        'product',
        'pending_product',
        'product_brand',
        'product_description',
        'product_size',
        'order_quantity',
        'order_uom',
        'case_quantity',
        'unit_price',
        'total_price',
        'price_needs_confirmation',
        'paid_amount',
        'status_code',
        'notes',
    ]

    def query(self, session):
        return session.query(model.CustomerOrderItem)\
                      .join(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrderItem.order)\
                               .joinedload(model.CustomerOrder.person))

    def configure_grid(self, g):
        super(CustomerOrderItemView, self).configure_grid(g)

        g.set_renderer('order_id', self.render_order_id)

        g.set_joiner('person', lambda q: q.outerjoin(model.Person))

        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            default_active=True, default_verb='contains')

        g.set_sorter('person', model.Person.display_name)
        g.set_sorter('order_created', model.CustomerOrder.created)

        g.set_sort_defaults('order_created', 'desc')

        g.set_type('case_quantity', 'quantity')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')
        g.set_type('total_price', 'currency')
        g.set_type('order_quantity', 'quantity')

        g.set_enum('order_uom', self.enum.UNIT_OF_MEASURE)

        g.set_renderer('person', self.render_person_text)
        g.set_renderer('order_created', self.render_order_created)

        g.set_renderer('status_code', self.render_status_code_column)

        g.set_label('person', "Person Name")
        g.set_label('product_brand', "Brand")
        g.set_label('product_description', "Description")
        g.set_label('product_size', "Size")

        g.set_link('order_id')
        g.set_link('person')
        g.set_link('product_brand')
        g.set_link('product_description')

    def render_order_id(self, item, field):
        return item.order.id

    def render_person_text(self, item, field):
        person = item.order.person
        if person:
            text = six.text_type(person)
            return text

    def render_order_created(self, item, column):
        value = localtime(self.rattail_config, item.order.created, from_utc=True)
        return raw_datetime(self.rattail_config, value)

    def render_status_code_column(self, item, field):
        text = self.enum.CUSTORDER_ITEM_STATUS.get(item.status_code,
                                                   six.text_type(item.status_code))
        if item.status_text:
            return HTML.tag('span', title=item.status_text, c=[text])
        return text

    def configure_form(self, f):
        super(CustomerOrderItemView, self).configure_form(f)
        use_buefy = self.get_use_buefy()
        item = f.model_instance

        # order
        f.set_renderer('order', self.render_order)

        # (pending) product
        f.set_renderer('product', self.render_product)
        f.set_renderer('pending_product', self.render_pending_product)
        if self.viewing:
            if item.product and not item.pending_product:
                f.remove('pending_product')
            elif item.pending_product and not item.product:
                f.remove('product')

        # product uom
        f.set_enum('product_unit_of_measure', self.enum.UNIT_OF_MEASURE)

        # highlight pending fields
        f.set_renderer('product_brand', self.highlight_pending_field)
        f.set_renderer('product_description', self.highlight_pending_field)
        f.set_renderer('product_size', self.highlight_pending_field)
        f.set_renderer('case_quantity', self.highlight_pending_field_quantity)

        'unit_price',
        'total_price',
        'price_needs_confirmation',
        'paid_amount',
        'status_code',
        'notes',

        # quantity fields
        f.set_type('cases_ordered', 'quantity')
        f.set_type('units_ordered', 'quantity')
        f.set_type('order_quantity', 'quantity')
        f.set_enum('order_uom', self.enum.UNIT_OF_MEASURE)

        # price fields
        f.set_renderer('unit_price', self.render_price_with_confirmation)
        f.set_renderer('total_price', self.render_price_with_confirmation)
        f.set_renderer('price_needs_confirmation', self.render_price_needs_confirmation)
        f.set_type('paid_amount', 'currency')

        # person
        f.set_renderer('person', self.render_person)

        # status_code
        f.set_renderer('status_code', self.render_status_code)

        # notes
        if use_buefy:
            f.set_renderer('notes', self.render_notes)
        else:
            f.remove('notes')

    def highlight_pending_field(self, item, field, value=None):
        if value is None:
            value = getattr(item, field)
        if not item.product_uuid and item.pending_product_uuid:
            return HTML.tag('span', c=[value],
                            class_='has-text-success')
        return value

    def highlight_pending_field_quantity(self, item, field):
        app = self.get_rattail_app()
        value = getattr(item, field)
        value = app.render_quantity(value)
        return self.highlight_pending_field(item, field, value)

    def render_price_with_confirmation(self, item, field):
        price = getattr(item, field)
        app = self.get_rattail_app()
        text = app.render_currency(price)
        if not item.product_uuid and item.pending_product_uuid:
            text = HTML.tag('span', c=[text],
                            class_='has-text-success')
        if item.price_needs_confirmation:
            return HTML.tag('span', class_='has-background-warning',
                            c=[text])
        return text

    def render_price_needs_confirmation(self, item, field):

        value = item.price_needs_confirmation
        text = "Yes" if value else "No"
        items = [text]

        if value and self.has_perm('confirm_price'):
            button = HTML.tag('b-button', type='is-primary', c="Confirm Price",
                              style='margin-left: 1rem;',
                              icon_pack='fas', icon_left='check',
                              **{'@click': "$emit('confirm-price')"})
            items.append(button)

        left = HTML.tag('div', class_='level-left', c=items)
        outer = HTML.tag('div', class_='level', c=[left])
        return outer

    def render_status_code(self, item, field):
        use_buefy = self.get_use_buefy()
        text = self.enum.CUSTORDER_ITEM_STATUS[item.status_code]
        if item.status_text:
            text = "{} ({})".format(text, item.status_text)
        items = [HTML.tag('span', c=[text])]

        if use_buefy and self.has_perm('change_status'):
            button = HTML.tag('b-button', type='is-primary', c="Change Status",
                              style='margin-left: 1rem;',
                              icon_pack='fas', icon_left='edit',
                              **{'@click': "$emit('change-status')"})
            items.append(button)

        left = HTML.tag('div', class_='level-left', c=items)
        outer = HTML.tag('div', class_='level', c=[left])
        return outer

    def render_notes(self, item, field):
        route_prefix = self.get_route_prefix()

        factory = self.get_grid_factory()
        g = factory(
            key='{}.notes'.format(route_prefix),
            data=[],
            columns=[
                'text',
                'created_by',
                'created',
            ],
            labels={
                'text': "Note",
            },
        )

        table = HTML.literal(
            g.render_buefy_table_element(data_prop='notesData'))
        elements = [table]

        if self.has_perm('add_note'):
            button = HTML.tag('b-button', type='is-primary', c="Add Note",
                              class_='is-pulled-right',
                              icon_pack='fas', icon_left='plus',
                              **{'@click': "$emit('add-note')"})
            button_wrapper = HTML.tag('div', c=[button],
                                      style='margin-top: 0.5rem;')
            elements.append(button_wrapper)

        return HTML.tag('div',
                        style='display: flex; flex-direction: column;',
                        c=elements)

    def template_kwargs_view(self, **kwargs):
        kwargs = super(CustomerOrderItemView, self).template_kwargs_view(**kwargs)
        app = self.get_rattail_app()
        item = kwargs['instance']

        # fetch notes for current item
        kwargs['notes_data'] = self.get_context_notes(item)

        # fetch "other" order items, siblings of current one
        order = item.order
        other_items = self.Session.query(model.CustomerOrderItem)\
                                  .filter(model.CustomerOrderItem.order == order)\
                                  .filter(model.CustomerOrderItem.uuid != item.uuid)\
                                  .all()
        other_data = []
        for other in other_items:

            order_date = None
            if order.created:
                order_date = localtime(self.rattail_config, order.created, from_utc=True).date()

            other_data.append({
                'uuid': other.uuid,
                'brand_name': other.product_brand,
                'product_description': other.product_description,
                'product_case_quantity': app.render_quantity(other.case_quantity),
                'order_quantity': app.render_quantity(other.order_quantity),
                'order_uom': self.enum.UNIT_OF_MEASURE[other.order_uom],
                'department_name': other.department_name,
                'product_barcode': other.product_upc.pretty() if other.product_upc else None,
                'unit_price': app.render_currency(other.unit_price),
                'total_price': app.render_currency(other.total_price),
                'order_date': app.render_date(order_date),
                'status_code': self.enum.CUSTORDER_ITEM_STATUS[other.status_code],
            })
        kwargs['other_order_items_data'] = other_data

        return kwargs

    def get_context_notes(self, item):
        notes = []
        for note in reversed(item.notes):
            created = localtime(self.rattail_config, note.created, from_utc=True)
            notes.append({
                'created': raw_datetime(self.rattail_config, created),
                'created_by': note.created_by.display_name,
                'text': note.text,
            })
        return notes

    def confirm_price(self):
        """
        View for confirming price of an order item.
        """
        item = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', item))

        # locate user responsible for change
        user = self.request.user

        # grab user-provided note to attach to event
        note = self.request.POST.get('note')

        # declare item no longer in need of price confirmation
        item.price_needs_confirmation = False
        item.add_event(self.enum.CUSTORDER_ITEM_EVENT_PRICE_CONFIRMED,
                       user, note=note)

        # advance item to next status
        if item.status_code == self.enum.CUSTORDER_ITEM_STATUS_INITIATED:
            item.status_code = self.enum.CUSTORDER_ITEM_STATUS_READY
            item.status_text = "price has been confirmed"

        self.request.session.flash("Price has been confirmed.")
        return redirect

    def change_status(self):
        """
        View for changing status of one or more order items.
        """
        order_item = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', order_item))

        # validate new status
        new_status_code = int(self.request.POST['new_status_code'])
        if new_status_code not in self.enum.CUSTORDER_ITEM_STATUS:
            self.request.session.flash("Invalid status code", 'error')
            return redirect

        # locate order items to which new status will be applied
        order_items = [order_item]
        uuids = self.request.POST['uuids']
        if uuids:
            for uuid in uuids.split(','):
                item = self.Session.query(model.CustomerOrderItem).get(uuid)
                if item:
                    order_items.append(item)

        # locate user responsible for change
        user = self.request.user

        # maybe grab extra user-provided note to attach
        extra_note = self.request.POST.get('note')

        # apply new status to order item(s)
        for item in order_items:
            if item.status_code != new_status_code:

                # attach event
                note = "status changed from \"{}\" to \"{}\"".format(
                    self.enum.CUSTORDER_ITEM_STATUS[item.status_code],
                    self.enum.CUSTORDER_ITEM_STATUS[new_status_code])
                if extra_note:
                    note = "{} - NOTE: {}".format(note, extra_note)
                item.events.append(model.CustomerOrderItemEvent(
                    type_code=self.enum.CUSTORDER_ITEM_EVENT_STATUS_CHANGE,
                    user=user, note=note))

                # change status
                item.status_code = new_status_code
                # nb. must blank this out, b/c user cannot specify new
                # text and the old text no longer applies
                item.status_text = None

        self.request.session.flash("Status has been updated to: {}".format(
            self.enum.CUSTORDER_ITEM_STATUS[new_status_code]))
        return redirect

    def add_note(self):
        """
        View for adding a new note to current order item, optinally
        also adding it to all other items under the parent order.
        """
        order_item = self.get_instance()
        data = self.request.json_body
        new_note = data['note']
        apply_all = data['apply_all'] == True
        user = self.request.user

        if apply_all:
            order_items = order_item.order.items
        else:
            order_items = [order_item]

        for item in order_items:
            item.notes.append(model.CustomerOrderItemNote(
                created_by=user, text=new_note))

            # # attach event
            # item.events.append(model.CustomerOrderItemEvent(
            #     type_code=self.enum.CUSTORDER_ITEM_EVENT_ADDED_NOTE,
            #     user=user, note=new_note))

        self.Session.flush()
        self.Session.refresh(order_item)
        return {'success': True,
                'notes': self.get_context_notes(order_item)}

    def render_order(self, item, field):
        order = item.order
        if not order:
            return ""
        text = six.text_type(order)
        url = self.request.route_url('custorders.view', uuid=order.uuid)
        return tags.link_to(text, url)

    def render_person(self, item, field):
        person = item.order.person
        if person:
            text = six.text_type(person)
            url = self.request.route_url('people.view', uuid=person.uuid)
            return tags.link_to(text, url)

    def get_row_data(self, item):
        return self.Session.query(model.CustomerOrderItemEvent)\
                           .filter(model.CustomerOrderItemEvent.item == item)\
                           .order_by(model.CustomerOrderItemEvent.occurred.desc(),
                                     model.CustomerOrderItemEvent.type_code)

    def configure_row_grid(self, g):
        super(CustomerOrderItemView, self).configure_row_grid(g)

        g.set_enum('type_code', self.enum.CUSTORDER_ITEM_EVENT)

        g.set_label('occurred', "When")
        g.set_label('type_code', "What") # TODO: enum renderer
        g.set_label('user', "Who")
        g.set_label('note', "Notes")

    @classmethod
    def defaults(cls, config):
        cls._order_item_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_item_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix permission group name
        config.add_tailbone_permission_group(permission_prefix, model_title_plural)

        # confirm price
        config.add_tailbone_permission(permission_prefix,
                                       '{}.confirm_price'.format(permission_prefix),
                                       "Confirm price for a {}".format(model_title))
        config.add_route('{}.confirm_price'.format(route_prefix),
                         '{}/confirm-price'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='confirm_price',
                        route_name='{}.confirm_price'.format(route_prefix),
                        permission='{}.confirm_price'.format(permission_prefix))

        # change status
        config.add_tailbone_permission(permission_prefix,
                                       '{}.change_status'.format(permission_prefix),
                                       "Change status for 1 or more {}".format(model_title_plural))
        config.add_route('{}.change_status'.format(route_prefix),
                         '{}/change-status'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='change_status',
                        route_name='{}.change_status'.format(route_prefix),
                        permission='{}.change_status'.format(permission_prefix))

        # add note
        config.add_tailbone_permission(permission_prefix,
                                       '{}.add_note'.format(permission_prefix),
                                       "Add arbitrary notes for {}".format(model_title_plural))
        config.add_route('{}.add_note'.format(route_prefix),
                         '{}/add-note'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='add_note',
                        route_name='{}.add_note'.format(route_prefix),
                        renderer='json',
                        permission='{}.add_note'.format(permission_prefix))


# TODO: deprecate / remove this
CustomerOrderItemsView = CustomerOrderItemView


def includeme(config):
    CustomerOrderItemView.defaults(config)
