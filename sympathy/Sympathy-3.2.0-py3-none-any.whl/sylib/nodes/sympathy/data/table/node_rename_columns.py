# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017-2019, Combine Control Systems AB
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
import re
import collections

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api import table
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust


def rename_tables(input_file, output_file, dictionary, source,
                  destination):
    # Create a translations dictionary from a single source name to (possibly)
    # many destination names.
    translations = collections.defaultdict(list)
    reverse = {}  # Map from destination to source

    for (src, dst) in zip(source, destination):
        if src not in input_file:
            continue
        if dst in reverse:
            translations[reverse[dst]].remove(dst)
        reverse[dst] = src
        translations[src].append(dst)

    for column in input_file.column_names():
        if column in translations:
            new_column_names = translations[column]
            for new_column_name in new_column_names:
                output_file.update_column(
                    new_column_name, input_file, column)
        elif column not in reverse:
            output_file.update_column(
                column, input_file, column)


def replace_regex(column, src_expr, dst_expr):
    match = re.search(src_expr, column)
    if match:
        new_name = re.sub(src_expr, dst_expr, column)
        return new_name


def replace_text(column, src_expr, dst_expr):
    if src_expr in column:
        return column.replace(src_expr, dst_expr)


def rename_column(input_file, output_file, src_expr, dst_expr, func):
    new_names = set()
    for column in input_file.column_names():
        new_name = func(column, src_expr, dst_expr)
        if new_name:
            new_names.add(new_name)
            output_file.update_column(new_name, input_file, column)
        elif column in new_names:
            # This name has already been taken by some renamed column. Renamed
            # columns have priority over non-renamed columns.
            continue
        else:
            output_file.update_column(column, input_file)


_with_table_doc = """
    Rename columns from the input data using a lookup table.

    The lookup table must include one column with search keywords and another
    column with replacements. When the node is executed all column names in the
    input data are checked against keyword column in the lookup table. If a
    match is found the corresponding name in the replacement column will
    replace the original column name.  For the case with no match the column
    names are left unchanged.

    If a name appears more than once in the search column of the lookup, that
    column will be renamed to each of the replacement names.  Essentially
    copying the single input column to several columns in the output.

    If a name appears more than once in the replacements column the last one
    that is also present in the input data will be used. Also note that renamed
    columns always take precedence over non-renamed ones.
    """


class RenameTableColumnsTables(synode.Node):
    __doc__ = _with_table_doc

    name = 'Rename columns in Tables with Table'
    author = 'Greger Cronquist'
    version = '1.0'
    nodeid = 'org.sysess.sympathy.data.table.renametablecolumnstable'
    icon = 'rename_columns.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.data.table.renamesingletablecolumns',
               'org.sysess.sympathy.setcolumnnamesintablewithtable']

    inputs = Ports([
        Port.Table('Lookup', name='dictionary'),
        Port.Tables('Data', name='tables')])
    outputs = Ports([
        Port.Tables('Data', name='tables')])

    parameters = synode.parameters()
    parameters.set_list('source', label='Search column',
                        description=(
                            'Column containing names to search for'),
                        editor=synode.Util.combo_editor(
                            edit=True, filter=True))
    parameters.set_list('destination', label='Replace column',
                        description=(
                            'Column containing names to replace with'),
                        editor=synode.Util.combo_editor(
                            edit=True, filter=True))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['source'],
               node_context.input['dictionary'])
        adjust(node_context.parameters['destination'],
               node_context.input['dictionary'])

    def execute(self, node_context):
        input_files = node_context.input['tables']
        output_files = node_context.output['tables']

        if not input_files:
            return

        input_files = node_context.input['tables']
        dictionary = node_context.input['dictionary']
        output_files = node_context.output['tables']

        source = dictionary._require_column(
            node_context.parameters['source'], types='U')
        destination = dictionary._require_column(
            node_context.parameters['destination'], types='U')

        for input_file in input_files:
            output_file = table.File()
            output_file.set_name(input_file.get_name())
            rename_tables(input_file, output_file, dictionary,
                          source, destination)
            output_file.set_table_attributes(input_file.get_table_attributes())
            output_files.append(output_file)


def _set_mode_parameter(parameters, value):
    parameters.set_string(
        'mode', label='Mode',
        value=value,
        editor=synode.editors.combo_editor(options=['Text', 'Regex']))


