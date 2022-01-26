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
Views for maintaining vendor catalogs
"""

from __future__ import unicode_literals, absolute_import

import logging

import six

from rattail.db import model

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags

from tailbone import forms
from tailbone.views.batch import FileBatchMasterView
from tailbone.diffs import Diff
from tailbone.db import Session


log = logging.getLogger(__name__)


class VendorCatalogView(FileBatchMasterView):
    """
    Master view for vendor catalog batches.
    """
    model_class = model.VendorCatalogBatch
    model_row_class = model.VendorCatalogBatchRow
    default_handler_spec = 'rattail.batch.vendorcatalog:VendorCatalogHandler'
    route_prefix = 'vendorcatalogs'
    url_prefix = '/vendors/catalogs'
    template_prefix = '/batch/vendorcatalog'
    bulk_deletable = True
    results_executable = True
    rows_bulk_deletable = True
    has_input_file_templates = True
    configurable = True

    labels = {
        'vendor_id': "Vendor ID",
        'parser_key': "Parser",
    }

    grid_columns = [
        'id',
        'vendor',
        'description',
        'filename',
        'rowcount',
        'created',
        'executed',
    ]

    form_fields = [
        'id',
        'filename',
        'parser_key',
        'vendor',
        'future',
        'effective',
        'description',
        'notes',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'vendor_code',
        'is_preferred_vendor',
        'old_unit_cost',
        'unit_cost',
        'unit_cost_diff',
        'unit_cost_diff_percent',
        'starts',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'item_entry',
        'product',
        'upc',
        'brand_name',
        'description',
        'size',
        'is_preferred_vendor',
        'suggested_retail',
        'starts',
        'ends',
        'discount_starts',
        'discount_ends',
        'discount_amount',
        'discount_percent',
        'case_cost_diff',
        'unit_cost_diff',
        'status_code',
        'status_text',
    ]

    def get_input_file_templates(self):
        return [
            {'key': 'default',
             'label': "Default",
             'default_url': self.request.static_url(
                 'tailbone:static/files/vendor_catalog_template.xlsx')},
        ]

    def get_parsers(self):
        if not hasattr(self, 'parsers'):
            app = self.get_rattail_app()
            vendor_handler = app.get_vendor_handler()
            self.parsers = vendor_handler.get_supported_catalog_parsers()
        return self.parsers

    def configure_grid(self, g):
        super(VendorCatalogView, self).configure_grid(g)
        g.joiners['vendor'] = lambda q: q.join(model.Vendor)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name,
                                            default_active=True, default_verb='contains')
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        g.set_link('vendor')
        g.set_link('filename')

    def configure_form(self, f):
        super(VendorCatalogView, self).configure_form(f)
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()

        # filename
        f.set_label('filename', "Catalog File")

        # parser_key
        if self.creating:
            if 'parser_key' not in f:
                f.insert_after('filename', 'parser_key')
            parsers = self.get_parsers()
            values = [(p.key, p.display) for p in parsers]
            if len(values) == 1:
                f.set_default('parser_key', parsers[0].key)
            use_buefy = self.get_use_buefy()
            if not use_buefy:
                values.insert(0, ('', "(please choose)"))
            f.set_widget('parser_key', dfwidget.SelectWidget(values=values))
        else:
            f.set_readonly('parser_key')
            f.set_renderer('parser_key', self.render_parser_key)

        # vendor
        f.set_renderer('vendor', self.render_vendor)
        if self.creating and 'vendor' in f:
            f.replace('vendor', 'vendor_uuid')
            f.set_label('vendor_uuid', "Vendor")
            use_dropdown = vendor_handler.choice_uses_dropdown()
            if use_dropdown:
                vendors = self.Session.query(model.Vendor)\
                                      .order_by(model.Vendor.id)
                vendor_values = [(vendor.uuid, "({}) {}".format(vendor.id,
                                                                vendor.name))
                                 for vendor in vendors]
                f.set_widget('vendor_uuid',
                             dfwidget.SelectWidget(values=vendor_values))
            else:
                vendor_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('vendor_uuid'):
                        vendor = self.Session.query(model.Vendor).get(
                            self.request.POST['vendor_uuid'])
                        if vendor:
                            vendor_display = six.text_type(vendor)
                vendors_url = self.request.route_url('vendors.autocomplete')
                f.set_widget('vendor_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=vendor_display, service_url=vendors_url,
                    assigned_label='vendorName'))
        else:
            f.set_readonly('vendor')

        if self.batch_handler.allow_future():

            # effective
            f.set_type('effective', 'date_jquery')

        else: # future not allowed
            f.remove('future',
                     'effective')

    def render_parser_key(self, batch, field):
        key = getattr(batch, field)
        if not key:
            return
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()
        parser = vendor_handler.get_catalog_parser(key)
        return parser.display

    def template_kwargs_create(self, **kwargs):
        use_buefy = self.get_use_buefy()
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()
        parsers = self.get_parsers()
        parsers_data = {}
        for parser in parsers:
            if use_buefy:
                pdata = {'key': parser.key,
                         'vendor_key': parser.vendor_key}
                if parser.vendor_key:
                    vendor = vendor_handler.get_vendor(self.Session(),
                                                       parser.vendor_key)
                    if vendor:
                        pdata['vendor_uuid'] = vendor.uuid
                        pdata['vendor_name'] = vendor.name
                parsers_data[parser.key] = pdata
            else:
                if parser.vendor_key:
                    vendor = vendor_handler.get_vendor(self.Session(),
                                                       parser.vendor_key)
                    if vendor:
                        parser.vendormap_value = "{{uuid: '{}', name: '{}'}}".format(
                            vendor.uuid, vendor.name.replace("'", "\\'"))
                    else:
                        log.warning("vendor '{}' not found for parser: {}".format(
                            parser.vendor_key, parser.key))
                        parser.vendormap_value = 'null'
                else:
                    parser.vendormap_value = 'null'
        kwargs['parsers'] = parsers
        kwargs['parsers_data'] = parsers_data
        return kwargs

    def get_batch_kwargs(self, batch):
        kwargs = super(VendorCatalogView, self).get_batch_kwargs(batch)
        kwargs['parser_key'] = batch.parser_key
        if batch.vendor:
            kwargs['vendor'] = batch.vendor
        elif batch.vendor_uuid:
            kwargs['vendor_uuid'] = batch.vendor_uuid
        if batch.vendor_id:
            kwargs['vendor_id'] = batch.vendor_id
        if batch.vendor_name:
            kwargs['vendor_name'] = batch.vendor_name
        if self.batch_handler.allow_future():
            kwargs['future'] = batch.future
            kwargs['effective'] = batch.effective
        return kwargs

    def configure_row_grid(self, g):
        super(VendorCatalogView, self).configure_row_grid(g)
        batch = self.get_instance()

        # starts
        if not batch.future:
            g.remove('starts')

        g.set_type('old_unit_cost', 'currency')
        g.set_type('unit_cost', 'currency')
        g.set_type('unit_cost_diff', 'currency')

        g.set_type('unit_cost_diff_percent', 'percent')
        g.set_label('unit_cost_diff_percent', "Diff. %")

        g.set_label('is_preferred_vendor', "Pref. Vendor")

        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('old_unit_cost', "Old Cost")
        g.set_label('unit_cost', "New Cost")
        g.set_label('unit_cost_diff', "Diff. $")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'
        if row.status_code in (row.STATUS_NEW_COST,
                               row.STATUS_UPDATE_COST, # TODO: deprecate/remove this one
                               row.STATUS_CHANGE_VENDOR_ITEM_CODE,
                               row.STATUS_CHANGE_CASE_SIZE,
                               row.STATUS_CHANGE_COST,
                               row.STATUS_CHANGE_PRODUCT):
            return 'notice'

    def configure_row_form(self, f):
        super(VendorCatalogView, self).configure_row_form(f)
        f.set_renderer('product', self.render_product)
        f.set_type('upc', 'gpc')
        f.set_type('discount_percent', 'percent')

    def template_kwargs_view_row(self, **kwargs):
        row = kwargs['instance']
        batch = row.batch

        fields = [
            'vendor_code',
            'case_size',
            'case_cost',
            'unit_cost',
        ]
        old_data = dict([(field, getattr(row, 'old_{}'.format(field)))
                         for field in fields])
        new_data = dict([(field, getattr(row, field))
                         for field in fields])
        kwargs['catalog_entry_diff'] = Diff(old_data, new_data, fields=fields,
                                            monospace=True)

        return kwargs

    def configure_get_simple_settings(self):
        settings = super(VendorCatalogView, self).configure_get_simple_settings() or []
        settings.extend([

            # key field
            {'section': 'rattail.batch',
             'option': 'vendor_catalog.allow_future',
             'type': bool},

        ])
        return settings

    def configure_get_context(self):
        context = super(VendorCatalogView, self).configure_get_context()
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()

        Parsers = vendor_handler.get_all_catalog_parsers()
        Supported = vendor_handler.get_supported_catalog_parsers()
        context['catalog_parsers'] = Parsers
        context['catalog_parsers_data'] = dict([(Parser.key, Parser in Supported)
                                                for Parser in Parsers])

        return context

    def configure_gather_settings(self, data):
        settings = super(VendorCatalogView, self).configure_gather_settings(data)
        app = self.get_rattail_app()
        vendor_handler = app.get_vendor_handler()

        supported = []
        for Parser in vendor_handler.get_all_catalog_parsers():
            name = 'catalog_parser_{}'.format(Parser.key)
            if data.get(name) == 'true':
                supported.append(Parser.key)
        settings.append({'name': 'rattail.vendors.supported_catalog_parsers',
                         'value': ', '.join(supported)})

        return settings

    def configure_remove_settings(self):
        super(VendorCatalogView, self).configure_remove_settings()
        model = self.model
        names = [
            'rattail.vendors.supported_catalog_parsers',
            'tailbone.batch.vendorcatalog.supported_parsers', # deprecated
        ]

        Session().query(model.Setting)\
                 .filter(model.Setting.name.in_(names))\
                 .delete(synchronize_session=False)


# TODO: deprecate / remove this
VendorCatalogsView = VendorCatalogView


def includeme(config):
    VendorCatalogView.defaults(config)
