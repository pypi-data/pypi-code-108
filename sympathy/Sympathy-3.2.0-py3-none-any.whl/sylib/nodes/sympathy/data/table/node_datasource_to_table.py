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
import os.path
import numpy as np
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sylib import datasource_conversion as dc
from sympathy.api.exceptions import SyDataError


common_docs = """
The outgoing :ref:`Table` will consist of a single column with filepaths. The
length of the column will be equal to the incoming number of datasources.

In the configuration GUI it is possible to select if one wants to convert
the paths in the Datasources to absolute filepaths.

For an explanation of relative datasource file paths, see
:ref:`datasource_node_file`.
"""


class SuperNode(synode.Node):
    author = "Magnus Sanden"
    version = "1.1"
    icon = "dsrc2table.svg"
    tags = Tags(Tag.DataProcessing.Convert)
    related = ['org.sysess.sympathy.data.table.dsrctotable',
               'org.sysess.sympathy.data.table.dsrcstotable',
               'org.sysess.sympathy.data.table.tabletodsrcs']

    outputs = Ports(
        [Port.Table("Table with a single column with a filepath", name="out")])

    parameters = synode.parameters()
    dc.set_output_relative_topflow_param(parameters)
    dc.set_output_relative_subflow_param(parameters)

    controllers = (
        synode.controller(
            when=synode.field('relpath', state='checked'),
            action=(
                synode.field('subpath', state='disabled'),
            ),
        ),
        synode.controller(
            when=synode.field('subpath', state='checked'),
            action=(
                synode.field('relpath', state='disabled'),
            ),
        ),
    )


class DsrcToTable(SuperNode):
    __doc__ = common_docs

    name = "Datasource to Table"
    description = ("Convert a single data source into a table containing that "
                   "filename.")
    nodeid = "org.sysess.sympathy.data.table.dsrctotable"

    inputs = Ports(
        [Port.Datasource("Datasource with filepaths", name="in")])

    def execute(self, node_context):
        flow_path = dc.flow_path(node_context.parameters['subpath'])

        filepath = []
        if node_context.input['in'].decode_path() is not None:
            filepath = [_format_path(
                node_context.input['in'].decode_path(),
                node_context.parameters['relpath'].value,
                flow_path)]
        node_context.output['out'].set_column_from_array(
            'filepaths', np.array(filepath, dtype='U'))


class DsrcsToTable(SuperNode):
    __doc__ = common_docs

    name = "Datasources to Table"
    description = "Converts a list of data sources into a table of filenames."
    nodeid = "org.sysess.sympathy.data.table.dsrcstotable"

    inputs = Ports(
        [Port.Datasources("Datasources with filepaths", name="in")])

    def execute(self, node_context):
        flow_path = dc.flow_path(node_context.parameters['subpath'])
        rel_path = node_context.parameters['relpath'].value

        filepaths = []
        for infile in node_context.input['in']:
            filepath = _format_path(
                infile.decode_path(),
                rel_path,
                flow_path)
            filepaths.append(filepath)
        node_context.output['out'].set_column_from_array(
            'filepaths', np.array(filepaths, dtype='U'))


def _format_path(path, relpath, flow_path):
    relative = None
    if flow_path:
        relative = flow_path
    elif relpath:
        relative = os.curdir
    try:
        if relative:
            return os.path.relpath(path, relative)
    except Exception:
        raise SyDataError(
            f'Path: "{path}", can not be made relative to "{relative}".')
    return os.path.abspath(path)
