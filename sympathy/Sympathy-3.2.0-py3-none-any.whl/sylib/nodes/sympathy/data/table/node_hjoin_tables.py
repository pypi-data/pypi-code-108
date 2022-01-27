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
The operation of horizontal join, or HJoin, stacks the columns in the incoming
:ref:`Tables` horizontally beside each other. The outgoing Table will have all
the columns from all the incoming Tables.

If the setting 'Complement missing rows' is false then all Tables that should
be joined must have the same number of rows. Otherwise, Tables with different
number of rows are padded with masked values.

If a column name exists in both inputs the latter Table (or lower port) will
take precedence and the corresponding column from the former Table (or upper
port) will be lost.

The node always tries to give the output table a name, so if the chosen
port has a table without name, the other port will be used. This is
to preserve backwards compatibility.
"""
import itertools
from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError


def _join_table(table1, table2, first_name, mask=False, rename=False):
    if ((table1.number_of_rows() != table2.number_of_rows())
            and table1.number_of_columns() and table2.number_of_columns()
            and not mask):
        raise SyDataError(
            'Number of rows mismatch in tables ({} vs {})'.format(
                table1.number_of_rows(), table2.number_of_rows()))
    name1 = table1.get_name()
    name2 = table2.get_name()
    if not name1:
        name = name2
    elif not name2:
        name = name1
    else:
        name = name1 if first_name else name2
    table1.hjoin(table2, mask=mask, rename=rename)
    table1.set_name(name)
    return table1


class HJoinTableSuper(synode.Node):
    author = "Alexander Busck"
    version = '1.1'
    icon = 'hjoin_table.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = [
        'org.sysess.sympathy.data.table.hjointable',
        'org.sysess.sympathy.data.table.hjointables',
        'org.sysess.sympathy.data.table.hjointablessingle',
        'org.sysess.sympathy.data.table.hsplittablenode',
    ]

    parameters = {}
    parameter_root = synode.parameters(parameters)
    parameter_root.set_boolean(
        'mask', value=True, label='Complement missing rows',
        description='Select if rows that are not represented in all '
                    'Tables should be complemented with masked values')
    parameter_root.set_boolean(
        'rename', value=False, label='Rename duplicate columns',
        description=('If true columns with same name as an earlier column '
                     'will be renamed and joined, otherwise columns will '
                     'overwrite existing data'))
    parameter_root.set_list(
        'name',
        plist=['Lower', 'Upper'],
        label='Input port name for joined table',
        description='Select which port decides the output table(s) names',
        value=[0],
        editor=synode.Util.combo_editor())

    def update_parameters(self, old_params):
        if 'mask' not in old_params:
            old_params['mask'] = self.parameter_root['mask']
            old_params['mask'].value = False
        if 'rename' not in old_params:
            old_params['rename'] = self.parameter_root['rename']
            old_params['rename'].value = False


class HJoinTable(HJoinTableSuper):
    """
    Horizontal join of two Tables into a single Table.

    For convenience, it is possible to duplicate the second port.  This makes
    it possible to join several inputs using one nodes.
    """

    name = 'HJoin Table'
    description = 'Horizontal join of two Tables'
    nodeid = 'org.sysess.sympathy.data.table.hjointable'

    inputs = Ports([
        Port.Custom('table', 'Input Table', name='port1', n=(1, 1)),
        Port.Custom('table', 'Input Table', name='port2', n=(1, None))])
    outputs = Ports([Port.Table(
        'Table with horizontally joined data', name='port1')])

    def execute(self, ctx):
        out_table = ctx.output['port1']
        iter_in_tables1 = iter(ctx.input.group('port1'))
        in_table1 = next(iter_in_tables1)

        for in_table2 in itertools.chain(
                iter_in_tables1, ctx.input.group('port2')):
            _join_table(in_table1, in_table2,
                        ctx.parameters['name'].value[0],
                        mask=ctx.parameters['mask'].value,
                        rename=ctx.parameters['rename'].value)
        out_table.source(in_table1)


@node_helper.list_node_decorator(['port1', 'port2'], ['port1'])
class HJoinTables(HJoinTable):
    nodeid = 'org.sysess.sympathy.data.table.hjointables'
    name = 'HJoin Tables pairwise'


class HJoinTablesSingle(synode.Node):
    """
    Horizontal join of all incoming Tables into a single outgoing Table.
    Columns from Tables later in the list will take precedence in the case when
    a certain column name exists in two or more Tables.
    """

    author = "Greger Cronquist"
    version = '1.0'
    icon = 'hjoin_table.svg'
    name = 'HJoin Tables'
    description = 'HJoin Tables to Table'
    nodeid = 'org.sysess.sympathy.data.table.hjointablessingle'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = [
        'org.sysess.sympathy.data.table.hjointable',
        'org.sysess.sympathy.data.table.hjointables',
        'org.sysess.sympathy.data.table.hjointablessingle',
        'org.sysess.sympathy.data.table.hsplittablenode',
    ]

    inputs = Ports([Port.Tables('Input Tables', name='port1')])
    outputs = Ports([
        Port.Table('Table with horizontally joined data from the incoming '
                   'list of Tables.', name='port1')])

    parameters = {}
    parameter_root = synode.parameters(parameters)
    parameter_root.set_boolean(
        'mask', value=True, label='Complement missing rows',
        description='Select if rows that are not represented in all '
                    'Tables should be complemented with masked values')
    parameter_root.set_boolean(
        'rename', value=False, label='Rename duplicate columns',
        description=('If true columns with same name as an earlier column '
                     'will be renamed and joined, otherwise columns will '
                     'overwrite existing data'))

    def update_parameters(self, old_params):
        if 'mask' not in old_params:
            old_params['mask'] = self.parameter_root['mask']
            old_params['mask'].value = False
        if 'rename' not in old_params:
            old_params['rename'] = self.parameter_root['rename']
            old_params['rename'].value = False

    def execute(self, ctx):
        in_files = ctx.input['port1']
        out_tablefile = ctx.output['port1']

        if not in_files:
            return

        for i, table in enumerate(in_files):
            progress = (100.0 * i) / len(in_files)
            self.set_progress(progress)
            out_tablefile.hjoin(
                table,
                mask=ctx.parameters['mask'].value,
                rename=ctx.parameters['rename'].value)
        out_tablefile.set_name(in_files[-1].get_name())
