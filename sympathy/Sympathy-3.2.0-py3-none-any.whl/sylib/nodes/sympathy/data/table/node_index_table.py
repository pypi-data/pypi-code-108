# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
from sympathy.api.exceptions import SyDataError, NoDataError
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api import node_helper
import sylib.index


def _get_single_col_editor():
    return node.Util.combo_editor('', filter=True, edit=True)


class IndexTable(node.Node):
    name = 'Index table'
    description = (
        'Uses index-table to perform row indexation from value-table.\n'
        'No other datatypes than integer or boolean are allowed in the index '
        'column')
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'lookup.svg'

    nodeid = 'org.sysess.sympathy.data.table.indextable'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    inputs = Ports([
        Port.Table('Value table', name='value'),
        Port.Table('Index table', name='index')
    ])
    outputs = Ports([
        Port.Table('Result table', name='out')
    ])

    editor = _get_single_col_editor()

    parameters = node.parameters()
    parameters.set_list(
        'index column', label='Select indexing column',
        description='Select column used for indexing.',
        value=[], editor=editor)
    parameters.set_boolean(
        'at_one', label='Start at one',
        description='Start indexing at one, otherwise at zero',
        value=False)
    parameters.set_list(
                'operation', label='Operation',
                list=['Include', 'Exclude'], value=[0],
                description='If to include or exclude rows',
                editor=node.Util.combo_editor().value())

    def update_parameters(self, old_params):
        param = 'index column'
        if param in old_params:
            old_params[param].editor = _get_single_col_editor()

    def execute(self, node_context):
        index_tbl = node_context.input['index']
        value_tbl = node_context.input['value']
        out_tbl = node_context.output['out']
        at_one = node_context.parameters['at_one'].value
        exclude = node_context.parameters['operation'].selected == 'Exclude'

        index_param = node_context.parameters['index column']
        index_col = index_param.selected
        if not index_col:
            column_names = index_tbl.column_names()
            if column_names:
                index_col = column_names[0]
        indices = index_tbl._require_column(index_param, name=index_col)

        if indices.dtype.kind == 'i':

            try:
                fail = at_one and np.min(np.ma.compressed(indices)) < 1
            except ValueError:
                fail = False

            if fail:
                raise SyDataError('Start at one requires integer column '
                                  'with values >= 1.')
            indices = indices - at_one
        elif at_one:
            raise SyDataError('Invalid datatype {} in index column. '
                              'Start at one requires integer column.'
                              .format(indices.dtype))

        if indices.dtype.kind not in ['b', 'i']:
            raise SyDataError('Invalid datatype {} in index column'
                              .format(indices.dtype))

        for col in value_tbl.cols():
            if exclude:
                mask = np.ones(col.data.shape[0], dtype=bool)
                mask[indices] = False
                out_tbl.set_column_from_array(col.name, col.data[mask])
            else:
                out_tbl.set_column_from_array(col.name, col.data[indices])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['index column'],
               node_context.input['index'])


class CreateIndexTable(node.Node):
    """
    Create an index column for table data.

    The name of the resulting index column depends on the *name* parameter and
    its values are computed depending on the *method* used and the *columns*
    selected.
    """
    name = 'Create Index Table'
    description = 'Create an index column for table data'
    icon = 'lookup.svg'
    nodeid = 'org.sysess.sympathy.data.table.createindextable'
    tags = Tags(Tag.DataProcessing.Index)

    inputs = Ports([
        Port.Table('Input table', name='input'),
    ])
    outputs = Ports([
        Port.Table('Output table', name='output')
    ])

    _enumerate_rows, _enumerate_unique = _options = [
        'Enumerate rows', 'Enumerate unique rows']

    parameters = node.parameters()
    parameters.set_string(
        'method', label='Select index creation method',
        description='Select method used for index creation.',
        value=_enumerate_rows,
        editor=node.Editors.combo_editor(options=_options))

    parameters.set_list(
        'columns', label='Select columns',
        description='Select columns used for building the index.',
        value=[], editor=node.Editors.multilist_editor(edit=True))

    parameters.set_string(
        'name', label='Name of index column',
        description='Select name for index column.',
        value='index')

    controllers = node.controller(
        when=node.field('method', 'value', value=_enumerate_rows),
        action=node.field('columns', 'disabled'))

    def execute(self, node_context):
        input_ = node_context.input['input']
        output = node_context.output['output']
        output.source(input_)
        method = node_context.parameters['method'].value
        name = node_context.parameters['name'].value

        method = node_context.parameters['method'].value
        if method == self._enumerate_rows:
            output[name] = np.arange(input_.number_of_rows())
        elif method == self._enumerate_unique:
            selected_names = node_context.parameters['columns'].selected_names(
                input_.column_names())
            unique = {}
            indices = []
            count = 0
            for values in zip(*[input_[col].tolist()
                                for col in selected_names]):
                values = tuple(values)
                i = unique.get(values)
                if i is not None:
                    indices.append(i)
                else:
                    unique[values] = count
                    indices.append(count)
                    count += 1
            output[name] = np.array(indices)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'],
               node_context.input['input'])


