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
Customer Orders Handler

Please note this is different from the Customer Order Batch Handler.
"""

from __future__ import unicode_literals, absolute_import

from rattail.app import GenericHandler


class CustomerOrderHandler(GenericHandler):
    """
    Base class and default implementation for customer order handlers.
    """

    def resolve_person(self, pending, person, user, **kwargs):
        """
        Resolve a pending person for all customer orders.
        """
        for order in list(pending.custorder_records):
            order.person = person
            order.pending_customer = None
            for item in order.items:
                item.add_event(self.enum.CUSTORDER_ITEM_EVENT_CUSTOMER_RESOLVED,
                               user)

    def resolve_product(self, pending, product, user, **kwargs):
        """
        Resolve a pending product for all customer orders.
        """
        for item in pending.custorder_item_records:
            item.product = product
            item.pending_product = None

            item.product_upc = product.upc
            item.product_item_id = product.item_id
            item.product_scancode = product.scancode
            item.product_brand = product.brand.name if product.brand else None
            item.product_description = product.description
            item.product_size = product.size

            # TODO: not sure this is needed really?
            item.product_weighed = product.weighed

            # TODO: model notes say this is not needed
            #item.product_unit_of_measure = product.unit_of_measure

            department = product.department
            item.department_number = department.number if department else None
            item.department_name = department.name if department else None

            # TODO: should be smarter about getting this
            item.case_quantity = product.case_size

            cost = product.cost
            item.product_unit_cost = cost.unit_cost if cost else None

            regprice = product.regular_price
            item.unit_regular_price = regprice.price if regprice else None

            curprice = product.current_price
            item.unit_sale_price = curprice.price if curprice else None
            item.sale_ends = curprice.ends if curprice else None

            item.unit_price = item.unit_sale_price or item.unit_regular_price

            # TODO: should recalculate total price
            #item.total_price = ...

            item.add_event(self.enum.CUSTORDER_ITEM_EVENT_PRODUCT_RESOLVED,
                           user)
