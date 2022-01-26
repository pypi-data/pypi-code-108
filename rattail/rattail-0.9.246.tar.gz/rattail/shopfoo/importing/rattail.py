# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Rattail -> Shopfoo export
"""

class ProductImporterMixin(object):
    """
    Product data importer mixin
    """

    def setup(self):

        # do normal setup (open output file etc.)
        super(ProductImporterMixin, self).setup()

        # get our "runas" user straight
        assert self.runas_username
        self.host_session.set_continuum_user(self.runas_username)
        self.runas_user = self.host_session.continuum_user

        # make a DB record for the export
        self.init_export(self.host_session)

    def teardown(self):

        # do normal teardown (close output file etc.)
        super(ProductImporterMixin, self).teardown()

        # wrap up the export record, maybe upload file
        self.finalize_export()

    def update_object(self, product, data, local_data=None):
        product = super(ProductImporterMixin, self).update_object(product, data, local_data)

        # keep track of how many records are exported
        self.record_count += 1

        return product
