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
import operator
import collections
import sys
import html
import ast

import numpy as np

from sympathy.api import node as synode
from sympathy.api import table
from sympathy.api import ParameterView
from sympathy.api import qt2 as qt_compat
from sympathy.api.nodeconfig import (
    Port, Ports, Tag, Tags, adjust, deprecated_warn, deprecated_node)
from sympathy.api import node_helper
from sympathy.api.exceptions import (SyConfigurationError, SyDataError,
                                     SyUserCodeError)
from sympathy.api import dtypes
from sylib import util

from sympathy.platform.widget_library import BasePreviewTable
from sympathy.platform.table_viewer import TableModel

QtGui = qt_compat.import_module('QtGui')
QtWidgets = qt_compat.import_module('QtWidgets')
QtCore = qt_compat.QtCore

SELECT_WITH_GUI_DOCS = """
Select rows in Tables by applying a constraint to a number of columns in the
incoming Table. The output Table has the selected rows from incoming Table with
order preserved. The number of rows in the output is therefore always less than
or equal to the number of rows in the input. The number of columns is the same.

Constraint
==========
The constraint can be defined by selecting a comparison operator in the drop
down menu and a entering a constraint value in the text field, the constraint
value will be read as a value of the same type as the column it is compared to.
For information about how to enter text, see :ref:`appendix_typed_text`.
Alternatively a custom filter function can be used.

Reduction
=========
The constraint will be applied for each selected column. The results per column
are then combined using the selected reduction method. If set to 'all' (the
default) the constraint needs to be True in all selected column for a row to be
included in the output. If set to 'any' it is enough that the constraint is
True for any single selected column. When only one column is selected this
option has no effect.

Masked values
=============
Rows where any of the selected columns are masked are considered to fail the
constraint check. In other words they are never included in the output. Custom
filter functions can override this behavior.

Custom filter
=============
A custom filter function can be defined by writing a lambda function. The
lambda function will be called once for each selected column with that
column as a numpy array as argument. The lambda function should return
an array-like object (e.g. `numpy.ndarray` or `pandas.Series`) with boolean
dtype and as many items as there was in the argument.

See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
for a description of lambda functions. Have a look at the :ref:`Data type
APIs<datatypeapis>` to see what methods and attributes are available on the
data type that you are working with.

If the custom filter returns a masked array, masked values are treated as
False (i.e. such rows are not included in the output).

"""

SELECT_WITH_TABLE_DOCS = """
Select rows in Table by using an additional Table with predefined comparison
relations. The output Table has the selected rows from incoming Table with
order preserved. The number of rows in the output is therefore always less than
or equal to the number of rows in the input. The number of columns is the same.

The selection Table should have at least three columns that define a set of
constraints. Each row will set up one constraint with a column name, a
comparison operator and a constraint value.

The following operators are recognized by the node, either in their string form
(e.g. ``equal``) or their symbolic form (e.g. ``==``):

    - equal (==)
    - less than (<)
    - less than or equal (<=)
    - greater than (>)
    - greater than or equal (>=)
    - not equal (!=)

Each constraint will be applied in turn. The results per constraint are then
combined using the selected reduction method. If set to *all* (the default) all
the constraint needs to be True for a row to be included in the output. If set
to *any* it is enough any single constraint is True. When the configuration
table only contains a single constraint this option has no effect. Each
constraint value will be read as a value of the same type as the column it is
compared to. For information about how to enter text, see
:ref:`appendix_typed_text`.


Rows where any of the selected columns are masked are never included in the
output.

Older versions of this node evaluated the constraint values as Python
code. This behavior is no longer supported.

"""


comparisons = collections.OrderedDict([
    ('equal', '=='),
    ('less than', '<'),
    ('less than or equal', '<='),
    ('greater than', '>'),
    ('greater than or equal', '>='),
    ('not equal', '!=')])


def get_operator(relation):
    if relation in comparisons.keys():
        relation = comparisons[relation]
    elif relation in comparisons.values():
        relation = relation
    else:
        raise SyConfigurationError(
            "Unknown comparison operator: {}".format(relation))
    if relation == '==':
        op = operator.eq
    elif relation == '<':
        op = operator.lt
    elif relation == '<=':
        op = operator.le
    elif relation == '>':
        op = operator.gt
    elif relation == '>=':
        op = operator.ge
    elif relation == '!=':
        op = operator.ne
    else:
        raise SyConfigurationError(
            "Unknown comparison operator: {}".format(relation))
    return op


