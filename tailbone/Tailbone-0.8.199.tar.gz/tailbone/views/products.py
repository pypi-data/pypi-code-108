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
Product Views
"""

from __future__ import unicode_literals, absolute_import

import re
import logging

import six
import humanize
import sqlalchemy as sa
from sqlalchemy import orm
import sqlalchemy_continuum as continuum

from rattail import enum, pod, sil
from rattail.db import model, api, auth, Session as RattailSession
from rattail.gpc import GPC
from rattail.threads import Thread
from rattail.exceptions import LabelPrintingError
from rattail.util import load_object, pretty_quantity, OrderedDict, simple_error
from rattail.time import localtime, make_utc

import colander
from deform import widget as dfwidget
from pyramid import httpexceptions
from webhelpers2.html import tags, HTML

from tailbone import forms, grids
from tailbone.views import MasterView
from tailbone.util import raw_datetime


log = logging.getLogger(__name__)


# TODO: For a moment I thought this was going to be necessary, but now I think
# not.  Leaving it around for a bit just in case...

# class VendorAnyFilter(grids.filters.AlchemyStringFilter):
#     """
#     Custom filter for "vendor (any)" so we can avoid joining on that unless we
#     really have to.  This is because it seems to throw off the number of
#     records which are showed in the result set, when this filter is included in
#     the active set but no criteria is specified.
#     """

#     def filter(self, query, **kwargs):
#         original = query
#         query = super(VendorAnyFilter, self).filter(query, **kwargs)
#         if query is not original:
#             query = self.joiner(query)
#         return query


