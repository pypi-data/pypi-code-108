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
New Report Feature
"""

from __future__ import unicode_literals, absolute_import

import re

from rattail.features import Feature

import colander


class NewReportFeature(Feature):
    """
    New Report Feature
    """
    feature_key = 'new-report'
    feature_title = "New Report"

    def make_schema(self, **kwargs):

        class Schema(colander.MappingSchema):

            name = colander.SchemaNode(colander.String())

            description = colander.SchemaNode(colander.String())

        return Schema(**kwargs)

    def get_defaults(self):
        return {
            'name': "Latest Widgets",
            'description': "Shows all the latest widgets.",
        }

    def generate(self, **kwargs):
        context = dict(kwargs)
        context['app_package'] = self.config.app_package()
        context['app_slug'] = context['app_package'] # TODO
        context['code_name'] = re.sub(r'[\s-]', '_', context['name']).lower()
        context['cap_name'] = context['name'].replace(' ', '')

        return self.generate_mako('/new-report/instructions.mako', **context)