def get_predicate(relation, constraint):
    """Return a predicate function defined by relation and constraint."""
    if relation in comparisons.keys():
        comparison = comparisons[relation]
    elif relation in comparisons.values():
        comparison = relation
    else:
        raise SyConfigurationError(
            "Unknown comparison operator: {}".format(relation))
    predicate_fn = 'lambda x: x {} {}'.format(comparison, constraint)
    ctx = {}
    try:
        constraint_value = util.base_eval(constraint, {'x': None})
    except NameError:
        # Assume that the constraint is a string.
        constraint_value = constraint
        ctx = {'constraint_value': constraint_value}
        predicate_fn = 'lambda x: x {0} constraint_value'.format(comparison)
    except Exception:
        # Assume that the constraint depends on x.
        pass
    return util.base_eval(predicate_fn, ctx)


class ParseConstraintError(Exception):
    pass


class ParseCustomError(Exception):
    pass


def _get_constraint_predicate(relation, constraint):
    op = get_operator(relation)

    def is_nat(value):
        return np.isnat(value)

    def is_not_nat(value):
        return np.logical_not(np.isnat(value))

    def is_nan(value):
        return np.isnan(value)

    def is_not_nan(value):
        return np.logical_not(np.isnan(value))

    def no_cmp_op(value):
        return np.zeros(len(value), dtype=bool)

    def inner(array):
        dtype = array.dtype
        dtype = dtypes.numpy_dtype_factory_for_dtype(dtype)
        cons = constraint

        try:
            parsed_constraint = dtypes.numpy_value_from_dtype_str(
                dtype, cons)

        except Exception as e:
            raise ParseConstraintError(', '.join(e.args))

        if parsed_constraint.dtype.kind == 'M':
            if np.isnat(parsed_constraint):
                if op is operator.eq:
                    return is_nat(array)
                elif op is operator.ne:
                    return is_not_nat(array)
                else:
                    no_cmp_op(array)
        elif parsed_constraint.dtype.kind == 'f':
            if np.isnan(parsed_constraint):
                if op is operator.eq:
                    return is_nan(array)
                elif op is operator.ne:
                    return is_not_nan(array)
                else:
                    return no_cmp_op(array)

        return op(array, parsed_constraint)

    return inner


def get_parameter_predicate(parameters):
    """Return a predicate function defined by the node parameters."""
    if parameters['use_custom_predicate'].value:
        try:
            return util.base_eval(parameters['predicate'].value)
        except Exception:
            raise ParseCustomError(sys.exc_info())
    else:
        return _get_constraint_predicate(
            parameters['relation'].selected,
            parameters['constraint'].value)


def logical_operator_function(value):
    if value == 'all':
        return np.logical_and
    elif value == 'any':
        return np.logical_or
    raise SyConfigurationError('Unknown logic operation.')


def logical_init_function(value):
    if value == 'all':
        return np.ones
    elif value == 'any':
        return np.zeros
    raise SyConfigurationError('Unknown logic operation.')


def filter_rows_memopt(in_table, out_table, parameters):
    """Update out_table with the filtered rows from in_table."""
    def sydata_error_predicate(predicate, *args, **kwargs):
        try:
            return predicate(*args, **kwargs)
        except Exception as e:
            raise SyDataError(
                f'Error evaluating custom filter, {e}.')

    columns_param = parameters['columns']
    columns = columns_param.selected_names(in_table.names())
    predicate = get_parameter_predicate(parameters)
    nbr_rows = in_table.number_of_rows()

    try:
        exist = parameters['exist'].value.lower()
    except KeyError:
        exist = 'all'

    # Produce selection, a boolean array with same length as in_table
    # indicating which rows to keep.

    selection = logical_init_function(exist)(nbr_rows, dtype=bool)
    operator = logical_operator_function(exist)

    if nbr_rows:
        column_name = None
        try:
            for column_name in columns:
                selection = operator(
                    selection,
                    sydata_error_predicate(
                        predicate,
                        in_table._require_column(
                            columns_param, name=column_name)))
        except ParseConstraintError as e:
            raise SyConfigurationError(
                'In column: {}, failed to parse constraint. {}'
                .format(column_name, e.args[0]))
        except SyDataError:
            raise
        except Exception:
            if parameters['use_custom_predicate'].value:
                raise SyUserCodeError(
                    sys.exc_info(),
                    'In column: {}, failed to apply custom filter: {}'.format(
                        column_name, parameters['predicate'].value))
            else:
                raise SyDataError(
                    'In column: {}, failed to compare constraint: {}'.format(
                        column_name, parameters['constraint'].value))

    if isinstance(selection, np.ma.MaskedArray):
        selection = selection.filled(False)

    out_table.update(in_table[np.array(selection)])


