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
Features
"""

from __future__ import unicode_literals, absolute_import

import json
from mako.lookup import TemplateLookup

from rattail.files import resource_path


class Feature(object):
    """
    Base class for features.
    """

    def __init__(self, config):
        self.config = config

        # TODO: make templates dir configurable
        templates = [resource_path('rattail:templates/feature')]
        self.templates = TemplateLookup(directories=templates)

    def get_defaults(self):
        return {}

    def get_template(self, path):
        """
        Locate and return the given Mako feature template.
        """
        return self.templates.get_template(path)

    def generate_mako(self, template, **context):
        """
        Generate and return output from the given template.
        """
        template = self.get_template(template)
        text = template.render(**context)
        return text


class JSONWidget(object):
    """
    This is a minimal "widget" for use with certain colander schema nodes,
    which lets us accept a JSON-encoded string, whereas otherwise Deform would
    be expecting a peppercorn-compatible series of field mappings.
    """

    def deserialize(self, field, pstruct):
        return json.loads(pstruct)