class RenameTableColumns(synode.Node):
    """
    Rename columns in Table(s) using a regular expression.

    Group references may be used in the replacement expression.

    If several columns match the search expression resulting in the same column
    name, the last of the matching columns will be copied to the output and the
    other columns will be removed. Note that renamed columns (i.e. any columns
    that match the search expression) always take precedence over non-renamed
    ones.
    """

    author = 'Greger Cronquist'
    version = '1.0'

    name = 'Rename columns in Table'
    description = 'Rename the Table columns by using regular expressions.'
    nodeid = 'org.sysess.sympathy.data.table.renamesingletablecolumns'
    icon = 'rename_columns.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)
    related = ['org.sysess.sympathy.data.table.renametablecolumns',
               'org.sysess.sympathy.data.table.renametablecolumnstable',
               'org.sysess.sympathy.setcolumnnamesintablewithtable']

    inputs = Ports([
        Port.Table('Input', name='Input')])
    outputs = Ports([
        Port.Table('Output', name='Output')])

    parameters = synode.parameters()
    _set_mode_parameter(parameters, 'Text')

    parameters.set_string(
        'src_expr', label='Search', value='',
        description=('Specify the regular expression which will be '
                     'replaced'))
    parameters.set_string(
        'dst_expr', label='Replace', value='',
        description='Specify the regular expression for replacement')

    def execute(self, ctx):
        parameters = ctx.parameters
        in_table = ctx.input['Input']
        out_table = ctx.output['Output']
        src_expr = parameters['src_expr'].value
        dst_expr = parameters['dst_expr'].value
        mode = parameters['mode'].value

        if mode == 'Regex':
            func = replace_regex
        elif mode == 'Text':
            func = replace_text
        else:
            assert False, 'Unknown replace mode'

        rename_column(in_table, out_table, src_expr,
                      dst_expr, func)
        out_table.set_table_attributes(
            in_table.get_table_attributes())
        out_table.set_name(in_table.get_name())

    def update_parameters(self, old_parameters):
        if 'mode' not in old_parameters:
            _set_mode_parameter(old_parameters, 'Regex')


@node_helper.list_node_decorator(['Input'], ['Output'])
class RenameTablesColumns(RenameTableColumns):
    name = 'Rename columns in Tables'
    nodeid = 'org.sysess.sympathy.data.table.renametablecolumns'


class RenameAdafColumnsTable(synode.Node):
    __doc__ = _with_table_doc

    name = 'Rename columns in ADAF with Table'
    nodeid = 'org.sysess.sympathy.adaf.renamecolumntable'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'rename_columns.svg'
    tags = Tags(Tag.DataProcessing.TransformStructure)

    related = ['org.sysess.sympathy.data.table.renametablecolumnstable']

    inputs = Ports([
        Port.ADAF('Data', name='data'),
        Port.Table('Lookup', name='lookup')])
    outputs = Ports([
        Port.ADAF('Data', name='data')])

    parameters = synode.parameters()
    parameters.set_string('search', label='Search column',
                          description=(
                              'Column containing names to search for'),
                          editor=synode.editors.combo_editor(
                              edit=True, filter=True))
    parameters.set_string('replace', label='Replace column',
                          description=(
                              'Column containing names to replace with'),
                          editor=synode.editors.combo_editor(
                            edit=True, filter=True))

    def adjust_parameters(self, ctx):
        adjust(ctx.parameters['search'],
               ctx.input['lookup'])
        adjust(ctx.parameters['replace'],
               ctx.input['lookup'])

    def execute(self, ctx):
        out_data = ctx.output['data']
        in_data = ctx.input['data']
        lookup = ctx.input['lookup']
        search_names = lookup._require_column(
            ctx.parameters['search'], types='U')
        replace_names = lookup._require_column(
            ctx.parameters['replace'], types='U')

        def update_table(in_table, out_table):
            column_names = in_table.column_names()
            found = set(column_names).intersection(mappings)

            out_table.set_table_attributes(in_table.get_table_attributes())

            if found:
                for column_name in column_names:
                    if column_name not in found:
                        out_table.update_column(column_name, in_table)
                    else:
                        for replace_name in mappings[column_name]:
                            out_table.update_column(
                                replace_name, in_table, column_name)
            else:
                out_table.source(in_table)

        mappings = {}
        for search_name, replace_name in zip(search_names, replace_names):
            mappings.setdefault(search_name, []).append(replace_name)

        for in_group, out_group in [(in_data.meta, out_data.meta),
                                    (in_data.res, out_data.res)]:
            in_table = in_group.to_table()
            out_table = table.File()
            update_table(in_table, out_table)
            out_group.from_table(out_table)

        for system_key, in_system in in_data.sys.items():
            out_system = out_data.sys.create(system_key)
            for raster_key, in_raster in in_system.items():
                out_raster = out_system.create(raster_key)
                in_table = in_raster.to_table()
                out_table = table.File()
                update_table(in_table, out_table)
                out_raster.from_table(out_table)
                try:
                    out_raster.update_basis(in_raster)
                except Exception:
                    pass


@node_helper.list_node_decorator(['data'], ['data'])
class RenameAdafsColumnsTable(RenameAdafColumnsTable):
    name = 'Rename columns in ADAFs with Table'
    nodeid = 'org.sysess.sympathy.adaf.renamecolumnstable.list'
