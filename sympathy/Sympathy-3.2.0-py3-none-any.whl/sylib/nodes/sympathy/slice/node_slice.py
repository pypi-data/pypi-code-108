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
import numpy
import re
import traceback
import numpy as np

from sympathy.api import qt2 as qt_compat
from sympathy.api import node as synode
from sympathy.api import table
from sympathy.api import ParameterView
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, deprecated_node
from sympathy.api.exceptions import NoDataError, SyConfigurationError

from sympathy.platform import widget_library as sywidgets
from sympathy.platform.table_viewer import TableModel

QtGui = qt_compat.import_module('QtGui')  # noqa
QtWidgets = qt_compat.import_module('QtWidgets')  # noqa


_old_slice_doc = """
    Slice the rows in Tables or elements in lists of Tables or ADAFs.

    The slice pattern is expressed with standard Python syntax,
    [start:stop:step].
    See example below to get a clear view how it works for a list.
    ::

        >>> li = ['elem0', 'elem1', 'elem2', 'elem3', 'elem4']
        >>> li[1:3]
        ['elem1', 'elem2']
        >>> li[1:-1]
        ['elem1', 'elem2', 'elem3']
        >>> li[0:3]
        ['elem0', 'elem1', 'elem2']
        >>> li[:3]
        ['elem0', 'elem1', 'elem2']
        >>> li[3:]
        ['elem3', 'elem4']
        >>> li[:]
        ['elem0', 'elem1', 'elem2', 'elem3', 'elem4']
        >>> li[::2]
        ['elem0', 'elem2', 'elem4']
        >>> li[:4:2]
        ['elem0', 'elem2']
        >>> li[1::2]
        ['elem1', 'elem3']
"""



class SliceError(Exception):
    pass


class GetSlice(object):

    def __getitem__(self, index):
        return index

    @staticmethod
    def from_string(string):
        """
        Construct a slice object from index string.

        >>> GetSlice.from_string('[:]')
        slice(None, None, None)

        >>> GetSlice.from_string('[:1:]')
        slice(None, 1, None)

        >>> GetSlice.from_string('[::1]')
        slice(None, None, 1)

        >>> GetSlice.from_string('[0:-1:-1]')
        slice(0, -1, -1)
        """
        # Compact but insecure method, mitigated by limiting characters.
        if re.match(r'\[[\[\]0-9:, -]*\]', string):
            try:
                return eval('GetSlice(){}'.format(string))
            except SyntaxError:
                pass

    @staticmethod
    def valid_string(string, dims=2, allow_int=True):
        """Validates input string index and returns true if the index was
        valid.
        """
        index = GetSlice.from_string(string)
        if index or index == 0:
            if not allow_int and isinstance(index, int):
                return False
            return len(index) <= dims if isinstance(index, tuple) else True
        else:
            return False


def slice_base_parameters():
    parameters = synode.parameters()
    parameters.set_string(
        'slice', label='Slice', value='[:]',
        description=('Use standard Python syntax to define pattern for slice '
                     'operation, [start:stop:step]'))
    parameters.set_integer(
        'limit', label='Limit preview to', value=100,
        editor=synode.Editors.bounded_spinbox_editor(0, 10000, 1),
        description='Specify the maximum number of rows in the preview table')
    return parameters


@deprecated_node('5.0.0', 'Slice or index nodes')
class SliceDataTable(synode.Node):
    __doc__ = f"""
    Slice data in Table.

    {_old_slice_doc}
    """

    author = "Erik der Hagopian"
    name = 'Slice data Table (deprecated)'
    nodeid = 'org.sysess.sympathy.slice.slicedatatable'
    version = '1.0'
    icon = 'select_table_rows.svg'
    tags = Tags(Tag.DataProcessing.Select)
    related = ['org.sysess.sympathy.slice.slicedatatables']

    inputs = Ports([Port.Table('Input Table', name='port1')])
    outputs = Ports([Port.Table(
        'Table consisting of the rows that been sliced out from the incoming '
        'Table according to the defined pattern. The number of columns are '
        'conserved during the slice operation', name='port2')])

    parameters = slice_base_parameters()

    def execute(self, node_context):
        itable = node_context.input['port1']
        otable = node_context.output['port2']
        index = node_context.parameters['slice'].value
        slice_index = GetSlice.from_string(index)

        otable.update(itable[slice_index])
        otable.set_name(itable.get_name())
        otable.set_table_attributes(itable.get_table_attributes())

    def verify_parameters(self, node_context):
        return GetSlice.valid_string(node_context.parameters['slice'].value)

    def exec_parameter_view(self, node_context):
        itable = node_context.input['port1']
        if not itable.is_valid():
            itable = None
        return SliceWidget(node_context, itable)


