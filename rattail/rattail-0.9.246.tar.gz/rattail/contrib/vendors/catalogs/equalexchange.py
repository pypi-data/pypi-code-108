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
Vendor catalog parser for Equal Exchange
"""

from __future__ import unicode_literals, absolute_import

import re
import decimal

import six
import xlrd

from rattail.db import model
from rattail.gpc import GPC
from rattail.vendors.catalogs import CatalogParser


class EqualExchangeCatalogParser(CatalogParser):
    """
    Vendor catalog parser for Equal Exchange.
    """
    key = 'rattail.contrib.equalexchange'
    display = "Equal Exchange"
    vendor_key = 'equal-exchange'

    def parse_rows(self, path, progress=None):
        book = xlrd.open_workbook(path)

        # Bulk
        sheet = book.sheet_by_index(0)
        for row in self.parse_sheet_rows(sheet, "Bulk", progress=progress):
            yield row

        # Grocery
        sheet = book.sheet_by_index(1)
        for row in self.parse_sheet_rows(sheet, "Grocery", progress=progress):
            yield row

    def parse_sheet_rows(self, sheet, department_name, progress=None):
        unit_price_pattern = re.compile(r'^\$(\d+\.\d\d)/lb$')

        for r in range(sheet.nrows):
            row = model.VendorCatalogBatchRow()
            row.brand_name = "Equal Exchange"
            row.department_name = department_name

            # column A (ITEM DESCRIPTION)
            row.description = sheet.cell_value(r, 0)

            # column B (ITEM CODE)
            # note that this must be numeric, or else we're not interested
            item_code = sheet.cell_value(r, 1)
            if not isinstance(item_code, (int, float)):
                continue
            row.vendor_code = six.text_type(int(item_code))

            # column C (UNIT UPC)
            # note that this must be present, or else we're not interested
            unit_upc = sheet.cell_value(r, 2)
            if isinstance(unit_upc, float):
                unit_upc = six.text_type(int(unit_upc))
            unit_upc = unit_upc.replace(' ', '')
            if not unit_upc:
                continue
            # note that if UPC is "NA" then we'll still keep the record, it
            # just won't have a UPC value
            if unit_upc != 'NA':
                assert len(unit_upc) == 12
                row.item_entry = unit_upc
                row.upc = GPC(unit_upc, calc_check_digit=False)

            # column E (UNIT PRICE)
            unit_price = sheet.cell_value(r, 4)
            if isinstance(unit_price, float):
                row.unit_cost = decimal.Decimal(six.text_type(unit_price))\
                                       .quantize(decimal.Decimal('0.12345'))
            else:
                match = unit_price_pattern.match(unit_price)
                row.unit_cost = decimal.Decimal(match.group(1))

            # column F (CASE SIZE)
            case_size = sheet.cell_value(r, 5)
            row.case_size = self.parse_case_size(case_size, department_name)
            if department_name == 'Grocery':
                row.size = self.parse_size(case_size)

            # column G (PRICE/CASE)
            price_per_case = sheet.cell_value(r, 6)
            row.case_cost = decimal.Decimal(six.text_type(price_per_case))\
                                   .quantize(decimal.Decimal('0.12345'))

            yield row

    def parse_case_size(self, case_size, department_name):

        # e.g. '2 x 5lb'
        match = re.match(r'^(\d+) x (\d+)lbs?$', case_size)
        if match:
            return int(match.group(1)) * int(match.group(2))

        # e.g. '25 lbs'
        match = re.match(r'^(\d+(?:\.\d+)?) lbs$', case_size)
        if match:
            return decimal.Decimal(match.group(1))

        # e.g. '3 x 5kgs'
        match = re.match(r'^(\d+) x (\d+)kgs$', case_size)
        if match:
            # TODO: assuming 2.2 lb/kg here; what else can we do?
            return 2.2 * int(match.group(1)) * int(match.group(2))

        # e.g. '888 pieces'
        match = re.match(r'^(\d+) pieces$', case_size)
        if match:
            return int(match.group(1))

        # e.g. '12 bars'
        match = re.match(r'^(\d+) bars$', case_size)
        if match:
            return int(match.group(1))

        # e.g. '6 boxes'
        match = re.match(r'^(\d+) boxes$', case_size)
        if match:
            return int(match.group(1))

        if department_name == 'Grocery':

            # e.g. '6 x 8 oz'
            match = re.match(r'^(\d+) x \d+ oz$', case_size)
            if match:
                return int(match.group(1))

            # e.g. '6 x 500 ml'
            match = re.match(r'^(\d+) x \d+ ml$', case_size)
            if match:
                return int(match.group(1))

        raise NotImplementedError("do not know how to parse case size: {}".format(case_size))

    def parse_size(self, case_size):

        # e.g. '6 x 8 oz'
        match = re.match(r'^\d+ x (\d+ oz)$', case_size)
        if match:
            return match.group(1)

        # e.g. '6 x 500 ml'
        match = re.match(r'^\d+ x (\d+ ml)$', case_size)
        if match:
            return match.group(1)
