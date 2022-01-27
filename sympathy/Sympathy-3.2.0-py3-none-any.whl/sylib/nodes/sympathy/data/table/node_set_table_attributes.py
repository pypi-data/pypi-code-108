# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017, Combine Control Systems AB
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
import numpy as np
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api import table
from sympathy.api.exceptions import SyDataError, sywarn


class SetNameSuper(synode.Node):
    author = 'Greger Cronquist'
    version = '1.0'
    icon = 'rename_table.svg'
    tags = Tags(Tag.DataProcessing.TransformMeta)

    parameters = synode.parameters()
    parameters.set_string(
        'name', label='Name',
        description='Name to assign to the table(s).')


class SetTableName(SetNameSuper):
    """Set the name of a Table."""

    name = 'Set Table Name'
    description = 'Set the name of a Table'
    nodeid = 'org.sysess.sympathy.data.table.settablename'

    inputs = Ports([Port.Table('Input Table')])
    outputs = Ports([Port.Table(
        'Table with the name attribute changed according to node '
        'configuration')])

    def execute(self, node_context):
        node_context.output[0].update(node_context.input[0])
        node_context.output[0].set_name(node_context.parameters['name'].value)
        node_context.output[0].set_table_attributes(
            node_context.input[0].get_table_attributes())


@node_helper.list_node_decorator([0], [0])
class SetTablesName(SetTableName):
    name = 'Set Tables Name'
    nodeid = 'org.sysess.sympathy.data.table.settablesname'


def _get_single_col_editor():
    return synode.Util.combo_editor('', filter=True, edit=True)


class SetTablesNameTable(synode.Node):
    """Set name of a list of tables using another table with names."""

    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'rename_table.svg'
    name = 'Set Tables Name with Table'
    description = 'Set the name of a list of Tables'
    nodeid = 'org.sysess.sympathy.data.table.settablesnametable'
    tags = Tags(Tag.DataProcessing.TransformMeta)

    parameters = synode.parameters()
    editor = _get_single_col_editor()
    parameters.set_list(
        'names', label='Select name column',
        description='Select the columns with Table names',
        value=[0], editor=editor)

    inputs = Ports([
        Port.Tables('Input Tables', name='input'),
        Port.Table('A Table containing a column with names', name='names')])
    outputs = Ports([Port.Tables(
        'The list of Tables with the name attribute changed according to node '
        'configuration. All Tables will get the same name.', name='output')])

    def update_parameters(self, old_params):
        param = 'names'
        if param in old_params:
            old_params[param].editor = _get_single_col_editor()

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['names'],
               node_context.input[1])

    def validate_data(self, node_context):
        try:
            column_names = node_context.input[1].column_names()
        except ValueError:
            column_names = []
        return node_context.parameters['names'].selected in column_names

    def execute(self, node_context):
        input_len = len(node_context.input[0])

        if not input_len:
            return

        names_column = node_context.parameters['names'].selected
        if not self.validate_data(node_context):
            raise SyDataError('Selected column name needs to exist.')

        if node_context.input[1].is_empty():
            return
        names = node_context.input[1].get_column_to_array(names_column)
        output_list = node_context.output[0]

        if input_len != len(names):
            sywarn('Input list is of different length than the names column. '
                   'The output will follow the shorest length.')

        for input_table, new_name in zip(node_context.input[0], names):
            output = table.File()
            output.update(input_table)
            output.set_name(new_name)
            output.set_table_attributes(
                input_table.get_table_attributes())
            output_list.append(output)


class GetTableNameSuper(synode.Node):
    author = 'Andreas Tågerud'
    version = '1.0'
    icon = 'rename_table.svg'
    tags = Tags(Tag.DataProcessing.TransformMeta)


class GetTableName(GetTableNameSuper):
    """Get the name of a Table."""

    name = 'Get Table Name'
    description = 'Get name of a Table'
    nodeid = 'org.sysess.sympathy.data.table.gettablesnamestable'

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Table('Table name', name='port1')])

    def execute(self, node_context):
        node_context.output['port1'].set_column_from_array(
            'Table names', np.array([node_context.input['port1'].get_name()]))


class GetTablesNames(GetTableNameSuper):
    """Get the names of a list of Tables."""

    name = 'Get Tables Name'
    description = 'Get names of a list of Tables'
    nodeid = 'org.sysess.sympathy.data.table.gettablesnamestables'

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Table('All table names', name='port1')])

    def execute(self, node_context):
        names = [table.get_name() if table.get_name() is not None else ''
                 for table in node_context.input['port1']]
        node_context.output['port1'].set_column_from_array(
            'Table names', np.array(names))
