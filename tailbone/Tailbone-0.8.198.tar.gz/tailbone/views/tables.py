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
Views with info about the underlying Rattail tables
"""

from __future__ import unicode_literals, absolute_import

from tailbone.views import MasterView


class TableView(MasterView):
    """
    Master view for tables
    """
    normalized_model_name = 'table'
    model_key = 'name'
    model_title = "Table"
    creatable = False
    editable = False
    deletable = False
    viewable = False
    filterable = False
    pageable = False

    grid_columns = [
        'name',
        'row_count',
    ]

    def get_data(self, **kwargs):
        """
        Fetch existing table names and estimate row counts via PG SQL
        """
        # note that we only show 'public' schema tables, i.e. avoid the 'batch'
        # schema, at least for now?  maybe should include all, plus show the
        # schema name within the results grid?
        sql = """
        select relname, n_live_tup
        from pg_stat_user_tables
        where schemaname = 'public'
        order by n_live_tup desc;
        """
        result = self.Session.execute(sql)
        return [dict(name=row['relname'], row_count=row['n_live_tup'])
                for row in result]

    def configure_grid(self, g):
        g.sorters['name'] = g.make_simple_sorter('name', foldcase=True)
        g.sorters['row_count'] = g.make_simple_sorter('row_count')
        g.set_sort_defaults('name')

# TODO: deprecate / remove this
TablesView = TableView


def includeme(config):
    TableView.defaults(config)
