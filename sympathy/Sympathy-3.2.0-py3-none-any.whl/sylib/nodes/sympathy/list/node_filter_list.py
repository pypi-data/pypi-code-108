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
import collections
import numpy as np

from sylib import util
from sympathy.api import node as synode
from sympathy.api.nodeconfig import (
    Port, Ports, Tag, Tags, adjust)
from sympathy.api.nodeconfig import join_doc
from sympathy.api.exceptions import (
    SyDataError, SyConfigurationError, SyNodeError)
from sympathy.platform.exceptions import try_result


class FilterListTable(synode.Node):
    """
    This node takes a table on the upper port and use it to filter the list on
    the lower port. The table must contain a single column which should be at
    least as long as the list on the lower port. Lets call it the
    filter column. Then for each item in the incoming list the corresponding
    row of the filter column is inspected. If it is True (or is considered
    True in Python, e.g. any non-zero integer or a non-empty string) the item
    is included in the filtered list. And vice versa, if the value in the
    filter column is False (or is considered False in Python, e.g. 0 or an
    empty string) the corresponding item is not included in the filtered list.
    """

    name = "Filter List with Table"
    nodeid = "org.sysess.sympathy.list.filterlisttable"
    description = "Filter a list using a column from an incoming table."
    icon = "filter_list.svg"
    author = "Magnus Sanden"
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    related = ['org.sysess.sympathy.list.filterlistpredicate']

    inputs = Ports([Port.Table('Filter', name="filter"),
                    Port.Custom('[<a>]', 'List of items', name='in')])
    outputs = Ports(
        [Port.Custom('[<a>]', 'Filtered list of items', name='out')])

    parameters = synode.parameters()
    parameters.set_list(
        'filter', label='Filter column',
        description='Select the column which holds the filter '
        '(leave empty to use first column)',
        value=[],
        editor=synode.Util.combo_editor(edit=True, filter=True))

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['filter'], node_context.input['filter'])

    def execute(self, node_context):
        filterfile = node_context.input['filter']
        infiles = node_context.input['in']
        if filterfile.number_of_rows() == 0:
            node_context.output['out'].source(node_context.input['in'][:0])
            return
        columns = filterfile.column_names()
        column = node_context.parameters['filter'].selected
        if not column:
            column = columns[0]
        elif column not in columns:
            raise SyDataError('Selected filter column does not exist.')

        filter_values = filterfile.get_column_to_array(column)
        outfiles = node_context.output['out']

        for filter_value, infile in zip(filter_values, infiles):
            if filter_value:
                outfiles.append(infile)


def function_result(node_context):
    predicate_str = node_context.parameters['predicate'].value
    return try_result(Exception, util.base_eval, predicate_str).map_fail(
        lambda e: SyConfigurationError(
            f'Error compiling predicate, {e}.'))


def check_function_result(node_context):
    try:
        function_result(node_context).ok()
    except Exception:
        return False
    return True


def eval_function_result(function_result, arg):
    def apply(predicate):
        return predicate(arg)
    return function_result.try_map_ok(apply).map_fail(fail_eval).ok()


def fail_eval(e):
    if isinstance(e, SyNodeError):
        return e
    return SyDataError(
        f'Error evaluating predicate, {e}')


class FilterListPredicate(synode.Node):
    """
    This node takes a predicate function (a function that returns True or
    False) from the configuration and uses it to decide which inputs to include
    in the output.

    The function is applied once for each input element in the list and for
    each element where the function returned True the element is also included
    in the output.

    Examples with port type == [table] and item type == table:

    Propagate tables with at least 10 rows to output::

        lambda item: item.number_of_rows() >= 10

    Propagate only non-empty tables::

        lambda item: not item.is_empty()

    The name of the argument is not important.

    See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
    for a description of lambda functions. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.
    """

    name = 'Filter List Predicate'
    nodeid = 'org.sysess.sympathy.list.filterlistpredicate'
    description = 'Filter a list using a configured item-based predicate.'
    icon = 'filter_list.svg'
    author = 'Erik der Hagopian'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    related = ['org.sysess.sympathy.list.filterlisttable']

    inputs = Ports([
        Port.Custom('[<a>]', 'List', name='list')])

    outputs = Ports([
        Port.Table('Index', name='index'),
        Port.Custom('[<a>]', 'List', name='list')])

    parameters = synode.parameters()
    parameters.set_string(
        'predicate',
        label='Filter function',
        value='lambda item: True',
        editor=synode.Util.code_editor(),
        description=(
            'Function, called for each item in `list` to determine which '
            'inputs to filter. Should return a boolean'))

    def verify_parameters(self, node_context):
        return check_function_result(node_context)

    def execute(self, node_context):
        infiles = node_context.input['list']
        outfiles = node_context.output['list']
        index = node_context.output['index']
        predicate_fn = function_result(node_context)

        index_data = []

        for i, infile in enumerate(infiles):
            self.set_progress(i * 100 / len(infiles))
            if eval_function_result(predicate_fn, infile):
                outfiles.append(infile)
                index_data.append(True)
            else:
                index_data.append(False)

        index.set_column_from_array('filter', np.array(index_data))


