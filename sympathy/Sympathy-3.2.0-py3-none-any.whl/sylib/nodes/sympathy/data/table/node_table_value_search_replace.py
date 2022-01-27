# This file is part of Sympathy for Data.
# Copyright (c) 2013, 2017 Combine Control Systems AB
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
r"""In the standard library there exist four nodes which perform a search and
replace of values among the elements in Tables. Of the four nodes, one
operates on single Table while the second operates on multiple Tables.
The third and fourth are the same but instead of a GUI configuration, they take
another table as configuration. See below.

In the configuration of the nodes one has to specify the columns in the Tables
which will be regarded during the execution of the node. The node works with
string, unicode, integer, and float values.

In general, search and replace expression should be scalar literals
For string and unicode columns the search and replace expressions may be
regular expressions. Here, it is possible to use ()-grouping in the search
expression to reuse the match of the expression within the parentheses in the
replace expression. In the regular expression for the replace use
``\\1`` (or higher numbers) to insert matches.

As an example let's say that you have an input table with a column containing
the strings ``x``, ``y``, and ``z``. If you enter the search expression
``(.*)`` and the replace expression ``\\1_new`` the output will be the
strings ``x_new``, ``y_new``, and ``z_new``.

For the expression table (for the 'with Table' versions) it should it have the
following structure:

+------------------------+------------------------------+
| Search column          | Replace column               |
+========================+==============================+
| Expression to search 1 | Replace for expression 1     |
+------------------------+------------------------------+
| Expression to search 2 | Replace for expression 2     |
+------------------------+------------------------------+
| ...                    | ...                          |
+------------------------+------------------------------+


Unless configured to use regex replacement, search, replace and default values
will be read as a values of the same type as the column it is replacing in.
For information about how to enter text, see :ref:`appendix_typed_text`.

"""
from sympathy.api import node as synode
from sympathy.api import table
import re
import numpy as np
from sympathy.api import node_helper, dtypes
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust
from sympathy.api.exceptions import SyConfigurationError


class ConvertError(Exception):
    pass


_config_error_msg = (
    'Failure in column {column}: could not convert {name}: '
    '"{value}" to {type}.')


def _convert(value, dtype, name):
    try:
        return dtypes.numpy_value_from_dtype_str(dtype, value)
    except ValueError:
        raise ConvertError(
            dict(name=name, value=value, type=dtypes.typename_from_kind(
                dtype.kind)))


def _item_size(dtype):
    if dtype.kind == 'U':
        return dtype.itemsize / 4
    elif dtype.kind == 'S':
        return dtype.itemsize


def replace_array_values_regex(arr, search, replace, use_default, default,
                               re_flags):
    arr_type = dtypes.numpy_dtype_factory_for_dtype(
        arr.dtype)

    if arr_type.kind in ['U', 'S']:

        if arr_type.kind == 'S':
            search.encode('ascii')
            replace.encode('ascii')
            if use_default:
                default.encode('ascii')

        search = re.compile(search, flags=re_flags)
        values = []

        if use_default:
            for value in arr.tolist():
                value, n = search.subn(replace, value)
                value = value if n else default
                values.append(value)
            arr = np.array(values, dtype=arr_type)
        else:
            replaced = 0
            for value in arr.tolist():
                value, n = search.subn(replace, value)
                replaced += n
                values.append(value)

            if replaced:
                arr = np.array(values, dtype=arr_type)
    return arr


def replace_array_values_literal(arr, search, replace, use_default, default):
    arr_type = dtypes.numpy_dtype_factory_for_dtype(
        arr.dtype)
    search = _convert(search, arr_type, 'Search')
    replace = _convert(replace, arr_type, 'Replace')

    if arr_type.kind == 'f' and np.isnan(search):
        bindex = np.isnan(arr)
    elif arr_type.kind == 'M' and np.isnat(search):
        bindex = np.isnat(arr)
    else:
        bindex = arr == search

    if arr_type.kind in ['U', 'S']:
        # For fixed size string columns we convert to object
        # to ensure that the replacements fit.
        if use_default:
            default = _convert(default, arr_type, 'Default')
            # Copy.
            arr = np.array(arr, dtype='O')
            arr[bindex] = replace
            arr[~bindex] = default
            arr = np.array(arr, dtype=arr_type.kind)
        else:
            if np.any(bindex):
                # Copy.
                arr = np.array(arr, dtype='O')
                arr[bindex] = replace
                arr = np.array(arr, dtype=arr_type)
    else:
        if use_default:
            default = _convert(default, arr_type, 'Default')
            # Copy.
            arr = np.array(arr, dtype=arr_type)
            arr[bindex] = replace
            arr[~bindex] = default
        else:
            if np.any(bindex):
                # Copy.
                arr = np.array(arr, dtype=arr_type)
                arr[bindex] = replace
    return arr


