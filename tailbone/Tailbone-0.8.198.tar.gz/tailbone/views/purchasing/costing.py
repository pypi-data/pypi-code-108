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
Views for 'costing' (purchasing) batches
"""

from __future__ import unicode_literals, absolute_import

import six

import colander
from deform import widget as dfwidget

from tailbone import forms
from tailbone.views.purchasing import PurchasingBatchView


class CostingBatchView(PurchasingBatchView):
    """
    Master view for costing batches
    """
    route_prefix = 'invoice_costing'
    url_prefix = '/invoice-costing'
    model_title = "Invoice Costing Batch"
    model_title_plural = "Invoice Costing Batches"
    index_title = "Invoice Costing"
    downloadable = True
    bulk_deletable = True

    purchase_order_fieldname = 'purchase'

    labels = {
        'invoice_parser_key': "Invoice Parser",
    }

    grid_columns = [
        'id',
        'vendor',
        'description',
        'department',
        'buyer',
        'date_ordered',
        'created',
        'created_by',
        'rowcount',
        'invoice_total',
        'status_code',
        'executed',
    ]

    form_fields = [
        'id',
        'store',
        'buyer',
        'vendor',
        'costing_workflow',
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
        'cases_received',
        'units_received',
        'case_quantity',
        'catalog_unit_cost',
        'invoice_unit_cost',
        # 'invoice_total_calculated',
        'invoice_total',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'upc',
        'item_id',
        'product',
        'vendor_code',
        'brand_name',
        'description',
        'size',
        'department_name',
        'case_quantity',
        'cases_ordered',
        'units_ordered',
        'cases_shipped',
        'units_shipped',
        'cases_received',
        'units_received',
        'po_line_number',
        'po_unit_cost',
        'po_total',
        'invoice_line_number',
        'invoice_unit_cost',
        'invoice_total',
        'invoice_total_calculated',
        'catalog_unit_cost',
        'status_code',
    ]

    @property
    def batch_mode(self):
        return self.enum.PURCHASE_BATCH_MODE_COSTING

    def create(self, form=None, **kwargs):
        """
        Custom view for creating a new costing batch.  We split the
        process into two steps, 1) choose workflow and 2) create
        batch.  This is because the specific form details for creating
        a batch will depend on which "type" of batch creation is to be
        done, and it's much easier to keep conditional logic for that
        in the server instead of client-side etc.

        See also
        :meth:`tailbone.views.purchasing.receiving:ReceivingBatchView.create()`
        which uses similar logic.
        """
        route_prefix = self.get_route_prefix()
        workflows = self.handler.supported_costing_workflows()
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
            return super(CostingBatchView, self).create(**kwargs)

        # okay, at this point we need the user to select a vendor and workflow
        self.creating = True
        use_buefy = self.get_use_buefy()
        model = self.model
        context = {}

        # form to accept user choice of vendor/workflow
        schema = NewCostingBatch().bind(valid_workflows=valid_workflows)
        form = forms.Form(schema=schema, request=self.request,
                          use_buefy=use_buefy)
        if len(valid_workflows) == 1:
            form.set_default('workflow', valid_workflows[0])

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

    def configure_form(self, f):
        super(CostingBatchView, self).configure_form(f)
        route_prefix = self.get_route_prefix()
        use_buefy = self.get_use_buefy()
        model = self.model
        workflow = self.request.matchdict.get('workflow_key')

        if self.creating:
            f.set_fields([
                'vendor_uuid',
                'costing_workflow',
                'invoice_file',
                'invoice_parser_key',
                'purchase',
            ])
            f.set_required('invoice_file')

        # tweak some things if we are in "step 2" of creating new batch
        if self.creating and workflow:

            # display vendor but do not allow changing
            vendor = self.Session.query(model.Vendor).get(
                self.request.matchdict['vendor_uuid'])
            assert vendor

            f.set_hidden('vendor_uuid')
            f.set_default('vendor_uuid', vendor.uuid)
            f.set_widget('vendor_uuid', dfwidget.HiddenWidget())

            f.insert_after('vendor_uuid', 'vendor_name')
            f.set_readonly('vendor_name')
            f.set_default('vendor_name', vendor.name)
            f.set_label('vendor_name', "Vendor")

            # cancel should take us back to choosing a workflow
            f.cancel_url = self.request.route_url('{}.create'.format(route_prefix))

        # costing_workflow
        if self.creating and workflow:
            f.set_readonly('costing_workflow')
            f.set_renderer('costing_workflow', self.render_costing_workflow)
        else:
            f.remove('costing_workflow')

        # batch_type
        if self.creating:
            f.set_widget('batch_type', dfwidget.HiddenWidget())
            f.set_default('batch_type', workflow)
            f.set_hidden('batch_type')
        else:
            f.remove_field('batch_type')

        # purchase
        if (self.creating and workflow == 'invoice_with_po'
            and self.purchase_order_fieldname == 'purchase'):
            if use_buefy:
                f.replace('purchase', 'purchase_uuid')
                purchases = self.handler.get_eligible_purchases(
                    vendor, self.enum.PURCHASE_BATCH_MODE_COSTING)
                values = [(p.uuid, self.handler.render_eligible_purchase(p))
                          for p in purchases]
                f.set_widget('purchase_uuid', dfwidget.SelectWidget(values=values))
                f.set_label('purchase_uuid', "Purchase Order")
                f.set_required('purchase_uuid')

    def render_costing_workflow(self, batch, field):
        key = self.request.matchdict['workflow_key']
        info = self.handler.costing_workflow_info(key)
        if info:
            return info['display']

    def configure_row_grid(self, g):
        super(CostingBatchView, self).configure_row_grid(g)

        g.set_label('case_quantity', "Case Qty")
        g.filters['case_quantity'].label = "Case Quantity"
        g.set_type('case_quantity', 'quantity')

    @classmethod
    def defaults(cls, config):
        cls._costing_defaults(config)
        cls._purchasing_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)

    @classmethod
    def _costing_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # new costing batch using workflow X
        config.add_route('{}.create_workflow'.format(route_prefix),
                         '{}/new/{{workflow_key}}/{{vendor_uuid}}'.format(url_prefix))
        config.add_view(cls, attr='create',
                        route_name='{}.create_workflow'.format(route_prefix),
                        permission='{}.create'.format(permission_prefix))


@colander.deferred
def valid_workflow(node, kw):
    """
    Deferred validator for ``workflow`` field, for new batches.
    """
    valid_workflows = kw['valid_workflows']

    def validate(node, value):
        # we just need to provide possible values, and let stock
        # validator handle the rest
        oneof = colander.OneOf(valid_workflows)
        return oneof(node, value)

    return validate


class NewCostingBatch(colander.Schema):
    """
    Schema for choosing which "type" of new receiving batch should be created.
    """
    vendor = colander.SchemaNode(colander.String(),
                                 label="Vendor")

    workflow = colander.SchemaNode(colander.String(),
                                   validator=valid_workflow)


def includeme(config):
    CostingBatchView.defaults(config)
