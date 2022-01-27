# This file is part of Sympathy for Data.
# Copyright (c) 2016-2017, Combine Control Systems AB
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
The Table data type includes an additional container, besides the data
container, for storing attributes. An attribute is stored as a scalar value
together with a header.

The standard library contains two nodes for setting and getting Table
attributes.
"""
import numpy as np

from sympathy.api import node as synode
from sympathy.api import table
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust


def get_table_attributes(in_table, out_table):
    """Add table attribute in in_table as column in out_table."""
    for key, value in in_table.get_table_attributes().items():
        out_table.set_column_from_array(key, np.array([value]))


def set_table_attributes(attr_table, out_table):
    """Update table attributes in out_table with the content of attr_table."""
    new_attr = {}
    for key in attr_table.column_names():
        new_attr[key] = attr_table.get_column_to_array(key)[0]

    out_attr = out_table.get_table_attributes()
    out_attr.update(new_attr)
    out_table.set_table_attributes(out_attr)


def set_column_attributes(attr_table, out_table, parameters):
    """Update column attributes in out_table with the content of attr_table."""
    names = attr_table.get_column_to_array(parameters['columns'].selected)
    attrs = attr_table.get_column_to_array(parameters['attributes'].selected)
    values = attr_table.get_column_to_array(parameters['values'].selected)
    clear = parameters['clear'].value

    for name in set(names):
        if out_table.has_column(name):
            mask = names == name
            data_attributes = {}
            if not clear:
                data_attributes = out_table.get_column_attributes(name)

            new_attributes = {
                attr: value for attr, value in zip(
                    attrs[mask], values[mask])}

            data_attributes.update(new_attributes)
            out_table.set_column_attributes(name, data_attributes)


def get_column_attributes(in_table, out_table):
    """Add column attributes in in_table as data in out_table."""
    part_tables = []
    for column in in_table.column_names():
        part_table = table.File()
        attributes = in_table.get_column_attributes(column)
        key_col = list(attributes.keys())
        val_col = list(attributes.values())

        if len(key_col):
            part_table.set_column_from_array(
                'Attribute names', np.array(key_col))
            part_table.set_column_from_array(
                'Attribute values', np.array(val_col))
            part_table.set_column_from_array(
                'Column names', np.array([column] * len(key_col)))
        else:
            part_table.set_column_from_array(
                'Column names', np.array([column]))

        part_tables.append(part_table)

    out_table.vjoin(part_tables)


class SuperNodeAttributes(synode.Node):
    author = 'Daniel Hedendahl'
    version = '1.0'
    tags = Tags(Tag.DataProcessing.TransformMeta)


class GetColumnAttributesTable(SuperNodeAttributes):
    name = 'Get column attributes in Table'
    description = 'Get column attributes in Table.'
    nodeid = 'org.sysess.sympathy_course.getcolumnattributestable'
    icon = 'column_attribute.svg'

    inputs = Ports([
        Port.Table('Input Data', name='data')])
    outputs = Ports([
        Port.Table('Attributes', name='attributes')])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        get_column_attributes(in_table, out_table)


@node_helper.list_node_decorator(['data'], ['attributes'])
class GetColumnAttributesTables(GetColumnAttributesTable):
    name = 'Get column attributes in Tables'
    nodeid = 'org.sysess.sympathy_course.getcolumnattributestables'


class SuperNodeSetColAttributes(SuperNodeAttributes):
    icon = 'column_attribute.svg'
    parameters = synode.parameters()
    parameters.set_boolean(
        'clear', label='Clear existing attributes', value=False,
        description='Clear existing attributes before applying the operation.')
    parameters.set_list(
        'columns', label='Column names',
        description='Select column with column names',
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'attributes', label='Attribute names',
        description='Select column with attributes',
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'values', label='Attribute values',
        description='Select column with values',
        editor=synode.Util.combo_editor(edit=True))


class SetColumnAttributesTable(SuperNodeSetColAttributes):
    name = 'Set column attributes in Table'
    description = 'Set column attributes in Table.'
    nodeid = 'org.sysess.sympathy_course.setcolumnattributestable'

    inputs = Ports([
        Port.Table(
            'Table with, at least, three column, one for column '
            'names, another for attribute names and a third for '
            'attribute values', name='attributes'),
        Port.Table('Table with data columns', name='in_data')])
    outputs = Ports([
        Port.Table('Table with updated columns attributes', name='out_data')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'],
               node_context.input['attributes'])
        adjust(node_context.parameters['attributes'],
               node_context.input['attributes'])
        adjust(node_context.parameters['values'],
               node_context.input['attributes'])

    def execute(self, node_context):
        parameters = node_context.parameters
        attr_table = node_context.input['attributes']
        data_table = node_context.input['in_data']
        out_table = node_context.output['out_data']
        out_table.update(data_table)
        if not (attr_table.is_empty() or data_table.is_empty()):
            set_column_attributes(attr_table, out_table, parameters)


@node_helper.list_node_decorator(['attributes', 'in_data'], ['out_data'])
class SetColumnAttributesTables(SetColumnAttributesTable):
    name = 'Set column attributes in Tables'
    nodeid = 'org.sysess.sympathy_course.setcolumnattributestables'


class GetTableAttributes(SuperNodeAttributes):
    name = 'Get Table attributes'
    description = 'Get Table attributes.'
    nodeid = 'org.sysess.sympathy_course.gettableattributes'
    icon = 'table_attribute.svg'

    inputs = Ports([
        Port.Table('Table with data.', name='in_data')])
    outputs = Ports([
        Port.Table(
            'Table with a single row where the columns are representing '
            'the exported attributes', name='attributes')])

    def execute(self, node_context):
        in_table = node_context.input[0]
        out_table = node_context.output[0]
        get_table_attributes(in_table, out_table)


class GetTablesAttributes(SuperNodeAttributes):

    name = 'Get Tables attributes'
    description = 'Get Tables attributes.'
    nodeid = 'org.sysess.sympathy_course.gettablesattributes'
    icon = 'table_attribute.svg'

    inputs = Ports([
        Port.Tables('Table with data', name='in_data')])
    outputs = Ports([
        Port.Tables(
            'Table with a single row where the columns are representing '
            'the exported attributes', name='attributes')])

    def execute(self, node_context):
        in_tables = node_context.input[0]
        out_tables = node_context.output[0]

        for in_table in in_tables:
            out_table = table.File()
            get_table_attributes(in_table, out_table)
            out_tables.append(out_table)


class SetTableAttributes(SuperNodeAttributes):
    """
    Set the attributes in Table with the headers and values in another Table,
    only the values on the first row.
    """

    name = 'Set Table attributes'
    description = 'Set Table attributes.'
    nodeid = 'org.sysess.sympathy_course.settableattributes'
    icon = 'table_attribute.svg'

    inputs = Ports([
        Port.Table(
            'A Table with attributes along the columns. Only the first row of '
            'the Table will be imported as attributes, due to that an '
            'attribute is defined to be a scalar value', name='attributes'),
        Port.Table('Table with data', name='in_data')])
    outputs = Ports([
        Port.Table('Table with updated attribute container', name='out_data')])

    def execute(self, node_context):
        attr_table = node_context.input['attributes']
        data_table = node_context.input['in_data']
        out_table = node_context.output['out_data']
        out_table.update(data_table)

        set_table_attributes(attr_table, out_table)


class SetTablesAttributes(SuperNodeAttributes):
    """
    Set the attributes in Tables with the headers and values in
    attribute Tables, only the values on the first row.
    """

    name = 'Set Tables attributes'
    description = 'Set Tables attributes.'
    nodeid = 'org.sysess.sympathy_course.settablesattributes'
    icon = 'table_attribute.svg'

    inputs = Ports([
        Port.Tables(
            'Table with attributes along the columns. Only the first row of '
            'the Table will be imported as attributes, due to that an '
            'attribute is defined to be a scalar value', name='attributes'),
        Port.Tables('Table with data', name='in_data')])
    outputs = Ports([
        Port.Tables(
            'Table with updated attribute container', name='out_data')])

    def execute(self, node_context):
        attr_tables = node_context.input[0]
        data_tables = node_context.input[1]
        out_tables = node_context.output[0]

        for data_table, attr_table in zip(data_tables, attr_tables):
            out_table = table.File()
            out_table.update(data_table)
            set_table_attributes(attr_table, out_table)
            out_tables.append(out_table)
