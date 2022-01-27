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
This module contains classes that wrap ADAFs or lists of ADAFs for use in
various function selector, F(x), nodes in Sympathy for Data.
"""
from sympathy.platform import exceptions as syexceptions
from sympathy.api import adaf  # NOQA
from . import fx_wrapper


class ADAFWrapper(fx_wrapper.FxWrapper):
    """
    ADAFWrapper should be used as the parent class for classes to be used
    in the ADAF F(x) nodes.
    """
    arg_types = ['adaf']
    list_wrapper = False

    def __init__(self, in_adaf, out_adaf, extra_table=None):
        self.required_signals = []
        self.in_adaf = in_adaf
        self.out_adaf = out_adaf
        self.extra_table = extra_table

    def execute(self):
        """Execute is called from the F(x) node."""
        raise syexceptions.SyConfigurationError(
            "This f(x) script doesn't implement an execute method.")


class ADAFsWrapper(ADAFWrapper):
    """ADAFsWrapper should be used as the parent class for classes to be used
    in the ADAFs F(x) nodes.

    Interact with the tables through in_table_list and out_table_list.
    """
    arg_types = ['[adaf]']
    list_wrapper = True

    def __init__(self, in_adaf, out_adaf, extra_table=None):
        super(ADAFsWrapper, self).__init__(in_adaf, out_adaf, extra_table)
        self.in_adaf_list = in_adaf
        self.out_adaf_list = out_adaf


class ADAFToTableWrapper(ADAFWrapper):
    """ADAFsToTablesWrapper should be used as the parent class for classes to
    be used in the ADAFs to Tables F(x) nodes.

    Interact with the files through in_adaf_list and out_table_list.
    """

    def __init__(self, in_adaf, out_table, extra_table=None):
        super(ADAFToTableWrapper, self).__init__(in_adaf, out_table,
                                                 extra_table)
        self.out_table = out_table


class ADAFsToTablesWrapper(ADAFToTableWrapper):
    """ADAFsToTablesWrapper should be used as the parent class for classes to
    be used in the ADAFs to Tables F(x) nodes.

    Interact with the files through in_adaf_list and out_table_list.
    """
    list_wrapper = True

    def __init__(self, in_adaf, out_table, extra_table=None):
        super(ADAFsToTablesWrapper, self).__init__(in_adaf, out_table,
                                                   extra_table)
        self.in_adaf_list = in_adaf
        self.out_table_list = out_table