class SelectRowsWidget(ParameterView):
    def __init__(self, in_table, parameters, parent=None):
        super().__init__(parent)
        self._in_table = in_table
        self._parameters = parameters
        self._status_message = ''

        vlayout = QtWidgets.QVBoxLayout()

        self._use_custom_predicate_pw = (
            self._parameters['use_custom_predicate'].gui())
        self._predicate_pwidget = (
            self._parameters['predicate'].gui())

        preview_button = QtWidgets.QPushButton("Preview")
        self._preview_table = BasePreviewTable()
        self._preview_table_model = TableModel()
        self._preview_table.setModel(self._preview_table_model)

        limit_label = QtWidgets.QLabel('Previewed rows:')
        self._limit_gui = self._parameters['limit'].gui()
        self.limit_spinbox = self._limit_gui.editor()

        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.addWidget(preview_button)
        preview_layout.addWidget(limit_label)
        preview_layout.addWidget(self.limit_spinbox)

        vlayout.addWidget(self._parameters['columns'].gui())
        self._exist = self._parameters['exist'].gui()
        vlayout.addWidget(self._exist)
        self._relation = self._parameters['relation'].gui()
        vlayout.addWidget(self._relation)
        self._constraint = self._parameters['constraint'].gui()
        vlayout.addWidget(self._constraint)

        vlayout.addWidget(self._use_custom_predicate_pw)
        vlayout.addWidget(self._predicate_pwidget)
        vlayout.addLayout(preview_layout)
        vlayout.addWidget(self._preview_table)

        self._post_init_gui_from_parameters()

        self.setLayout(vlayout)

        self._use_custom_predicate_pw.stateChanged[int].connect(
            self._use_custom_predicate_changed)
        preview_button.clicked[bool].connect(
            self._preview_clicked)
        self._predicate_pwidget.valueChanged[str].connect(
            self._predicate_changed)

    def _post_init_gui_from_parameters(self):
        self._use_custom_predicate_changed()

    def _use_custom_predicate_changed(self):
        use_custom_predicate = (
            self._parameters['use_custom_predicate'].value)
        self._constraint.setEnabled(not use_custom_predicate)
        self._relation.setEnabled(not use_custom_predicate)
        self._predicate_pwidget.setEnabled(use_custom_predicate)

    def _predicate_changed(self):
        color = QtGui.QColor(0, 0, 0, 0)
        try:
            get_parameter_predicate(self._parameters)
        except (SyntaxError, NameError):
            color = QtCore.Qt.red
        except Exception:
            color = QtCore.Qt.red
        palette = self._predicate_pwidget.palette()
        palette.setColor(self._predicate_pwidget.backgroundRole(), color)
        self._predicate_pwidget.setPalette(palette)

    def _preview_clicked(self):
        try:
            in_table = self._in_table['Input']
        except KeyError:
            in_table = None

        out_table = table.File()
        self._status_message = ''
        if in_table.is_valid():

            if in_table is None or in_table.is_empty():
                self._preview_table_model.set_table(table.File())
                return

            limit = self._parameters['limit'].value
            try:
                filter_rows_memopt(in_table, out_table, self._parameters)
                out_table = out_table[:limit]
            except ParseCustomError:
                self._status_message = 'Invalid filter!'
            except Exception as e:
                self._status_message = str(e)
        else:
            self._status_message = 'No input data'

        self.status_changed.emit()
        self._preview_table_model.set_table(out_table)

    @property
    def status(self):
        if self._status_message:
            return '<p>{}</p>'.format(
                html.escape(str(self._status_message)))
        return ''


