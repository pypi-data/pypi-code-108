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
The operation of vertical join, or VJoin, stacks the columns from
the incoming :ref:`Tables` that have the same name vertically upon
each other, under the condition that they exist in all Tables. If the
condition is fulfilled the number of rows in the outgoing Table will
be equal to the sum of the number of rows in the incoming Tables. If
there exist no overlap over all Tables the output will be an empty
Table.

In the GUI it is possible to override the overlap requirement and let
the node work in a state where the output will include all columns
that exist in the incoming Tables. The columns that do not exist in
all Tables are either ignored, created as a "masked" value, or
complemented with default values.  The strategy for this is decided by
the "Complement missing columns"-checkbox as well as the
"Complement-strategy" combo options. In the case of complementing with
a value a column with numerical values is filled with NaNs while for a
column with strings the elements it is filled with empty strings.

When the columns stacked have different types, the node will try to find a
result type to accommodate the new values. For example, combining an integer
and a boolean would result in an integer column with the boolean values
translated from False to 0 and True to 1. LIMITATION: If the types differ and
part of the column is date-time or time-delta no resulting type can be found.

An index column will be created in the outgoing Table if a name is specified
for the column in the GUI, by default the index column has the name
"VJoin-index". In the index column, elements in the joined output that
originate from the same incoming Table will be given the same index number.
If one wants to do the reversed operation, :ref:`VSplit Table`, the index
column is important. No index column will be created if the specified name
is an empty string.

In the GUI it is also possible to specify the name of an incoming index column,
a column with information about previous VJoin operations. If the specified
index column exists in the incoming Tables the information of the previous join
operations will be regarded when the new index column is constructed. The new
index column will replace the old ones in the output of the node.

An increment will be applied to the outgoing index column if there exist
incoming Tables with the number of rows equal to zero. The size of this
increment can be specified in the GUI of the node, where default value is 0.
The vertical join, or VJoin, is one of two operations that merge the
content of a number of :ref:`Tables` into a new Table. The other operation
in this category is the horizontal join, see :ref:`HJoin Table` to obtain more
information.
"""
import itertools
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions as exc
from sylib import vjoin


class VJoinBase(synode.Node):
    parameters = vjoin.base_params()
    controllers = vjoin.base_controller()
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = [
        'org.sysess.sympathy.data.table.vjointablenode',
        'org.sysess.sympathy.data.table.vjointablenodelist',
        'org.sysess.sympathy.data.table.vjointablenodes',
        'org.sysess.sympathy.data.table.vsplittablenode',
    ]

    def update_parameters(self, old_params):
        if 'fill_strategy' not in old_params:
            vjoin.set_fill_strategy_param(old_params, 0)

    def vjoin(self, output_table, input_tables, input_index, output_index,
              fill, minimum_increment):

        try:
            output_table.vjoin(
                input_tables,
                input_index,
                output_index,
                fill,
                minimum_increment)
        except exc.SyColumnTypeError:
            raise exc.SyDataError(
                'Input columns to stack have incompatible types',
                details=(
                    'Input columns to stack have incompatible types. '
                    'Keep in mind that datetime and timedelta cannot be '
                    'combined with other types'))


class VJoinTableNode(VJoinBase):
    """
    Vertical join of two Tables.

    For convenience, it is possible to duplicate the second port.  This makes
    it possible to join several inputs using one nodes.
    """

    author = "Alexander Busck"
    version = '1.0'
    icon = 'vjoin_table.svg'

    name = 'VJoin Table'
    description = ('Vertical join of two Tables.')
    nodeid = 'org.sysess.sympathy.data.table.vjointablenode'

    inputs = Ports([
        Port.Custom('table', 'Input Table', name='port1', n=(1, 1)),
        Port.Custom('table', 'Input Table', name='port2', n=(1, None))])
    outputs = Ports([Port.Table('Joined Table', name='port1')])

    def execute(self, node_context):
        input_tables1 = node_context.input.group('port1')
        input_tables2 = node_context.input.group('port2')
        output_table = node_context.output['port1']
        input_index, output_index, minimum_increment, fill = vjoin.base_values(
            node_context.parameters)

        self.vjoin(
            output_table,
            list(itertools.chain(input_tables1, input_tables2)),
            input_index,
            output_index,
            fill,
            minimum_increment)


@node_helper.list_node_decorator(['port1', 'port2'], ['port1'])
class VJoinTableMultipleNode(VJoinTableNode):
    name = 'VJoin Tables pairwise'
    nodeid = 'org.sysess.sympathy.data.table.vjointablenodelist'


class VJoinTablesNode(VJoinBase):
    """
    Vertical join of Tables.
    """

    author = "Alexander Busck"
    version = '1.0'
    icon = 'vjoin_table.svg'

    name = 'VJoin Tables'
    description = ('Vertical join of Tables.')
    nodeid = 'org.sysess.sympathy.data.table.vjointablenodes'

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([Port.Table('Joined Tables', name='port1')])

    def execute(self, node_context):
        input_tables = node_context.input['port1']
        output_table = node_context.output['port1']
        input_index, output_index, minimum_increment, fill = vjoin.base_values(
            node_context.parameters)

        self.vjoin(
            output_table,
            input_tables,
            input_index,
            output_index,
            fill,
            minimum_increment)
