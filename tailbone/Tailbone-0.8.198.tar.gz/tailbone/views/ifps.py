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
IFPS Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView


class IFPS_PLUView(MasterView):
    """
    Master view for the Department class.
    """
    model_class = model.IFPS_PLU
    route_prefix = 'ifps_plus'
    url_prefix = '/ifps-plu-codes'
    results_downloadable = True
    has_versions = True

    labels = {
        'plu': "PLU",
        'gpc': "GPC",
        'aka': "AKA",
        'measurements_north_america': "Measurements (North America)",
        'measurements_rest_of_world': "Measurements (rest of world)",
    }

    grid_columns = [
        'plu',
        'category',
        'commodity',
        'variety',
        'size',
        'botanical_name',
        'revision_date',
    ]

    def configure_grid(self, g):
        super(IFPS_PLUView, self).configure_grid(g)

        g.filters['plu'].default_active = True
        g.filters['plu'].default_verb = 'equal'

        g.filters['commodity'].default_active = True
        g.filters['commodity'].default_verb = 'contains'

        g.set_sort_defaults('plu')

        # variety
        # this is actually a TEXT field, so potentially large
        g.set_renderer('variety', self.render_truncated_value)

        g.set_link('plu')
        g.set_link('commodity')
        g.set_link('variety')

    def configure_form(self, f):
        super(IFPS_PLUView, self).configure_form(f)

        if self.creating:
            f.remove('revision_date',
                     'date_added')
        else:
            f.set_readonly('revision_date')
            f.set_readonly('date_added')



def includeme(config):
    IFPS_PLUView.defaults(config)
