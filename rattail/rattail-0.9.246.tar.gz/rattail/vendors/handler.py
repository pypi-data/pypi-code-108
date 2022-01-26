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
Vendors Handler
"""

from __future__ import unicode_literals, absolute_import

from rattail.app import GenericHandler
from rattail.util import load_entry_points


class VendorHandler(GenericHandler):
    """
    Base class and default implementation for vendor handlers.
    """

    def choice_uses_dropdown(self):
        """
        Returns boolean indicating whether a vendor choice should be
        presented to the user via a dropdown (select) element, vs.  an
        autocomplete field.  The latter is the default because
        potentially the vendor list can be quite large, so we avoid
        loading them all in the dropdown unless so configured.

        :returns: Boolean; if true then a dropdown should be used;
           otherwise (false) autocomplete is used.
        """
        return self.config.getbool('rattail', 'vendors.choice_uses_dropdown',
                                   default=False)

    def get_vendor(self, session, key, **kwargs):
        """
        Locate and return the vendor corresponding to the given key.

        The key can be a UUID value, but most often it will instead be
        a "generic" key specific to this purpose.  Any generic key can
        be defined within the settings, pointing to a valid vendor.
        
        For instance, we can define a key of ``'poser.acme'`` to
        denote the hypothetical "Acme Distribution" vendor, and we add
        a namespace unique to our app just to be safe.

        We then create a setting in the DB pointing to our *actual*
        vendor by way of its UUID:

        .. code-block:: sql

           INSERT INTO SETTING (name, value) 
           VALUES ('rattail.vendor.poser.acme',
                   '7e6d69a2700911ec93533ca9f40bc550');

        From then on we could easily fetch the vendor by this key.
        This is mainly useful to allow catalog and invoice parsers to
        "loosely" associate with a particular vendor by way of this
        key, which could be shared across organizations etc.
        """
        from rattail.db.api.vendors import get_vendor
        return get_vendor(session, key)

    def get_all_catalog_parsers(self):
        """
        Should return *all* catalog parsers known to exist.

        Note that this returns classes and not instances.

        :returns: List of
           :class:`~rattail.vendors.catalogs.CatalogParser` classes.
        """
        Parsers = list(
            load_entry_points('rattail.vendors.catalogs.parsers').values())
        Parsers.sort(key=lambda Parser: Parser.display)
        return Parsers
        
    def get_supported_catalog_parsers(self):
        """
        Should return only those catalog parsers which are "supported"
        by the current app.  Usually "supported" just means what we
        want to expose to the user.

        Note that this returns classes and not instances.

        :returns: List of
           :class:`~rattail.vendors.catalogs.CatalogParser` classes.
        """
        Parsers = self.get_all_catalog_parsers()
        
        supported_keys = self.config.getlist(
            'rattail', 'vendors.supported_catalog_parsers')
        if supported_keys is None:
            supported_keys = self.config.getlist(
                'tailbone', 'batch.vendorcatalog.supported_parsers')
        if supported_keys:
            Parsers = [Parser for Parser in Parsers
                       if Parser.key in supported_keys]
            
        return Parsers

    def get_catalog_parser(self, key, require=False):
        """
        Retrieve the catalog parser for the given parser key.

        Note that this returns an instance, not the class.

        :param key: Unique key indicating which parser to get.

        :returns: A :class:`~rattail.vendors.catalogs.CatalogParser`
           instance.
        """
        from rattail.vendors.catalogs import CatalogParserNotFound

        for Parser in self.get_all_catalog_parsers():
            if Parser.key == key:
                return Parser(self.config)

        if require:
            raise CatalogParserNotFound(key)