@node_helper.list_node_decorator(['port1'], ['port2'])
class SliceDataTables(SliceDataTable):
    name = 'Slice data Tables'
    nodeid = 'org.sysess.sympathy.slice.slicedatatables'


_slice_doc = """
    Briefly, the slice operation removes values in the input data outside the
    index range between given `start` and `stop`. `Step` determines which value
    to keep inside the range. 1: every value, 2: every other value, etc.

    In more detail, slicing can be thought of as an operation which generates
    an index list starting from `start`, taking steps of length `step` and
    finishes at the last index <= `stop`.

    The generated index is list then compared with the indices of the
    values in the input data (the first value has index 0).
    Values whose index is contained in the generated index list are
    kept and the others are removed.

    To handle an unknown number of values (normal case), the indices can also
    be specified relative to the end (last index). "Count stop from the end" is
    enabled by default for `stop`, and when enabled, the effective index is:
    end - `stop`. "Count start from the end" is also available and can be
    enabled to treat `start` in a similar fashion.

    .. warning::

       Compared to slicing in Python, this method has some notable changes:

       - Using `start` > `stop` to reverse the output is not supported.
         Consequently strides can not be negative. Should `start` be larger
         than `stop`, the output will be empty.

       - The range is inclusive for both `start` and `stop`, meaning that the
         value that matches the `stop` index can also be included.

    Examples
    ^^^^^^^^

    :input: `['a', 'b', 'c', 'd', 'e', 'f']`

    Example 1:

    :start: 1
    :stop: 4
    :step: 1
    :index: `[1, 2, 3, 4]`
    :output: `['b', 'c', 'd', 'e']`

    Example 2:

    :start: 0
    :stop: 5
    :step: 2
    :index: `[0, 2, 4]`
    :output: `['a', 'c', 'e']`

    Example 3:

    :start: 0
    :stop: 0 (Count stop from the end)
    :step: 1
    :index: `[0, 1, 2, 3, 4, 5]`
    :output: `['b', 'c', 'd', 'e', 'f']`

    Example 4:

    :start: 0
    :stop: 1 (Count stop from the end)
    :step: 1
    :index: `[0, 1, 2, 3, 4, 5]`
    :output: `['b', 'c', 'd', 'e']`
"""


def set_slice_parameters(parameters):
    parameters.set_integer(
        'start', value=0, label='Start',
        editor=synode.editors.bounded_spinbox_editor(0, None, step=1),
        description=(
            'Start, '
            'specifies the start index of the value range.'
        ))

    parameters.set_boolean(
        'decrement_start', value=False, label='Count start from the end',
        description=(
            'Count start from the end, '
            'when enabled, start is counted backwards from the end '
            '(last index).'
        ))

    parameters.set_integer(
        'stop', value=0, label='Stop',
        editor=synode.editors.bounded_spinbox_editor(0, None, step=1),
        description=(
            'Stop, '
            'specifies the stop index of the value range.'
        ))

    parameters.set_boolean(
        'decrement_stop', value=True, label='Count stop from the end',
        description=(
            'Count stop from the end, '
            'when enabled, stop is counted backwards from the end '
            '(last index).'
        ))

    parameters.set_integer(
        'step', value=1, label='Step',
        editor=synode.editors.bounded_spinbox_editor(1, None, step=1),
        description=(
            'Step, '
            'specifies the step length taken in the value range and '
            'determines which values inside of the range to keep.'
        ))


def get_slice(start, stop, step, length, decrement_start, decrement_stop):
    if step <= 0:
        raise SyConfigurationError('Step must be greater than 0.')

    if start < 0:
        raise SyConfigurationError('Start can not be negative.')

    if stop < 0:
        raise SyConfigurationError('Stop can not be negative.')

    max_index = max(length - 1, 0)

    if decrement_start:
        start = max_index - start

    if decrement_stop:
        stop = max_index - stop

    if start > stop:
        # Slice which will return an empty result.
        start = 0
        stop = 0
        step = 1
    else:
        # Indices before 0 are treated as non-existant.
        stop = max(stop + 1, 0)
        start = max(start, 0)
    return slice(start, stop, step)


class SliceRowsTable(synode.Node):
    __doc__ = f"""
    Slice rows in Table.

    Slicing is used to remove rows from the input.

    {_slice_doc}

    """

    author = "Erik der Hagopian"
    name = 'Slice rows in Table'
    nodeid = 'org.sysess.sympathy.slice.rows.table'
    icon = 'select_table_rows.svg'
    tags = Tags(Tag.DataProcessing.Select)
    related = ['org.sysess.sympathy.slice.columns.table']

    inputs = Ports([Port.Table('Input Table', name='data')])
    outputs = Ports([Port.Custom('table', 'Output Table', name='data',
                                 preview=True)])

    parameters = synode.parameters()
    set_slice_parameters(parameters)

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']

        start = ctx.parameters['start'].value
        stop = ctx.parameters['stop'].value
        step = ctx.parameters['step'].value
        decrement_start = ctx.parameters['decrement_start'].value
        decrement_stop = ctx.parameters['decrement_stop'].value

        length = input_data.number_of_rows()
        index = get_slice(start, stop, step, length,
                          decrement_start, decrement_stop)
        output_data.update(input_data[index])
        output_data.set_name(input_data.get_name())
        output_data.set_table_attributes(input_data.get_table_attributes())


