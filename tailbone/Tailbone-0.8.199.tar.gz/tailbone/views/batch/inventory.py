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
Views for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import re
import decimal
import logging

import six

from rattail import pod
from rattail.db import model
from rattail.db.util import make_full_description
from rattail.gpc import GPC
from rattail.util import pretty_quantity, OrderedDict

import colander
from deform import widget as dfwidget
from webhelpers2.html import HTML, tags

from tailbone import forms, grids
from tailbone.views import MasterView
from tailbone.views.batch import BatchMasterView


log = logging.getLogger(__name__)


class InventoryBatchView(BatchMasterView):
    """
    Master view for inventory batches.
    """
    model_class = model.InventoryBatch
    model_title_plural = "Inventory Batches"
    default_handler_spec = 'rattail.batch.inventory:InventoryBatchHandler'
    route_prefix = 'batch.inventory'
    url_prefix = '/batch/inventory'
    index_title = "Inventory"
    rows_creatable = True
    bulk_deletable = True

    # set to True for the UI to "prefer" case amounts, as opposed to unit
    prefer_cases = False

    labels = {
        'mode': "Count Mode",
    }

    grid_columns = [
        'id',
        'created',
        'created_by',
        'description',
        'mode',
        'rowcount',
        'total_cost',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'id',
        'description',
        'notes',
        'created',
        'created_by',
        'handheld_batches',
        'mode',
        'reason_code',
        'total_cost',
        'rowcount',
        'complete',
        'executed',
        'executed_by',
    ]

    model_row_class = model.InventoryBatchRow
    rows_editable = True

    row_labels = {
        'upc': "UPC",
        'previous_units_on_hand': "Prev. On Hand",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'item_id',
        'brand_name',
        'description',
        'size',
        'previous_units_on_hand',
        'cases',
        'units',
        'unit_cost',
        'total_cost',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'status_code',
        'previous_units_on_hand',
        'case_quantity',
        'cases',
        'units',
        'unit_cost',
        'total_cost',
        'variance',
    ]

    def configure_grid(self, g):
        super(InventoryBatchView, self).configure_grid(g)

        # mode
        g.set_enum('mode', self.enum.INVENTORY_MODE)
        g.filters['mode'].set_value_renderer(
            grids.filters.EnumValueRenderer(self.enum.INVENTORY_MODE))

        # total_cost
        g.set_type('total_cost', 'currency')

    def mutable_batch(self, batch):
        return not batch.executed and not batch.complete and batch.mode != self.enum.INVENTORY_MODE_ZERO_ALL

    def allow_worksheet(self, batch):
        return self.mutable_batch(batch)

    def get_available_modes(self):
        permission_prefix = self.get_permission_prefix()
        if self.request.is_root:
            modes = self.handler.get_count_modes()
        else:
            modes = self.handler.get_allowed_count_modes(
                self.Session(), self.request.user,
                permission_prefix=permission_prefix)

        modes = OrderedDict([(mode['code'], mode['label'])
                             for mode in modes])
        return modes

    def configure_form(self, f):
        super(InventoryBatchView, self).configure_form(f)

        # mode
        modes = self.get_available_modes()
        f.set_enum('mode', modes)
        f.set_label('mode', "Count Mode")
        if len(modes) == 1:
            f.set_widget('mode', forms.widgets.ReadonlyWidget())
            f.set_default('mode', list(modes)[0])

        # total_cost
        if self.creating:
            f.remove_field('total_cost')
        else:
            f.set_readonly('total_cost')
            f.set_type('total_cost', 'currency')

        # handheld_batches
        if self.creating:
            f.remove_field('handheld_batches')
        else:
            f.set_readonly('handheld_batches')
            f.set_renderer('handheld_batches', self.render_handheld_batches)

        # complete
        if self.creating:
            f.remove_field('complete')

    def render_handheld_batches(self, inventory_batch, field):
        items = []
        for handheld in inventory_batch._handhelds:
            text = handheld.handheld.id_str
            url = self.request.route_url('batch.handheld.view', uuid=handheld.handheld_uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def row_editable(self, row):
        return self.mutable_batch(row.batch)

    def row_deletable(self, row):
        return self.mutable_batch(row.batch)

    def save_edit_row_form(self, form):
        row = form.model_instance
        batch = row.batch
        if batch.total_cost is not None and row.total_cost is not None:
            batch.total_cost -= row.total_cost
        return super(InventoryBatchView, self).save_edit_row_form(form)

    def delete_row(self):
        row = self.Session.query(model.InventoryBatchRow).get(self.request.matchdict['row_uuid'])
        if not row:
            raise self.notfound()
        batch = row.batch
        if batch.total_cost is not None and row.total_cost is not None:
            batch.total_cost -= row.total_cost
        return super(InventoryBatchView, self).delete_row()

    def create_row(self):
        """
        Desktop workflow view for adding items to inventory batch.
        """
        batch = self.get_instance()
        if batch.executed:
            return self.redirect(self.get_action_url('view', batch))

        schema = DesktopForm().bind(session=self.Session())
        form = forms.Form(schema=schema, request=self.request)
        if form.validate(newstyle=True):

            product = self.Session.query(model.Product).get(form.validated['product'])

            row = None
            if self.should_aggregate_products(batch):
                row = self.find_row_for_product(batch, product)
                if row:
                    row.cases = form.validated['cases']
                    row.units = form.validated['units']
                    self.handler.refresh_row(row)

            if not row:
                row = model.InventoryBatchRow()
                row.product = product
                row.upc = form.validated['upc']
                row.brand_name = form.validated['brand_name']
                row.description = form.validated['description']
                row.size = form.validated['size']
                row.case_quantity = form.validated['case_quantity']
                row.cases = form.validated['cases']
                row.units = form.validated['units']
                self.handler.capture_current_units(row)
                self.handler.add_row(batch, row)

            description = make_full_description(form.validated['brand_name'],
                                                form.validated['description'],
                                                form.validated['size'])
            self.request.session.flash("{} cases, {} units: {} {}".format(
                form.validated['cases'] or 0, form.validated['units'] or 0,
                form.validated['upc'].pretty(), description))
            return self.redirect(self.request.current_route_url())

        title = self.get_instance_title(batch)
        return self.render_to_response('desktop_form', {
            'batch': batch,
            'instance': batch,
            'instance_title': title,
            'index_title': "{}: {}".format(self.get_model_title(), title),
            'index_url': self.get_action_url('view', batch),
            'form': form,
            'dform': form.make_deform_form(),
            'allow_cases': self.allow_cases(batch),
            'prefer_cases': self.prefer_cases,
        })

    # TODO: deprecate / remove this
    def allow_cases(self, batch):
        return self.handler.allow_cases(batch)

    # TODO: deprecate / remove this
    def should_aggregate_products(self, batch):
        """
        Must return a boolean indicating whether rows should be aggregated by
        product for the given batch.
        """
        return self.handler.should_aggregate_products(batch)

    # TODO: deprecate / remove
    def find_type2_product(self, entry):
        return self.handler.get_type2_product_info(self.Session(), entry)

    def desktop_lookup(self):
        """
        Try to locate a product by UPC, and validate it in the context of
        current batch, returning some data for client JS.
        """
        batch = self.get_instance()
        if batch.executed:
            return {
                'error': "Current batch has already been executed",
                'redirect': self.get_action_url('view', batch),
            }
        entry = self.request.GET.get('upc', '')
        aggregate = self.should_aggregate_products(batch)

        type2 = self.find_type2_product(entry)
        if type2:
            product, price = type2
        else:
            product = self.find_product(entry)

        force_unit_item = True # TODO: make configurable?
        unit_forced = False
        if force_unit_item and product and product.is_pack_item():
            product = product.unit
            unit_forced = True

        data = self.product_info(product)
        if type2:
            data['type2'] = True
            if not aggregate:
                if price is None:
                    data['units'] = 1
                else:
                    data['units'] = float((price / product.regular_price.price).quantize(decimal.Decimal('0.01')))

        result = {'product': data, 'upc_raw': entry, 'upc': None, 'force_unit_item': unit_forced}
        if not data:
            upc = re.sub(r'\D', '', entry.strip())
            if upc:
                upc = GPC(upc)
                result['upc'] = six.text_type(upc)
                result['upc_pretty'] = upc.pretty()
                result['image_url'] = pod.get_image_url(self.rattail_config, upc)

        if product and aggregate:
            row = self.find_row_for_product(batch, product)
            if row:
                result['already_present_in_batch'] = True
                result['cases'] = float(row.cases) if row.cases is not None else None
                result['units'] = float(row.units) if row.units is not None else None

        return result

    # TODO: deprecate / remove
    def find_row_for_product(self, batch, product):
        return self.handler.find_row_for_product(self.Session(), batch, product)

    # TODO: deprecate / remove (?)
    def find_product(self, entry):
        lookup_by_code = self.rattail_config.getbool(
            'tailbone', 'inventory.lookup_by_code', default=False)

        return self.handler.locate_product_for_entry(
            self.Session(), entry, lookup_by_code=lookup_by_code)

    def product_info(self, product):
        data = {}
        if product and (not product.deleted or self.request.has_perm('products.view_deleted')):
            data['uuid'] = product.uuid
            data['upc'] = six.text_type(product.upc)
            data['upc_pretty'] = product.upc.pretty()
            data['full_description'] = product.full_description
            data['brand_name'] = six.text_type(product.brand or '')
            data['description'] = product.description
            data['size'] = product.size
            data['case_quantity'] = 1 # default
            data['cost_found'] = False
            data['image_url'] = pod.get_image_url(self.rattail_config, product.upc)
        return data

    def add_row_for_upc(self, batch, entry, warn_if_present=False):
        """
        Add a row to the batch for the given UPC, if applicable.
        """
        row = self.handler.quick_entry(self.Session(), batch, entry)
        if row:

            if row.product and getattr(row.product, '__forced_unit_item__', False):
                self.request.session.flash("You scanned a pack item, but must count the units instead.", 'error')

            if warn_if_present and getattr(row, '__existing_reused__', False):
                self.request.session.flash("Product already exists in batch; please confirm counts", 'error')

            return row

    def template_kwargs_view_row(self, **kwargs):
        row = kwargs['instance']
        kwargs['product_image_url'] = pod.get_image_url(self.rattail_config, row.upc)
        return kwargs

    def get_batch_kwargs(self, batch, **kwargs):
        kwargs = super(InventoryBatchView, self).get_batch_kwargs(batch, **kwargs)
        kwargs['mode'] = batch.mode
        kwargs['complete'] = False
        kwargs['reason_code'] = batch.reason_code
        return kwargs

    def get_row_instance_title(self, row):
        if row.upc:
            return row.upc.pretty()
        if row.item_id:
            return row.item_id
        return "row {}".format(row.sequence)

    def configure_row_grid(self, g):
        super(InventoryBatchView, self).configure_row_grid(g)

        # quantity fields
        g.set_type('previous_units_on_hand', 'quantity')
        g.set_type('cases', 'quantity')
        g.set_type('units', 'quantity')

        # currency fields
        g.set_type('unit_cost', 'currency')
        g.set_type('total_cost', 'currency')

        # short labels
        g.set_label('brand_name', "Brand")
        g.set_label('status_code', "Status")

        # links
        g.set_link('upc')
        g.set_link('item_id')
        g.set_link('description')

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'

    def configure_row_form(self, f):
        super(InventoryBatchView, self).configure_row_form(f)
        row = f.model_instance

        # readonly fields
        f.set_readonly('upc')
        f.set_readonly('item_id')
        f.set_readonly('brand_name')
        f.set_readonly('description')
        f.set_readonly('size')
        f.set_readonly('previous_units_on_hand')
        f.set_readonly('case_quantity')
        f.set_readonly('variance')
        f.set_readonly('total_cost')

        # quantity fields
        f.set_type('case_quantity', 'quantity')
        f.set_type('previous_units_on_hand', 'quantity')
        f.set_type('cases', 'quantity')
        f.set_type('units', 'quantity')
        f.set_type('variance', 'quantity')

        # currency fields
        f.set_type('unit_cost', 'currency')
        f.set_type('total_cost', 'currency')

        # upc
        f.set_renderer('upc', self.render_upc)

        # cases
        if self.editing:
            if not self.allow_cases(row.batch):
                f.set_readonly('cases')

    @classmethod
    def defaults(cls, config):
        cls._batch_defaults(config)
        cls._defaults(config)
        cls._inventory_defaults(config)

    @classmethod
    def _inventory_defaults(cls, config):
        rattail_config = config.registry.settings['rattail_config']
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # we need batch handler to determine available permissions
        factory = cls.get_handler_factory(rattail_config)
        handler = factory(rattail_config)

        # extra perms for creating batches per "mode"
        config.add_tailbone_permission(permission_prefix, '{}.create.replace'.format(permission_prefix),
                                       "Create new {} with 'replace' mode".format(model_title))
        if handler.allow_zero_all:
            config.add_tailbone_permission(permission_prefix, '{}.create.zero'.format(permission_prefix),
                                           "Create new {} with 'zero' mode".format(model_title))
        if handler.allow_variance:
            config.add_tailbone_permission(permission_prefix, '{}.create.variance'.format(permission_prefix),
                                           "Create new {} with 'variance' mode".format(model_title))

        # row UPC lookup, for desktop
        config.add_route('{}.desktop_lookup'.format(route_prefix), '{}/{{{}}}/desktop-form/lookup'.format(url_prefix, model_key))
        config.add_view(cls, attr='desktop_lookup', route_name='{}.desktop_lookup'.format(route_prefix),
                        renderer='json', permission='{}.create_row'.format(permission_prefix))


# TODO: this is a stopgap measure to fix an obvious bug, which exists when the
# session is not provided by the view at runtime (i.e. when it was instead
# being provided by the type instance, which was created upon app startup).
@colander.deferred
def valid_product(node, kw):
    session = kw['session']
    def validate(node, value):
        product = session.query(model.Product).get(value)
        if not product:
            raise colander.Invalid(node, "Product not found")
        return product.uuid
    return validate


class DesktopForm(colander.Schema):

    product = colander.SchemaNode(colander.String(),
                                  validator=valid_product)

    upc = colander.SchemaNode(forms.types.GPCType())

    brand_name = colander.SchemaNode(colander.String())

    description = colander.SchemaNode(colander.String())

    size = colander.SchemaNode(colander.String(), missing=colander.null)

    case_quantity = colander.SchemaNode(colander.Decimal())

    cases = colander.SchemaNode(colander.Decimal(),
                                missing=None)

    units = colander.SchemaNode(colander.Decimal(),
                                missing=None)


def includeme(config):
    InventoryBatchView.defaults(config)