class SelectRowsOperation(node_helper._TableOperation):
    __doc__ = SELECT_WITH_GUI_DOCS

    author = "Alexander Busck"
    version = '1.1'
    description = 'Reduction of rows in Table according to specified filter.'
    icon = 'select_table_rows.svg'
    tags = Tags(Tag.DataProcessing.Select)
    related = ['org.sysess.sympathy.data.table.selecttablerows',
               'org.sysess.sympathy.data.table.selecttablerowss',
               'org.sysess.sympathy.data.table.selecttablerowsfromtable',
               'org.sysess.sympathy.slice.rows.table',
               'org.sysess.sympathy.filters.columnfilternode']

    inputs = ['Input']
    outputs = ['Output']
    has_custom_widget = True

    @staticmethod
    def get_parameters(parameter_group):
        editor = synode.Util.multilist_editor(edit=True)
        parameter_group.set_list(
            'columns', label='Columns to filter',
            value=[],
            description='Select columns for comparison relation',
            editor=editor)

        parameter_group.set_string(
            'exist',
            value='all',
            label='Constraint must be satisfied in',
            description=(
                'Constraint must be satisfied in: Any selected column or '
                'All selected columns.'),
            editor=synode.Util.combo_editor(
                options=['all', 'any']))
        parameter_group.set_list(
            'relation', plist=comparisons.keys(),
            label='Relation',
            description='Select comparison operator for relation',
            editor=synode.Util.combo_editor())

        parameter_group.set_string(
            'constraint', label='Filter constraint',
            description='Specify constraint value for comparison relation',
            value='')

        parameter_group.set_boolean(
            'use_custom_predicate', label='Use custom filter',
            description='Select to use custom filter')

        parameter_group.set_string(
            'predicate', label='Custom filter',
            description='Write a custom filter as a Python lambda function')

        parameter_group.set_integer(
            'limit', label='Preview rows', description='Rows to display',
            editor=synode.Editors.bounded_spinbox_editor(0, 10000, 1),
            value=100)

    def custom_widget(self, in_table, parameters):
        return SelectRowsWidget(in_table, parameters)

    def adjust_table_parameters(self, in_table, parameters):
        try:
            in_data = in_table['Input']
        except KeyError:
            in_data = None
        adjust(parameters['columns'], in_data)

    def execute_table(self, in_table, out_table, parameters):
        """Execute"""
        in_table = in_table['Input']
        if not in_table.is_empty():
            out_table = out_table['Output']
            try:
                filter_rows_memopt(in_table, out_table, parameters)
            except ParseCustomError as e:
                raise SyDataError(
                    f'Error building custom filter, {e.args[0][1]}.')
            out_table.set_table_attributes(in_table.get_table_attributes())
            out_table.set_name(in_table.get_name())

    def update_parameters(self, parameters):
        if isinstance(self, node_helper._ADAFsCalculation):
            # Workaround for adafs_node_factory.
            try:
                parameters = parameters[node_helper.CHILD_GROUP]
            except KeyError:
                pass


SelectTableRows = node_helper._table_node_factory(
    'SelectTableRows', SelectRowsOperation,
    'Select rows in Table',
    'org.sysess.sympathy.data.table.selecttablerows')


SelectTablesRows = node_helper._tables_node_factory(
    'SelectTablesRows', SelectRowsOperation,
    'Select rows in Tables',
    'org.sysess.sympathy.data.table.selecttablerowss')


# This is the only instance, please do not introduce new ones!
SelectADAFsRows = deprecated_node(
    '4.0.0',
    'ADAF to Table, Select rows in Table, and Update ADAF with Table in '
    'a Lambda and run using Map')(
        node_helper._adafs_node_factory(
            'SelectADAFsRows', SelectRowsOperation,
            'Select rows in ADAFs',
            'org.sysess.sympathy.data.table.selectadafrows', 'Time series'))
SelectADAFsRows.icon = 'select_adaf_rows.svg'


