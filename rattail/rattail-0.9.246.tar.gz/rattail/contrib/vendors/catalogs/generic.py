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
"Generic" Catalog Parser
"""

import datetime
import decimal
import logging

import six

from rattail.vendors.catalogs import CatalogParser
from rattail.excel import ExcelReaderXLSX
from rattail.db import model
from rattail.gpc import GPC
from rattail.time import localtime, make_utc


log = logging.getLogger(__name__)


class GenericCatalogParser(CatalogParser):
    """
    Generic vendor catalog parser, for Excel XLSX files.
    """
    key = 'rattail.contrib.generic'
    display = "Generic Excel (XLSX only)"

    def parse_rows(self, path, progress=None):
        """
        This parser expects a "standard" XLSX file with one header row.
        """
        reader = ExcelReaderXLSX(path)
        xlrows = reader.read_rows(progress=progress)

        for xlrow in xlrows:
            row = model.VendorCatalogBatchRow()

            # upc (required)
            upc = xlrow['UPC']
            if not upc or not six.text_type(upc).strip():
                continue        # skip lines with no UPC value
            upc = str(upc).replace(' ', '').replace('-', '')
            row.item_entry = upc
            row.upc = GPC(upc, calc_check_digit=False if len(upc) in (12, 13) else 'upc')

            # cost values (required in some combination)
            if 'Case Cost' in xlrow:
                case_cost = xlrow['Case Cost']
                if isinstance(case_cost, int):
                    row.case_cost = decimal.Decimal('{}.00'.format(case_cost))
                else:
                    row.case_cost = self.decimal(case_cost)
            if 'Case Size' in xlrow:
                row.case_size = int(xlrow['Case Size'])
            if 'Unit Cost' in xlrow:
                row.unit_cost = self.decimal(xlrow['Unit Cost'])
            elif row.case_cost and row.case_size:
                row.unit_cost = row.case_cost / row.case_size

            # optional values
            if 'Vendor Code' in xlrow:
                row.vendor_code = six.text_type(xlrow['Vendor Code'])
            if 'Brand' in xlrow:
                row.brand_name = xlrow['Brand']
            if 'Description' in xlrow:
                row.description = xlrow['Description']
            if 'Unit Size' in xlrow:
                row.size = xlrow['Unit Size']

            if 'SRP' in xlrow:
                value = xlrow['SRP']
                try:
                    row.suggested_retail = self.decimal(value)
                except decimal.InvalidOperation:
                    log.warning("cannot parse SRP value: %s", value)

            # discount_starts
            if 'Vendor Discount Start Date' in xlrow:
                row.discount_starts = xlrow['Vendor Discount Start Date']
                if row.discount_starts: # must convert to UTC, at local midnight
                    date = localtime(self.config, row.discount_starts).date()
                    starts = datetime.datetime.combine(date, datetime.time(0))
                    starts = localtime(self.config, starts)
                    row.discount_starts = make_utc(starts)

            # discount_ends
            if 'Vendor Discount End Date' in xlrow:
                row.discount_ends = xlrow['Vendor Discount End Date']
                if row.discount_ends: # must convert to UTC, 1 minute shy of local midnight
                    date = localtime(self.config, row.discount_ends).date()
                    ends = datetime.datetime.combine(date, datetime.time(23, 59))
                    ends = localtime(self.config, ends)
                    row.discount_ends = make_utc(ends)

            # discount_amount
            if 'Vendor Discount Amount' in xlrow:
                row.discount_amount = self.decimal(xlrow['Vendor Discount Amount'])

            # discount_percent
            if 'Vendor Discount Percent' in xlrow:
                row.discount_percent = self.decimal(xlrow['Vendor Discount Percent'])

            yield row
