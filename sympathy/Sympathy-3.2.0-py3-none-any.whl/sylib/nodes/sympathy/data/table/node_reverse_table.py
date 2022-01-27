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
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import node_helper


class ReverseColumnsTable(synode.Node):
    """
    Reverse columns in Table.
    """

    author = "Erik der Hagopian"
    name = 'Reverse columns in Table'
    nodeid = 'org.sysess.sympathy.reverse.columns.table'
    icon = 'sort_table_cols.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.reverse.rows.table']
    inputs = Ports([Port.Table('Input Table', name='data')])
    outputs = Ports([Port.Table('Output Table', name='data')])
    parameters = synode.parameters()

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']
        output_data.update(input_data[:, ::-1])
        output_data.set_name(input_data.get_name())
        output_data.set_table_attributes(input_data.get_table_attributes())


@node_helper.list_node_decorator(['data'], ['data'])
class ReverseColumnsTables(ReverseColumnsTable):
    name = 'Reverse columns in Tables'
    nodeid = 'org.sysess.sympathy.reverse.columns.tables'


class ReverseRowsTable(synode.Node):
    """
    Reverse rows in Table.
    """

    author = "Erik der Hagopian"
    name = 'Reverse rows in Table'
    nodeid = 'org.sysess.sympathy.reverse.rows.table'
    icon = 'sort_table_rows.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.reverse.columns.table']
    inputs = Ports([Port.Table('Input Table', name='data')])
    outputs = Ports([Port.Table('Output Table', name='data')])
    parameters = synode.parameters()

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']
        output_data.update(input_data[::-1])
        output_data.set_name(input_data.get_name())
        output_data.set_table_attributes(input_data.get_table_attributes())


@node_helper.list_node_decorator(['data'], ['data'])
class ReverseRowsTables(ReverseRowsTable):
    name = 'Reverse rows in Tables'
    nodeid = 'org.sysess.sympathy.reverse.rows.tables'
