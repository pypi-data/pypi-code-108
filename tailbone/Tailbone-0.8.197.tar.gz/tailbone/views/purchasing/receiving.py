# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Views for 'receiving' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import re
import decimal
import logging

import six
import humanize
import sqlalchemy as sa

from rattail import pod
from rattail.db import model, Session as RattailSession
from rattail.time import localtime, make_utc
from rattail.util import pretty_quantity, prettify, OrderedDict, simple_error
from rattail.threads import Thread

import colander
from deform import widget as dfwidget
from pyramid import httpexceptions
from webhelpers2.html import tags, HTML

from tailbone import forms, grids
from tailbone.views.purchasing import PurchasingBatchView


log = logging.getLogger(__name__)

POSSIBLE_RECEIVING_MODES = [
    'received',
    'damaged',
    'expired',
    # 'mispick',
    'missing',
]

POSSIBLE_CREDIT_TYPES = [
    'damaged',
    'expired',
    # 'mispick',
    'missing',
]


class ReceivingBatchView(PurchasingBatchView):
    """
    Master view for receiving batches
    """
    route_prefix = 'receiving'
    url_prefix = '/receiving'
    model_title = "Receiving Batch"
    model_title_plural = "Receiving Batches"
    index_title = "Receiving"
    downloadable = True
    bulk_deletable = True
    configurable = True
    config_title = "Receiving"

    rows_editable = False
    rows_editable_but_not_directly = True
    rows_deletable = True

    default_uom_is_case = True

    purchase_order_fieldname = 'purchase'

    labels = {
        'truck_dump_batch': "Truck Dump Parent",
        'invoice_parser_key': "Invoice Parser",
    }

    grid_columns = [
        'id',
        'vendor',
        'truck_dump',
        'description',
        'department',
        'date_ordered',
        'created',
        'created_by',
        'rowcount',
        'invoice_total_calculated',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'batch_type',           # TODO: ideally would get rid of this one
        'store',
        'vendor',
        'receiving_workflow',
        'description',
        'truck_dump',
        'truck_dump_children_first',
        'truck_dump_children',
        'truck_dump_ready',
        'truck_dump_batch',
        'invoice_file',
        'invoice_parser_key',
        'department',
        'purchase',
        'vendor_email',
        'vendor_fax',
        'vendor_contact',
        'vendor_phone',
        'date_ordered',
        'date_received',
        'po_number',
        'po_total',
        'invoice_date',
        'invoice_number',
        'invoice_total',
        'invoice_total_calculated',
        'notes',
        'created',
        'created_by',
        'status_code',
        'truck_dump_status',
        'rowcount',
        'order_quantities_known',
        'receiving_complete',
        'complete',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        # 'item_id',
        'vendor_code',
        'brand_name',
        'description',
        'size',
        'department_name',
        'cases_shipped',
        'units_shipped',
        'cases_received',
        'units_received',
        'catalog_unit_cost',
        'po_unit_cost',
        'invoice_unit_cost',
        'invoice_total_calculated',
        'credits',
        'status_code',
        'truck_dump_status',
    ]

    row_form_fields = [
        'sequence',
        'item_entry',
        'upc',
        'item_id',
        'vendor_code',
        'product',
        'brand_name',
        'description',
        'size',
        'case_quantity',
        'ordered',
        'cases_ordered',
        'units_ordered',
        'shipped',
        'cases_shipped',
        'units_shipped',
        'received',
        'cases_received',
        'units_received',
        'damaged',
        'cases_damaged',
        'units_damaged',
        'expired',
        'cases_expired',
        'units_expired',
        'mispick',
        'cases_mispick',
        'units_mispick',
        'missing',
        'cases_missing',
        'units_missing',
        'catalog_unit_cost',
        'po_line_number',
        'po_unit_cost',
        'po_case_size',
        'po_total',
        'invoice_line_number',
        'invoice_unit_cost',
        'invoice_cost_confirmed',
        'invoice_case_size',
        'invoice_total',
        'invoice_total_calculated',
        'status_code',
        'truck_dump_status',
        'claims',
        'credits',
    ]

    # convenience list of all quantity attributes involved for a truck dump claim
    claim_keys = [
        'cases_received',
        'units_received',
        'cases_damaged',
        'units_damaged',
        'cases_expired',
        'units_expired',
    ]

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_RECEIVING

    def configure_grid(self, g):
        super(ReceivingBatchView, self).configure_grid(g)

        if not self.handler.allow_truck_dump_receiving():
            g.remove('truck_dump')

    def create(self, form=None, **kwargs):
        """
        Custom view for creating a new receiving batch.  We split the process
        into two steps, 1) choose and 2) create.  This is because the specific
        form details for creating a batch will depend on which "type" of batch
        creation is to be done, and it's much easier to keep conditional logic
        for that in the server instead of client-side etc.

        See also
        :meth:`tailbone.views.purchasing.costing:CostingBatchView.create()`
        which uses similar logic.
        """
        route_prefix = self.get_route_prefix()
        workflows = self.handler.supported_receiving_workflows()
        valid_workflows = [workflow['workflow_key']
                           for workflow in workflows]

        # if user has already identified their desired workflow, then we can
        # just farm out to the default logic.  we will of course configure our
        # form differently, based on workflow, but this create() method at
        # least will not need customization for that.
        if self.request.matched_route.name.endswith('create_workflow'):

            # however we do have one more thing to check - the workflow
            # requested must of course be valid!
            workflow_key = self.request.matchdict['workflow_key']
            if workflow_key not in valid_workflows:
                self.request.session.flash(
                    "Not a supported workflow: {}".format(workflow_key),
                    'error')
                raise self.redirect(self.request.route_url('{}.create'.format(route_prefix)))

            # okay now do the normal thing, per workflow
            return super(ReceivingBatchView, self).create(**kwargs)

        # on the other hand, if caller provided a form, that means we are in
        # the middle of some other custom workflow, e.g. "add child to truck
        # dump parent" or some such.  in which case we also defer to the normal
        # logic, so as to not interfere with that.
        if form:
            return super(ReceivingBatchView, self).create(form=form, **kwargs)

        # okay, at this point we need the user to select a vendor and workflow
        self.creating = True
        use_buefy = self.get_use_buefy()
        context = {}

        # form to accept user choice of vendor/workflow
        schema = NewReceivingBatch().bind(valid_workflows=valid_workflows)
        form = forms.Form(schema=schema, request=self.request,
                          use_buefy=use_buefy)

        # configure vendor field
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()
        use_dropdown = vendor_handler.choice_uses_dropdown()
        if use_dropdown:
            vendors = self.Session.query(model.Vendor)\
                                  .order_by(model.Vendor.id)
            vendor_values = [(vendor.uuid, "({}) {}".format(vendor.id, vendor.name))
                             for vendor in vendors]
            if use_buefy:
                form.set_widget('vendor', dfwidget.SelectWidget(values=vendor_values))
            else:
                form.set_widget('vendor', forms.widgets.JQuerySelectWidget(values=vendor_values))
        else:
            vendor_display = ""
            if self.request.method == 'POST':
                if self.request.POST.get('vendor'):
                    vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor'])
                    if vendor:
                        vendor_display = six.text_type(vendor)
            vendors_url = self.request.route_url('vendors.autocomplete')
            form.set_widget('vendor', forms.widgets.JQueryAutocompleteWidget(
                field_display=vendor_display, service_url=vendors_url))

        # configure workflow field
        values = [(workflow['workflow_key'], workflow['display'])
                  for workflow in workflows]
        if use_buefy:
            form.set_widget('workflow',
                            dfwidget.SelectWidget(values=values))
        else:
            form.set_widget('workflow',
                            forms.widgets.JQuerySelectWidget(values=values))
        if len(workflows) == 1:
            form.set_default('workflow', workflows[0]['workflow_key'])

        form.submit_label = "Continue"
        form.cancel_url = self.get_index_url()

        # if form validates, that means user has chosen a creation type, so we
        # just redirect to the appropriate "new batch of type X" page
        if form.validate(newstyle=True):
            workflow_key = form.validated['workflow']
            vendor_uuid = form.validated['vendor']
            url = self.request.route_url('{}.create_workflow'.format(route_prefix),
                                         workflow_key=workflow_key,
                                         vendor_uuid=vendor_uuid)
            raise self.redirect(url)

        context['form'] = form
        if hasattr(form, 'make_deform_form'):
            context['dform'] = form.make_deform_form()
        return self.render_to_response('create', context)

    def row_deletable(self, row):

        # first run it through the normal logic, if that doesn't like
        # it then we won't either
        if not super(ReceivingBatchView, self).row_deletable(row):
            return False

        batch = row.batch

        # can always delete rows from truck dump parent
        if batch.is_truck_dump_parent():
            return True

        # can always delete rows from truck dump child
        elif batch.is_truck_dump_child():
            return True

        else: # okay, normal batch
            if batch.order_quantities_known:
                return False
            else: # allow delete if receiving rom scratch
                return True

        # cannot delete row by default
        return False

    def get_instance_title(self, batch):
        title = super(ReceivingBatchView, self).get_instance_title(batch)
        if batch.is_truck_dump_parent():
            title = "{} (TRUCK DUMP PARENT)".format(title)
        elif batch.is_truck_dump_child():
            title = "{} (TRUCK DUMP CHILD)".format(title)
        return title

    def configure_form(self, f):
        super(ReceivingBatchView, self).configure_form(f)
        model = self.model
        batch = f.model_instance
        allow_truck_dump = self.batch_handler.allow_truck_dump_receiving()
        workflow = self.request.matchdict.get('workflow_key')
        route_prefix = self.get_route_prefix()
        use_buefy = self.get_use_buefy()

        # tweak some things if we are in "step 2" of creating new batch
        if self.creating and workflow:

            # display vendor but do not allow changing
            vendor = self.Session.query(model.Vendor).get(
                self.request.matchdict['vendor_uuid'])
            assert vendor
            f.set_readonly('vendor_uuid')
            f.set_default('vendor_uuid', six.text_type(vendor))

            # cancel should take us back to choosing a workflow
            f.cancel_url = self.request.route_url('{}.create'.format(route_prefix))

        # receiving_workflow
        if self.creating and workflow:
            f.set_readonly('receiving_workflow')
            f.set_renderer('receiving_workflow', self.render_receiving_workflow)
        else:
            f.remove('receiving_workflow')

        # batch_type
        if self.creating:
            f.set_widget('batch_type', dfwidget.HiddenWidget())
            f.set_default('batch_type', workflow)
            f.set_hidden('batch_type')
        else:
            f.remove_field('batch_type')

        # truck_dump*
        if allow_truck_dump:

            # truck_dump
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump')
            else:
                f.set_readonly('truck_dump')

            # truck_dump_children_first
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump_children_first')

            # truck_dump_children
            if self.viewing and batch.is_truck_dump_parent():
                f.set_renderer('truck_dump_children', self.render_truck_dump_children)
            else:
                f.remove_field('truck_dump_children')

            # truck_dump_ready
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump_ready')

            # truck_dump_status
            if self.creating or not batch.is_truck_dump_parent():
                f.remove_field('truck_dump_status')
            else:
                f.set_readonly('truck_dump_status')
                f.set_enum('truck_dump_status', model.PurchaseBatch.STATUS)

            # truck_dump_batch
            if self.creating:
                f.replace('truck_dump_batch', 'truck_dump_batch_uuid')
                batches = self.Session.query(model.PurchaseBatch)\
                                      .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)\
                                      .filter(model.PurchaseBatch.truck_dump == True)\
                                      .filter(model.PurchaseBatch.complete == True)\
                                      .filter(model.PurchaseBatch.executed == None)\
                                      .order_by(model.PurchaseBatch.id)
                batch_values = [(b.uuid, "({}) {}, {}".format(b.id_str, b.date_received, b.vendor))
                                for b in batches]
                batch_values.insert(0, ('', "(please choose)"))
                f.set_widget('truck_dump_batch_uuid', forms.widgets.JQuerySelectWidget(values=batch_values))
                f.set_label('truck_dump_batch_uuid', "Truck Dump Parent")
            elif batch.is_truck_dump_child():
                f.set_readonly('truck_dump_batch')
                f.set_renderer('truck_dump_batch', self.render_truck_dump_batch)
            else:
                f.remove_field('truck_dump_batch')

            # truck_dump_vendor
            if self.creating:
                f.set_label('truck_dump_vendor', "Vendor")
                f.set_readonly('truck_dump_vendor')
                f.set_renderer('truck_dump_vendor', self.render_truck_dump_vendor)

        else:
            f.remove_fields('truck_dump',
                            'truck_dump_children_first',
                            'truck_dump_children',
                            'truck_dump_ready',
                            'truck_dump_status',
                            'truck_dump_batch')

        # store
        if self.creating:
            store = self.rattail_config.get_store(self.Session())
            f.set_default('store_uuid', store.uuid)
            # TODO: seems like set_hidden() should also set HiddenWidget
            f.set_hidden('store_uuid')
            f.set_widget('store_uuid', dfwidget.HiddenWidget())

        # purchase
        if (self.creating and workflow in ('from_po', 'from_po_with_invoice')
            and self.purchase_order_fieldname == 'purchase'):
            if use_buefy:
                f.replace('purchase', 'purchase_uuid')
                purchases = self.batch_handler.get_eligible_purchases(
                    vendor, self.enum.PURCHASE_BATCH_MODE_RECEIVING)
                values = [(p.uuid, self.batch_handler.render_eligible_purchase(p))
                          for p in purchases]
                f.set_widget('purchase_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('purchase_uuid', "Purchase Order")
                f.set_required('purchase_uuid')
        else:
            f.remove_field('purchase')

        # department
        if self.creating:
            f.remove_field('department_uuid')

        # order_quantities_known
        if not self.editing:
            f.remove_field('order_quantities_known')

        # invoice totals
        f.set_label('invoice_total', "Invoice Total (Orig.)")
        f.set_label('invoice_total_calculated', "Invoice Total (Calc.)")
        if self.creating:
            f.remove('invoice_total_calculated')

        # hide all invoice fields if batch does not have invoice file
        if not self.creating and not self.batch_handler.has_invoice_file(batch):
            f.remove('invoice_file',
                     'invoice_date',
                     'invoice_number',
                     'invoice_total')

        # receiving_complete
        if self.creating:
            f.remove('receiving_complete')

        # now that all fields are setup, some final tweaks based on workflow
        if self.creating and workflow:

            if workflow == 'from_scratch':
                f.remove('truck_dump_batch_uuid',
                         'invoice_file',
                         'invoice_parser_key')

            elif workflow == 'from_invoice':
                f.set_required('invoice_file')
                f.set_required('invoice_parser_key')
                f.remove('truck_dump_batch_uuid',
                         'po_number',
                         'invoice_date',
                         'invoice_number')

            elif workflow == 'from_po':
                f.remove('truck_dump_batch_uuid',
                         'date_ordered',
                         'po_number',
                         'invoice_file',
                         'invoice_parser_key',
                         'invoice_date',
                         'invoice_number')

            elif workflow == 'from_po_with_invoice':
                f.set_required('invoice_file')
                f.set_required('invoice_parser_key')
                f.remove('truck_dump_batch_uuid',
                         'date_ordered',
                         'po_number',
                         'invoice_date',
                         'invoice_number')

            elif workflow == 'truck_dump_children_first':
                f.remove('truck_dump_batch_uuid',
                         'invoice_file',
                         'invoice_parser_key',
                         'date_ordered',
                         'po_number',
                         'invoice_date',
                         'invoice_number')

            elif workflow == 'truck_dump_children_last':
                f.remove('truck_dump_batch_uuid',
                         'invoice_file',
                         'invoice_parser_key',
                         'date_ordered',
                         'po_number',
                         'invoice_date',
                         'invoice_number')

    def render_receiving_workflow(self, batch, field):
        key = self.request.matchdict['workflow_key']
        info = self.handler.receiving_workflow_info(key)
        if info:
            return info['display']

    def template_kwargs_create(self, **kwargs):
        kwargs = super(ReceivingBatchView, self).template_kwargs_create(**kwargs)
        if self.handler.allow_truck_dump_receiving():
            vmap = {}
            batches = self.Session.query(model.PurchaseBatch)\
                                  .filter(model.PurchaseBatch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING)\
                                  .filter(model.PurchaseBatch.truck_dump == True)\
                                  .filter(model.PurchaseBatch.complete == True)
            for batch in batches:
                vmap[batch.uuid] = batch.vendor_uuid
            kwargs['batch_vendor_map'] = vmap
        return kwargs

    def get_batch_kwargs(self, batch, **kwargs):
        kwargs = super(ReceivingBatchView, self).get_batch_kwargs(batch, **kwargs)
        batch_type = self.request.POST['batch_type']

        # must pull vendor from URL if it was not in form data
        if 'vendor_uuid' not in kwargs and 'vendor' not in kwargs:
            if 'vendor_uuid' in self.request.matchdict:
                kwargs['vendor_uuid'] = self.request.matchdict['vendor_uuid']

        if batch_type == 'from_scratch':
            kwargs.pop('truck_dump_batch', None)
            kwargs.pop('truck_dump_batch_uuid', None)
        elif batch_type == 'from_invoice':
            pass
        elif batch_type == 'from_po':
            # TODO: how to best handle this field?  this doesn't seem flexible
            kwargs['purchase_key'] = batch.purchase_uuid
        elif batch_type == 'from_po_with_invoice':
            # TODO: how to best handle this field?  this doesn't seem flexible
            kwargs['purchase_key'] = batch.purchase_uuid
        elif batch_type == 'truck_dump_children_first':
            kwargs['truck_dump'] = True
            kwargs['truck_dump_children_first'] = True
            kwargs['order_quantities_known'] = True
            # TODO: this makes sense in some cases, but all?
            # (should just omit that field when not relevant)
            kwargs['date_ordered'] = None
        elif batch_type == 'truck_dump_children_last':
            kwargs['truck_dump'] = True
            kwargs['truck_dump_ready'] = True
            # TODO: this makes sense in some cases, but all?
            # (should just omit that field when not relevant)
            kwargs['date_ordered'] = None
        elif batch_type.startswith('truck_dump_child'):
            truck_dump = self.get_instance()
            kwargs['store'] = truck_dump.store
            kwargs['vendor'] = truck_dump.vendor
            kwargs['truck_dump_batch'] = truck_dump
        else:
            raise NotImplementedError
        return kwargs

    def make_po_vs_invoice_breakdown(self, batch):
        """
        Returns a simple breakdown as list of 2-tuples, each of which
        has the display title as first member, and number of rows as
        second member.
        """
        grouped = {}
        labels = OrderedDict([
            ('both', "Found in both PO and Invoice"),
            ('po_not_invoice', "Found in PO but not Invoice"),
            ('invoice_not_po', "Found in Invoice but not PO"),
            ('neither', "Not found in PO nor Invoice"),
        ])

        for row in batch.active_rows():
            if row.po_line_number and not row.invoice_line_number:
                grouped.setdefault('po_not_invoice', []).append(row)
            elif row.invoice_line_number and not row.po_line_number:
                grouped.setdefault('invoice_not_po', []).append(row)
            elif row.po_line_number and row.invoice_line_number:
                grouped.setdefault('both', []).append(row)
            else:
                grouped.setdefault('neither', []).append(row)

        breakdown = []

        for key, label in labels.items():
            if key in grouped:
                breakdown.append({
                    'title': label,
                    'count': len(grouped[key]),
                })

        return breakdown

    def template_kwargs_view(self, **kwargs):
        kwargs = super(ReceivingBatchView, self).template_kwargs_view(**kwargs)
        batch = kwargs['instance']

        if self.handler.has_purchase_order(batch) and self.handler.has_invoice_file(batch):
            breakdown = self.make_po_vs_invoice_breakdown(batch)

            factory = self.get_grid_factory()
            kwargs['po_vs_invoice_breakdown_grid'] = factory(
                'batch_po_vs_invoice_breakdown',
                data=breakdown,
                columns=['title', 'count'])

        return kwargs

    def get_context_credits(self, row):
        app = self.get_rattail_app()
        credits_data = []
        for credit in row.credits:
            credits_data.append({
                'uuid': credit.uuid,
                'credit_type': credit.credit_type,
                'expiration_date': six.text_type(credit.expiration_date) if credit.expiration_date else None,
                'cases_shorted': app.render_quantity(credit.cases_shorted),
                'units_shorted': app.render_quantity(credit.units_shorted),
                'shorted': app.render_cases_units(credit.cases_shorted,
                                                  credit.units_shorted),
                'credit_total': app.render_currency(credit.credit_total),
                'mispick_upc': '-',
                'mispick_brand_name': '-',
                'mispick_description': '-',
                'mispick_size': '-',
            })
        return credits_data

    def template_kwargs_view_row(self, **kwargs):
        kwargs = super(ReceivingBatchView, self).template_kwargs_view_row(**kwargs)
        use_buefy = self.get_use_buefy()
        app = self.get_rattail_app()
        products_handler = app.get_products_handler()
        row = kwargs['instance']

        if row.product:
            kwargs['image_url'] = products_handler.get_image_url(row.product)
        elif row.upc:
            kwargs['image_url'] = products_handler.get_image_url(upc=row.upc)

        if use_buefy:
            kwargs['row_context'] = self.get_context_row(row)
            kwargs['possible_receiving_modes'] = POSSIBLE_RECEIVING_MODES
            kwargs['possible_credit_types'] = POSSIBLE_CREDIT_TYPES

        return kwargs

    def department_for_purchase(self, purchase):
        pass

    def delete_instance(self, batch):
        """
        Delete all data (files etc.) for the batch.
        """
        truck_dump = batch.truck_dump_batch
        if batch.is_truck_dump_parent():
            for child in batch.truck_dump_children:
                self.delete_instance(child)
        super(ReceivingBatchView, self).delete_instance(batch)
        if truck_dump:
            self.handler.refresh(truck_dump)

    def render_truck_dump_batch(self, batch, field):
        truck_dump = batch.truck_dump_batch
        if not truck_dump:
            return ""
        text = "({}) {}".format(truck_dump.id_str, truck_dump.description or '')
        url = self.request.route_url('receiving.view', uuid=truck_dump.uuid)
        return tags.link_to(text, url)

    def render_truck_dump_vendor(self, batch, field):
        truck_dump = self.get_instance()
        vendor = truck_dump.vendor
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)

    def render_truck_dump_children(self, batch, field):
        contents = []
        children = batch.truck_dump_children
        if children:
            items = []
            for child in children:
                text = "({}) {}".format(child.id_str, child.description or '')
                url = self.request.route_url('receiving.view', uuid=child.uuid)
                items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
            contents.append(HTML.tag('ul', c=items))
        if not batch.executed and (batch.complete or batch.truck_dump_children_first):
            buttons = self.make_truck_dump_child_buttons(batch)
            if buttons:
                buttons = HTML.literal(' ').join(buttons)
                contents.append(HTML.tag('div', class_='buttons', c=[buttons]))
        if not contents:
            return ""
        return HTML.tag('div', c=contents)

    def make_truck_dump_child_buttons(self, batch):
        return [
            tags.link_to("Add from Invoice File", self.get_action_url('add_child_from_invoice', batch), class_='button autodisable'),
        ]

    def add_child_from_invoice(self):
        """
        View for adding a child batch to a truck dump, from invoice file.
        """
        batch = self.get_instance()
        if not batch.is_truck_dump_parent():
            self.request.session.flash("Batch is not a truck dump: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        if batch.executed:
            self.request.session.flash("Batch has already been executed: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        if not batch.complete and not batch.truck_dump_children_first:
            self.request.session.flash("Batch is not marked as complete: {}".format(batch))
            return self.redirect(self.get_action_url('view', batch))
        self.creating = True
        form = self.make_child_from_invoice_form(self.get_model_class())
        return self.create(form=form)

    def make_child_from_invoice_form(self, instance, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        kwargs['configure'] = self.configure_child_from_invoice_form
        return self.make_form(instance=instance, **kwargs)

    def configure_child_from_invoice_form(self, f):
        assert self.creating
        truck_dump = self.get_instance()

        self.configure_form(f)

        # cancel should go back to truck dump parent
        f.cancel_url = self.get_action_url('view', truck_dump)

        f.set_fields([
            'batch_type',
            'truck_dump_parent',
            'truck_dump_vendor',
            'invoice_file',
            'invoice_parser_key',
            'invoice_number',
            'description',
            'notes',
        ])

        # batch_type
        f.set_widget('batch_type', forms.widgets.ReadonlyWidget())
        f.set_default('batch_type', 'truck_dump_child_from_invoice')
        f.set_hidden('batch_type', False)

        # truck_dump_batch_uuid
        f.set_readonly('truck_dump_parent')
        f.set_renderer('truck_dump_parent', self.render_truck_dump_parent)

        # invoice_parser_key
        f.set_required('invoice_parser_key')

    def render_truck_dump_parent(self, batch, field):
        truck_dump = self.get_instance()
        text = six.text_type(truck_dump)
        url = self.request.route_url('receiving.view', uuid=truck_dump.uuid)
        return tags.link_to(text, url)

    @staticmethod
    @colander.deferred
    def validate_purchase(node, kw):
        session = kw['session']
        def validate(node, value):
            purchase = session.query(model.Purchase).get(value)
            if not purchase:
                raise colander.Invalid(node, "Purchase not found")
            return purchase.uuid
        return validate

    def assign_purchase_order(self, batch, po_form):
        """
        Assign the original purchase order to the given batch.  Default
        behavior assumes a Rattail Purchase object is what we're after.
        """
        purchase = self.handler.assign_purchase_order(
            batch, po_form.validated[self.purchase_order_fieldname],
            session=self.Session())

        department = self.department_for_purchase(purchase)
        if department:
            batch.department_uuid = department.uuid

    def configure_row_grid(self, g):
        super(ReceivingBatchView, self).configure_row_grid(g)
        batch = self.get_instance()

        # vendor_code
        g.filters['vendor_code'].default_active = True
        g.filters['vendor_code'].default_verb = 'contains'

        # catalog_unit_cost
        if (self.handler.has_purchase_order(batch)
            or self.handler.has_invoice_file(batch)):
            g.remove('catalog_unit_cost')

        # po_unit_cost
        if self.handler.has_invoice_file(batch):
            g.remove('po_unit_cost')

        # invoice_unit_cost
        if not self.handler.has_invoice_file(batch):
            g.remove('invoice_unit_cost')

        # credits
        # note that sorting by credits involves a subquery with group by clause.
        # seems likely there may be a better way? but this seems to work fine
        Credits = self.Session.query(model.PurchaseBatchCredit.row_uuid,
                                     sa.func.count().label('credit_count'))\
                              .group_by(model.PurchaseBatchCredit.row_uuid)\
                              .subquery()
        g.set_joiner('credits', lambda q: q.outerjoin(Credits))
        g.sorters['credits'] = lambda q, d: q.order_by(getattr(Credits.c.credit_count, d)())

        # hide 'ordered' columns for truck dump parent, if its "children first"
        # flag is set, since that batch type is only concerned with receiving
        if batch.is_truck_dump_parent() and not batch.truck_dump_children_first:
            g.remove('cases_ordered',
                     'units_ordered')

        # add "Transform to Unit" action, if appropriate
        if batch.is_truck_dump_parent():
            permission_prefix = self.get_permission_prefix()
            if self.request.has_perm('{}.edit_row'.format(permission_prefix)):
                transform = grids.GridAction('transform',
                                             icon='shuffle',
                                             label="Transform to Unit",
                                             url=self.transform_unit_url)
                g.more_actions.append(transform)
                if g.main_actions and g.main_actions[-1].key == 'delete':
                    delete = g.main_actions.pop()
                    g.more_actions.append(delete)

        # truck_dump_status
        if not batch.is_truck_dump_parent():
            g.remove('truck_dump_status')
        else:
            g.set_enum('truck_dump_status', model.PurchaseBatchRow.STATUS)

    def row_grid_extra_class(self, row, i):
        css_class = super(ReceivingBatchView, self).row_grid_extra_class(row, i)

        if row.catalog_cost_confirmed:
            css_class = '{} catalog_cost_confirmed'.format(css_class or '')

        if row.invoice_cost_confirmed:
            css_class = '{} invoice_cost_confirmed'.format(css_class or '')

        return css_class

    def get_row_instance_title(self, row):
        if row.product:
            return six.text_type(row.product)
        if row.upc:
            return row.upc.pretty()
        return super(ReceivingBatchView, self).get_row_instance_title(row)

    def transform_unit_url(self, row, i):
        # grid action is shown only when we return a URL here
        if self.row_editable(row):
            if row.batch.is_truck_dump_parent():
                if row.product and row.product.is_pack_item():
                    return self.get_row_action_url('transform_unit', row)

    def make_row_credits_grid(self, row):

        # first make grid like normal
        g = super(ReceivingBatchView, self).make_row_credits_grid(row)

        if (self.get_use_buefy()
            and self.has_perm('edit_row')
            and self.row_editable(row)):

            # add the Un-Declare action
            g.main_actions.append(self.make_action(
                'remove', label="Un-Declare",
                url='#', icon='trash',
                link_class='has-text-danger',
                click_handler='removeCreditInit(props.row)'))

        return g

    def vuejs_convert_quantity(self, cstruct):
        result = dict(cstruct)
        if result['cases'] is colander.null:
            result['cases'] = None
        elif isinstance(result['cases'], decimal.Decimal):
            result['cases'] = float(result['cases'])
        if result['units'] is colander.null:
            result['units'] = None
        elif isinstance(result['units'], decimal.Decimal):
            result['units'] = float(result['units'])
        return result

    def receive_row(self, **kwargs):
        """
        Primary desktop view for row-level receiving.
        """
        # TODO: this code was largely copied from mobile_receive_row() but it
        # tries to pave the way for shared logic, i.e. where the latter would
        # simply invoke this method and return the result.  however we're not
        # there yet...for now it's only tested for desktop
        self.viewing = True
        use_buefy = self.get_use_buefy()
        row = self.get_row_instance()

        # things are a bit different now w/ buefy support..
        if use_buefy:

            # don't even bother showing this page if that's all the
            # request was about
            if self.request.method == 'GET':
                return self.redirect(self.get_row_action_url('view', row))

            # make sure edit is allowed
            if not (self.has_perm('edit_row') and self.row_editable(row)):
                raise self.forbidden()

            # check for JSON POST, which is submitted via AJAX from
            # the "view row" page
            if self.request.method == 'POST' and not self.request.POST:
                data = self.request.json_body
                kwargs = dict(data)

                # TODO: for some reason quantities can come through as strings?
                cases = kwargs['quantity']['cases']
                if cases is not None:
                    if cases == '':
                        cases = None
                    else:
                        cases = decimal.Decimal(cases)
                kwargs['cases'] = cases
                units = kwargs['quantity']['units']
                if units is not None:
                    if units == '':
                        units = None
                    else:
                        units = decimal.Decimal(units)
                kwargs['units'] = units
                del kwargs['quantity']

                # handler takes care of the receiving logic for us
                try:
                    self.batch_handler.receive_row(row, **kwargs)

                except Exception as error:
                    return self.json_response({'error': six.text_type(error)})

                self.Session.flush()
                self.Session.refresh(row)
                return self.json_response({
                    'ok': True,
                    'row': self.get_context_row(row)})

        batch = row.batch
        permission_prefix = self.get_permission_prefix()
        possible_modes = [
            'received',
            'damaged',
            'expired',
        ]
        context = {
            'row': row,
            'batch': batch,
            'parent_instance': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': self.get_row_image_url(row),
            'allow_expired': self.handler.allow_expired_credits(),
            'allow_cases': self.handler.allow_cases(),
            'quick_receive': False,
            'quick_receive_all': False,
        }

        schema = ReceiveRowForm().bind(session=self.Session())
        form = forms.Form(schema=schema, request=self.request, use_buefy=use_buefy)
        form.cancel_url = self.get_row_action_url('view', row)

        # mode
        mode_values = [(mode, mode) for mode in possible_modes]
        if use_buefy:
            mode_widget = dfwidget.SelectWidget(values=mode_values)
        else:
            mode_widget = forms.widgets.JQuerySelectWidget(values=mode_values)
        form.set_widget('mode', mode_widget)

        # quantity
        form.set_widget('quantity', forms.widgets.CasesUnitsWidget(amount_required=True,
                                                                   one_amount_only=True))
        form.set_vuejs_field_converter('quantity', self.vuejs_convert_quantity)

        # expiration_date
        form.set_type('expiration_date', 'date_jquery')

        # TODO: what is this one about again?
        form.remove_field('quick_receive')

        if form.validate(newstyle=True):

            # handler takes care of the row receiving logic for us
            kwargs = dict(form.validated)
            kwargs['cases'] = kwargs['quantity']['cases']
            kwargs['units'] = kwargs['quantity']['units']
            del kwargs['quantity']
            self.handler.receive_row(row, **kwargs)

            # keep track of last-used uom, although we just track
            # whether or not it was 'CS' since the unit_uom can vary
            # TODO: should this be done for desktop too somehow?
            sticky_case = None
            # if mobile and not form.validated['quick_receive']:
            #     cases = form.validated['cases']
            #     units = form.validated['units']
            #     if cases and not units:
            #         sticky_case = True
            #     elif units and not cases:
            #         sticky_case = False
            if sticky_case is not None:
                self.request.session['tailbone.mobile.receiving.sticky_uom_is_case'] = sticky_case

            return self.redirect(self.get_row_action_url('view', row))

        # unit_uom can vary by product
        context['unit_uom'] = 'LB' if row.product and row.product.weighed else 'EA'

        if context['quick_receive'] and context['quick_receive_all']:
            if context['allow_cases']:
                context['quick_receive_uom'] = 'CS'
                raise NotImplementedError("TODO: add CS support for quick_receive_all")
            else:
                context['quick_receive_uom'] = context['unit_uom']
                accounted_for = self.handler.get_units_accounted_for(row)
                remainder = self.handler.get_units_ordered(row) - accounted_for

                if accounted_for:
                    # some product accounted for; button should receive "remainder" only
                    if remainder:
                        remainder = pretty_quantity(remainder)
                        context['quick_receive_quantity'] = remainder
                        context['quick_receive_text'] = "Receive Remainder ({} {})".format(remainder, context['unit_uom'])
                    else:
                        # unless there is no remainder, in which case disable it
                        context['quick_receive'] = False

                else: # nothing yet accounted for, button should receive "all"
                    if not remainder:
                        raise ValueError("why is remainder empty?")
                    remainder = pretty_quantity(remainder)
                    context['quick_receive_quantity'] = remainder
                    context['quick_receive_text'] = "Receive ALL ({} {})".format(remainder, context['unit_uom'])

        # effective uom can vary in a few ways...the basic default is 'CS' if
        # self.default_uom_is_case is true, otherwise whatever unit_uom is.
        sticky_case = None
        # if mobile:
        #     # TODO: should do this for desktop also, but rename the session variable
        #     sticky_case = self.request.session.get('tailbone.mobile.receiving.sticky_uom_is_case')
        if sticky_case is None:
            context['uom'] = 'CS' if self.default_uom_is_case else context['unit_uom']
        elif sticky_case:
            context['uom'] = 'CS'
        else:
            context['uom'] = context['unit_uom']
        if context['uom'] == 'CS' and row.units_ordered and not row.cases_ordered:
            context['uom'] = context['unit_uom']

        # # TODO: should do this for desktop in addition to mobile?
        # if mobile and batch.order_quantities_known and not row.cases_ordered and not row.units_ordered:
        #     warn = True
        #     if batch.is_truck_dump_parent() and row.product:
        #         uuids = [child.uuid for child in batch.truck_dump_children]
        #         if uuids:
        #             count = self.Session.query(model.PurchaseBatchRow)\
        #                                 .filter(model.PurchaseBatchRow.batch_uuid.in_(uuids))\
        #                                 .filter(model.PurchaseBatchRow.product == row.product)\
        #                                 .count()
        #             if count:
        #                 warn = False
        #     if warn:
        #         self.request.session.flash("This item was NOT on the original purchase order.", 'receiving-warning')

        # # TODO: should do this for desktop in addition to mobile?
        # if mobile:
        #     # maybe alert user if they've already received some of this product
        #     alert_received = self.rattail_config.getbool('tailbone', 'receiving.alert_already_received',
        #                                                  default=False)
        #     if alert_received:
        #         if self.handler.get_units_confirmed(row):
        #             msg = "You have already received some of this product; last update was {}.".format(
        #                 humanize.naturaltime(make_utc() - row.modified))
        #             self.request.session.flash(msg, 'receiving-warning')

        context['form'] = form
        context['dform'] = form.make_deform_form()
        context['parent_url'] = self.get_action_url('view', batch)
        context['parent_title'] = self.get_instance_title(batch)
        return self.render_to_response('receive_row', context)

    def declare_credit(self):
        """
        View for declaring a credit, i.e. converting some "received" or similar
        quantity, to a credit of some sort.
        """
        use_buefy = self.get_use_buefy()
        row = self.get_row_instance()

        # things are a bit different now w/ buefy support..
        if use_buefy:

            # don't even bother showing this page if that's all the
            # request was about
            if self.request.method == 'GET':
                return self.redirect(self.get_row_action_url('view', row))

            # make sure edit is allowed
            if not (self.has_perm('edit_row') and self.row_editable(row)):
                raise self.forbidden()

            # check for JSON POST, which is submitted via AJAX from
            # the "view row" page
            if self.request.method == 'POST' and not self.request.POST:
                data = self.request.json_body
                kwargs = dict(data)

                # TODO: for some reason quantities can come through as strings?
                if kwargs['cases'] is not None:
                    if kwargs['cases'] == '':
                        kwargs['cases'] = None
                    else:
                        kwargs['cases'] = decimal.Decimal(kwargs['cases'])
                if kwargs['units'] is not None:
                    if kwargs['units'] == '':
                        kwargs['units'] = None
                    else:
                        kwargs['units'] = decimal.Decimal(kwargs['units'])

                try:
                    result = self.handler.can_declare_credit(row, **kwargs)

                except Exception as error:
                    return self.json_response({'error': six.text_type(error)})

                else:
                    if result:
                        self.handler.declare_credit(row, **kwargs)

                    else:
                        return self.json_response({
                            'error': "Handler says you can't declare that credit; "
                            "not sure why"})

                self.Session.flush()
                self.Session.refresh(row)
                return self.json_response({
                    'ok': True,
                    'row': self.get_context_row(row)})

        batch = row.batch
        context = {
            'row': row,
            'batch': batch,
            'parent_instance': batch,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'product_image_url': self.get_row_image_url(row),
            'allow_expired': self.handler.allow_expired_credits(),
            'allow_cases': self.handler.allow_cases(),
        }

        schema = DeclareCreditForm()
        form = forms.Form(schema=schema, request=self.request,
                          use_buefy=use_buefy)
        form.cancel_url = self.get_row_action_url('view', row)

        # credit_type
        values = [(m, m) for m in POSSIBLE_CREDIT_TYPES]
        if use_buefy:
            widget = dfwidget.SelectWidget(values=values)
        else:
            widget = forms.widgets.JQuerySelectWidget(values=values)
        form.set_widget('credit_type', widget)

        # quantity
        form.set_widget('quantity', forms.widgets.CasesUnitsWidget(
            amount_required=True, one_amount_only=True))
        form.set_vuejs_field_converter('quantity', self.vuejs_convert_quantity)

        # expiration_date
        form.set_type('expiration_date', 'date_jquery')

        if form.validate(newstyle=True):

            # handler takes care of the row receiving logic for us
            kwargs = dict(form.validated)
            kwargs['cases'] = kwargs['quantity']['cases']
            kwargs['units'] = kwargs['quantity']['units']
            del kwargs['quantity']
            try:
                result = self.handler.can_declare_credit(row, **kwargs)
            except Exception as error:
                self.request.session.flash("Handler says you can't declare that credit: {}".format(error), 'error')
            else:
                if result:
                    self.handler.declare_credit(row, **kwargs)
                    return self.redirect(self.get_row_action_url('view', row))

                self.request.session.flash("Handler says you can't declare that credit; not sure why", 'error')

        context['form'] = form
        context['dform'] = form.make_deform_form()
        context['parent_url'] = self.get_action_url('view', batch)
        context['parent_title'] = self.get_instance_title(batch)
        return self.render_to_response('declare_credit', context)

    def undeclare_credit(self):
        """
        View for un-declaring a credit, i.e. moving the credit amounts
        back into the "received" tally.
        """
        model = self.model
        row = self.get_row_instance()
        data = self.request.json_body

        # make sure edit is allowed
        if not (self.has_perm('edit_row') and self.row_editable(row)):
            raise self.forbidden()

        # figure out which credit to un-declare
        credit = None
        uuid = data.get('uuid')
        if uuid:
            credit = self.Session.query(model.PurchaseBatchCredit).get(uuid)
        if not credit:
            return {'error': "Credit not found"}

        # un-declare it
        self.batch_handler.undeclare_credit(row, credit)
        self.Session.flush()
        self.Session.refresh(row)

        return {'ok': True,
                'row': self.get_context_row(row)}

    def get_context_row(self, row):
        app = self.get_rattail_app()
        return {
            'sequence': row.sequence,
            'case_quantity': float(row.case_quantity) if row.case_quantity is not None else None,
            'ordered': self.render_row_quantity(row, 'ordered'),
            'shipped': self.render_row_quantity(row, 'shipped'),
            'received': self.render_row_quantity(row, 'received'),
            'cases_received': float(row.cases_received) if row.cases_received is not None else None,
            'units_received': float(row.units_received) if row.units_received is not None else None,
            'damaged': self.render_row_quantity(row, 'damaged'),
            'expired': self.render_row_quantity(row, 'expired'),
            'mispick': self.render_row_quantity(row, 'mispick'),
            'missing': self.render_row_quantity(row, 'missing'),
            'credits': self.get_context_credits(row),
            'invoice_total_calculated': app.render_currency(row.invoice_total_calculated),
            'status': row.STATUS[row.status_code],
        }

    def transform_unit_row(self):
        """
        View which transforms the given row, which is assumed to associate with
        a "pack" item, such that it instead associates with the "unit" item,
        with quantities adjusted accordingly.
        """
        batch = self.get_instance()

        row_uuid = self.request.params.get('row_uuid')
        row = self.Session.query(model.PurchaseBatchRow).get(row_uuid) if row_uuid else None
        if row and row.batch is batch and not row.removed:
            pass # we're good
        else:
            if self.request.method == 'POST':
                raise self.notfound()
            return {'error': "Row not found."}

        def normalize(product):
            data = {
                'upc': product.upc,
                'item_id': product.item_id,
                'description': product.description,
                'size': product.size,
                'case_quantity': None,
                'cases_received': row.cases_received,
            }
            cost = product.cost_for_vendor(batch.vendor)
            if cost:
                data['case_quantity'] = cost.case_size
            return data

        if self.request.method == 'POST':
            self.handler.transform_pack_to_unit(row)
            self.request.session.flash("Transformed pack to unit item for: {}".format(row.product))
            return self.redirect(self.get_action_url('view', batch))

        pack_data = normalize(row.product)
        pack_data['units_received'] = row.units_received
        unit_data = normalize(row.product.unit)
        unit_data['units_received'] = None
        if row.units_received:
            unit_data['units_received'] = row.units_received * row.product.pack_size
        diff = self.make_diff(pack_data, unit_data, monospace=True)
        return self.render_to_response('transform_unit_row', {
            'batch': batch,
            'row': row,
            'diff': diff,
        })

    def configure_row_form(self, f):
        super(ReceivingBatchView, self).configure_row_form(f)
        batch = self.get_instance()

        # allow input for certain fields only; all others are readonly
        mutable = [
            'invoice_unit_cost',
        ]
        for name in f.fields:
            if name not in mutable:
                f.set_readonly(name)

        # invoice totals
        f.set_label('invoice_total', "Invoice Total (Orig.)")
        f.set_label('invoice_total_calculated', "Invoice Total (Calc.)")

        # claims
        f.set_readonly('claims')
        if batch.is_truck_dump_parent():
            f.set_renderer('claims', self.render_parent_row_claims)
            f.set_helptext('claims', "Parent row is claimed by these child rows.")
        elif batch.is_truck_dump_child():
            f.set_renderer('claims', self.render_child_row_claims)
            f.set_helptext('claims', "Child row makes claims against these parent rows.")
        else:
            f.remove_field('claims')

        # truck_dump_status
        if self.creating or not batch.is_truck_dump_parent():
            f.remove_field('truck_dump_status')
        else:
            f.set_readonly('truck_dump_status')
            f.set_enum('truck_dump_status', model.PurchaseBatchRow.STATUS)

        # misc. labels
        f.set_label('vendor_code', "Vendor Item Code")

    def render_parent_row_claims(self, row, field):
        items = []
        for claim in row.claims:
            child_row = claim.claiming_row
            child_batch = child_row.batch
            text = child_batch.id_str
            if child_batch.description:
                text = "{} ({})".format(text, child_batch.description)
            text = "{}, row {}".format(text, child_row.sequence)
            url = self.get_row_action_url('view', child_row)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def render_child_row_claims(self, row, field):
        items = []
        for claim in row.truck_dump_claims:
            parent_row = claim.claimed_row
            parent_batch = parent_row.batch
            text = parent_batch.id_str
            if parent_batch.description:
                text = "{} ({})".format(text, parent_batch.description)
            text = "{}, row {}".format(text, parent_row.sequence)
            url = self.get_row_action_url('view', parent_row)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def validate_row_form(self, form):

        # if normal validation fails, stop there
        if not super(ReceivingBatchView, self).validate_row_form(form):
            return False

        # if user is editing row from truck dump child, then we must further
        # validate the form to ensure whatever new amounts they've requested
        # would in fact fall within the bounds of what is available from the
        # truck dump parent batch...
        if self.editing:
            batch = self.get_instance()
            if batch.is_truck_dump_child():
                old_row = self.get_row_instance()
                case_quantity = old_row.case_quantity

                # get all "existing" (old) claim amounts
                old_claims = {}
                for claim in old_row.truck_dump_claims:
                    for key in self.claim_keys:
                        amount = getattr(claim, key)
                        if amount is not None:
                            old_claims[key] = old_claims.get(key, 0) + amount

                # get all "proposed" (new) claim amounts
                new_claims = {}
                for key in self.claim_keys:
                    amount = form.validated[key]
                    if amount is not colander.null and amount is not None:
                        # do not allow user to request a negative claim amount
                        if amount < 0:
                            self.request.session.flash("Cannot claim a negative amount for: {}".format(key), 'error')
                            return False
                        new_claims[key] = amount

                # figure out what changes are actually being requested
                claim_diff = {}
                for key in new_claims:
                    if key not in old_claims:
                        claim_diff[key] = new_claims[key]
                    elif new_claims[key] != old_claims[key]:
                        claim_diff[key] = new_claims[key] - old_claims[key]
                        # do not allow user to request a negative claim amount
                        if claim_diff[key] < (0 - old_claims[key]):
                            self.request.session.flash("Cannot claim a negative amount for: {}".format(key), 'error')
                            return False
                for key in old_claims:
                    if key not in new_claims:
                        claim_diff[key] = 0 - old_claims[key]

                # find all rows from truck dump parent which "may" pertain to child row
                # TODO: perhaps would need to do a more "loose" match on UPC also?
                if not old_row.product_uuid:
                    raise NotImplementedError("Don't (yet) know how to handle edit for row with no product")
                parent_rows = [row for row in batch.truck_dump_batch.active_rows()
                               if row.product_uuid == old_row.product_uuid]

                # NOTE: "confirmed" are the proper amounts which exist in the
                # parent batch.  "claimed" are the amounts claimed by this row.

                # get existing "confirmed" and "claimed" amounts for all
                # (possibly related) truck dump parent rows
                confirmed = {}
                claimed = {}
                for parent_row in parent_rows:
                    for key in self.claim_keys:
                        amount = getattr(parent_row, key)
                        if amount is not None:
                            confirmed[key] = confirmed.get(key, 0) + amount
                    for claim in parent_row.claims:
                        for key in self.claim_keys:
                            amount = getattr(claim, key)
                            if amount is not None:
                                claimed[key] = claimed.get(key, 0) + amount

                # now to see if user's request is possible, given what is
                # available...

                # first we must (pretend to) "relinquish" any claims which are
                # to be reduced or eliminated, according to our diff
                for key, amount in claim_diff.items():
                    if amount < 0:
                        amount = abs(amount) # make positive, for more readable math
                        if key not in claimed or claimed[key] < amount:
                            self.request.session.flash("Cannot relinquish more claims than the "
                                                       "parent batch has to offer.", 'error')
                            return False
                        claimed[key] -= amount

                # next we must determine if any "new" requests would increase
                # the claim(s) beyond what is available
                for key, amount in claim_diff.items():
                    if amount > 0:
                        claimed[key] = claimed.get(key, 0) + amount
                        if key not in confirmed or confirmed[key] < claimed[key]:
                            self.request.session.flash("Cannot request to claim more product than "
                                                       "is available in Truck Dump Parent batch", 'error')
                            return False

                # looks like the claim diff is all good, so let's attach that
                # to the form now and then pick this up again in save()
                form._claim_diff = claim_diff

        # all validation went ok
        return True

    def save_edit_row_form(self, form):
        batch = self.get_instance()
        row = self.objectify(form)

        # editing a row for truck dump child batch can be complicated...
        if batch.is_truck_dump_child():

            # grab the claim diff which we attached to the form during validation
            claim_diff = form._claim_diff

            # first we must "relinquish" any claims which are to be reduced or
            # eliminated, according to our diff
            for key, amount in claim_diff.items():
                if amount < 0:
                    amount = abs(amount) # make positive, for more readable math

                    # we'd prefer to find an exact match, i.e. there was a 1CS
                    # claim and our diff said to reduce by 1CS
                    matches = [claim for claim in row.truck_dump_claims
                               if getattr(claim, key) == amount]
                    if matches:
                        claim = matches[0]
                        setattr(claim, key, None)

                    else:
                        # but if no exact match(es) then we'll just whittle
                        # away at whatever (smallest) claims we do find
                        possible = [claim for claim in row.truck_dump_claims
                                    if getattr(claim, key) is not None]
                        for claim in sorted(possible, key=lambda claim: getattr(claim, key)):
                            previous = getattr(claim, key)
                            if previous:
                                if previous >= amount:
                                    if (previous - amount):
                                        setattr(claim, key, previous - amount)
                                    else:
                                        setattr(claim, key, None)
                                    amount = 0
                                    break
                                else:
                                    setattr(claim, key, None)
                                    amount -= previous

                        if amount:
                            raise NotImplementedError("Had leftover amount when \"relinquishing\" claim(s)")

            # next we must stake all new claim(s) as requested, per our diff
            for key, amount in claim_diff.items():
                if amount > 0:

                    # if possible, we'd prefer to add to an existing claim
                    # which already has an amount for this key
                    existing = [claim for claim in row.truck_dump_claims
                                if getattr(claim, key) is not None]
                    if existing:
                        claim = existing[0]
                        setattr(claim, key, getattr(claim, key) + amount)

                    # next we'd prefer to add to an existing claim, of any kind
                    elif row.truck_dump_claims:
                        claim = row.truck_dump_claims[0]
                        setattr(claim, key, (getattr(claim, key) or 0) + amount)

                    else:
                        # otherwise we must create a new claim...

                        # find all rows from truck dump parent which "may" pertain to child row
                        # TODO: perhaps would need to do a more "loose" match on UPC also?
                        if not row.product_uuid:
                            raise NotImplementedError("Don't (yet) know how to handle edit for row with no product")
                        parent_rows = [parent_row for parent_row in batch.truck_dump_batch.active_rows()
                                       if parent_row.product_uuid == row.product_uuid]

                        # remove any parent rows which are fully claimed
                        # TODO: should perhaps leverage actual amounts for this, instead
                        parent_rows = [parent_row for parent_row in parent_rows
                                       if parent_row.status_code != parent_row.STATUS_TRUCKDUMP_CLAIMED]

                        # try to find a parent row which is exact match on claim amount
                        matches = [parent_row for parent_row in parent_rows
                                   if getattr(parent_row, key) == amount]
                        if matches:

                            # make the claim against first matching parent row
                            claim = model.PurchaseBatchRowClaim()
                            claim.claimed_row = parent_rows[0]
                            setattr(claim, key, amount)
                            row.truck_dump_claims.append(claim)

                        else:
                            # but if no exact match(es) then we'll just whittle
                            # away at whatever (smallest) parent rows we do find
                            for parent_row in sorted(parent_rows, lambda prow: getattr(prow, key)):

                                available = getattr(parent_row, key) - sum([getattr(claim, key) for claim in parent_row.claims])
                                if available:
                                    if available >= amount:
                                        # make claim against this parent row, making it fully claimed
                                        claim = model.PurchaseBatchRowClaim()
                                        claim.claimed_row = parent_row
                                        setattr(claim, key, amount)
                                        row.truck_dump_claims.append(claim)
                                        amount = 0
                                        break
                                    else:
                                        # make partial claim against this parent row
                                        claim = model.PurchaseBatchRowClaim()
                                        claim.claimed_row = parent_row
                                        setattr(claim, key, available)
                                        row.truck_dump_claims.append(claim)
                                        amount -= available

                            if amount:
                                raise NotImplementedError("Had leftover amount when \"staking\" claim(s)")

            # now we must be sure to refresh all truck dump parent batch rows
            # which were affected.  but along with that we also should purge
            # any empty claims, i.e. those which were fully relinquished
            pending_refresh = set()
            for claim in list(row.truck_dump_claims):
                parent_row = claim.claimed_row
                if claim.is_empty():
                    row.truck_dump_claims.remove(claim)
                    self.Session.flush()
                pending_refresh.add(parent_row)
            for parent_row in pending_refresh:
                self.handler.refresh_row(parent_row)
            self.handler.refresh_batch_status(batch.truck_dump_batch)

        self.after_edit_row(row)
        self.Session.flush()
        return row

    def redirect_after_edit_row(self, row, **kwargs):
        return self.redirect(self.get_row_action_url('view', row))

    def update_row_cost(self):
        """
        AJAX view for updating the invoice (actual) unit cost for a row.
        """
        batch = self.get_instance()
        data = dict(self.request.POST)

        # validate row
        uuid = data.get('row_uuid')
        row = self.Session.query(model.PurchaseBatchRow).get(uuid) if uuid else None
        if not row or row.batch is not batch:
            return {'error': "Row not found"}

        # validate/normalize cost value(s)
        for field in ('catalog_unit_cost', 'invoice_unit_cost'):
            if field in data:
                cost = data[field]
                if cost == '':
                    return {'error': "You must specify a cost"}
                try:
                    cost = decimal.Decimal(six.text_type(cost))
                except decimal.InvalidOperation:
                    return {'error': "Cost is not valid!"}
                else:
                    data[field] = cost

        # okay, update our row
        self.handler.update_row_cost(row, **data)

        return {
            'row': {
                'catalog_unit_cost': '{:0.3f}'.format(row.catalog_unit_cost),
                'catalog_cost_confirmed': row.catalog_cost_confirmed,
                'invoice_unit_cost': '{:0.3f}'.format(row.invoice_unit_cost),
                'invoice_cost_confirmed': row.invoice_cost_confirmed,
                'invoice_total_calculated': '{:0.2f}'.format(row.invoice_total_calculated),
            },
            'batch': {
                'invoice_total_calculated': '{:0.2f}'.format(batch.invoice_total_calculated),
            },
        }

    def save_quick_row_form(self, form):
        batch = self.get_instance()
        entry = form.validated['quick_entry']
        row = self.handler.quick_entry(self.Session(), batch, entry)
        return row

    def get_row_image_url(self, row):
        if self.rattail_config.getbool('rattail.batch', 'purchase.mobile_images', default=True):
            return pod.get_image_url(self.rattail_config, row.upc)

    def can_auto_receive(self, batch):
        if batch.executed:
            return False
        if batch.complete:
            return False

        if batch.is_truck_dump_related():
            if not batch.is_truck_dump_parent():
                return False
            if not batch.truck_dump_children_first():
                return False

        # only auto-receive once per batch
        if batch.get_param('auto_received'):
            return False

        return True

    def auto_receive(self):
        """
        View which can "auto-receive" all items in the batch.  Meant only as a
        convenience for developers.
        """
        batch = self.get_instance()
        key = '{}.receive_all'.format(self.get_grid_key())
        progress = self.make_progress(key)
        kwargs = {'progress': progress}
        thread = Thread(target=self.auto_receive_thread, args=(batch.uuid, self.request.user.uuid), kwargs=kwargs)
        thread.start()

        return self.render_progress(progress, {
            'instance': batch,
            'cancel_url': self.get_action_url('view', batch),
            'cancel_msg': "Auto-receive was canceled",
        })

    def auto_receive_thread(self, uuid, user_uuid, progress=None):
        """
        Thread target for receiving all items on the given batch.
        """
        session = RattailSession()
        batch = session.query(model.PurchaseBatch).get(uuid)
        user = session.query(model.User).get(user_uuid)
        try:
            self.handler.auto_receive_all_items(batch, progress=progress)

        # if anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("auto-receive failed for: %s".format(batch))
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Auto-receive failed: {}".format(
                    simple_error(error))
                progress.session.save()

        # if no error, check result flag (false means user canceled)
        else:
            session.commit()
            session.refresh(batch)
            success_url = self.get_action_url('view', batch)
            session.close()
            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    def configure_get_simple_settings(self):
        config = self.rattail_config
        return [

            # supported workflows
            {'section': 'rattail.batch',
             'option': 'purchase.allow_receiving_from_scratch',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.allow_receiving_from_invoice',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.allow_receiving_from_purchase_order',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.allow_receiving_from_purchase_order_with_invoice',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.allow_truck_dump_receiving',
             'type': bool},

            # product handling
            {'section': 'rattail.batch',
             'option': 'purchase.allow_cases',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.allow_expired_credits',
             'type': bool},

            # mobile interface
            {'section': 'rattail.batch',
             'option': 'purchase.mobile_images',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.mobile_quick_receive',
             'type': bool},
            {'section': 'rattail.batch',
             'option': 'purchase.mobile_quick_receive_all',
             'type': bool},
        ]

    @classmethod
    def defaults(cls, config):
        cls._receiving_defaults(config)
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)

    @classmethod
    def _receiving_defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        permission_prefix = cls.get_permission_prefix()

        # new receiving batch using workflow X
        config.add_route('{}.create_workflow'.format(route_prefix), '{}/new/{{workflow_key}}/{{vendor_uuid}}'.format(url_prefix))
        config.add_view(cls, attr='create', route_name='{}.create_workflow'.format(route_prefix),
                        permission='{}.create'.format(permission_prefix))

        # row-level receiving
        config.add_route('{}.receive_row'.format(route_prefix), '{}/rows/{{row_uuid}}/receive'.format(instance_url_prefix))
        config.add_view(cls, attr='receive_row', route_name='{}.receive_row'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix))

        # declare credit for row
        config.add_route('{}.declare_credit'.format(route_prefix), '{}/rows/{{row_uuid}}/declare-credit'.format(instance_url_prefix))
        config.add_view(cls, attr='declare_credit', route_name='{}.declare_credit'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix))

        # un-declare credit
        config.add_route('{}.undeclare_credit'.format(route_prefix),
                         '{}/rows/{{row_uuid}}/undeclare-credit'.format(instance_url_prefix))
        config.add_view(cls, attr='undeclare_credit',
                        route_name='{}.undeclare_credit'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix),
                        renderer='json')

        # update row cost
        config.add_route('{}.update_row_cost'.format(route_prefix), '{}/update-row-cost'.format(instance_url_prefix))
        config.add_view(cls, attr='update_row_cost', route_name='{}.update_row_cost'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix),
                        renderer='json')

        # add TD child batch, from invoice file
        config.add_route('{}.add_child_from_invoice'.format(route_prefix), '{}/add-child-from-invoice'.format(instance_url_prefix))
        config.add_view(cls, attr='add_child_from_invoice', route_name='{}.add_child_from_invoice'.format(route_prefix),
                        permission='{}.create'.format(permission_prefix))

        # transform TD parent row from "pack" to "unit" item
        config.add_route('{}.transform_unit_row'.format(route_prefix), '{}/transform-unit'.format(instance_url_prefix))
        config.add_view(cls, attr='transform_unit_row', route_name='{}.transform_unit_row'.format(route_prefix),
                        permission='{}.edit_row'.format(permission_prefix), renderer='json')

        # auto-receive all items
        config.add_tailbone_permission(permission_prefix,
                                       '{}.auto_receive'.format(permission_prefix),
                                       "Auto-receive all items for a {}".format(model_title))
        config.add_route('{}.auto_receive'.format(route_prefix), '{}/auto-receive'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='auto_receive', route_name='{}.auto_receive'.format(route_prefix),
                        permission='{}.auto_receive'.format(permission_prefix))


