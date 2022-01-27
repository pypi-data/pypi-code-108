# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
This module contains classes that wrap tables or lists of tables for use in
various function selector, F(x), nodes in Sympathy for Data.
"""
from sympathy.platform import exceptions as syexceptions
from sympathy.api import table  # NOQA
from . import fx_wrapper


class TableWrapper(fx_wrapper.FxWrapper):
    """
    TableWrapper should be used as the parent class for classes to be used
    in the table F(x) nodes.

    Interact with the table through in_table and out_table.
    """
    arg_types = ['table']
    list_wrapper = False

    def __init__(self, in_table, out_table, extra_table=None):
        self.in_table = in_table
        self.out_table = out_table
        self.extra_table = extra_table

    def execute(self):
        """Execute is called from the F(x) node."""
        raise syexceptions.SyConfigurationError(
            "This f(x) script doesn't implement an execute method.")


class TablesWrapper(TableWrapper):
    """TablesWrapper should be used as the parent class for classes to be used
    in the tables F(x) nodes.

    Interact with the tables through in_table_list and out_table_list.
    """
    arg_types = ['[table]']
    list_wrapper = True

    def __init__(self, in_table, out_table, extra_table=None):
        super(TablesWrapper, self).__init__(in_table, out_table, extra_table)
        self.in_table_list = in_table
        self.out_table_list = out_table
