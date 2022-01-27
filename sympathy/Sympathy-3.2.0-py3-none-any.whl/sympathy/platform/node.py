# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
import sys

from . import basicnode as synode
from . parameter_helper import Editors
from .. utils.prim import combined_key
from .. utils.context import deprecated_method, deprecated_warn
from . controller import Controller, Field, Port
from .. platform import exceptions


managed_context = synode.managed_context
parameters = synode.sy_parameters
ParameterRoot = synode.ParameterRoot


class BasicNode(synode.BasicNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __init__.__doc__ = synode.BasicNode.__init__.__doc__


class Node(BasicNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._managed = True
        self._expanded = False

    __init__.__doc__ = synode.BasicNode.__init__.__doc__

    def _manual_context(self, node_context):
        # Rebuild input and output.
        close_handles = {
            'input': [
                value.close
                for value in node_context.input],
            'output': [
                value.close
                for value in node_context.output]}

        return (node_context, close_handles)

    # Methods to be overidden by user for manual node context management.
    @synode.original
    @managed_context
    def verify_parameters_basic(self, node_context):
        return self.verify_parameters(node_context)

    @managed_context
    def adjust_parameters_basic(self, node_context):
        return self.adjust_parameters(node_context)

    def update_parameters_basic(self, old_params):
        params = parameters(old_params)
        res = self.update_parameters(params)
        if isinstance(res, Exception):
            return res
        return params._parameter_dict

    @managed_context
    def execute_basic(self, node_context):
        try:
            self._beg_capture_text_streams(node_context)
            return self.execute(node_context)
        finally:
            self._end_capture_text_streams(node_context)

    def exec_parameter_view_basic(self, node_context):
        return self.exec_parameter_view(node_context)

    @managed_context
    def _execute_parameter_view(self, node_context, return_widget=False):
        return super(Node, self)._execute_parameter_view(
            node_context, return_widget)

    #   Methods to be overidden by user
    @synode.original
    def verify_parameters(self, node_context):
        return super(Node, self).verify_parameters_basic(node_context)

    def adjust_parameters(self, node_context):
        return super(Node, self).adjust_parameters_basic(node_context)

    def update_parameters(self, old_params):
        return super(Node, self).update_parameters_basic(old_params)

    def execute(self, node_context):
        return super(Node, self).execute_basic(node_context)

    def exec_parameter_view(self, node_context):
        return super(Node, self).exec_parameter_view_basic(node_context)


def adjust(parameter, sydata, kind=None, lists='all', **kwargs):
    """
    Helper function to standardize implementation of adjust_parameters.
    Possible kwargs depends on the actual sydata type.
    """
    def _names(sydata):
        try:
            names = sydata.names(kind, **kwargs)
        except (AttributeError, NotImplementedError):
            names = []
        return names

    names = []

    if sydata is not None and sydata.is_valid():
        # Primitive check for list types without isinstance.
        is_list = str(sydata.container_type).startswith('[')

        if is_list:
            # Special case handling for single list.
            if lists == 'all':
                names_set = set()
                for item in sydata:
                    names_set.update(_names(item))
                names = sorted(names_set, key=combined_key)
            elif lists == 'first':
                if len(sydata):
                    names = _names(sydata[0])
            elif lists == 'index':
                names = [str(i) for i in range(len(sydata))]
            else:
                assert False, (
                    'Unknown list handling: "{}" in adjust.'.format(
                        lists))
        else:
            names = _names(sydata)

    parameter.adjust(list(names))


controller = Controller
field = Field
port = Port
editors = Editors

# For backwards compatibility:
Util = Editors


def _set_child_progress_func(set_parent_progress, parent_value, factor):
    def inner(child_value):
        return set_parent_progress(
            parent_value + (child_value * factor / 100.))
    return inner


def map_list_node(func, input_list, output_list, set_progress):
    n_items = len(input_list)

    for i, input_item in enumerate(input_list):
        factor = 100. / n_items
        parent_progress = i * factor
        set_progress(parent_progress)
        set_child_progress = _set_child_progress_func(
            set_progress, parent_progress, factor)
        output_item = output_list.create()
        try:
            func(input_item, output_item, set_child_progress)
            output_list.append(output_item)
        except Exception:
            raise exceptions.SyListIndexError(i, sys.exc_info())

    set_progress(100)