@colander.deferred
def valid_workflow(node, kw):
    """
    Deferred validator for ``workflow`` field, for new batches.
    """
    valid_workflows = kw['valid_workflows']

    def validate(node, value):
        # we just need to provide possible values, and let stock validator
        # handle the rest
        oneof = colander.OneOf(valid_workflows)
        return oneof(node, value)

    return validate


class NewReceivingBatch(colander.Schema):
    """
    Schema for choosing which "type" of new receiving batch should be created.
    """
    vendor = colander.SchemaNode(colander.String(),
                                 label="Vendor")

    workflow = colander.SchemaNode(colander.String(),
                                   validator=valid_workflow)


class ReceiveRowForm(colander.MappingSchema):

    mode = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf(
                                   POSSIBLE_RECEIVING_MODES))

    quantity = forms.types.ProductQuantity()

    expiration_date = colander.SchemaNode(colander.Date(),
                                          widget=dfwidget.TextInputWidget(),
                                          missing=colander.null)

    quick_receive = colander.SchemaNode(colander.Boolean())

    def deserialize(self, *args):
        result = super(ReceiveRowForm, self).deserialize(*args)

        if result['mode'] == 'expired' and not result['expiration_date']:
            msg = "Expiration date is required for items with 'expired' mode."
            self.raise_invalid(msg, node=self.get('expiration_date'))

        return result


class DeclareCreditForm(colander.MappingSchema):

    credit_type = colander.SchemaNode(colander.String(),
                                      validator=colander.OneOf(
                                          POSSIBLE_CREDIT_TYPES))

    quantity = forms.types.ProductQuantity()

    expiration_date = colander.SchemaNode(colander.Date(),
                                          widget=dfwidget.TextInputWidget(),
                                          missing=colander.null)


def includeme(config):
    ReceivingBatchView.defaults(config)