@node_helper.list_node_decorator(['data'], ['data'])
class SliceRowsTables(SliceRowsTable):
    name = 'Slice rows in Tables'
    nodeid = 'org.sysess.sympathy.slice.rows.tables'


class SliceColumnsTable(synode.Node):
    __doc__ = f"""
    Slice columns in Table.

    Slicing is used to remove columns from the input.

    {_slice_doc}
    """

    author = "Erik der Hagopian"
    name = 'Slice columns in Table'
    nodeid = 'org.sysess.sympathy.slice.columns.table'
    icon = 'select_table_columns.svg'
    tags = Tags(Tag.DataProcessing.Select)
    related = ['org.sysess.sympathy.slice.rows.table']

    inputs = Ports([Port.Table('Input Table', name='data')])
    outputs = Ports([Port.Custom('table', 'Output Table', name='data',
                                 preview=True)])

    parameters = synode.parameters()
    set_slice_parameters(parameters)

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']

        start = ctx.parameters['start'].value
        stop = ctx.parameters['stop'].value
        step = ctx.parameters['step'].value
        decrement_start = ctx.parameters['decrement_start'].value
        decrement_stop = ctx.parameters['decrement_stop'].value

        length = input_data.number_of_columns()
        index = get_slice(start, stop, step, length,
                          decrement_start, decrement_stop)
        output_data.update(input_data[:, index])
        output_data.set_name(input_data.get_name())
        output_data.set_table_attributes(input_data.get_table_attributes())


@node_helper.list_node_decorator(['data'], ['data'])
class SliceColumnsTables(SliceColumnsTable):
    name = 'Slice columns in Tables'
    nodeid = 'org.sysess.sympathy.slice.columns.tables'


class SliceItemsList(synode.Node):
    __doc__ = f"""
    Slice List.

    Slicing is used to remove items from the input list.

    {_slice_doc}

    """

    author = "Erik der Hagopian"
    name = 'Slice List'
    nodeid = 'org.sysess.sympathy.slice.list'
    icon = 'slice_list.svg'
    tags = Tags(Tag.DataProcessing.Select)

    inputs = Ports([Port.Custom('[<a>]', 'Input List', name='data')])
    outputs = Ports([Port.Custom('[<a>]', 'Output Table', name='data',
                                 preview=True)])

    parameters = synode.parameters()
    set_slice_parameters(parameters)

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']

        start = ctx.parameters['start'].value
        stop = ctx.parameters['stop'].value
        step = ctx.parameters['step'].value
        decrement_start = ctx.parameters['decrement_start'].value
        decrement_stop = ctx.parameters['decrement_stop'].value

        length = len(input_data)
        index = get_slice(start, stop, step, length,
                          decrement_start, decrement_stop)

        for i in range(length)[index]:
            output_data.append(input_data[i])