class SelectTableRowsFromTable(synode.Node):
    __doc__ = SELECT_WITH_TABLE_DOCS

    name = 'Select rows in Table with Table'
    description = ('Select rows in Table by using an additional selection '
                   'Table with predefined comparison relations.')
    icon = 'select_table_rows.svg'
    nodeid = 'org.sysess.sympathy.data.table.selecttablerowsfromtable'
    author = 'Greger Cronquist'
    version = '1.0'
    tags = Tags(Tag.DataProcessing.Select)
    related = ['org.sysess.sympathy.data.table.selecttablesrowsfromtable',
               'org.sysess.sympathy.data.table.selecttablerows',
               'org.sysess.sympathy.slice.rows.table',
               'org.sysess.sympathy.filters.columnfilternode']

    parameters = synode.parameters()
    parameters.set_list(
        'column',
        label="Column with column names",
        description=('Select column in the selection Table that '
                     'includes listed column names.'),
        editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'relation',
        label="Column with comparison operators",
        description=('Select column in the selection Table that '
                     'includes listed comparison operators.'),
        editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'constraint',
        label="Column with constraint values",
        description=('Select column in the selection Table that '
                     'includes listed constraint values.'),
        editor=synode.Util.combo_editor(edit=True, filter=True))
    parameters.set_list(
        'reduction', label="Reduction:",
        plist=['all', 'any'], value=[0],
        description=(
            'If there are multiple selection criteria, do ALL of them need to '
            'be fulfilled for a data row to be selected, or is it enough that '
            'ANY single criterion is fulfilled?'),
        editor=synode.Util.combo_editor())

    inputs = Ports([
        Port.Table(
            'Table with three columns that defines a set of comparison '
            'relations. Each row in the set will set up a comparison relation '
            'with a column name, a comparison operator and a constraint '
            'value.',
            name='port1'),
        Port.Table('Input Table', name='port2')])
    outputs = Ports([Port.Table('Table with rows in Selection', name='port1')])

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['column'],
               node_context.input[0])
        adjust(node_context.parameters['relation'],
               node_context.input[0])
        adjust(node_context.parameters['constraint'],
               node_context.input[0])

    def _generate_selection(self, node_context, tablefile):
        """Return a zip-iterator of the three configuration columns."""
        config_table = node_context.input['port1']

        column_names = config_table._require_column(
            self._parameters['column'], 'U')
        relations = config_table._require_column(
            self._parameters['relation'], 'U')
        constraints = config_table._require_column(
            self._parameters['constraint'])

        new_constraints = []

        for col_name, constr in zip(column_names, constraints):
            dtype = tablefile.column_type(col_name)
            dtype = dtypes.numpy_dtype_factory_for_dtype(dtype)
            try:
                if constraints.dtype.kind in ['U', 'S']:
                    constr = dtypes.numpy_value_from_dtype_str(
                        dtype, constr)
                elif (constraints.dtype.kind != dtype.kind and
                      np.find_common_type(
                        [constraints.dtype, dtype], []).kind == 'O'):
                    # This allows some conversions, like bool <-> float and
                    # disallows datetime <-> float. Intentionally non-strict
                    # for compatible behavior.
                    raise SyDataError(
                        'Constraint type is incompatible with value type.')
                new_constraints.append(constr)
            except SyDataError:
                raise
            except Exception as e:
                raise SyDataError(f'Constraint type: {e}.')

        return zip(column_names, relations, new_constraints)

    def _filter_single_file(self, tablefile, node_context):
        """Return a new table with the selected rows from tablefile."""
        indices = []

        for column_name, relation, constraint in self._generate_selection(
                node_context, tablefile):
            col = tablefile.get_column_to_array(column_name)

            try:
                res = get_operator(relation)(col, constraint)
            except TypeError as e:
                raise SyDataError(*e.args)

            if isinstance(res, np.ma.MaskedArray):
                res = res.filled(False)

            if not isinstance(res, np.ndarray):
                # Assume bool scalar due to failed comparison.
                res = np.array([res] * len(col))

            indices.append(res)

        if len(indices) == 1:
            index = indices[0]
        else:
            reduction = self._parameters['reduction'].selected
            if reduction != 'any':
                reduction = 'all'
            index = logical_operator_function(reduction).reduce(indices)

        filtered_file = table.File()
        for cname in tablefile.column_names():
            filtered_file.set_column_from_array(
                cname, tablefile.get_column_to_array(cname)[index])

        filtered_file.set_attributes(tablefile.get_attributes())
        return filtered_file

    def execute(self, node_context):
        self._parameters = node_context.parameters

        tablefile = node_context.input['port2']
        if tablefile.is_empty():
            return
        if node_context.input['port1'].is_empty():
            node_context.output['port1'].source(tablefile)
            return
        filtered_table = self._filter_single_file(tablefile, node_context)
        node_context.output['port1'].source(filtered_table)


class SelectTablesRowsFromTable(SelectTableRowsFromTable):
    __doc__ = SELECT_WITH_TABLE_DOCS

    name = 'Select rows in Tables with Table'
    description = ('Select rows in Tables by using an additional selection '
                   'Table with predefined comparison relations.')
    nodeid = 'org.sysess.sympathy.data.table.selecttablesrowsfromtable'
    related = ['org.sysess.sympathy.data.table.selecttablerowsfromtable',
               'org.sysess.sympathy.data.table.selecttablerows',
               'org.sysess.sympathy.slice.rows.table',
               'org.sysess.sympathy.filters.columnfilternode']

    inputs = Ports([Port.Table('Selection', name='port1'),
                    Port.Tables('Input Tables', name='port2')])
    outputs = Ports([Port.Tables(
        'Tables with rows in Selection', name='port1')])

    def execute(self, node_context):
        self._parameters = node_context.parameters

        input_list = node_context.input['port2']
        output_list = node_context.output['port1']

        for tablefile in input_list:
            filtered_table = self._filter_single_file(tablefile, node_context)
            output_list.append(filtered_table)
