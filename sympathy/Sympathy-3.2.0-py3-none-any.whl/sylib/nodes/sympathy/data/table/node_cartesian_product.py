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
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
# from sympathy.api.exceptions import SyDataError

import numpy as np


common_docs = """
Cartesian product of a number of tables create a new table
containing all combinations of rows of the inputs. This output have
one column for each unique column in the input tables. For example two
tables with A and B columns of length N and M each create a new table
of length N * M and containing A + B columns. It is an error to have
duplicate column names.
"""


class CartesianProductTable(synode.Node):
    __doc__ = common_docs

    name = 'Cartesian Product Table'
    description = 'Cartesian product of two or more Tables into a single Table.'
    nodeid = 'se.combine.sympathy.data.table.cartesian_product_table'
    author = "Mathias Broxvall"
    version = '1.0'
    icon = 'cartesian_product.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['se.combine.sympathy.data.table.cartesian_product_tables']

    parameters = {}
    parameter_root = synode.parameters(parameters)

    inputs = Ports([
        Port.Custom('table', 'Input Tables', name='in', n=(2, None))])
    outputs = Ports([
        Port.Table('Table with cartesian product of inputs', name='out')])

    def execute(self, node_context):
        """Execute"""
        inputs = node_context.input.group('in')
        output = node_context.output['out']
        lens = [i.number_of_rows() for i in inputs]

        for i in range(len(list(inputs))):
            left = int(np.product(lens[:i]))
            right = int(np.product(lens[i+1:]))
            for column in inputs[i].cols():
                data = [val for val in column.data for _ in range(right)] * left
                output.set_column_from_array(column.name, np.array(data))


class CartesianProductTables(synode.Node):
    __doc__ = common_docs

    name = 'Cartesian Product Tables'
    description = 'Cartesian product of a list of Tables into a single Table.'
    nodeid = 'se.combine.sympathy.data.table.cartesian_product_tables'
    author = "Mathias Broxvall"
    version = '1.0'
    icon = 'cartesian_product.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['se.combine.sympathy.data.table.cartesian_product_table']

    parameters = {}
    parameter_root = synode.parameters(parameters)

    inputs = Ports([
        Port.Custom('[table]', 'List of input tables', name='in')])
    outputs = Ports([
        Port.Table('Table with cartesian product of inputs', name='out')])

    def execute(self, node_context):
        """Execute"""
        inputs = node_context.input['in']
        output = node_context.output['out']
        lens = [i.number_of_rows() for i in inputs]

        for i in range(len(list(inputs))):
            left = int(np.product(lens[:i]))
            right = int(np.product(lens[i+1:]))
            for column in inputs[i].cols():
                data = [val for val in column.data for _ in range(right)] * left
                output.set_column_from_array(column.name, np.array(data))