class ProductView(MasterView):
    """
    Master view for the Product class.
    """
    model_class = model.Product
    has_versions = True
    results_downloadable_xlsx = True
    supports_autocomplete = True
    configurable = True

    labels = {
        'item_id': "Item ID",
        'upc': "UPC",
        'status_code': "Status",
        'tax1': "Tax 1",
        'tax2': "Tax 2",
        'tax3': "Tax 3",
        'tpr_price': "TPR Price",
        'tpr_price_ends': "TPR Price Ends",
    }

    grid_columns = [
        'upc',
        'brand',
        'description',
        'size',
        'department',
        'vendor',
        'regular_price',
        'current_price',
    ]

    form_fields = [
        'item_id',
        'scancode',
        'upc',
        'brand',
        'description',
        'unit_size',
        'unit_of_measure',
        'size',
        'packs',
        'pack_size',
        'unit',
        'default_pack',
        'case_size',
        'weighed',
        'average_weight',
        'department',
        'subdepartment',
        'category',
        'family',
        'report_code',
        'suggested_price',
        'regular_price',
        'current_price',
        'current_price_ends',
        'sale_price',
        'sale_price_ends',
        'tpr_price',
        'tpr_price_ends',
        'vendor',
        'cost',
        'deposit_link',
        'tax',
        'tax1',
        'tax2',
        'tax3',
        'organic',
        'kosher',
        'vegan',
        'vegetarian',
        'gluten_free',
        'sugar_free',
        'discountable',
        'special_order',
        'not_for_sale',
        'ingredients',
        'notes',
        'status_code',
        'discontinued',
        'deleted',
        'last_sold',
        'inventory_on_hand',
        'inventory_on_order',
    ]

    # These aliases enable the grid queries to filter products which may be
    # purchased from *any* vendor, and yet sort by only the "preferred" vendor
    # (since that's what shows up in the grid column).
    ProductVendorCost = orm.aliased(model.ProductCost)
    ProductVendorCostAny = orm.aliased(model.ProductCost)
    VendorAny = orm.aliased(model.Vendor)

    # same, but for prices
    RegularPrice = orm.aliased(model.ProductPrice)
    CurrentPrice = orm.aliased(model.ProductPrice)
    SalePrice = orm.aliased(model.ProductPrice)
    TPRPrice = orm.aliased(model.ProductPrice)

    def __init__(self, request):
        super(ProductView, self).__init__(request)
        self.expose_label_printing = self.rattail_config.getbool(
            'tailbone', 'products.print_labels', default=False)

        app = self.get_rattail_app()
        self.product_handler = app.get_products_handler()
        # TODO: deprecate / remove this
        self.handler = self.product_handler

    def query(self, session):
        user = self.request.user
        if user and user not in session:
            user = session.merge(user)

        query = session.query(model.Product)
        # TODO: was this old `has_permission()` call here for a reason..? hope not..
        # if not auth.has_permission(session, user, 'products.view_deleted'):
        if not self.request.has_perm('products.view_deleted'):
            query = query.filter(model.Product.deleted == False)

        # TODO: This used to be a good idea I thought...but in dev it didn't
        # seem to make much difference, except with a larger (50K) data set it
        # totally bogged things down instead of helping...
        # query = query\
        #     .options(orm.joinedload(model.Product.brand))\
        #     .options(orm.joinedload(model.Product.department))\
        #     .options(orm.joinedload(model.Product.subdepartment))\
        #     .options(orm.joinedload(model.Product.regular_price))\
        #     .options(orm.joinedload(model.Product.current_price))\
        #     .options(orm.joinedload(model.Product.vendor))

        query = query.outerjoin(model.ProductInventory)

        return query

    def get_departments(self):
        """
        Returns the list of departments to be exposed in a drop-down.
        """
        model = self.model
        return self.Session.query(model.Department)\
                           .filter(sa.or_(
                               model.Department.product == True,
                               model.Department.product == None))\
                           .order_by(model.Department.name)\
                           .all()

    def configure_grid(self, g):
        super(ProductView, self).configure_grid(g)
        app = self.get_rattail_app()
        use_buefy = self.get_use_buefy()

        def join_vendor(q):
            return q.outerjoin(self.ProductVendorCost,
                               sa.and_(
                                   self.ProductVendorCost.product_uuid == model.Product.uuid,
                                   self.ProductVendorCost.preference == 1))\
                    .outerjoin(model.Vendor)

        def join_vendor_any(q):
            return q.outerjoin(self.ProductVendorCostAny,
                               self.ProductVendorCostAny.product_uuid == model.Product.uuid)\
                    .outerjoin(self.VendorAny,
                               self.VendorAny.uuid == self.ProductVendorCostAny.vendor_uuid)

        ProductCostCode = orm.aliased(model.ProductCost)
        ProductCostCodeAny = orm.aliased(model.ProductCost)

        def join_vendor_code(q):
            return q.outerjoin(ProductCostCode,
                               sa.and_(
                                   ProductCostCode.product_uuid == model.Product.uuid,
                                   ProductCostCode.preference == 1))

        def join_vendor_code_any(q):
            return q.outerjoin(ProductCostCodeAny,
                               ProductCostCodeAny.product_uuid == model.Product.uuid)

        g.joiners['brand'] = lambda q: q.outerjoin(model.Brand)

        # department
        g.set_joiner('department', lambda q: q.outerjoin(model.Department))
        g.set_sorter('department', model.Department.name)
        departments = self.get_departments()
        department_choices = OrderedDict([('', "(any)")]
                                         + [(d.uuid, d.name) for d in departments])
        if not use_buefy:
            department_choices = [tags.Option(name, uuid)
                                  for uuid, name in six.iteritems(department_choices)]
        g.set_filter('department', model.Department.uuid,
                     value_enum=department_choices,
                     verbs=['equal', 'not_equal', 'is_null', 'is_not_null', 'is_any'],
                     default_active=True, default_verb='equal')

        g.joiners['subdepartment'] = lambda q: q.outerjoin(model.Subdepartment,
                                                           model.Subdepartment.uuid == model.Product.subdepartment_uuid)
        g.joiners['code'] = lambda q: q.outerjoin(model.ProductCode)
        g.joiners['vendor'] = join_vendor
        g.joiners['vendor_any'] = join_vendor_any
        g.joiners['vendor_code'] = join_vendor_code
        g.joiners['vendor_code_any'] = join_vendor_code_any

        g.sorters['brand'] = g.make_sorter(model.Brand.name)
        g.sorters['subdepartment'] = g.make_sorter(model.Subdepartment.name)
        g.sorters['vendor'] = g.make_sorter(model.Vendor.name)

        ProductTrueCost = orm.aliased(model.ProductVolatile)
        ProductTrueMargin = orm.aliased(model.ProductVolatile)

        # true_cost
        g.set_joiner('true_cost', lambda q: q.outerjoin(ProductTrueCost))
        g.set_filter('true_cost', ProductTrueCost.true_cost)
        g.set_sorter('true_cost', ProductTrueCost.true_cost)
        g.set_renderer('true_cost', self.render_true_cost)

        # true_margin
        g.set_joiner('true_margin', lambda q: q.outerjoin(ProductTrueMargin))
        g.set_filter('true_margin', ProductTrueMargin.true_margin)
        g.set_sorter('true_margin', ProductTrueMargin.true_margin)
        g.set_renderer('true_margin', self.render_true_margin)

        # on_hand
        g.set_sorter('on_hand', model.ProductInventory.on_hand)
        g.set_filter('on_hand', model.ProductInventory.on_hand)

        # on_order
        g.set_sorter('on_order', model.ProductInventory.on_order)
        g.set_filter('on_order', model.ProductInventory.on_order)

        g.filters['upc'].default_active = True
        g.filters['upc'].default_verb = 'equal'
        g.filters['description'].default_active = True
        g.filters['description'].default_verb = 'contains'
        g.filters['brand'] = g.make_filter('brand', model.Brand.name,
                                           default_active=True, default_verb='contains')
        g.filters['subdepartment'] = g.make_filter('subdepartment', model.Subdepartment.name)
        g.filters['code'] = g.make_filter('code', model.ProductCode.code)
        g.filters['vendor'] = g.make_filter('vendor', model.Vendor.name)
        g.filters['vendor_any'] = g.make_filter('vendor_any', self.VendorAny.name)
                                                # factory=VendorAnyFilter, joiner=join_vendor_any)
        g.filters['vendor_code'] = g.make_filter('vendor_code', ProductCostCode.code)
        g.filters['vendor_code_any'] = g.make_filter('vendor_code_any', ProductCostCodeAny.code)

        # category
        g.set_joiner('category', lambda q: q.outerjoin(model.Category))
        g.set_filter('category', model.Category.name)

        # family
        g.set_joiner('family', lambda q: q.outerjoin(model.Family))
        g.set_filter('family', model.Family.name)

        g.set_label('regular_price', "Reg. Price")
        g.set_joiner('regular_price', lambda q: q.outerjoin(
            self.RegularPrice, self.RegularPrice.uuid == model.Product.regular_price_uuid))
        g.set_sorter('regular_price', self.RegularPrice.price)
        g.set_filter('regular_price', self.RegularPrice.price, label="Regular Price")

        g.set_label('current_price', "Cur. Price")
        g.set_renderer('current_price', self.render_current_price_for_grid)
        g.set_joiner('current_price', lambda q: q.outerjoin(
            self.CurrentPrice, self.CurrentPrice.uuid == model.Product.current_price_uuid))
        g.set_sorter('current_price', self.CurrentPrice.price)
        g.set_filter('current_price', self.CurrentPrice.price, label="Current Price")

        # tpr_price
        g.set_joiner('tpr_price', lambda q: q.outerjoin(
            self.TPRPrice, self.TPRPrice.uuid == model.Product.tpr_price_uuid))
        g.set_filter('tpr_price', self.TPRPrice.price)

        # sale_price
        g.set_joiner('sale_price', lambda q: q.outerjoin(
            self.SalePrice, self.SalePrice.uuid == model.Product.sale_price_uuid))
        g.set_filter('sale_price', self.SalePrice.price)

        # suggested_price
        g.set_renderer('suggested_price', self.render_grid_suggested_price)

        # (unit) cost
        g.set_joiner('cost', lambda q: q.outerjoin(model.ProductCost,
                                                   sa.and_(
                                                       model.ProductCost.product_uuid == model.Product.uuid,
                                                       model.ProductCost.preference == 1)))
        g.set_sorter('cost', model.ProductCost.unit_cost)
        g.set_filter('cost', model.ProductCost.unit_cost)
        g.set_renderer('cost', self.render_cost)
        g.set_label('cost', "Unit Cost")

        # report_code_name
        g.set_joiner('report_code_name', lambda q: q.outerjoin(model.ReportCode))
        g.set_filter('report_code_name', model.ReportCode.name)

        g.set_sort_defaults('upc')

        if self.expose_label_printing and self.has_perm('print_labels'):
            if use_buefy:
                g.more_actions.append(self.make_action(
                    'print_label', icon='print', url='#',
                    click_handler='quickLabelPrint(props.row)'))
            else:
                g.more_actions.append(grids.GridAction('print_label', icon='print'))

        g.set_type('upc', 'gpc')

        g.set_renderer('regular_price', self.render_price)
        g.set_renderer('on_hand', self.render_on_hand)
        g.set_renderer('on_order', self.render_on_order)

        g.set_link('upc')
        g.set_link('item_id')
        g.set_link('description')

        g.set_label('vendor', "Vendor (preferred)")
        g.set_label('vendor_any', "Vendor (any)")
        g.set_label('vendor', "Pref. Vendor")

    def configure_common_form(self, f):
        super(ProductView, self).configure_common_form(f)
        product = f.model_instance

        # upc
        f.set_type('upc', 'gpc')

        # unit_size
        f.set_type('unit_size', 'quantity')

        # unit_of_measure
        f.set_enum('unit_of_measure', self.enum.UNIT_OF_MEASURE)
        f.set_label('unit_of_measure', "Unit of Measure")

        # packs
        if self.creating:
            f.remove_field('packs')
        elif self.viewing and product.packs:
            f.set_renderer('packs', self.render_packs)
            f.set_label('packs', "Pack Items")
        else:
            f.remove_field('packs')

        # pack_size
        if self.viewing and not product.is_pack_item():
            f.remove_field('pack_size')
        else:
            f.set_type('pack_size', 'quantity')

        # default_pack
        if self.viewing and not product.is_pack_item():
            f.remove_field('default_pack')

        # unit
        if self.creating:
            f.remove_field('unit')
        elif self.viewing and product.is_pack_item():
            f.set_renderer('unit', self.render_unit)
            f.set_label('unit', "Unit Item")
        else:
            f.remove_field('unit')

        # suggested_price
        if self.creating:
            f.remove_field('suggested_price')
        else:
            f.set_readonly('suggested_price')
            f.set_renderer('suggested_price', self.render_suggested_price)

        # regular_price
        if self.creating:
            f.remove_field('regular_price')
        else:
            f.set_readonly('regular_price')
            f.set_renderer('regular_price', self.render_regular_price)

        # current_price
        if self.creating:
            f.remove_field('current_price')
        else:
            f.set_readonly('current_price')
            f.set_renderer('current_price', self.render_current_price)

        # current_price_ends
        if self.creating:
            f.remove_field('current_price_ends')
        else:
            f.set_readonly('current_price_ends')
            f.set_renderer('current_price_ends', self.render_current_price_ends)

        # sale_price
        if self.creating:
            f.remove_field('sale_price')
        else:
            f.set_readonly('sale_price')
            f.set_renderer('sale_price', self.render_price)

        # sale_price_ends
        if self.creating:
            f.remove_field('sale_price_ends')
        else:
            f.set_readonly('sale_price_ends')
            f.set_renderer('sale_price_ends', self.render_sale_price_ends)

        # tpr_price
        if self.creating:
            f.remove_field('tpr_price')
        else:
            f.set_readonly('tpr_price')
            f.set_renderer('tpr_price', self.render_price)

        # tpr_price_ends
        if self.creating:
            f.remove_field('tpr_price_ends')
        else:
            f.set_readonly('tpr_price_ends')
            f.set_renderer('tpr_price_ends', self.render_tpr_price_ends)

        # vendor
        if self.creating:
            f.remove_field('vendor')
        else:
            f.set_readonly('vendor')
            f.set_label('vendor', "Preferred Vendor")

        # cost
        if self.creating:
            f.remove_field('cost')
        else:
            f.set_readonly('cost')
            f.set_label('cost', "Preferred Unit Cost")
            f.set_renderer('cost', self.render_cost)

        # last_sold
        if self.creating:
            f.remove_field('last_sold')
        else:
            f.set_readonly('last_sold')

        # inventory_on_hand
        if self.creating:
            f.remove_field('inventory_on_hand')
        else:
            f.set_readonly('inventory_on_hand')
            f.set_renderer('inventory_on_hand', self.render_inventory_on_hand)
            f.set_label('inventory_on_hand', "On Hand")

        # inventory_on_order
        if self.creating:
            f.remove_field('inventory_on_order')
        else:
            f.set_readonly('inventory_on_order')
            f.set_renderer('inventory_on_order', self.render_inventory_on_order)
            f.set_label('inventory_on_order', "On Order")

    def render_cost(self, product, field):
        cost = getattr(product, field)
        if not cost:
            return ""
        if cost.unit_cost is None:
            return ""
        return "${:0.2f}".format(cost.unit_cost)

    def render_price(self, product, field):
        if not product.not_for_sale:
            price = product[field]
            if price:
                return self.product_handler.render_price(price)
        
    def render_current_price_for_grid(self, product, field):
        text = self.render_price(product, field) or ""

        price = product.current_price
        if price:
            app = self.get_rattail_app()

            if price.starts:
                starts = localtime(self.rattail_config, price.starts, from_utc=True)
                starts = app.render_date(starts.date())
            else:
                starts = "??"

            if price.ends:
                ends = localtime(self.rattail_config, price.ends, from_utc=True)
                ends = app.render_date(ends.date())
            else:
                ends = "??"

            return HTML.tag('span', c=text,
                            title="{} thru {}".format(starts, ends))

        return text

    def add_price_history_link(self, text, typ):
        if not self.rattail_config.versioning_enabled():
            return text
        if not self.has_perm('versions'):
            return text

        if self.get_use_buefy():
            kwargs = {'@click.prevent': 'showPriceHistory_{}()'.format(typ)}
        else:
            kwargs = {'id': 'view-{}-price-history'.format(typ)}
        history = tags.link_to("(view history)", '#', **kwargs)
        if not text:
            return history

        text = HTML.tag('span', c=[text])
        br = HTML.tag('br')
        return HTML.tag('div', c=[text, br, history])

    def show_price_effective_dates(self):
        if not self.rattail_config.versioning_enabled():
            return False
        return self.rattail_config.getbool(
            'tailbone', 'products.show_effective_price_dates',
            default=True)

    def render_regular_price(self, product, field):
        text = self.render_price(product, field)

        if text and self.show_price_effective_dates():
            history = self.get_regular_price_history(product)
            if history:
                date = localtime(self.rattail_config, history[0]['changed'], from_utc=True).date()
                text = "{} (as of {})".format(text, date)

        return self.add_price_history_link(text, 'regular')

    def render_current_price(self, product, field):
        text = self.render_price(product, field)

        if text and self.show_price_effective_dates():
            history = self.get_current_price_history(product)
            if history:
                date = localtime(self.rattail_config, history[0]['changed'], from_utc=True).date()
                text = "{} (as of {})".format(text, date)

        return self.add_price_history_link(text, 'current')

    def warn_if_regprice_more_than_srp(self, product, text):
        sugprice = product.suggested_price.price if product.suggested_price else None
        regprice = product.regular_price.price if product.regular_price else None
        if sugprice and regprice and sugprice < regprice:
            return HTML.tag('span', style='color: red;', c=text)
        return text

    def render_suggested_price(self, product, column):
        text = self.render_price(product, column)
        if not text:
            return

        if self.show_price_effective_dates():
            history = self.get_suggested_price_history(product)
            if history:
                date = localtime(self.rattail_config, history[0]['changed'], from_utc=True).date()
                text = "{} (as of {})".format(text, date)

        text = self.warn_if_regprice_more_than_srp(product, text)
        return self.add_price_history_link(text, 'suggested')

    def render_grid_suggested_price(self, product, field):
        text = self.render_price(product, field)
        if not text:
            return ""

        text = self.warn_if_regprice_more_than_srp(product, text)
        return text

    def render_true_cost(self, product, field):
        if not product.volatile:
            return ""
        if product.volatile.true_cost is None:
            return ""
        return "${:0.3f}".format(product.volatile.true_cost)

    def render_true_margin(self, product, field):
        if not product.volatile:
            return ""
        if product.volatile.true_margin is None:
            return ""
        return "{:0.3f} %".format(product.volatile.true_margin * 100)

    def render_on_hand(self, product, column):
        inventory = product.inventory
        if not inventory:
            return ""
        return pretty_quantity(inventory.on_hand)

    def render_on_order(self, product, column):
        inventory = product.inventory
        if not inventory:
            return ""
        return pretty_quantity(inventory.on_order)

    def template_kwargs_index(self, **kwargs):
        kwargs = super(ProductView, self).template_kwargs_index(**kwargs)
        model = self.model

        if self.expose_label_printing:

            kwargs['label_profiles'] = self.Session.query(model.LabelProfile)\
                                                   .filter(model.LabelProfile.visible == True)\
                                                   .order_by(model.LabelProfile.ordinal)\
                                                   .all()

            kwargs['quick_label_speedbump_threshold'] = self.rattail_config.getint(
                'tailbone', 'products.quick_labels.speedbump_threshold')

        return kwargs

    def grid_extra_class(self, product, i):
        classes = []
        if product.not_for_sale:
            classes.append('not-for-sale')
        if product.discontinued:
            classes.append('discontinued')
        if product.deleted:
            classes.append('deleted')
        if classes:
            return ' '.join(classes)

    def get_xlsx_fields(self):
        fields = super(ProductView, self).get_xlsx_fields()

        i = fields.index('department_uuid')
        fields.insert(i + 1, 'department_number')
        fields.insert(i + 2, 'department_name')

        i = fields.index('subdepartment_uuid')
        fields.insert(i + 1, 'subdepartment_number')
        fields.insert(i + 2, 'subdepartment_name')

        i = fields.index('category_uuid')
        fields.insert(i + 1, 'category_code')

        i = fields.index('family_uuid')
        fields.insert(i + 1, 'family_code')

        i = fields.index('report_code_uuid')
        fields.insert(i + 1, 'report_code')

        i = fields.index('deposit_link_uuid')
        fields.insert(i + 1, 'deposit_link_code')

        i = fields.index('tax_uuid')
        fields.insert(i + 1, 'tax_code')

        i = fields.index('brand_uuid')
        fields.insert(i + 1, 'brand_name')

        i = fields.index('suggested_price_uuid')
        fields.insert(i + 1, 'suggested_price')

        i = fields.index('regular_price_uuid')
        fields.insert(i + 1, 'regular_price')

        i = fields.index('current_price_uuid')
        fields.insert(i + 1, 'current_price')

        fields.append('vendor_uuid')
        fields.append('vendor_id')
        fields.append('vendor_name')
        fields.append('vendor_item_code')
        fields.append('unit_cost')
        fields.append('true_margin')

        return fields

    def get_xlsx_row(self, product, fields):
        row = super(ProductView, self).get_xlsx_row(product, fields)

        if 'upc' in fields and isinstance(row['upc'], GPC):
            row['upc'] = row['upc'].pretty()

        if 'department_number' in fields:
            row['department_number'] = product.department.number if product.department else None
        if 'department_name' in fields:
            row['department_name'] = product.department.name if product.department else None

        if 'subdepartment_number' in fields:
            row['subdepartment_number'] = product.subdepartment.number if product.subdepartment else None
        if 'subdepartment_name' in fields:
            row['subdepartment_name'] = product.subdepartment.name if product.subdepartment else None

        if 'category_code' in fields:
            row['category_code'] = product.category.code if product.category else None

        if 'family_code' in fields:
            row['family_code'] = product.family.code if product.family else None

        if 'report_code' in fields:
            row['report_code'] = product.report_code.code if product.report_code else None

        if 'deposit_link_code' in fields:
            row['deposit_link_code'] = product.deposit_link.code if product.deposit_link else None

        if 'tax_code' in fields:
            row['tax_code'] = product.tax.code if product.tax else None

        if 'brand_name' in fields:
            row['brand_name'] = product.brand.name if product.brand else None

        if 'suggested_price' in fields:
            row['suggested_price'] = product.suggested_price.price if product.suggested_price else None

        if 'regular_price' in fields:
            row['regular_price'] = product.regular_price.price if product.regular_price else None

        if 'current_price' in fields:
            row['current_price'] = product.current_price.price if product.current_price else None

        if 'vendor_uuid' in fields:
            row['vendor_uuid'] = product.cost.vendor.uuid if product.cost else None

        if 'vendor_id' in fields:
            row['vendor_id'] = product.cost.vendor.id if product.cost else None

        if 'vendor_name' in fields:
            row['vendor_name'] = product.cost.vendor.name if product.cost else None

        if 'vendor_item_code' in fields:
            row['vendor_item_code'] = product.cost.code if product.cost else None

        if 'unit_cost' in fields:
            row['unit_cost'] = product.cost.unit_cost if product.cost else None

        if 'true_margin' in fields:
            row['true_margin'] = None
            if product.volatile and product.volatile.true_margin:
                row['true_margin'] = product.volatile.true_margin

        return row

    def download_results_normalize(self, product, fields, **kwargs):
        data = super(ProductView, self).download_results_normalize(
            product, fields, **kwargs)

        if 'upc' in data:
            if isinstance(data['upc'], GPC):
                data['upc'] = six.text_type(data['upc'])

        return data

    def get_instance(self):
        key = self.request.matchdict['uuid']
        product = self.Session.query(model.Product).get(key)
        if product:
            return product
        price = self.Session.query(model.ProductPrice).get(key)
        if price:
            return price.product
        raise httpexceptions.HTTPNotFound()

    def configure_form(self, f):
        super(ProductView, self).configure_form(f)
        product = f.model_instance

        # department
        if self.creating or self.editing:
            if 'department' in f.fields:
                f.replace('department', 'department_uuid')
                departments = self.get_departments()
                dept_values = [(d.uuid, "{} {}".format(d.number, d.name))
                               for d in departments]
                require_department = False
                if not require_department:
                    dept_values.insert(0, ('', "(none)"))
                f.set_widget('department_uuid', dfwidget.SelectWidget(values=dept_values))
                f.set_label('department_uuid', "Department")
        else:
            f.set_readonly('department')
            f.set_renderer('department', self.render_department)

        # subdepartment
        if self.creating or self.editing:
            if 'subdepartment' in f.fields:
                f.replace('subdepartment', 'subdepartment_uuid')
                subdepartments = self.Session.query(model.Subdepartment)\
                                          .order_by(model.Subdepartment.number)
                subdept_values = [(s.uuid, "{} {}".format(s.number, s.name))
                                  for s in subdepartments]
                require_subdepartment = False
                if not require_subdepartment:
                    subdept_values.insert(0, ('', "(none)"))
                f.set_widget('subdepartment_uuid', dfwidget.SelectWidget(values=subdept_values))
                f.set_label('subdepartment_uuid', "Subdepartment")
        else:
            f.set_readonly('subdepartment')
            f.set_renderer('subdepartment', self.render_subdepartment)

        # category
        if self.creating or self.editing:
            if 'category' in f.fields:
                f.replace('category', 'category_uuid')
                categories = self.Session.query(model.Category)\
                                          .order_by(model.Category.code)
                category_values = [(c.uuid, "{} {}".format(c.code, c.name))
                                   for c in categories]
                require_category = False
                if not require_category:
                    category_values.insert(0, ('', "(none)"))
                f.set_widget('category_uuid', dfwidget.SelectWidget(values=category_values))
                f.set_label('category_uuid', "Category")
        else:
            f.set_readonly('category')
            f.set_renderer('category', self.render_category)

        # family
        if self.creating or self.editing:
            if 'family' in f.fields:
                f.replace('family', 'family_uuid')
                families = self.Session.query(model.Family)\
                                          .order_by(model.Family.name)
                family_values = [(fam.uuid, fam.name) for fam in families]
                require_family = False
                if not require_family:
                    family_values.insert(0, ('', "(none)"))
                f.set_widget('family_uuid', dfwidget.SelectWidget(values=family_values))
                f.set_label('family_uuid', "Family")
        else:
            f.set_readonly('family')
            # f.set_renderer('family', self.render_family)

        # report_code
        if self.creating or self.editing:
            if 'report_code' in f.fields:
                f.replace('report_code', 'report_code_uuid')
                report_codes = self.Session.query(model.ReportCode)\
                                          .order_by(model.ReportCode.code)
                report_code_values = [(rc.uuid, "{} {}".format(rc.code, rc.name))
                                      for rc in report_codes]
                require_report_code = False
                if not require_report_code:
                    report_code_values.insert(0, ('', "(none)"))
                f.set_widget('report_code_uuid', dfwidget.SelectWidget(values=report_code_values))
                f.set_label('report_code_uuid', "Report Code")
        else:
            f.set_readonly('report_code')
            # f.set_renderer('report_code', self.render_report_code)

        # regular_price_amount
        if self.editing:
            f.set_node('regular_price_amount', colander.Decimal())
            f.set_default('regular_price_amount', product.regular_price.price if product.regular_price else None)
            f.set_label('regular_price_amount', "Regular Price")

        # deposit_link
        if self.creating or self.editing:
            if 'deposit_link' in f.fields:
                f.replace('deposit_link', 'deposit_link_uuid')
                deposit_links = self.Session.query(model.DepositLink)\
                                          .order_by(model.DepositLink.code)
                deposit_link_values = [(dl.uuid, "{} {}".format(dl.code, dl.description))
                                      for dl in deposit_links]
                require_deposit_link = False
                if not require_deposit_link:
                    deposit_link_values.insert(0, ('', "(none)"))
                f.set_widget('deposit_link_uuid', dfwidget.SelectWidget(values=deposit_link_values))
                f.set_label('deposit_link_uuid', "Deposit Link")
        else:
            f.set_readonly('deposit_link')
            # f.set_renderer('deposit_link', self.render_deposit_link)

        # tax
        if self.creating or self.editing:
            if 'tax' in f.fields:
                f.replace('tax', 'tax_uuid')
                taxes = self.Session.query(model.Tax)\
                                          .order_by(model.Tax.code)
                tax_values = [(tax.uuid, "{} {}".format(tax.code, tax.description))
                              for tax in taxes]
                require_tax = False
                if not require_tax:
                    tax_values.insert(0, ('', "(none)"))
                f.set_widget('tax_uuid', dfwidget.SelectWidget(values=tax_values))
                f.set_label('tax_uuid', "Tax")
        else:
            f.set_readonly('tax')
            # f.set_renderer('tax', self.render_tax)

        # tax1/2/3
        f.set_readonly('tax1')
        f.set_readonly('tax2')
        f.set_readonly('tax3')

        # brand
        if self.creating or self.editing:
            if 'brand' in f.fields:
                f.replace('brand', 'brand_uuid')
                f.set_node('brand_uuid', colander.String(), missing=colander.null)
                brand_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('brand_uuid'):
                        brand = self.Session.query(model.Brand).get(self.request.POST['brand_uuid'])
                        if brand:
                            brand_display = six.text_type(brand)
                elif self.editing:
                    brand_display = six.text_type(product.brand or '')
                brands_url = self.request.route_url('brands.autocomplete')
                f.set_widget('brand_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=brand_display, service_url=brands_url))
                f.set_label('brand_uuid', "Brand")
        else:
            f.set_readonly('brand')

        # case_size
        f.set_type('case_size', 'quantity')

        # status_code
        f.set_label('status_code', "Status")

        # ingredients
        f.set_widget('ingredients', dfwidget.TextAreaWidget(cols=80, rows=10))

        # notes
        f.set_widget('notes', dfwidget.TextAreaWidget(cols=80, rows=10))

        if not self.request.has_perm('products.view_deleted'):
            f.remove('deleted')

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated
        product = super(ProductView, self).objectify(form, data=data)

        # regular_price_amount
        if (self.creating or self.editing) and 'regular_price_amount' in form.fields:
            api.set_regular_price(product, data['regular_price_amount'])

        return product

    def render_department(self, product, field):
        department = product.department
        if not department:
            return ""
        if department.number:
            text = '({}) {}'.format(department.number, department.name)
        else:
            text = department.name
        url = self.request.route_url('departments.view', uuid=department.uuid)
        return tags.link_to(text, url)

    def render_subdepartment(self, product, field):
        subdepartment = product.subdepartment
        if not subdepartment:
            return ""
        if subdepartment.number:
            text = '({}) {}'.format(subdepartment.number, subdepartment.name)
        else:
            text = subdepartment.name
        url = self.request.route_url('subdepartments.view', uuid=subdepartment.uuid)
        return tags.link_to(text, url)

    def render_category(self, product, field):
        category = product.category
        if not category:
            return ""
        if category.code:
            text = '({}) {}'.format(category.code, category.name)
        elif category.number:
            text = '({}) {}'.format(category.number, category.name)
        else:
            text = category.name
        url = self.request.route_url('categories.view', uuid=category.uuid)
        return tags.link_to(text, url)

    def render_packs(self, product, field):
        if product.is_pack_item():
            return ""

        links = []
        for pack in product.packs:
            if pack.upc:
                code = pack.upc.pretty()
            elif pack.scancode:
                code = pack.scancode
            else:
                code = pack.item_id
            text = "({}) {}".format(code, pack.full_description)
            url = self.get_action_url('view', pack)
            links.append(tags.link_to(text, url))

        items = [HTML.tag('li', c=[link]) for link in links]
        return HTML.tag('ul', c=items)

    def render_unit(self, product, field):
        unit = product.unit
        if not unit:
            return ""

        if unit.upc:
            code = unit.upc.pretty()
        elif unit.scancode:
            code = unit.scancode
        else:
            code = unit.item_id

        text = "({}) {}".format(code, unit.full_description)
        url = self.get_action_url('view', unit)
        return tags.link_to(text, url)

    def render_current_price_ends(self, product, field):
        if not product.current_price:
            return ""
        value = product.current_price.ends
        if not value:
            return ""
        return raw_datetime(self.request.rattail_config, value)

    def render_sale_price_ends(self, product, field):
        if not product.sale_price:
            return
        ends = product.sale_price.ends
        if not ends:
            return
        return raw_datetime(self.rattail_config, ends)

    def render_tpr_price_ends(self, product, field):
        if not product.tpr_price:
            return
        ends = product.tpr_price.ends
        if not ends:
            return
        return raw_datetime(self.rattail_config, ends)

    def render_inventory_on_hand(self, product, field):
        if not product.inventory:
            return ""
        value = product.inventory.on_hand
        if not value:
            return ""
        return pretty_quantity(value)

    def render_inventory_on_order(self, product, field):
        if not product.inventory:
            return ""
        value = product.inventory.on_order
        if not value:
            return ""
        return pretty_quantity(value)

    def price_history(self):
        """
        AJAX view for fetching various types of price history for a product.
        """
        app = self.get_rattail_app()
        product = self.get_instance()

        typ = self.request.params.get('type', 'regular')
        assert typ in ('regular', 'current', 'suggested')

        getter = getattr(self, 'get_{}_price_history'.format(typ))
        data = getter(product)

        # make some data JSON-friendly
        jsdata = []
        for history in data:
            history = dict(history)
            price = history['price']
            if price is not None:
                history['price'] = float(price)
                history['price_display'] = app.render_currency(price)
            changed = localtime(self.rattail_config, history['changed'], from_utc=True)
            history['changed'] = six.text_type(changed)
            history['changed_display_html'] = raw_datetime(self.rattail_config, changed)
            user = history.pop('changed_by')
            history['changed_by_uuid'] = user.uuid if user else None
            history['changed_by_display'] = six.text_type(user or "??")
            jsdata.append(history)
        return jsdata

    def cost_history(self):
        """
        AJAX view for fetching cost history for a product.
        """
        product = self.get_instance()
        data = self.get_cost_history(product)

        # make some data JSON-friendly
        jsdata = []
        for history in data:
            history = dict(history)
            cost = history['cost']
            if cost is not None:
                history['cost'] = float(cost)
                history['cost_display'] = "${:0.2f}".format(cost)
            else:
                history['cost_display'] = None
            changed = localtime(self.rattail_config, history['changed'], from_utc=True)
            history['changed'] = six.text_type(changed)
            history['changed_display_html'] = raw_datetime(self.rattail_config, changed)
            user = history.pop('changed_by')
            history['changed_by_uuid'] = user.uuid
            history['changed_by_display'] = six.text_type(user)
            jsdata.append(history)
        return jsdata

    def template_kwargs_view(self, **kwargs):
        product = kwargs['instance']
        use_buefy = self.get_use_buefy()

        kwargs['image_url'] = self.product_handler.get_image_url(product)
        kwargs['product_key_field'] = self.rattail_config.product_key()

        # add price history, if user has access
        if self.rattail_config.versioning_enabled() and self.has_perm('versions'):

            # regular price
            if use_buefy:
                data = []       # defer fetching until user asks for it
            else:
                data = self.get_regular_price_history(product)
            grid = grids.Grid('products.regular_price_history', data,
                              request=self.request,
                              columns=[
                                  'price',
                                  'since',
                                  'changed',
                                  'changed_by',
                              ])
            grid.set_type('price', 'currency')
            grid.set_type('changed', 'datetime')
            kwargs['regular_price_history_grid'] = grid

            # current price
            if use_buefy:
                data = []       # defer fetching until user asks for it
            else:
                data = self.get_current_price_history(product)
            grid = grids.Grid('products.current_price_history', data,
                              request=self.request,
                              columns=[
                                  'price',
                                  'price_type',
                                  'since',
                                  'changed',
                                  'changed_by',
                              ],
                              labels={
                                  'price_type': "Type",
                              })
            grid.set_type('price', 'currency')
            grid.set_type('changed', 'datetime')
            kwargs['current_price_history_grid'] = grid

            # suggested price
            if use_buefy:
                data = []       # defer fetching until user asks for it
            else:
                data = self.get_suggested_price_history(product)
            grid = grids.Grid('products.suggested_price_history', data,
                              request=self.request,
                              columns=[
                                  'price',
                                  'since',
                                  'changed',
                                  'changed_by',
                              ])
            grid.set_type('price', 'currency')
            grid.set_type('changed', 'datetime')
            kwargs['suggested_price_history_grid'] = grid

            # cost history
            if use_buefy:
                data = []       # defer fetching until user asks for it
            else:
                data = self.get_cost_history(product)
            grid = grids.Grid('products.cost_history', data,
                              request=self.request,
                              columns=[
                                  'cost',
                                  'vendor',
                                  'since',
                                  'changed',
                                  'changed_by',
                              ],
                              labels={
                                  'price_type': "Type",
                              })
            grid.set_type('cost', 'currency')
            grid.set_type('changed', 'datetime')
            kwargs['cost_history_grid'] = grid

        kwargs['costs_label_preferred'] = "Pref."
        kwargs['costs_label_vendor'] = "Vendor"
        kwargs['costs_label_code'] = "Order Code"
        kwargs['costs_label_case_size'] = "Case Size"

        if use_buefy:
            kwargs['vendor_sources'] = self.get_context_vendor_sources(product)
            kwargs['lookup_codes'] = self.get_context_lookup_codes(product)

        return kwargs

    def get_context_vendor_sources(self, product):
        app = self.get_rattail_app()
        route_prefix = self.get_route_prefix()

        factory = self.get_grid_factory()
        g = factory(
            key='{}.vendor_sources'.format(route_prefix),
            data=[],
            columns=[
                'preferred',
                'vendor',
                'vendor_item_code',
                'case_size',
                'case_cost',
                'unit_cost',
                'status',
            ],
            labels={
                'preferred': "Pref.",
                'vendor_item_code': "Order Code",
            },
        )

        sources = []
        link_vendor = self.request.has_perm('vendors.view')
        for cost in product.costs:

            source = {
                'uuid': cost.uuid,
                'preferred': "X" if cost.preference == 1 else None,
                'vendor_item_code': cost.code,
                'case_size': app.render_quantity(cost.case_size),
                'case_cost': app.render_currency(cost.case_cost),
                'unit_cost': app.render_currency(cost.unit_cost, scale=4),
                'status': "discontinued" if cost.discontinued else "available",
            }

            text = six.text_type(cost.vendor)
            if link_vendor:
                url = self.request.route_url('vendors.view', uuid=cost.vendor.uuid)
                source['vendor'] = tags.link_to(text, url)
            else:
                source['vendor'] = text

            sources.append(source)

        return {'grid': g, 'data': sources}

    def get_context_lookup_codes(self, product):
        route_prefix = self.get_route_prefix()

        factory = self.get_grid_factory()
        g = factory(
            key='{}.lookup_codes'.format(route_prefix),
            data=[],
            columns=[
                'sequence',
                'code',
            ],
            labels={
                'sequence': "Seq.",
            },
        )

        lookup_codes = []
        for code in product._codes:

            lookup_codes.append({
                'uuid': code.uuid,
                'sequence': code.ordinal,
                'code': code.code,
            })

        return {'grid': g, 'data': lookup_codes}

    def get_regular_price_history(self, product):
        """
        Returns a sequence of "records" which corresponds to the given
        product's regular price history.
        """
        Transaction = continuum.transaction_class(model.Product)
        ProductVersion = continuum.version_class(model.Product)
        ProductPriceVersion = continuum.version_class(model.ProductPrice)
        now = make_utc()
        history = []

        # first we find all relevant ProductVersion records
        versions = self.Session.query(ProductVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductVersion.transaction_id)\
                               .filter(ProductVersion.uuid == product.uuid)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_uuid = None
        for version in versions:
            if version.regular_price_uuid != last_uuid:
                changed = version.transaction.issued_at
                if version.regular_price:
                    assert isinstance(version.regular_price, ProductPriceVersion)
                    price = version.regular_price.price
                else:
                    price = None
                history.append({
                    'transaction_id': version.transaction.id,
                    'price': price,
                    'since': humanize.naturaltime(now - changed),
                    'changed': changed,
                    'changed_by': version.transaction.user,
                })
                last_uuid = version.regular_price_uuid

        # next we find all relevant ProductPriceVersion records
        versions = self.Session.query(ProductPriceVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductPriceVersion.transaction_id)\
                               .filter(ProductPriceVersion.product_uuid == product.uuid)\
                               .filter(ProductPriceVersion.type == self.enum.PRICE_TYPE_REGULAR)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_price = None
        for version in versions:
            if version.price != last_price:
                changed = version.transaction.issued_at
                price = version.price
                history.append({
                    'transaction_id': version.transaction.id,
                    'price': version.price,
                    'since': humanize.naturaltime(now - changed),
                    'changed': changed,
                    'changed_by': version.transaction.user,
                })
                last_price = version.price

        final_history = OrderedDict()
        for hist in sorted(history, key=lambda h: h['changed'], reverse=True):
            if hist['transaction_id'] not in final_history:
                final_history[hist['transaction_id']] = hist

        return list(final_history.values())

    def get_current_price_history(self, product):
        """
        Returns a sequence of "records" which corresponds to the given
        product's current price history.
        """
        Transaction = continuum.transaction_class(model.Product)
        ProductVersion = continuum.version_class(model.Product)
        ProductPriceVersion = continuum.version_class(model.ProductPrice)
        now = make_utc()
        history = []

        # first we find all relevant ProductVersion records
        versions = self.Session.query(ProductVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductVersion.transaction_id)\
                               .filter(ProductVersion.uuid == product.uuid)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_current_uuid = None
        last_regular_uuid = None
        for version in versions:

            changed = False
            if version.current_price_uuid != last_current_uuid:
                changed = True
            elif not version.current_price_uuid and version.regular_price_uuid != last_regular_uuid:
                changed = True

            if changed:
                changed = version.transaction.issued_at
                if version.current_price:
                    assert isinstance(version.current_price, ProductPriceVersion)
                    price = version.current_price.price
                    price_type = self.enum.PRICE_TYPE.get(version.current_price.type)
                elif version.regular_price:
                    price = version.regular_price.price
                    price_type = self.enum.PRICE_TYPE.get(version.regular_price.type)
                else:
                    price = None
                    price_type = None
                history.append({
                    'transaction_id': version.transaction.id,
                    'price': price,
                    'price_type': price_type,
                    'since': humanize.naturaltime(now - changed),
                    'changed': changed,
                    'changed_by': version.transaction.user,
                })

            last_current_uuid = version.current_price_uuid
            last_regular_uuid = version.regular_price_uuid

        # next we find all relevant *SALE* ProductPriceVersion records
        versions = self.Session.query(ProductPriceVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductPriceVersion.transaction_id)\
                               .filter(ProductPriceVersion.product_uuid == product.uuid)\
                               .filter(ProductPriceVersion.type == self.enum.PRICE_TYPE_SALE)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_price = None
        for version in versions:
            # only include this version if it was "current" at the time
            if version.uuid == version.product.current_price_uuid:
                if version.price != last_price:
                    changed = version.transaction.issued_at
                    price = version.price
                    history.append({
                        'transaction_id': version.transaction.id,
                        'price': version.price,
                        'price_type': self.enum.PRICE_TYPE[version.type],
                        'since': humanize.naturaltime(now - changed),
                        'changed': changed,
                        'changed_by': version.transaction.user,
                    })
                    last_price = version.price

        # next we find all relevant *TPR* ProductPriceVersion records
        versions = self.Session.query(ProductPriceVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductPriceVersion.transaction_id)\
                               .filter(ProductPriceVersion.product_uuid == product.uuid)\
                               .filter(ProductPriceVersion.type == self.enum.PRICE_TYPE_TPR)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_price = None
        for version in versions:
            # only include this version if it was "current" at the time
            if version.uuid == version.product.current_price_uuid:
                if version.price != last_price:
                    changed = version.transaction.issued_at
                    price = version.price
                    history.append({
                        'transaction_id': version.transaction.id,
                        'price': version.price,
                        'price_type': self.enum.PRICE_TYPE[version.type],
                        'since': humanize.naturaltime(now - changed),
                        'changed': changed,
                        'changed_by': version.transaction.user,
                    })
                    last_price = version.price

        # next we find all relevant *Regular* ProductPriceVersion records
        versions = self.Session.query(ProductPriceVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductPriceVersion.transaction_id)\
                               .filter(ProductPriceVersion.product_uuid == product.uuid)\
                               .filter(ProductPriceVersion.type == self.enum.PRICE_TYPE_REGULAR)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_price = None
        for version in versions:
            # only include this version if it was "regular" at the time
            if version.uuid == version.product.regular_price_uuid:
                if version.price != last_price:
                    changed = version.transaction.issued_at
                    price = version.price
                    history.append({
                        'transaction_id': version.transaction.id,
                        'price': version.price,
                        'price_type': self.enum.PRICE_TYPE[version.type],
                        'since': humanize.naturaltime(now - changed),
                        'changed': changed,
                        'changed_by': version.transaction.user,
                    })
                    last_price = version.price

        final_history = OrderedDict()
        for hist in sorted(history, key=lambda h: h['changed'], reverse=True):
            if hist['transaction_id'] not in final_history:
                final_history[hist['transaction_id']] = hist

        return list(final_history.values())

    def get_suggested_price_history(self, product):
        """
        Returns a sequence of "records" which corresponds to the given
        product's SRP history.
        """
        Transaction = continuum.transaction_class(model.Product)
        ProductVersion = continuum.version_class(model.Product)
        ProductPriceVersion = continuum.version_class(model.ProductPrice)
        now = make_utc()
        history = []

        # first we find all relevant ProductVersion records
        versions = self.Session.query(ProductVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductVersion.transaction_id)\
                               .filter(ProductVersion.uuid == product.uuid)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_uuid = None
        for version in versions:
            if version.suggested_price_uuid != last_uuid:
                changed = version.transaction.issued_at
                if version.suggested_price:
                    assert isinstance(version.suggested_price, ProductPriceVersion)
                    price = version.suggested_price.price
                else:
                    price = None
                history.append({
                    'transaction_id': version.transaction.id,
                    'price': price,
                    'since': humanize.naturaltime(now - changed),
                    'changed': changed,
                    'changed_by': version.transaction.user,
                })
                last_uuid = version.suggested_price_uuid

        # next we find all relevant ProductPriceVersion records
        versions = self.Session.query(ProductPriceVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductPriceVersion.transaction_id)\
                               .filter(ProductPriceVersion.product_uuid == product.uuid)\
                               .filter(ProductPriceVersion.type == self.enum.PRICE_TYPE_MFR_SUGGESTED)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_price = None
        for version in versions:
            if version.price != last_price:
                changed = version.transaction.issued_at
                price = version.price
                history.append({
                    'transaction_id': version.transaction.id,
                    'price': version.price,
                    'since': humanize.naturaltime(now - changed),
                    'changed': changed,
                    'changed_by': version.transaction.user,
                })
                last_price = version.price

        final_history = OrderedDict()
        for hist in sorted(history, key=lambda h: h['changed'], reverse=True):
            if hist['transaction_id'] not in final_history:
                final_history[hist['transaction_id']] = hist

        return list(final_history.values())

    def get_cost_history(self, product):
        """
        Returns a sequence of "records" which corresponds to the given
        product's cost history.
        """
        Transaction = continuum.transaction_class(model.Product)
        ProductVersion = continuum.version_class(model.Product)
        ProductCostVersion = continuum.version_class(model.ProductCost)
        now = make_utc()
        history = []

        # we just find all relevant (preferred!) ProductCostVersion records
        versions = self.Session.query(ProductCostVersion)\
                               .join(Transaction,
                                     Transaction.id == ProductCostVersion.transaction_id)\
                               .filter(ProductCostVersion.product_uuid == product.uuid)\
                               .filter(ProductCostVersion.preference == 1)\
                               .order_by(Transaction.issued_at,
                                         Transaction.id)\
                               .all()

        last_cost = None
        last_vendor_uuid = None
        for version in versions:

            changed = False
            if version.unit_cost != last_cost:
                changed = True
            elif version.vendor_uuid != last_vendor_uuid:
                changed = True

            if changed:
                changed = version.transaction.issued_at
                history.append({
                    'transaction_id': version.transaction.id,
                    'cost': version.unit_cost,
                    'vendor': version.vendor.name,
                    'since': humanize.naturaltime(now - changed),
                    'changed': changed,
                    'changed_by': version.transaction.user,
                })

            last_cost = version.unit_cost
            last_vendor_uuid = version.vendor_uuid

        final_history = OrderedDict()
        for hist in sorted(history, key=lambda h: h['changed'], reverse=True):
            if hist['transaction_id'] not in final_history:
                final_history[hist['transaction_id']] = hist

        return list(final_history.values())

    def edit(self):
        # TODO: Should add some more/better hooks, so don't have to duplicate
        # so much code here.
        self.editing = True
        instance = self.get_instance()
        form = self.make_form(instance)
        product_deleted = instance.deleted
        if self.request.method == 'POST':
            if self.validate_form(form):
                self.save_edit_form(form)
                self.request.session.flash("{} {} has been updated.".format(
                    self.get_model_title(), self.get_instance_title(instance)))
                return self.redirect(self.get_action_url('view', instance))
        if product_deleted:
            self.request.session.flash("This product is marked as deleted.", 'error')
        return self.render_to_response('edit', {'instance': instance,
                                                'instance_title': self.get_instance_title(instance),
                                                'form': form})

    def get_version_child_classes(self):
        return [
            (model.ProductCode, 'product_uuid'),
            (model.ProductCost, 'product_uuid'),
            (model.ProductPrice, 'product_uuid'),
        ]

    def image(self):
        """
        View which renders the product's image as a response.
        """
        product = self.get_instance()
        if not product.image:
            raise httpexceptions.HTTPNotFound()
        # TODO: how to properly detect image type?
        # self.request.response.content_type = six.binary_type('image/png')
        self.request.response.content_type = six.binary_type('image/jpeg')
        self.request.response.body = product.image.bytes
        return self.request.response

    def print_labels(self):
        app = self.get_rattail_app()
        label_handler = app.get_label_handler()
        model = self.model

        profile = self.request.params.get('profile')
        profile = self.Session.query(model.LabelProfile).get(profile) if profile else None
        if not profile:
            return {'error': "Label profile not found"}

        product = self.request.params.get('product')
        product = self.Session.query(model.Product).get(product) if product else None
        if not product:
            return {'error': "Product not found"}

        quantity = self.request.params.get('quantity')
        if not quantity.isdigit():
            return {'error': "Quantity must be numeric"}
        quantity = int(quantity)

        printer = label_handler.get_printer(profile)
        if not printer:
            return {'error': "Couldn't get printer from label profile"}

        try:
            printer.print_labels([({'product': product}, quantity)])
        except Exception as error:
            log.warning("error occurred while printing labels", exc_info=True)
            return {'error': six.text_type(error)}
        return {'ok': True}

    def search(self):
        """
        Locate a product(s) by UPC.

        Eventually this should be more generic, or at least offer more fields for
        search.  For now it operates only on the ``Product.upc`` field.
        """
        data = None
        upc = self.request.GET.get('upc', '').strip()
        upc = re.sub(r'\D', '', upc)
        if upc:
            product = api.get_product_by_upc(self.Session(), upc)
            if not product:
                # Try again, assuming caller did not include check digit.
                upc = GPC(upc, calc_check_digit='upc')
                product = api.get_product_by_upc(self.Session(), upc)
            if product and (not product.deleted or self.request.has_perm('products.view_deleted')):
                data = {
                    'uuid': product.uuid,
                    'upc': six.text_type(product.upc),
                    'upc_pretty': product.upc.pretty(),
                    'full_description': product.full_description,
                    'image_url': pod.get_image_url(self.rattail_config, product.upc),
                }
                uuid = self.request.GET.get('with_vendor_cost')
                if uuid:
                    vendor = self.Session.query(model.Vendor).get(uuid)
                    if not vendor:
                        return {'error': "Vendor not found"}
                    cost = product.cost_for_vendor(vendor)
                    if cost:
                        data['cost_found'] = True
                        if int(cost.case_size) == cost.case_size:
                            data['cost_case_size'] = int(cost.case_size)
                        else:
                            data['cost_case_size'] = '{:0.4f}'.format(cost.case_size)
                    else:
                        data['cost_found'] = False
        return {'product': data}

    def get_supported_batches(self):
        return OrderedDict([
            ('labels', {
                'spec': self.rattail_config.get('rattail.batch', 'labels.handler',
                                                default='rattail.batch.labels:LabelBatchHandler'),
            }),
            ('pricing', {
                'spec': self.rattail_config.get('rattail.batch', 'pricing.handler',
                                                default='rattail.batch.pricing:PricingBatchHandler'),
            }),
            ('delproduct', {
                'spec': self.rattail_config.get('rattail.batch', 'delproduct.handler',
                                                default='rattail.batch.delproduct:DeleteProductBatchHandler'),
            }),
        ])

    def make_batch(self):
        """
        View for making a new batch from current product grid query.
        """
        supported = self.get_supported_batches()
        batch_options = []
        for key, info in list(supported.items()):
            handler = load_object(info['spec'])(self.rattail_config)
            handler.spec = info['spec']
            handler.option_key = key
            handler.option_title = info.get('title', handler.get_model_title())
            supported[key] = handler
            batch_options.append((key, handler.option_title))

        schema = colander.SchemaNode(
            colander.Mapping(),
            colander.SchemaNode(colander.String(), name='batch_type', widget=dfwidget.SelectWidget(values=batch_options)),
            colander.SchemaNode(colander.String(), name='description', missing=colander.null),
            colander.SchemaNode(colander.String(), name='notes', missing=colander.null),
        )

        form = forms.Form(schema=schema, request=self.request,
                          cancel_url=self.get_index_url())
        form.auto_disable_save = True
        form.submit_label = "Create Batch"
        form.set_type('notes', 'text')

        params_forms = {}
        for key, handler in supported.items():
            make_schema = getattr(self, 'make_batch_params_schema_{}'.format(key), None)
            if make_schema:
                schema = make_schema()
                # must prefix node names with batch key, to guarantee unique
                for node in schema:
                    node.param_name = node.name
                    node.name = '{}_{}'.format(key, node.name)
                params_forms[key] = forms.Form(schema=schema, request=self.request)

        if self.request.method == 'POST':
            if form.validate(newstyle=True):
                data = form.validated
                fully_validated = True

                # collect general params
                batch_key = data['batch_type']
                params = {
                    'description': data['description'],
                    'notes': data['notes']}

                # collect batch-type-specific params
                pform = params_forms.get(batch_key)
                if pform:
                    if pform.validate(newstyle=True):
                        pdata = pform.validated
                        for field in pform.schema:
                            param_name = pform.schema[field.name].param_name
                            params[param_name] = pdata[field.name]
                    else:
                        fully_validated = False

                if fully_validated:

                    # TODO: should this be done elsewhere?
                    for name in params:
                        if params[name] is colander.null:
                            params[name] = None

                    handler = supported[batch_key]
                    products = self.get_products_for_batch(batch_key)
                    progress = self.make_progress('products.batch')
                    thread = Thread(target=self.make_batch_thread,
                                    args=(handler, self.request.user.uuid, products, params, progress))
                    thread.start()
                    return self.render_progress(progress, {
                        'cancel_url': self.get_index_url(),
                        'cancel_msg': "Batch creation was canceled.",
                    })

        return self.render_to_response('batch', {
            'form': form,
            'dform': form.make_deform_form(), # TODO: hacky? at least is explicit..
            'params_forms': params_forms,
        })

    def get_products_for_batch(self, batch_key):
        """
        Returns the products query to be used when making a batch (of type
        ``batch_key``) with the user's current filters in effect.  You can
        override this to add eager joins for certain batch types, etc.
        """
        return self.get_effective_data()

    def make_batch_params_schema_pricing(self):
        """
        Return params schema for making a pricing batch.
        """
        return colander.SchemaNode(
            colander.Mapping(),
            colander.SchemaNode(colander.Decimal(), name='min_diff_threshold',
                                quant='1.00', missing=colander.null,
                                title="Min $ Diff"),
            colander.SchemaNode(colander.Decimal(), name='min_diff_percent',
                                quant='1.00', missing=colander.null,
                                title="Min % Diff"),
            colander.SchemaNode(colander.Boolean(), name='calculate_for_manual'),
        )

    def make_batch_params_schema_delproduct(self):
        """
        Return params schema for making a "delete products" batch.
        """
        return colander.SchemaNode(
            colander.Mapping(),
            colander.SchemaNode(colander.Integer(), name='inactivity_months',
                                # TODO: probably should be configurable
                                default=18),
        )

    def make_batch_thread(self, handler, user_uuid, products, params, progress):
        """
        Threat target for making a batch from current products query.
        """
        session = RattailSession()
        user = session.query(model.User).get(user_uuid)
        assert user
        params['created_by'] = user
        try:
            batch = handler.make_batch(session, **params)
            batch.products = products.with_session(session).all()
            handler.do_populate(batch, user, progress=progress)

        except Exception as error:
            session.rollback()
            log.exception("failed to make '%s' batch with params: %s",
                          handler.batch_key, params)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Failed to make '{}' batch: {}".format(
                    handler.batch_key, simple_error(error))
                progress.session.save()

        else:
            session.commit()
            session.refresh(batch)
            session.close()

            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = self.get_batch_view_url(batch)
                progress.session['success_msg'] = 'Batch has been created: {}'.format(batch)
                progress.session.save()

    def get_batch_view_url(self, batch):
        if batch.batch_key == 'labels':
            return self.request.route_url('labels.batch.view', uuid=batch.uuid)
        if batch.batch_key == 'pricing':
            return self.request.route_url('batch.pricing.view', uuid=batch.uuid)
        if batch.batch_key == 'delproduct':
            return self.request.route_url('batch.delproduct.view', uuid=batch.uuid)

    def configure_get_simple_settings(self):
        return [

            # display
            {'section': 'rattail',
             'option': 'product.key'},
            {'section': 'rattail',
             'option': 'product.key_title'},
            {'section': 'tailbone',
             'option': 'products.show_pod_image',
             'type': bool},

            # handling
            {'section': 'rattail',
             'option': 'products.convert_type2_for_gpc_lookup',
             'type': bool},

            # labels
            {'section': 'tailbone',
             'option': 'products.print_labels',
             'type': bool},
            {'section': 'tailbone',
             'option': 'products.quick_labels.speedbump_threshold',
             'type': int},

        ]

    @classmethod
    def defaults(cls, config):
        cls._product_defaults(config)
        cls._defaults(config)

    @classmethod
    def _product_defaults(cls, config):
        rattail_config = config.registry.settings.get('rattail_config')
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        template_prefix = cls.get_template_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # print labels
        config.add_tailbone_permission(permission_prefix,
                                       '{}.print_labels'.format(permission_prefix),
                                       "Print labels for {}".format(model_title_plural))
        config.add_route('{}.print_labels'.format(route_prefix),
                         '{}/labels'.format(url_prefix))
        config.add_view(cls, attr='print_labels',
                        route_name='{}.print_labels'.format(route_prefix),
                        permission='{}.print_labels'.format(permission_prefix),
                        renderer='json')

        # view deleted products
        config.add_tailbone_permission('products', 'products.view_deleted',
                                       "View products marked as deleted")

        # make batch from product query
        config.add_tailbone_permission(permission_prefix, '{}.make_batch'.format(permission_prefix),
                                       "Create batch from {} query".format(model_title))
        config.add_route('{}.make_batch'.format(route_prefix), '{}/make-batch'.format(url_prefix))
        config.add_view(cls, attr='make_batch', route_name='{}.make_batch'.format(route_prefix),
                        renderer='{}/batch.mako'.format(template_prefix),
                        permission='{}.make_batch'.format(permission_prefix))

        # search (by upc)
        config.add_route('products.search', '/products/search')
        config.add_view(cls, attr='search', route_name='products.search',
                        renderer='json', permission='products.view')

        # product image
        config.add_route('products.image', '/products/{uuid}/image')
        config.add_view(cls, attr='image', route_name='products.image')

        # price history
        config.add_route('{}.price_history'.format(route_prefix), '{}/price-history'.format(instance_url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='price_history', route_name='{}.price_history'.format(route_prefix),
                        renderer='json',
                        permission='{}.versions'.format(permission_prefix))

        # cost history
        config.add_route('{}.cost_history'.format(route_prefix), '{}/cost-history'.format(instance_url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='cost_history', route_name='{}.cost_history'.format(route_prefix),
                        renderer='json',
                        permission='{}.versions'.format(permission_prefix))


class PendingProductView(MasterView):
    """
    Master view for the Pending Product class.
    """
    model_class = model.PendingProduct
    route_prefix = 'pending_products'
    url_prefix = '/products/pending'
    bulk_deletable = True

    labels = {
        'regular_price_amount': "Regular Price",
        'status_code': "Status",
        'user': "Created by",
    }

    grid_columns = [
        '_product_key_',
        'brand_name',
        'description',
        'size',
        'department_name',
        'created',
        'user',
        'status_code',
    ]

    form_fields = [
        '_product_key_',
        'brand_name',
        'brand',
        'description',
        'size',
        'department_name',
        'department',
        'vendor_name',
        'vendor',
        'unit_cost',
        'case_size',
        'regular_price_amount',
        'special_order',
        'notes',
        'created',
        'user',
        'status_code',
    ]

    def configure_grid(self, g):
        super(PendingProductView, self).configure_grid(g)

        g.set_enum('status_code', self.enum.PENDING_PRODUCT_STATUS)
        g.filters['status_code'].default_active = True
        g.filters['status_code'].default_verb = 'not_equal'
        g.filters['status_code'].default_value = six.text_type(self.enum.PENDING_PRODUCT_STATUS_RESOLVED)

        g.set_sort_defaults('created', 'desc')

        g.set_link('description')

    def configure_form(self, f):
        super(PendingProductView, self).configure_form(f)
        model = self.model
        pending = f.model_instance

        # department
        if self.creating or self.editing:
            if 'department' in f:
                f.remove('department_name')
                f.replace('department', 'department_uuid')
                f.set_widget('department_uuid', forms.widgets.DepartmentWidget(self.request, required=False))
                f.set_label('department_uuid', "Department")
        else:
            f.set_renderer('department', self.render_department)
            if pending.department:
                f.remove('department_name')

        # brand
        if self.creating or self.editing:
            f.remove('brand_name')
            f.replace('brand', 'brand_uuid')
            f.set_label('brand_uuid', "Brand")

            f.set_node('brand_uuid', colander.String(), missing=colander.null)
            brand_display = ""
            if self.request.method == 'POST':
                if self.request.POST.get('brand_uuid'):
                    brand = self.Session.query(model.Brand).get(self.request.POST['brand_uuid'])
                    if brand:
                        brand_display = six.text_type(brand)
            elif self.editing:
                brand_display = six.text_type(pending.brand or '')
            brands_url = self.request.route_url('brands.autocomplete')
            f.set_widget('brand_uuid', forms.widgets.JQueryAutocompleteWidget(
                field_display=brand_display, service_url=brands_url))
        else:
            f.set_renderer('brand', self.render_brand)
            if pending.brand:
                f.remove('brand_name')
            elif pending.brand_name:
                f.remove('brand')

        # description
        f.set_required('description')

        # vendor
        if self.creating or self.editing:
            if 'vendor' in f:
                f.remove('vendor_name')
                f.replace('vendor', 'vendor_uuid')
                f.set_node('vendor_uuid', colander.String())
                vendor_display = ""
                if self.request.method == 'POST':
                    if self.request.POST.get('vendor_uuid'):
                        vendor = self.Session.query(model.Vendor).get(self.request.POST['vendor_uuid'])
                        if vendor:
                            vendor_display = six.text_type(vendor)
                f.set_widget('vendor_uuid', forms.widgets.JQueryAutocompleteWidget(
                    field_display=vendor_display,
                    service_url=self.request.route_url('vendors.autocomplete')))
                f.set_label('vendor_uuid', "Vendor")
        else:
            f.set_renderer('vendor', self.render_vendor)
            if pending.vendor:
                f.remove('vendor_name')
            elif pending.vendor_name:
                f.remove('vendor')

        # case_size
        f.set_type('case_size', 'quantity')

        # regular_price_amount
        f.set_type('regular_price_amount', 'currency')

        # notes
        f.set_type('notes', 'text')

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

        # status_code
        if self.creating:
            f.remove('status_code')
        else:
            # f.set_readonly('status_code')
            f.set_enum('status_code', self.enum.PENDING_PRODUCT_STATUS)

    def editable_instance(self, pending):
        if pending.status_code == self.enum.PENDING_PRODUCT_STATUS_RESOLVED:
            return False
        return True

    def objectify(self, form, data=None):
        if data is None:
            data = form.validated

        pending = super(PendingProductView, self).objectify(form, data)

        if not pending.user:
            pending.user = self.request.user

        self.Session.add(pending)
        self.Session.flush()
        self.Session.refresh(pending)

        if pending.department:
            pending.department_name = pending.department.name

        if pending.brand:
            pending.brand_name = pending.brand.name

        return pending

    def before_delete(self, pending):
        """
        Event hook, called just before deletion is attempted.
        """
        model = self.model
        model_title = self.get_model_title()
        count = self.Session.query(model.CustomerOrderItem)\
                            .filter(model.CustomerOrderItem.pending_product == pending)\
                            .count()
        if count:
            self.request.session.flash("Cannot delete this {} because it is still "
                                       "referenced by {} Customer Orders.".format(model_title, count),
                                       'error')
            return self.redirect(self.get_action_url('view', pending))

        count = self.Session.query(model.CustomerOrderBatchRow)\
                            .filter(model.CustomerOrderBatchRow.pending_product == pending)\
                            .count()
        if count:
            self.request.session.flash("Cannot delete this {} because it is still "
                                       "referenced by {} \"new\" Customer Order Batches.".format(model_title, count),
                                       'error')
            return self.redirect(self.get_action_url('view', pending))

    def resolve_product(self):
        model = self.model
        pending = self.get_instance()
        redirect = self.redirect(self.get_action_url('view', pending))

        uuid = self.request.POST['product_uuid']
        product = self.Session.query(model.Product).get(uuid)
        if not product:
            self.request.session.flash("Product not found!", 'error')
            return redirect

        app = self.get_rattail_app()
        products_handler = app.get_products_handler()
        products_handler.resolve_product(pending, product, self.request.user)
        return redirect

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._pending_product_defaults(config)

    @classmethod
    def _pending_product_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        instance_url_prefix = cls.get_instance_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()

        # resolve product
        config.add_tailbone_permission(permission_prefix,
                                       '{}.resolve_product'.format(permission_prefix),
                                       "Resolve a {} as a Product".format(model_title))
        config.add_route('{}.resolve_product'.format(route_prefix),
                         '{}/resolve-product'.format(instance_url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='resolve_product',
                        route_name='{}.resolve_product'.format(route_prefix),
                        permission='{}.resolve_product'.format(permission_prefix))


def includeme(config):
    ProductView.defaults(config)
    PendingProductView.defaults(config)