def replace_table_values(out_table, columns, search, replace, use_default,
                         default, regex, ignore_case):
    out_table_tmp = table.File()
    re_flags = re.IGNORECASE if ignore_case else 0

    for col_name in columns:
        col = out_table[col_name]
        mask = None

        if isinstance(col, np.ma.MaskedArray):
            mask = col.mask
            col = col.data

        if regex:
            new_col = replace_array_values_regex(
                col, search, replace, use_default, default, re_flags)
        else:
            try:
                new_col = replace_array_values_literal(
                    col, search, replace, use_default, default)
            except ConvertError as ce:
                raise SyConfigurationError(_config_error_msg.format(
                    column=col_name, **ce.args[0]))

        if new_col is not col:

            if mask is not None:
                new_col = np.ma.MaskedArray(new_col, mask)

            out_table_tmp.set_column_from_array(col_name, new_col)

    out_table_tmp.set_attributes(out_table.get_attributes())
    out_table_tmp.set_name(out_table.get_name())
    out_table.update(out_table_tmp)
    return out_table


def _set_literal(params, value=True):
    params.set_boolean(
        'literal', label='Text replace only (using regex)',
        description=(
            'Perform regex replacements in string columns, i.e., columns with '
            'types text and bytes, other columns are ignored. '
            'Disable this option to replace full values, without using '
            'regex across all types of columns.'),
        value=value)


def common_params(parameters):
    _set_literal(parameters)
    parameters.set_boolean(
        'ignore_case', label='Ignore case',
        description='Ignore case when searching', value=False)
    return parameters


class TableSearchBase(synode.Node):
    author = 'Greger Cronquist'
    version = '1.0'
    icon = 'search_replace.svg'
    tags = Tags(Tag.DataProcessing.TransformData)

    parameters = synode.parameters()
    editor = synode.Editors.multilist_editor(edit=True)

    parameters.set_list(
        'columns', label='Select columns',
        description='Select the columns to use perform replace on',
        value=[], editor=editor)
    parameters.set_string('find', label='Search',
                          value='',
                          description='Specify search expression.')
    parameters.set_string('replace', label='Replace',
                          value='',
                          description='Specify replace expression.')
    parameters = common_params(parameters)
    parameters.set_boolean('use_default', label='Use default',
                           value=False,
                           description='Use default value when not found.')
    parameters.set_string('default', label='Default value',
                          value='',
                          description='Specify default value')

    controllers = (
        synode.controller(
            when=synode.field('use_default', state='checked'),
            action=synode.field('default', state='enabled')
        ),
        synode.controller(
            when=synode.field('literal', state='checked'),
            action=synode.field('ignore_case', state='enabled')
        ),
    )

    def update_parameters(self, old_params):
        cols = old_params['columns']
        if not cols.editor.get('mode', False):
            cols._multiselect_mode = 'selected_exists'

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def _get_params(self, node_context):
        params = node_context.parameters
        search = params['find'].value
        replace = params['replace'].value
        use_default = params['use_default'].value
        default = params['default'].value
        ignore_case = params['ignore_case'].value
        regex = params['literal'].value
        return search, replace, use_default, default, regex, ignore_case

    def _replace_in_table(self, in_table, columns, params):
        if in_table.number_of_rows() == 0:
            # Table contained no values (but perhaps empty columns).
            # Return original table to not mess up column types.
            return in_table

        out_table = table.File()
        out_table.source(in_table)
        replace_table_values(out_table, columns, *params)
        return out_table


