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
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.exceptions import SyDataError


class AssertEqualTable(node.Node):
    """Compare two incoming tables and raise an error if they differ."""

    name = 'Assert Equal Table'
    author = 'Magnus Sandén'
    version = '1.0'
    icon = ''
    description = ''
    nodeid = 'org.sysess.sympathy.data.table.assertequaltable'
    icon = 'assert_equal.svg'
    tags = Tags(Tag.Development.Test)

    inputs = Ports([
        Port.Table('Table A', name='table1'),
        Port.Custom('table', 'Table B', name='table2', n=(1, None))])
    outputs = Ports([
        Port.Table('Output Table', name='out')])

    parameters = node.parameters()
    parameters.set_boolean(
        'col_order', value=True, label='Compare column order',
        description='Differing column order will trigger error')
    parameters.set_boolean(
        'col_attrs', value=True, label='Compare column attributes',
        description='Differing column attributes will trigger error')
    parameters.set_boolean(
        'tbl_names', value=True, label='Compare table names',
        description='Differing table name will trigger error')
    parameters.set_boolean(
        'tbl_attrs', value=True, label='Compare table attributes',
        description='Differing table attributes will trigger error')
    parameters.set_boolean(
        'inexact_float', value=False, label='Approximate comparison of floats',
        description='If any arithemtics is invovled floats should probably '
                    'be compared approximately.')
    parameters.set_float(
        'rel_tol', value=1e-5, label='Relative tolerance',
        description='Floats are considered unequal if the relative difference '
                    'between them is larger than this value.',
        editor=node.editors.decimal_spinbox_editor(step=1e-5, decimals=10))
    parameters.set_float(
        'abs_tol', value=1e-8, label='Absolute tolerance',
        description='Floats are considered unequal if the absolute difference '
                    'between them is larger than this value.',
        editor=node.editors.decimal_spinbox_editor(step=1e-8, decimals=10))

    controllers = node.controller(
        when=node.field('inexact_float', 'checked'),
        action=(node.field('rel_tol', 'enabled'),
                node.field('abs_tol', 'enabled')))

    def execute(self, node_context):
        parameters = node_context.parameters
        table1 = node_context.input['table1']
        out_table = node_context.output['out']
        inexact_float = parameters['inexact_float'].value
        rel_tol = parameters['rel_tol'].value
        abs_tol = parameters['abs_tol'].value
        col_order = parameters['col_order'].value
        col_attrs = parameters['col_attrs'].value
        tbl_names = parameters['tbl_names'].value
        tbl_attrs = parameters['tbl_attrs'].value

        for table2 in node_context.input.group('table2'):
            try:
                table1.equal_to(
                    table2, col_order=col_order, col_attrs=col_attrs,
                    tbl_names=tbl_names, tbl_attrs=tbl_attrs,
                    inexact_float=inexact_float, rel_tol=rel_tol, abs_tol=abs_tol,
                    raise_exc=True)
            except AssertionError as e:
                raise SyDataError(*e.args)

        # Could use either one. They are equal after all.
        out_table.source(table1)
