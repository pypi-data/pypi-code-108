# This file is part of Sympathy for Data.
# Copyright (c) 2016-2017, Combine Control Systems AB
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
import json

from sympathy.api import node as synode
from sympathy.api import dtypes
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags

from sympathy.platform.editors.table_editor import TableWidget, JsonTableModel


class CreateTableConfigWidget(TableWidget):
    """
    Makes CreateTableWidget usable as a configuration gui for sympathy nodes
    hiding the parameters api from the CreateTableWidget implementation.
    """

    def __init__(self, parameters):
        self._parameters = parameters
        data = json.loads(parameters['json_table'].value)
        super().__init__(data)

    def save_parameters(self):
        data = [(name, dtypes.dtype(t).kind, rows) for name, t, rows in
                self.model().get_data()]
        self._parameters['json_table'].value = json.dumps(
            data)


class CreateTable(synode.Node):
    """
    By default the created Table will be empty so to add data to it you first
    need to create at least one column and then add at least one row.

    The name and type of a column can be changed at any time from the context
    menu of the column header.

    Cells can be masked or unmasked from the context menu of a cell or a
    selection of many cells.
    """

    name = 'Create Table'
    description = 'Create a Table from scratch in a configuration Gui.'
    author = 'Magnus Sandén'
    version = '1.0'
    icon = 'create_table.svg'
    tags = Tags(Tag.Input.Generate)

    nodeid = 'org.sysess.sympathy.create.createtable'
    outputs = Ports([Port.Table('Manually created table', name='port0')])

    parameters = synode.parameters()
    parameters.set_string(
        'json_table', value='[]',
        label='GUI', description='Configuration window')

    def exec_parameter_view(self, node_context):
        return CreateTableConfigWidget(node_context.parameters)

    def execute(self, node_context):
        out_table = node_context.output['port0']
        json_data = node_context.parameters['json_table'].value
        model = JsonTableModel(json.loads(json_data))
        for name, data in model.numpy_columns():
            out_table.set_column_from_array(name, data)