class IndexColumnsTable(node.Node):
    __doc__ = f"""
    Index columns in Table.

    {sylib.index.index_doc}
    """

    author = "Erik der Hagopian"
    name = 'Index columns in Table'
    nodeid = 'org.sysess.sympathy.index.columns.table'
    icon = 'lookup.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.index.rows.table']
    inputs = Ports([Port.Table('Input Table', name='data')])
    outputs = Ports([Port.Table('Output Table', name='data')])
    parameters = node.parameters()
    sylib.index.set_parameters(parameters)

    def _column_indices(self, table):
        return [str(i) for i in range(table.number_of_columns())]

    def adjust_parameters(self, ctx):
        indices = []
        try:
            indices = self._column_indices(ctx.input['data'])
        except NoDataError:
            pass
        ctx.parameters['index'].adjust(indices)

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']
        index = ctx.parameters['index']
        lookup = {str(i): name for i, name in
                  enumerate(input_data.column_names())}
        selected = index.selected_names(list(lookup.keys()))
        output_data.set_name(input_data.get_name())
        output_data.set_table_attributes(input_data.get_table_attributes())
        for i in selected:
            output_data.update_column(lookup[i], input_data)


@node_helper.list_node_decorator(['data'], ['data'])
class IndexColumnsTables(IndexColumnsTable):
    name = 'Index columns in Tables'
    nodeid = 'org.sysess.sympathy.index.columns.tables'

    def _column_indices(self, tables):
        rows = [t.number_of_rows() for t in tables]
        rows.append(0)
        return [str(i) for i in range(max(rows))]


class IndexRowsTable(node.Node):
    __doc__ = f"""
    Index rows in Table.

    {sylib.index.index_doc}

    Because the number of rows can become very large, only selected indices are
    shown. To add, right-click and press Insert. Then rename the entry to the
    desired integer index and check it.
    """

    author = "Erik der Hagopian"
    name = 'Index rows in Table'
    nodeid = 'org.sysess.sympathy.index.rows.table'
    icon = 'lookup.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.index.columns.table']
    inputs = Ports([Port.Table('Input Table', name='data')])
    outputs = Ports([Port.Table('Output Table', name='data')])
    parameters = node.parameters()
    sylib.index.set_parameters(
        parameters,
        description=(
            f'{sylib.index.index_description}\n'
            'Because the number of rows can become '
            'too large, only selected indices are shown. To add, right-click '
            'and press Insert.\nThe values must be edited to integer values'))

    def _row_indices(self, table):
        return [str(i) for i in range(table.number_of_rows())]

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']
        index = ctx.parameters['index']
        names = [i for i in self._row_indices(input_data)]
        indices = [int(i) for i in index.selected_names(names)]
        output_data.update(input_data[np.array(indices)])
        output_data.set_name(input_data.get_name())
        output_data.set_table_attributes(input_data.get_table_attributes())


@node_helper.list_node_decorator(['data'], ['data'])
class IndexRowsTables(IndexRowsTable):
    name = 'Index rows in Tables'
    nodeid = 'org.sysess.sympathy.index.rows.tables'