class PartitionListPredicate(synode.Node):
    """
    This node takes a predicate function (a function that returns True or
    False) from the configuration and uses it to decide how to partition the
    output.

    The function is applied once for each input element in the list. If it
    returns True, then the element is written to the first output, otherwise it
    is written to the second output.

    Examples with port type == [table] and item type == table:

        Put tables with more than 10 rows in the first output port::

            lambda item: item.number_of_rows() > 10

        Put nonempty tables in the first output port::

            lambda item: not item.is_empty()

    The name of the argument is not important.

    See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
    for a description of lambda functions. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.
    """

    name = 'Partition List Predicate'
    nodeid = 'org.sysess.sympathy.list.partitionlistpredicate'
    description = 'Partition a list using a configured item-based predicate.'
    icon = 'partition_list.svg'
    author = 'Erik der Hagopian'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    related = ['org.sysess.sympathy.list.grouplist']

    inputs = Ports([
        Port.Custom('[<a>]', 'List', name='list')])
    outputs = Ports([
        Port.Custom('[<a>]', 'List of items where predicate returned true',
                    name='list_true'),
        Port.Custom('[<a>]', 'List of items where predicate returned false',
                    name='list_false')])

    parameters = synode.parameters()
    parameters.set_string(
        'predicate',
        label='Partition function',
        value='lambda item: True',
        editor=synode.Util.code_editor(),
        description=(
            'Function, called for each item in `list` to determine its '
            'output partition. Should return a boolean'))

    def verify_parameters(self, node_context):
        return check_function_result(node_context)

    def execute(self, node_context):
        infiles = node_context.input['list']
        truefiles = node_context.output['list_true']
        falsefiles = node_context.output['list_false']
        predicate_fn = function_result(node_context)

        for i, infile in enumerate(infiles):
            self.set_progress(i * 100 / len(infiles))
            if eval_function_result(predicate_fn, infile):
                truefiles.append(infile)
            else:
                falsefiles.append(infile)


class GroupList(synode.Node):
    """
    This node takes a key function from the configuration and uses it to decide
    how to group the items in the input list.

    The key function is applied once for each input element in the list. All
    elements for which the key function returns the same value will end up in
    the same group.

    Examples with port type == [table] and item type == table:

        Put all tables with the same number of rows in the same group::

            lambda item: item.number_of_rows()

        Put empty tables in one group and nonempty tables in another group::

            lambda item: item.is_empty()

    The name of the argument is not important.

    See https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions
    for a description of lambda functions. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.
    """

    name = 'Group List'
    nodeid = 'org.sysess.sympathy.list.grouplist'
    description = 'Group a list using a configured item-based key function.'
    icon = 'partition_list.svg'
    author = 'Magnus Sandén'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    related = ['org.sysess.sympathy.list.partitionlistpredicate']

    inputs = Ports([
        Port.Custom('[<a>]', 'List of items', name='list')])
    outputs = Ports([
        Port.Custom('[[<a>]]', 'Grouped items', name='lists')])

    parameters = synode.parameters()
    parameters.set_string(
        'predicate',
        label='Key function',
        value='lambda item: 0  # All in 1 group',
        editor=synode.Util.code_editor(),
        description=(
            'Function, called for each item in `list` to determine its '
            'output group. Should return group keys.'))

    def verify_parameters(self, node_context):
        return check_function_result(node_context)

    def execute(self, node_context):
        infiles = node_context.input['list']
        outlists = node_context.output['lists']
        key_fn = function_result(node_context)

        grouped_indices = collections.defaultdict(list)
        for index, infile in enumerate(infiles):
            grouped_indices[eval_function_result(key_fn, infile)].append(
                index)

        i = 0
        for group in grouped_indices.values():
            current_list = outlists.create()
            for index in group:
                current_list.append(infiles[index])
                self.set_progress(i * 100 / len(infiles))
                i = i + 1
            outlists.append(current_list)
        self.set_progress(100)


class ConditionalPropagate(synode.Node):
    """
    This node takes a configurable predicate function (a function that returns
    True or False) from the configuration and uses it to decide which input to
    return to the output.

    The function is applied to the input data for the node. So for example if
    the input port is connected to a table port the argument of the lambda will
    be a :class:`table.File<tableapi>`. Have a look at the :ref:`Data type
    APIs<datatypeapis>` to see what methods and attributes are available on the
    data type that you are working with.

    If the lambda function returns True, the data from the first port is
    written to the output, otherwise the data from the second port is written
    to the output.
    """

    name = 'Conditional Propagate'
    nodeid = 'org.sysess.sympathy.list.eitherwithdatapredicate'
    description = ('Propagates one input or the other depending on a '
                   'configurable predicate function.')
    author = 'Erik der Hagopian'
    version = '1.0'
    tags = Tags(Tag.Generic.Control)
    icon = 'either.svg'

    inputs = Ports([
        Port.Custom('<a>', 'First, returned if predicate held true',
                    name='true'),
        Port.Custom('<a>', 'Second, returned if predicate did not hold true',
                    name='false'),
        Port.Custom('<b>', 'Data for the predicate comparison',
                    name='data')])

    outputs = Ports([Port.Custom(
        '<a>',
        'Output, First if the predicate holds true otherwise Second',
        name='output')])
    parameters = synode.parameters()

    parameters.set_string(
        'predicate',
        label='Condition function',
        value='lambda arg: True',
        editor=synode.Util.code_editor(),
        description=(
            'Function, called with `data` to determine which input to output. '
            'Should return a boolean'))

    def verify_parameters(self, node_context):
        return check_function_result(node_context)

    def execute(self, node_context):
        truefile = node_context.input['true']
        falsefile = node_context.input['false']
        infile = node_context.input['data']
        outputfile = node_context.output['output']
        predicate_fn = function_result(node_context)

        if eval_function_result(predicate_fn, infile):
            outputfile.source(truefile)
        else:
            outputfile.source(falsefile)
