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
from collections import OrderedDict
import itertools

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api.nodeconfig import TemplateTypes as t
from sympathy.api.exceptions import SyDataError


class SuperNodeGeneric(synode.Node):
    author = 'Erik der Hagopian'
    version = '1.0'
    tags = Tags(Tag.Generic.Tuple, Tag.DataProcessing.Tuple)


class Tuple(SuperNodeGeneric):
    """
    Create a tuple from two (or more) items.

    Add more input ports to create bigger tuples.
    """

    author = 'Erik der Hagopian'
    name = 'Tuple'
    nodeid = 'org.sysess.sympathy.tuple.tuple2'
    icon = 'tuple.svg'

    inputs = Ports([
        Port.Custom(t.generic(t.letters(t.index)),
                    'Input', 'input', n=(2, None))])

    outputs = Ports([
        Port.Custom(t.tuple(t.types(t.group('input'))),
                    'Output', 'output')])

    def execute(self, node_context):
        out = node_context.output[0]
        for i, item in enumerate(node_context.input):
            out[i] = node_context.input[i]


class Untuple(SuperNodeGeneric):
    """
    Deconstruct a tuple, getting the elements out.

    Add more output ports to deconstruct bigger tuples.
    """

    author = 'Erik der Hagopian'
    name = 'Untuple'
    nodeid = 'org.sysess.sympathy.tuple.untuple2'
    icon = 'untuple.svg'

    inputs = Ports([
        Port.Custom(t.tuple(t.types(t.group('output'))),
                    'Input', 'input')])

    outputs = Ports([
        Port.Custom(t.generic(t.letters(t.index)),
                    'Output', 'output', n=(2, None))])

    def execute(self, node_context):
        for in_, out in zip(node_context.input[0], node_context.output):
            out.source(in_, shallow=True)


class CartesianProductTuple(synode.Node):
    """
    Create a list of tuples with all combinations of elements from two (or
    more) lists.
    """

    version = '1.0'
    author = 'Magnus Sandén'
    name = 'Cartesian Product Tuple'
    nodeid = 'org.sysess.sympathy.tuple.carthesianproduct2'
    icon = 'product.svg'
    tags = Tags(Tag.Generic.Tuple, Tag.DataProcessing.Tuple)

    inputs = Ports([
        Port.Custom(t.list(t.generic(t.letters(t.index))),
                    'Input', 'input', n=(2, None))])

    outputs = Ports([
        Port.Custom(t.list(t.tuple(t.map(
            t.unlist, t.types(t.group('input'))))),
                    'Output', 'output')])

    def execute(self, node_context):
        inputs = list(node_context.input)
        outlist = node_context.output[0]

        for pytuple in itertools.product(*inputs):
            sytuple = outlist.create()

            for i, item in enumerate(pytuple):
                sytuple[i] = item
            outlist.append(sytuple)


ZIP_STRATEGIES = OrderedDict([
    ('shortest', "Use shortest list length"),
    ('longest', "Use longest list length"),
    ('error', "Error")])


def _add_strategy_param(parameters):
    parameters.set_string(
        'len_strategy',
        label='Strategy for different length lists:',
        description='How should the node handle the situation when the '
                    'input lists are of different lengths?',
        value='error',
        editor=synode.editors.combo_editor(options=ZIP_STRATEGIES))


class ZipTuple(SuperNodeGeneric):
    """Create a list of tuples from two (or more) lists."""

    author = 'Erik der Hagopian'
    name = 'Zip Tuple'
    nodeid = 'org.sysess.sympathy.tuple.ziptuple2'
    icon = 'zip.svg'

    inputs = Ports([
        Port.Custom(t.list(t.generic(t.letters(t.index))),
                    'Input', 'input', n=(2, None))])

    outputs = Ports([
        Port.Custom(t.list(t.tuple(t.map(t.unlist,
                                         t.types(t.group('input'))))),
                    'Output', 'output')])

    parameters = synode.parameters()
    _add_strategy_param(parameters)

    def update_parameters(self, parameters):
        if 'len_strategy' not in parameters:
            _add_strategy_param(parameters)
            parameters['len_strategy'].value = 'shortest'

    def execute(self, node_context):
        inputs = list(node_context.input)
        outlist = node_context.output[0]
        parameters = node_context.parameters
        strategy = parameters['len_strategy'].value

        if strategy == 'error':
            if not all(len(i) == len(inputs[0]) for i in inputs):
                raise SyDataError("Lists are of different lengths.")

        zip_func = zip
        if strategy == 'longest':
            zip_func = itertools.zip_longest
        elif strategy not in ZIP_STRATEGIES:
            raise ValueError('Unknown strategy: {}'.format(strategy))

        for pytuple in zip_func(*inputs):
            sytuple = outlist.create()

            for i, item in enumerate(pytuple):
                if item is not None:
                    sytuple[i] = item
            outlist.append(sytuple)


class UnzipTuple(SuperNodeGeneric):
    """
    Deconstruct each tuple in a list of tuples, getting two (or more) lists of
    elements out.
    """

    author = 'Erik der Hagopian'
    name = 'Unzip Tuple'
    nodeid = 'org.sysess.sympathy.tuple.unziptuple2'
    icon = 'unzip.svg'

    inputs = Ports([
        Port.Custom(t.list(t.tuple(t.map(t.unlist,
                                         t.types(t.group('output'))))),
                    'Input', 'input')])

    outputs = Ports([
        Port.Custom(t.list(t.generic(t.letters(t.index))),
                    'Output', 'output', n=(2, None))])

    def execute(self, node_context):
        in_list = node_context.input[0]
        outs = list(node_context.output)

        for tuplen in in_list:
            for i, item in enumerate(tuplen):
                outs[i].append(item)


class FirstTuple2(SuperNodeGeneric):
    """Get the first element out of a two-element tuple (pair)."""

    author = 'Erik der Hagopian'
    name = 'First Tuple2'
    nodeid = 'org.sysess.sympathy.tuple.firsttuple2'
    icon = 'first.svg'

    inputs = Ports([
        Port.Custom('(<a>, <b>)', 'Tuple')])

    outputs = Ports([
        Port.Custom('<a>', 'First')])

    def execute(self, node_context):
        node_context.output[0].source(node_context.input[0][0], shallow=True)


class SecondTuple2(SuperNodeGeneric):
    """Get the second element out of a two-element tuple (pair)."""

    author = 'Erik der Hagopian'
    name = 'Second Tuple2'
    nodeid = 'org.sysess.sympathy.tuple.secondtuple2'
    icon = 'second.svg'

    inputs = Ports([
        Port.Custom('(<a>, <b>)', 'Tuple2')])

    outputs = Ports([
        Port.Custom('<b>', 'Second')])

    def execute(self, node_context):
        node_context.output[0].source(node_context.input[0][1], shallow=True)
