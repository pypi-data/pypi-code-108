# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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
from sympathy.api import node


index_description = 'Edit indices to select (must be integers).'
index_doc = """
    Select items to output by specifying integer indices. Multiple indices can
    be used. The output has the same structure as the input but the same number
    of items or fewer depending on if just a few or if all indices were
    selected.
"""


def set_parameters(parameters, description=None):
    if description is None:
        description = index_description
    parameters.set_list(
        'index', label='Select index',
        description=description,
        editor=node.editors.multilist_editor(mode=True, edit=True))
