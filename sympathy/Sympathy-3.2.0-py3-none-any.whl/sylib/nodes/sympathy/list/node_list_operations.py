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
import itertools
import os

from sympathy.api import node as synode
from sympathy.api.nodeconfig import (Port, Ports, Tag, Tags,
                                     adjust)
from sympathy.api.exceptions import SyNodeError, SyDataError
import sylib.sort
import sylib.error
import sylib.index


def extend(list1, list2):
    for elem in list2:
        list1.append(elem)


def match_length(node_context, fill_data):
    input_list1 = node_context.input['guide']
    input_list2 = node_context.input['input']
    output_list = node_context.output['output']
    parameter_root = synode.parameters(node_context.parameters)

    len1 = len(input_list1)
    len2 = len(input_list2)

    fill = parameter_root['fill'].selected

    if fill == 'Last value' and len2:
        fill_data = input_list2[len2 - 1]

    if len1 >= len2:
        extend(output_list, input_list2)
        extend(output_list, itertools.repeat(fill_data, len1 - len2))
    else:
        extend(output_list, itertools.islice(input_list2, len1))


class AppendList(synode.Node):
    """Create a list with the items from list (input) followed by item."""

    author = 'Erik der Hagopian'
    name = 'Append List'
    nodeid = 'org.sysess.sympathy.list.appendlistnew'
    icon = 'append_list_new.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([
        Port.Custom('[<a>]', 'Appended List', name='list'),
        Port.Custom('<a>', 'The Item to be appended', name='item',
                    n=(1, None, 1))])
    outputs = Ports([
        Port.Custom('[<a>]', 'Appended List', name='list')])

    def execute(self, node_context):
        result = node_context.output['list']
        result.extend(node_context.input['list'])
        for item in node_context.input.group('item'):
            result.append(item)


class ItemToList(synode.Node):
    """Create a single item list containing item."""

    author = 'Erik der Hagopian'
    name = 'Item to List'
    nodeid = 'org.sysess.sympathy.list.itemtolist'
    icon = 'item_to_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([
        Port.Custom('<a>', 'Input Item', name='item', n=(1,))])
    outputs = Ports([
        Port.Custom('[<a>]', 'Item as List', name='list')])

    parameters = synode.parameters()
    parameters.set_integer(
        'n', label='Repeat number of times', value=1,
        description='Choose number of times to repeat items.')

    def execute(self, node_context):
        result = node_context.output['list']
        n = node_context.parameters['n'].value
        if n <= 0:
            n = 1
        for _ in range(n):
            for item in node_context.input.group('item'):
                result.append(item)


_basic_error_strategy = sylib.error.strategy('basic')


class GetItemList(synode.Node):
    """Get one item in list by index."""

    author = 'Erik der Hagopian'
    name = 'Get Item List'
    nodeid = "org.sysess.sympathy.list.getitemlist"
    inputs = Ports(
        [Port.Custom('[<a>]', 'Input List', name='list'),
         Port.Custom('<a>', 'Default item', name='default',
                     n=(0, 1, 0))])
    outputs = Ports(
        [Port.Custom('<a>', 'Output selected Item from List', name='item'),
         Port.Custom('[<a>]', 'Output non-selected Items from List',
                     name='rest', n=(0, 1, 0))])
    icon = 'get_item_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    parameters = synode.parameters()
    parameters.set_list(
        'index', label='Index', value_names=['0'],
        description='Choose item index in list.',
        editor=synode.Util.combo_editor(edit=True))
    parameters.set_list(
        'fail_strategy', label='Action on index out of bounds',
        list=_basic_error_strategy.descriptions,
        value=[0],
        description='Decide how an index out of bounds should be handled',
        editor=synode.Util.combo_editor())

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['index'], node_context.input[0],
               lists='index')

    def execute(self, node_context):
        selected = node_context.parameters['index'].selected
        try:
            index = int(selected)
        except Exception:
            raise SyDataError(f'Index must be numeric, it is {selected}.')

        if index < len(node_context.input['list']):
            node_context.output['item'].source(
                node_context.input['list'][index], shallow=True)
        else:
            defaults = node_context.input.group('default')
            if defaults:
                node_context.output['item'].source(defaults[0])
            elif _basic_error_strategy.is_error(
                    node_context.parameters['fail_strategy'].value[0]):
                raise SyNodeError("List index is out of bounds.")
        for rest in node_context.output.group('rest'):
            for i, item in enumerate(node_context.input['list']):
                if i != index:
                    rest.append(item)


