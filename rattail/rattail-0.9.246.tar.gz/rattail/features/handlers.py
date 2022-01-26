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
Handler for Generating Features
"""

from __future__ import unicode_literals, absolute_import

import six

import colander

from rattail.app import GenericHandler
from rattail.util import load_entry_points


class FeatureHandler(GenericHandler):
    """
    Base class for feature handlers.
    """
    entry_point_section = 'rattail.features'

    def all_features(self):
        """
        Returns a dict of available features, which are registered via
        setuptools entry points.
        """
        return load_entry_points(self.entry_point_section)

    def all_feature_types(self):
        """
        Returns a list of available feature type keys.
        """
        return list(self.all_features())

    def iter_features(self):
        """
        Iterate over all features.
        """
        for factory in six.itervalues(self.all_features()):
            yield factory(self.config)

    def get_feature(self, key):
        """
        Returns the specific feature identified by type key.
        """
        features = self.all_features()
        if key in features:
            return features[key](self.config)

    def make_schema(self, **kwargs):

        class Schema(colander.MappingSchema):

            app_prefix = colander.SchemaNode(colander.String())

            app_cap_prefix = colander.SchemaNode(colander.String())

        return Schema(**kwargs)

    def get_defaults(self):
        return {
            'app_prefix': self.config.app_title().lower(),
            'app_cap_prefix': self.config.app_title(),
        }

    def do_generate(self, feature, **kwargs):
        """
        Generate code and instructions for new feature.
        """
        return feature.generate(**kwargs)
