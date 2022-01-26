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
New Table Feature
"""

from __future__ import unicode_literals, absolute_import

from rattail.features import Feature
from rattail.features.base import JSONWidget

import colander


class NewTableFeature(Feature):
    """
    New Table Feature
    """
    feature_key = 'new-table'
    feature_title = "New Table"

    def make_schema(self, **kwargs):

        class Column(colander.MappingSchema):

            name = colander.SchemaNode(colander.String())

            data_type = colander.SchemaNode(colander.String())

            nullable = colander.SchemaNode(colander.Boolean())

            description = colander.SchemaNode(colander.String())

        class Columns(colander.SequenceSchema):

            column = Column()

        class Schema(colander.MappingSchema):

            table_name = colander.SchemaNode(colander.String())

            model_name = colander.SchemaNode(colander.String())

            model_title = colander.SchemaNode(colander.String())

            model_title_plural = colander.SchemaNode(colander.String())

            description = colander.SchemaNode(colander.String())

            versioned = colander.SchemaNode(colander.Boolean())

            columns = Columns(widget=JSONWidget())

        return Schema(**kwargs)

    def get_defaults(self):
        return {
            'table_name': 'cool_widget',
            'model_name': 'CoolWidget',
            'model_title': "Cool Widget",
            'model_title_plural': "Cool Widgets",
            'description': "Represents a Cool Widget.",
            'versioned': True,
            'columns': [
                {
                    'name': 'id',
                    'data_type': 'Integer()',
                    'nullable': False,
                    'description': "Numeric ID for the widget.",
                },
                {
                    'name': 'name',
                    'data_type': 'String(length=255)',
                    'nullable': False,
                    'description': "Name of the widget.",
                },
                {
                    'name': 'description',
                    'data_type': 'String(length=255)',
                    'nullable': True,
                    'description': "Description of the widget.",
                },
                {
                    'name': 'coolness_factor',
                    'data_type': 'Numeric(precision=4, scale=3)',
                    'nullable': True,
                    'description': "Just how cool is this widget, from 0.000 to 1.000.",
                },
            ],
        }

    def generate(self, **kwargs):
        context = dict(kwargs)
        context['app_package'] = self.config.app_package()
        context['app_slug'] = context['app_package'] # TODO
        context['envroot'] = '/srv/envs/{}'.format(context['app_slug']) # TODO
        context['prefixed_table_name'] = '{}_{}'.format(
            context['app_prefix'], context['table_name'])
        context['prefixed_model_name'] = '{}{}'.format(
            context['app_cap_prefix'], context['model_name'])

        return self.generate_mako('/new-table/instructions.mako', **context)
