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
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags


class HSplitTableNode(synode.Node):
    author = "Greger Cronquist"
    version = '1.0'
    icon = 'hsplit_table.svg'

    name = 'HSplit Table'
    description = ('Split a Table into multiple Tables by columns, '
                   'every column becomes a new table.')
    nodeid = 'org.sysess.sympathy.data.table.hsplittablenode'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.data.table.hsplittablenodes',
               'org.sysess.sympathy.data.table.hjointable']

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Tables('Split Tables', name='port1')])

    def execute(self, node_context):
        tablefile = node_context.input['port1']
        outfilelist = node_context.output['port1']
        columns = tablefile.column_names()
        number_of_columns = len(columns)
        original_name = tablefile.get_name()
        for col_number, column in enumerate(columns):
            table_outfile = outfilelist.create()
            table_outfile.update_column(column, tablefile, column)
            table_outfile.set_name(u'{0}-{1}'.format(
                original_name, col_number))
            outfilelist.append(table_outfile)
            self.set_progress(100.0 * (col_number + 1) /
                              number_of_columns)


class HSplitTablesNode(synode.Node):
    """
    Flattened output
    ----------------
    This node flattens the output into a single list of Tables which can be
    convenient, but it makes it difficult to know the origin of a specific
    table in the output. If this is important to your use case, you can also
    consider using :ref:`org.sysess.sympathy.data.table.hsplittablenode`
    inside a Lambda and Map that over the input resulting in the type
    ``[[table]]``.
    """

    author = "Greger Cronquist"
    version = '1.0'
    icon = 'hsplit_table.svg'

    name = 'HSplit Tables'
    description = ('Split a list of Table into multiple Tables, '
                   'every column becomes a new table.')
    nodeid = 'org.sysess.sympathy.data.table.hsplittablenodes'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.data.table.hsplittablenode',
               'org.sysess.sympathy.data.table.hjointable']

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Tables('Split Tables', name='port1')])

    def execute(self, node_context):
        infilelist = node_context.input['port1']
        outfilelist = node_context.output['port1']
        for intable in infilelist:
            original_name = intable.get_name()
            for col_number, column in enumerate(intable.column_names()):
                output = outfilelist.create()
                output.update_column(column, intable, column)
                output.set_name(u'{0}-{1}'.format(original_name, col_number))
                outfilelist.append(output)
