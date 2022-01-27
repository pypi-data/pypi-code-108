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
import os
import contextlib
import dask.array as da
import numpy as np

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.nodeconfig import settings
from sympathy.api.exceptions import sywarn, SyNodeError


DASK_NODEIDS = [
    'org.sysess.sympathy.examples.daskstack',
    'org.sysess.sympathy.examples.dasktail',
    'org.sysess.sympathy.examples.daskmax',
    'org.sysess.sympathy.examples.daskvisualize',
]


@contextlib.contextmanager
def prefix_paths(paths):
    old_path = new_path = os.environ.get('PATH')
    if old_path:
        paths = paths + [old_path]
    paths = [path for path in paths if path]
    new_path = os.pathsep.join(paths)
    os.environ['PATH'] = new_path
    try:
        yield
    finally:
        if old_path is None:
            del os.environ['PATH']
        else:
            os.environ['PATH'] = old_path


class DaskStack(synode.Node):
    """
    This example shows a basic version of *VJoin Table*, implemented using
    dask.
    It requires the same columns to be present, and of the same type, in all
    inputs.

    Dask nodes have biggest effect in locked subflows and lambdas where
    data between nodes is passed in memory.
    """
    name = 'Dask stack example'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating stacking tables using dask.'
    nodeid = 'org.sysess.sympathy.examples.daskstack'
    tags = Tags(Tag.Development.Example)
    related = DASK_NODEIDS + ['org.sysess.sympathy.data.table.vjointablenode']

    inputs = Ports(
        [Port.Custom('table', 'Input Table', name='input', n=(2, None))])
    outputs = Ports(
        [Port.Table('Output Table', name='output')])

    def execute(self, node_context):
        tis = node_context.input.group('input')
        to = node_context.output['output']

        for col in tis[0].column_names():
            to.set_column_from_array(col, da.concatenate(
                [ti.get_column_to_array(col, kind='dask') for ti in tis]))


class DaskTail(synode.Node):
    """
    This example shows a basic version of tail, implemented using dask.
    Tail produces a new table similar to *Slice data Table* with
    *1:* as the slice expression.

    Dask nodes have biggest effect in locked subflows and lambdas where
    data between nodes is passed in memory.
    """

    name = 'Dask tail example'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating the tail of a table using dask.'
    nodeid = 'org.sysess.sympathy.examples.dasktail'
    tags = Tags(Tag.Development.Example)
    related = DASK_NODEIDS + ['org.sysess.sympathy.slice.rows.table']

    inputs = Ports(
        [Port.Table('Input Table', name='input')])
    outputs = Ports(
        [Port.Table('Output Table', name='output')])

    def execute(self, node_context):
        ti = node_context.input['input']
        to = node_context.output['output']

        for col in ti.column_names():
            to.set_column_from_array(
                col,
                ti.get_column_to_array(col, kind='dask')[1:])


class DaskMax(synode.Node):
    """
    This example shows a basic table version of column-wise *max*,
    implemented using dask.

    Dask nodes have biggest effect in locked subflows and lambdas where
    data between nodes is passed in memory.
    """

    name = 'Dask max example'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating column-wise max using dask.'
    nodeid = 'org.sysess.sympathy.examples.daskmax'
    tags = Tags(Tag.Development.Example)
    related = DASK_NODEIDS + ['org.sysess.sympathy.keyvaluecalculation']

    inputs = Ports(
        [Port.Table('Input Table', name='input')])
    outputs = Ports(
        [Port.Table('Output Table', name='output')])

    def execute(self, node_context):
        ti = node_context.input['input']
        to = node_context.output['output']

        for col in ti.column_names():
            to.set_column_from_array(
                col, np.array(
                    [ti.get_column_to_array(
                        col, kind='dask').max().compute()]))


class DaskVisualize(synode.Node):
    """
    This example shows how to visualize a dask column graph as a image file
    written to disk.

    Output file format is selected by typing the desired file extension.
    .svg and .png are supported.

    This example requires `Graphviz <https://www.graphviz.org>`__
    to be installed and configured. Additionally the
    `graphviz <https://pypi.org/project/graphviz>`__ python package is also
    required, it can be installed by running::

        python -m pip install graphviz

    in the python environment that is used to run Sympathy.

    """
    name = 'Dask visualize example'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'example.svg'
    description = 'Node example demonstrating graph visualization using dask.'
    nodeid = 'org.sysess.sympathy.examples.daskvisualize'
    tags = Tags(Tag.Development.Example)
    related = DASK_NODEIDS

    inputs = Ports(
        [Port.Table('Input Table', name='input_table')])
    outputs = Ports(
        [Port.Datasource(
            'Output Datasource', name='output_datasource', n=(0, 1, 0))])

    parameters = synode.parameters()
    parameters.set_string(
        'column', label='Column',
        description='Column to visualize.',
        editor=synode.editors.combo_editor())

    parameters.set_string(
        'filename', label='Filename',
        editor=synode.editors.savename_editor(['Any files (*)']),
        description=('Manually enter a filename (use .svg extensions to get '
                     'vector graphics)'))

    def execute(self, node_context):
        gviz_path = settings()['Debug/graphviz_path']
        ti = node_context.input['input_table']
        column = node_context.parameters['column'].value
        filename = os.path.abspath(
            node_context.parameters['filename'].value)
        data = ti.get_column_to_array(column, kind='dask')

        with prefix_paths([gviz_path]):
            try:
                data.visualize(filename)
            except Exception as e:
                raise SyNodeError(
                    f'Error visualizing graph, '
                    f'make sure that Graphviz is installed and configured in '
                    f'Sympathy.\n'
                    f'{str(e).rstrip(".")}.')

        if node_context.output.group('output_datasource'):
            node_context.output['output_datasource'].encode_path(filename)

    def adjust_parameters(self, node_context):
        """
        This method is called before configure. In this example it fills one of
        the list of selectable columns with column names from the input table.
        """
        adjust(node_context.parameters['column'],
               node_context.input['input_table'])
