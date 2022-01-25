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
Tailbone Web API - Person Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from tailbone.api import APIMasterView2 as APIMasterView


class PersonView(APIMasterView):
    """
    API views for Person data
    """
    model_class = model.Person
    permission_prefix = 'people'
    collection_url_prefix = '/people'
    object_url_prefix = '/person'

    def normalize(self, person):
        return {
            'uuid': person.uuid,
            '_str': six.text_type(person),
            'first_name': person.first_name,
            'last_name': person.last_name,
            'display_name': person.display_name,
        }


def includeme(config):
    PersonView.defaults(config)
