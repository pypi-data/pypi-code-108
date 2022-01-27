# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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

from sympathy.api import node
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyDataError
from sympathy.api import node_helper


class SetColumnNamesInTableWithTable(node.Node):
    """
    Set column names in data table to new names from chosen column in the name
    table.

    Since the new names are assigned based on indices, the number of rows in
    the name column must match the number of columns in the data table.


    Example
    ^^^^^^^

    Input data:

    +---+---+---+
    | A | B | C |
    +===+===+===+
    | 0 | 1 | 2 |
    +---+---+---+


    Input names:

    +-------+
    | Names |
    +=======+
    |   X   |
    +-------+
    |   Y   |
    +-------+
    |   Z   |
    +-------+


    Output data:

    +---+---+---+
    | X | Y | Z |
    +===+===+===+
    | 0 | 1 | 2 |
    +---+---+---+

    """

    name = 'Set column names in Table with Table'
    description = 'Set column names from separate table column.'
    nodeid = 'org.sysess.sympathy.setcolumnnamesintablewithtable'
    author = 'Erik der Hagopian'
    icon = 'rename_columns.svg'
    version = '1.0'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    related = [
        'org.sysess.sympathy.setcolumnnamesintableswithtable',
        'org.sysess.sympathy.getcolumnnamesintable',
        'org.sysess.sympathy.data.table.renamesingletablecolumns',
    ]

    parameters = node.parameters()
    parameters.set_string(
        'name', label='New names',
        description='Column with new names',
        editor=node.editors.combo_editor())

    inputs = Ports([
        Port.Table('Data', name='data'),
        Port.Table('Name', name='name')])
    outputs = Ports([
        Port.Table('Data', name='data')])

    def adjust_parameters(self, ctx):
        adjust(ctx.parameters['name'], ctx.input['name'])

    def execute(self, ctx):
        in_data_table = ctx.input['data']
        in_name_table = ctx.input['name']
        out_data_table = ctx.output['data']

        name_col = in_name_table._require_column(
            ctx.parameters['name'], types='U')

        if in_data_table.number_of_columns() != in_name_table.number_of_rows():
            raise SyDataError(
                "Number of name rows must be the same as the number of data "
                "columns.")

        if len(set(name_col)) != len(name_col):
            raise SyDataError('All new names must be unique.')

        out_data_table.name = in_data_table.name
        out_data_table.name = in_data_table.name
        out_data_table.set_table_attributes(
            in_data_table.get_table_attributes())

        for new_name, old_name in zip(name_col, in_data_table.column_names()):
            out_data_table.update_column(new_name, in_data_table, old_name)


@node_helper.list_node_decorator(['data'], ['data'])
class SetColumnNamesInTablesWithTable(SetColumnNamesInTableWithTable):
    name = 'Set column names in Tables with Table'
    description = 'Set column names from separate table column.'
    nodeid = 'org.sysess.sympathy.setcolumnnamesintableswithtable'


class GetColumnNamesInTable(node.Node):
    name = 'Get column names in Table'
    description = 'Get all column names of input table as a column.'
    nodeid = 'org.sysess.sympathy.getcolumnnamesintable'
    author = 'Magnus Sandén'
    icon = 'rename_columns.svg'
    version = '1.0'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    related = [
        'org.sysess.sympathy.setcolumnnamesintablewithtable',
        'org.sysess.sympathy.data.table.renamesingletablecolumns',
    ]

    inputs = Ports([
        Port.Table('Data', name='data')])
    outputs = Ports([
        Port.Table('Column names', name='names')])

    def execute(self, node_context):
        input_table = node_context.input['data']
        output_table = node_context.output['names']
        output_table['Column names'] = np.array(input_table.column_names())
