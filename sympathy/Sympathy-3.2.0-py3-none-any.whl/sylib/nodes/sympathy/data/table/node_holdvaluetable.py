# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust


def hold_column(array):
    missing = []
    if array.dtype.kind == 'f':
        missing = np.where(np.isnan(array))[0]
    elif array.dtype.kind in ['m', 'M']:
        missing = np.where(np.isnat(array))[0]

    mask = None

    if isinstance(array, np.ma.core.MaskedArray):
        for i in np.where(~array.mask)[0]:
            if i > 0:
                mask = np.zeros(len(array), dtype=bool)
                mask[:i] = True
            break

        idx = set()
        maskidx = np.flatnonzero(array.mask)

        idx.update(maskidx)
        idx.update(missing)
        missing = sorted(set(idx))

    it = iter(missing)

    try:
        i = next(it)
    except StopIteration:
        return array

    # Local copy for in-place edit.
    array = np.array(array)

    if i != 0:
        array[i] = array[i - 1]

    for i in it:
        array[i] = array[i - 1]

    if mask is not None:
        return np.ma.MaskedArray(array, mask)

    return array


def hold_table(in_table, out_table, hold_cnames):
    for cname in in_table.column_names():
        if cname in hold_cnames:
            out_table.set_column_from_array(
                cname, hold_column(in_table.get_column_to_array(cname)))
            out_table.set_column_attributes(
                cname, in_table.get_column_attributes(cname))
        else:
            out_table.update_column(cname, in_table)

    out_table.set_table_attributes(in_table.get_table_attributes())
    out_table.name = in_table.name


class HoldValueTable(node.Node):
    """
    Replace occurences of nan in cells by the last non-nan value from the same
    column.
    """
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'drop_nan.svg'
    tags = Tags(Tag.DataProcessing.TransformData)
    description = (
        'Replace occurences of nan in cells by the last non-nan value from '
        'the same column.')
    related = ['org.sysess.sympathy.data.table.holdvaluetables',
               'org.sysess.sympathy.data.table.dropnantable']

    name = 'Hold value Table'
    nodeid = 'org.sysess.sympathy.data.table.holdvaluetable'

    inputs = Ports([
        Port.Table('Input Table')])
    outputs = Ports([
        Port.Table('Output Table with NaN replaced')])

    parameters = node.parameters()
    parameters.set_list(
        'columns', label='Select columns', description='Select columns.',
        value=[], editor=node.Editors.multilist_editor(edit=True))
    parameters['columns']._passthrough = True

    def adjust_parameters(self, ctx):
        adjust(ctx.parameters['columns'], ctx.input[0])

    def execute(self, ctx):
        in_table = ctx.input[0]
        out_table = ctx.output[0]
        cols = ctx.parameters['columns'].selected_names(
            in_table.column_names())
        hold_table(in_table, out_table, cols)


@node_helper.list_node_decorator([0], [0])
class HoldValueTables(HoldValueTable):
    name = 'Hold value Tables'
    nodeid = 'org.sysess.sympathy.data.table.holdvaluetables'
