# -*- coding: utf-8; -*-
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
Tailbone Web API - Customer Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from tailbone.api import APIMasterView2 as APIMasterView


class CustomerView(APIMasterView):
    """
    API views for Customer data
    """
    model_class = model.Customer
    collection_url_prefix = '/customers'
    object_url_prefix = '/customer'

    def normalize(self, customer):
        return {
            'uuid': customer.uuid,
            '_str': six.text_type(customer),
            'id': customer.id,
            'number': customer.number,
            'name': customer.name,
        }


def includeme(config):
    CustomerView.defaults(config)