class IndexList(synode.Node):
    __doc__ = f"""
    Index the items in the list.

    {sylib.index.index_doc}
    """
    author = "Erik der Hagopian"
    name = 'Index List'
    nodeid = 'org.sysess.sympathy.list.index'
    icon = os.path.join('..', 'slice', 'slice_list.svg')
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    inputs = Ports([Port.Custom('[<a>]', 'Input List', name='list')])
    outputs = Ports([Port.Custom('[<a>]', 'Output List', name='list')])

    parameters = synode.parameters()
    sylib.index.set_parameters(parameters)

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['index'], node_context.input['list'],
               lists='index')

    def execute(self, ctx):
        input_data = ctx.input['list']
        output_data = ctx.output['list']
        index = ctx.parameters['index']
        names = {str(i) for i in range(len(input_data))}
        indices = {int(i) for i in index.selected_names(names)}
        for i, data in enumerate(input_data):
            if i in indices:
                output_data.append(data)


class PadList(synode.Node):
    """Pad a list to match another list."""

    author = 'Erik der Hagopian'
    name = 'Pad List'
    description = 'Pad a list to match the length of template'
    nodeid = 'org.sysess.sympathy.list.padlist'
    inputs = Ports(
        [Port.Custom('[<a>]', 'List with deciding length', name='template'),
         Port.Custom('[<b>]', 'List that will be padded', name='list')])
    outputs = Ports(
        [Port.Custom('[<b>]', 'Padded List', name='list')])
    icon = 'pad_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    parameters = synode.parameters()
    parameters.set_list(
        'strategy', label='Pad values', value=[0],
        description='Specify strategy to use when padding.',
        plist=['Repeat last item', 'Empty item'],
        editor=synode.Util.combo_editor())

    def execute(self, node_context):
        template = node_context.input['template']
        input_ = node_context.input['list']
        output = node_context.output['list']

        if len(input_) == len(template) == 0:
            # Empty output
            return

        if node_context.parameters['strategy'].value[0] == 0:
            try:
                fv = input_[-1]
            except IndexError:
                raise SyDataError(
                    'Repeat last item requires non-empty list.')
        else:
            fv = output.create()

        for idx, (inp, templ) in enumerate(itertools.zip_longest(
                input_, template, fillvalue=fv)):
            output.append(inp)


class PadListItem(synode.Node):
    """Pad a list with item to match another list."""

    author = 'Erik der Hagopian'
    name = 'Pad List with Item'
    description = 'Pad a list with item match the length of template'
    nodeid = 'org.sysess.sympathy.list.padlistitem'
    inputs = Ports(
        [Port.Custom('[<a>]', 'List with deciding length', name='template'),
         Port.Custom('<b>', 'Item to be used as padding', name='item'),
         Port.Custom('[<b>]', 'List that will be padded', name='list')])
    outputs = Ports(
        [Port.Custom('[<b>]', 'The padded List', name='list')])
    icon = 'pad_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    def execute(self, node_context):
        template = node_context.input['template']
        item = node_context.input['item']
        input_ = node_context.input['list']
        output = node_context.output['list']

        for idx, (inp, templ) in enumerate(itertools.zip_longest(
                input_, template, fillvalue=item)):
            output.append(inp)


class PropagateFirst(synode.Node):
    """
    Propagate first input to output.

    This node is mostly useful for testing purposes.
    It can also be used to force a specific execution
    order.
    """

    author = 'Erik der Hagopian'
    name = 'Propagate First Input'
    description = 'Propagate first input to output'
    nodeid = 'org.sysess.sympathy.generic.propagatefirst'
    icon = 'propagate_first.svg'
    version = '1.0'
    tags = Tags(Tag.Generic.Control)

    inputs = Ports([
        Port.Custom('<a>', 'The Item to be propagated', name='item1'),
        Port.Custom('<b>', 'Item that will not be propagated', name='item2',
                    n=(0, None, 1))])

    outputs = Ports(
        [Port.Custom('<a>', 'Propagated Item', name='item')])

    def execute(self, node_context):
        node_context.output['item'].source(
            node_context.input['item1'], shallow=True)


class PropagateFirstSame(synode.Node):
    """
    Propagate first input to output.

    This node is mostly useful for testing purposes.
    It can also be used to force a specific execution
    order and to enforce a specific type.
    """

    author = 'Erik der Hagopian'
    name = 'Propagate First Input (Same Type)'
    description = 'Propagate first input to output'
    nodeid = 'org.sysess.sympathy.generic.propagatefirstsame'
    icon = 'propagate_first.svg'
    version = '1.0'
    tags = Tags(Tag.Generic.Control)

    inputs = Ports([
        Port.Custom('<a>', 'The Item to be propagated', name='item1'),
        Port.Custom('<a>', 'Item that will not be propagated', name='item2')])

    outputs = Ports(
        [Port.Custom('<a>', 'Propagated Item', name='item')])

    def execute(self, node_context):
        node_context.output['item'].source(
            node_context.input['item1'], shallow=True)


