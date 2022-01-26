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
Vendor Catalogs
"""

from __future__ import unicode_literals, absolute_import

import warnings
from decimal import Decimal

import six

from rattail.exceptions import RattailError
from rattail.util import load_entry_points


class CatalogParser(object):
    """
    Base class for all vendor catalog parsers.

    .. note::

       As of this writing the ``config`` param is technically optional
       for the class constructor method, but that will certainly
       change some day.  Please be sure to pass a ``config`` param
       when instantiating parsers in your code.

    .. attribute:: vendor_key

       Key for the vendor.  This key will be used to locate an entry in the
       settings table, e.g. ``'rattail.vendor.unfi'`` for a key of ``'unfi'``.
       The value of this setting must be an exact match to either a
       :attr:`rattail.db.model.Vendor.uuid` or
       :attr:`rattail.db.model.Vendor.id` within the system.  However this
       value may also be ``None`` (the default), in which case the user must
       ultimately specify which vendor should be used for the data import.
    """
    vendor_key = None

    def __init__(self, config=None, **kwargs):
        if config:
            self.config = config
            self.app = config.get_app()
            self.model = config.get_model()
            self.enum = config.get_enum()

    @property
    def key(self):
        """
        Key for the parser.  Must be unique among all catalog parsers.
        """
        raise NotImplementedError("Catalog parser has no key: {0}".format(repr(self)))

    def parse_effective_date(self, path):
        """
        Parse the overall effective date for a catalog file.
        """

    def parse_rows(self, data_path, progress=None):
        """
        Parse the given data file, returning all rows found within it.
        """
        raise NotImplementedError("Catalog parser has no `parse_rows()` method: {0}".format(repr(self.key)))

    def make_row(self):
        """
        Create and return a new row, suitable for use in a vendor
        catalog batch.  The row will be empty and not yet part of any
        database session.

        :returns: A
           :class:`~rattail.db.model.batch.vendorcatalog.VendorCatalogBatchRow`
           instance.
        """
        model = self.model
        return model.VendorCatalogBatchRow()

    def decimal(self, value, scale=4):
        """
        Convert a value to a decimal, unless it's ``None``.
        """
        if value is None:
            return None

        # No reason to convert integers, really.
        if isinstance(value, six.integer_types):
            return value
        if isinstance(value, Decimal):
            return value

        if isinstance(value, float):
            value = "{{0:0.{0}f}}".format(scale).format(value)
        else:
            value = value.strip()
        return Decimal(value)

    def int_(self, value):
        """
        Convert a value to an integer.
        """
        value = value.strip() or 0
        return int(value)


@six.python_2_unicode_compatible
class CatalogParserNotFound(RattailError):
    """
    Exception raised when a vendor catalog parser is required, but cannot be
    located.
    """

    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Vendor catalog parser with key {} cannot be located.".format(self.key)


def get_catalog_parsers(): # pragma: no cover
    """
    Returns a dictionary of installed vendor catalog parser classes.
    """
    warnings.warn("function is deprecated, please use "
                  "VendorHandler.get_all_catalog_parsers() instead",
                  DeprecationWarning)
    return load_entry_points('rattail.vendors.catalogs.parsers')


def get_catalog_parser(key): # pragma: no cover
    """
    Fetch a vendor catalog parser by key.  If the parser class can be located,
    this will return an instance thereof; otherwise returns ``None``.
    """
    warnings.warn("function is deprecated, please use "
                  "VendorHandler.get_catalog_parser() instead",
                  DeprecationWarning)
    parser = get_catalog_parsers().get(key)
    if parser:
        return parser()
    return None


def require_catalog_parser(key): # pragma: no cover
    """
    Fetch a vendor catalog parser by key.  If the parser class can be located,
    this will return an instance thereof; otherwise raises an exception.
    """
    warnings.warn("function is deprecated, please use "
                  "VendorHandler.get_catalog_parser() instead",
                  DeprecationWarning)
    parser = get_catalog_parser(key)
    if not parser:
        raise CatalogParserNotFound(key)
    return parser


def iter_catalog_parsers(): # pragma: no cover
    """
    Returns an iterator over the installed vendor catalog parsers.
    """
    warnings.warn("function is deprecated, please use "
                  "VendorHandler.get_all_catalog_parsers() instead",
                  DeprecationWarning)
    parsers = get_catalog_parsers()
    return parsers.values()