class TableValueSearchReplace(TableSearchBase):
    """Search and replace string and unicode values in Table."""

    name = 'Replace values in Table'
    description = 'Search and replace values in Table.'
    nodeid = 'org.sysess.sympathy.data.table.tablevaluesearchreplace'
    inputs = Ports([Port.Table('Input Table', name='table')])
    outputs = Ports([Port.Table('Table with replaced values', name='table')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['columns'], node_context.input[0])

    def execute(self, node_context):
        in_table = node_context.input[0]
        columns = node_context.parameters['columns'].selected_names(
            in_table.names())
        out_table = self._replace_in_table(
            in_table, columns, self._get_params(node_context))
        node_context.output[0].update(out_table)


@node_helper.list_node_decorator(
    {'table': {'name': 'tables'}}, {'table': {'name': 'tables'}})
class TableValueSearchReplaceMultiple(TableValueSearchReplace):
    name = 'Replace values in Tables'
    nodeid = 'org.sysess.sympathy.data.table.tablevaluesearchreplacemultiple'


def _get_single_col_editor():
    return synode.Util.combo_editor('', filter=True, edit=True)


def _get_multi_col_editor():
    return synode.Util.multilist_editor(edit=True)


class TableValueSearchReplaceWithTableSuper(synode.Node):
    description = (
        'Searches for and replaces values in specified columns using a table')
    author = (
        'Greger Cronquist <greger.cronquist@combine.se>, '
        'Andreas Tågerud <andreas.tagerud@combine.se>')
    version = '1.0'
    icon = 'search_replace.svg'
    tags = Tags(Tag.DataProcessing.TransformData)

    parameters = synode.parameters()
    editor_cols = _get_multi_col_editor()
    editor_col = _get_single_col_editor()
    parameters.set_list(
        'column', label='Columns to replace values in',
        description='Select in which to perform replace', value=[],
        editor=editor_cols)
    parameters.set_list(
        'find', label='Column with search expressions',
        description='Select which column contains search expressions',
        value=[], editor=editor_col)
    parameters.set_list(
        'replace', label='Column with replace expressions',
        description='Select which column contains replacements', value=[],
        editor=editor_col)
    parameters = common_params(parameters)

    def update_parameters(self, old_params):
        for param in ['find', 'replace']:
            if param in old_params:
                old_params[param].editor = _get_single_col_editor()
        param = 'column'
        if param in old_params:
            old_params[param].editor = _get_multi_col_editor()

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['find'],
               node_context.input['expressions'])
        adjust(node_context.parameters['replace'],
               node_context.input['expressions'])
        adjust(node_context.parameters['column'],
               node_context.input['data'])

    def execute_once(self, node_context, in_table):
        parameters = node_context.parameters
        exp = node_context.input['expressions']
        regex = parameters['literal'].value
        ignore_case = parameters['ignore_case'].value
        try:
            search = exp.get_column_to_array(parameters['find'].selected)
            replace = exp.get_column_to_array(parameters['replace'].selected)
        except (KeyError, ValueError):
            raise SyConfigurationError(
                'One or more of the selected columns do not seem to exist')

        out_table = table.File()
        selected_names = parameters['column'].selected_names(
            in_table.column_names())
        out_table.source(in_table)
        for search, replace in zip(list(search), list(replace)):
            replace_table_values(
                out_table, selected_names, search, replace, False, None, regex,
                ignore_case)
        return out_table


class TableValueSearchReplaceWithTable(TableValueSearchReplaceWithTableSuper):
    name = 'Replace values in Table with Table'
    nodeid = 'org.sysess.sympathy.data.table.tablevaluesearchreplacewithtable'

    inputs = Ports([
        Port.Table('Expressions', name='expressions'),
        Port.Table('Table Data', name='data')])
    outputs = Ports([Port.Table('Table with replaced values', name='data')])

    def execute(self, node_context):
        in_table = node_context.input['data']
        if not in_table.is_empty():
            node_context.output['data'].source(
                self.execute_once(node_context, in_table))


@node_helper.list_node_decorator(['data'], ['data'])
class TableValueSearchReplaceWithTableMultiple(
        TableValueSearchReplaceWithTable):
    name = 'Replace values in Tables with Table'
    nodeid = 'org.sysess.sympathy.data.table.tablesvaluesearchreplacewithtable'