class ExtendList(synode.Node):
    """Extend a list with another list."""

    author = 'Erik der Hagopian'
    name = 'Extend List'
    description = 'Extend a list'
    nodeid = 'org.sysess.sympathy.list.extendlist'
    icon = 'extend_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    inputs = Ports([
        Port.Custom('[<a>]', 'List that will be added', name='input',
                    n=(2,)),
    ])
    outputs = Ports(
        [Port.Custom('[<a>]', 'The extended List', name='output')])

    def execute(self, node_context):
        output_list = node_context.output[0]
        for input_list in node_context.input.group('input'):
            output_list.extend(input_list)


class FlattenList(synode.Node):
    """Flatten a nested list."""

    author = 'Magnus Sandén'
    name = 'Flatten List'
    description = 'Flatten a nested list'
    nodeid = 'org.sysess.sympathy.list.flattenlist'
    icon = 'flatten_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([
        Port.Custom('[[<a>]]', 'Nested List', name='in')])
    outputs = Ports(
        [Port.Custom('[<a>]', 'Flattened List', name='out')])

    def execute(self, node_context):
        input_list = node_context.input['in']
        output_list = node_context.output['out']
        for inner_list in input_list:
            output_list.extend(inner_list)


class TransposeList(synode.Node):
    """
    Swap the first and second layers of a nested list.

    For example a list with two inner lists, each of length three, will become
    a list with three inner lists, each of length two.

    This node requires all inner lists to be of equal length.
    """

    author = 'Magnus Sandén'
    name = 'Transpose List'
    description = 'Swap the first and second layers of a nested list'
    nodeid = 'org.sysess.sympathy.list.transposelist'
    icon = 'transpose_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    inputs = Ports([Port.Custom('[[<a>]]', 'List', name='in')])
    outputs = Ports([Port.Custom('[[<a>]]', 'Transposed List', name='out')])

    def execute(self, node_context):
        input_list = node_context.input['in']
        output_list = node_context.output['out']

        if not len(input_list):
            return
        length = len(input_list[0])
        if not all(len(inner_list) == length for inner_list in input_list):
            raise SyDataError("Inner lists are of different lengths.")

        for i in range(length):
            new_inner_list = output_list.create()
            for inner_list in input_list:
                new_inner_list.append(inner_list[i])
            output_list.append(new_inner_list)


class BisectList(synode.Node):
    """
    Split a list into two (or optionally more) parts.

    To get more than two parts, add more "Extra part" ports.
    """

    author = 'Magnus Sandén'
    name = 'Bisect List'
    description = 'Split a list into two (or optionally more) parts'
    nodeid = 'org.sysess.sympathy.list.bisectlist'
    icon = 'bisect_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    inputs = Ports([
        Port.Custom('[<a>]', 'Full List', name='in')])

    outputs = Ports([
        Port.Custom('[<a>]', 'Part List', name='part', n=(2, None, 2))])

    def execute(self, node_context):
        input_list = node_context.input['in']
        part_output_lists = node_context.output.group('part')

        # When there are an odd number of elements, put one more in the first
        # output lists:

        n_inputs = len(input_list)
        n_groups = len(part_output_lists)

        n_min = n_inputs // n_groups
        n_ext = n_inputs % n_groups

        iinput_list = iter(input_list)

        for part_output_list in part_output_lists[:n_groups]:
            n = n_min

            if n_ext > 0:
                n_ext -= 1
                n += 1

            part_output_list.extend(list(itertools.islice(iinput_list, n)))


class SortList(synode.Node):
    """
    Sort List of items using a Python key function that determines order.
    For details about how to write the key function see: `Key functions
    <https://docs.python.org/2/howto/sorting.html#key-functions>`_. Have a look
    at the :ref:`Data type APIs<datatypeapis>` to see what methods and
    attributes are available on the data type that you are working with.

    Example with port type == [adaf] and item type == adaf:

        Sorting input produced by Random ADAFs:

          lambda item: item.meta['meta_col0'].value()

    NaN values are treated as larger than any other value.
    """

    name = 'Sort List'
    description = 'Sort List using a key function.'
    author = 'Erik der Hagopian'
    nodeid = 'org.sysess.sympathy.list.sortlist'
    icon = 'sort_list.svg'
    version = '1.0'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    parameters = synode.parameters()
    parameters.set_string(
        'sort_function',
        description='Python key function that determines order.',
        value='lambda item: item  # Arbitrary key example.',
        editor=synode.Util.code_editor())
    parameters.set_boolean(
        'reverse',
        label='Reverse order',
        description='Use descending (reverse) order.',
        value=False)

    inputs = Ports([
        Port.Custom('[<a>]', 'List to be sorted', name='list')])
    outputs = Ports([
        Port.Custom('[<a>]', 'Sorted List', name='list')])

    def exec_parameter_view(self, node_context):
        return sylib.sort.SortWidget(node_context.input['list'],
                                     node_context)

    def execute(self, node_context):
        output_list = node_context.output['list']
        for item in sylib.sort.sorted_list(
                node_context.parameters['sort_function'].value,
                node_context.input['list'],
                reverse=node_context.parameters['reverse'].value):
            output_list.append(item)