class SliceWidget(ParameterView):

    def __init__(self, node_context, itable, dims=2, allow_int=True,
                 parent=None):
        super(SliceWidget, self).__init__(parent=parent)
        self._node_context = node_context
        self._itable = itable
        self._parameters = node_context.parameters
        self._dims = dims
        self._allow_int = allow_int
        self._init_gui()
        self._connect_gui()

    def _init_gui(self):
        vlayout = QtWidgets.QVBoxLayout()
        limit_hlayout = QtWidgets.QHBoxLayout()

        self.slice_label = QtWidgets.QLabel('Slice <I>[start:stop:step]</I>')
        self.slice_lineedit = sywidgets.ValidatedTextLineEdit()
        self.limit_label = QtWidgets.QLabel('Limit preview to:')
        self._limit_gui = self._parameters['limit'].gui()
        self.limit_spinbox = self._limit_gui.editor()

        self.preview_button = QtWidgets.QPushButton('Preview')
        self._preview_table = sywidgets.BasePreviewTable()
        self._preview_table_model = TableModel()
        self._preview_table.setModel(self._preview_table_model)

        limit_hlayout.addWidget(self.limit_label)
        limit_hlayout.addWidget(self.limit_spinbox)

        vlayout.addWidget(self.slice_label)
        vlayout.addWidget(self.slice_lineedit)
        vlayout.addLayout(limit_hlayout)
        vlayout.addWidget(self.preview_button)
        vlayout.addWidget(self._preview_table)

        self.slice_lineedit.clear()
        self._init_line_validator()
        self.slice_lineedit.setText(self._parameters['slice'].value)

        self._preview_table.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preview()

        self.setLayout(vlayout)

    def _connect_gui(self):
        self.slice_lineedit.valueChanged[str].connect(self.slice)
        self.preview_button.clicked.connect(self.preview)

    @property
    def valid(self):
        return GetSlice.valid_string(self._parameters['slice'].value,
                                     self._dims, self._allow_int)

    def _init_line_validator(self):
        def slice_validator(value):
            try:
                valid = GetSlice.valid_string(value,
                                              self._dims, self._allow_int)
                if not valid:
                    raise sywidgets.ValidationError(
                        '"{}" is not a valid slice value.'.format(value))
            except Exception as e:
                raise sywidgets.ValidationError(str(e))
            return value

        self.slice_lineedit.setBuilder(slice_validator)

    def slice(self, text):
        self._parameters['slice'].value = text
        self.status_changed.emit()

    def limit(self, value):
        self._parameters['limit'].value = int(value)

    def clear_preview(self, err_msg=''):
        empty_table = table.File()
        if err_msg:
            empty_table['Error'] = np.array([err_msg])
        self._preview_table_model.set_table(empty_table)

    def preview(self):
        # Fail immediately if there is no input data
        if self._itable is None:
            self.clear_preview('No input data')
            return

        try:
            index = self._parameters['slice'].value
            limit = self._parameters['limit'].value

            slice_index = GetSlice.from_string(index)
            slice_data = self._itable[slice_index]
            slice_data = slice_data[:limit]

            self._preview_table_model.set_table(slice_data)

            if not GetSlice.valid_string(index, self._dims):
                raise SliceError

        except SliceError:
            self.clear_preview('Invalid slice')
        except Exception:
            traceback.print_exc()
            self.clear_preview('Failed to create preview')


class SlicesWidget(ParameterView):

    def __init__(self, node_context, itables, parent=None):
        super(SlicesWidget, self).__init__(parent=parent)
        self._node_context = node_context
        self._parameters = node_context.parameters
        self._single = None
        self._itables = itables
        self._init_gui()
        self._connect_gui()

    @property
    def valid(self):
        return self._single.valid

    def _init_gui(self):
        self.vlayout = QtWidgets.QVBoxLayout()
        group_hlayout = QtWidgets.QHBoxLayout()

        self.group_label = QtWidgets.QLabel('Preview group nr:')
        self.group_spinbox = sywidgets.ValidatedIntSpinBox()

        group_hlayout.addWidget(self.group_label)
        group_hlayout.addWidget(self.group_spinbox)

        self.vlayout.addLayout(group_hlayout)

        self.group_spinbox.setMinimum(0)
        if self._itables.is_valid():
            self.group_spinbox.setMaximum(max(0, len(self._itables) - 1))
        else:
            self.group_spinbox.setMaximum(0)
        self.group_spinbox.setValue(self._parameters['group_index'].value)

        self.group(self._parameters['group_index'].value)
        self.setLayout(self.vlayout)

    def _connect_gui(self):
        self.group_spinbox.valueChanged[int].connect(self.group)
        self._single.status_changed.connect(self.status_changed)

    def group(self, value):
        try:
            self._single.hide()
        except Exception:
            pass
        self._parameters['group_index'].value = int(value)

        if self._itables.is_valid() and len(self._itables):
            itable = self._itables[int(value)]
        else:
            itable = None

        self._single = SliceWidget(self._node_context, itable)
        self.vlayout.addWidget(self._single)


@deprecated_node('5.0.0', 'Slice or index nodes')
class SliceList(synode.Node):
    __doc__ = f"""
    Slice elements in a list.

    {_old_slice_doc}
    """

    author = "Erik der Hagopian"
    name = 'Slice List (deprecated)'
    icon = 'slice_list.svg'
    nodeid = 'org.sysess.sympathy.slice.slicelist'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([
        Port.Custom('[<a>]', 'Input List', name='list')])
    outputs = Ports([
        Port.Custom('[<a>]', 'Sliced output List', name='list')])

    parameters = slice_base_parameters()

    def execute(self, node_context):
        slice_index = GetSlice.from_string(
            node_context.parameters['slice'].value)
        itables = node_context.input['list']
        otables = node_context.output['list']
        for itable in list(itables)[slice_index]:
            otables.append(itable)

    def verify_parameters(self, node_context):
        return GetSlice.valid_string(
            node_context.parameters['slice'].value, 1, allow_int=False)

    def exec_parameter_view(self, node_context):
        try:
            itable = table.File()
            itable.set_column_from_array(
                '0',
                numpy.arange(len(node_context.input['list'])))
        except NoDataError:
            itable = None
        return SliceWidget(node_context, itable, 1, allow_int=False)