class InsertItemList(synode.Node):
    """
    Create a list with the items from list (input) but with item inserted at
    selected index.
    """
    author = "Erik der Hagopian"
    name = 'Insert List'
    description = 'Insert item in list'
    nodeid = 'org.sysess.sympathy.list.insertlist'
    icon = 'append_list_new.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    parameters = synode.parameters()
    parameters.set_integer('index', label='Index', value=0)

    inputs = Ports([
        Port.Custom('[<a>]', 'Inserted List', name='list'),
        Port.Custom('<a>', 'The Item to be inserted', name='item')])
    outputs = Ports([
        Port.Custom('[<a>]', 'Inserted List', name='list')])

    def execute(self, node_context):
        result = node_context.output['list']

        input_list = node_context.input['list']

        test = list(range(len(input_list)))
        test.insert(node_context.parameters['index'].value, -1)
        iinput_list = iter(input_list)

        for i in test:
            if i == -1:
                result.append(node_context.input['item'])
                result.extend(iinput_list)
                break
            else:
                result.append(next(iinput_list))


class ChunkList(synode.Node):
    """
    Split a list into several chunks of at most the specified length
    or a specified number of chunks.
    """

    author = "Erik der Hagopian"
    name = 'Chunk List'
    description = ('Split a list into several chunks of at most the specified '
                   'length or a specified number of chunks')
    nodeid = 'org.sysess.sympathy.list.chunklist'
    icon = 'bisect_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)

    parameters = synode.parameters()
    _length_of_chunk, _length_of_list = _options = ['Length of each chunk',
                                                    'Length of chunk list']
    parameters.set_integer('length', label='Length', value=0,
                           description=(
                               'Length of chunk list, depending on '
                               'mode (0 => length of list.'))
    parameters.set_string(
        'mode', label='Length specifies', value=_length_of_chunk,
        editor=synode.Util.combo_editor(options=_options))

    parameters.set_integer('minimum', label='Minimum chunk size', value=0,
                           description='Minimum chunk size (0 => no minimum).')
    controllers = (
        synode.controller(
            when=synode.field('mode', 'value', value=_length_of_list),
            action=synode.field('minimum', 'enabled')))

    inputs = Ports([
        Port.Custom('[<a>]', 'List', name='list')])

    outputs = Ports([
        Port.Custom('[[<a>]]', 'Chunk List', name='chunks')])

    def execute(self, node_context):
        input_list = node_context.input['list']
        chunk_list = node_context.output['chunks']
        length = node_context.parameters['length'].value
        minimum = node_context.parameters['minimum'].value
        mode = node_context.parameters['mode'].value
        len_list = len(input_list)
        if len_list:
            if minimum <= 0:
                minimum = 1
            if length <= 0:
                length = len_list
            if mode == self._length_of_list:
                len_out_list = min(length, len_list)
                len_out_list = max(1, min((len_list // minimum), len_out_list))
            elif mode == self._length_of_chunk:
                len_out_list = len_list // length + (1 if len_list % length else 0)

            quot = len_list // len_out_list
            rest = len_list % len_out_list
            iter_input = iter(input_list)

            for i in range(len_out_list):
                chunk = chunk_list.create()
                items = quot + (1 if i < rest else 0)
                for _ in range(items):
                    chunk.append(next(iter_input))
                chunk_list.append(chunk)


class ReverseList(synode.Node):
    """
    Reverse List.
    """

    author = "Erik der Hagopian"
    name = 'Reverse List'
    nodeid = 'org.sysess.sympathy.list.reverse'
    icon = 'sort_list.svg'
    tags = Tags(Tag.Generic.List, Tag.DataProcessing.List)
    inputs = Ports([Port.Tables('Input Tables', name='data')])
    outputs = Ports([Port.Tables('Output Tables', name='data')])
    parameters = synode.parameters()

    def execute(self, ctx):
        input_data = ctx.input['data']
        output_data = ctx.output['data']

        for i in reversed(range(len(input_data))):
            output_data.append(input_data[i])
