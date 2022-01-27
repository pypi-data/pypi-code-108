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
import json

import numpy as np
import sys

from sympathy.api import node as synode
from sympathy.api import node_helper
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions
from sympathy.platform import parameter_helper_gui
from sympathy.utils.context import reraise
from sylib.util import base_eval


class CreateParameters(synode.Node):
    """
    Manually Create a Sympathy parameter structure by writing a python
    expression which modifies the parameters variable using the sympathy
    parameter api (same class as nodes use to create their parameters).

    Example:

    .. code-block:: python

        parameters.set_integer(
            'number',
            description='Description of the number parameter.',
            value=1)
        parameters.set_string(
            'string',
            description='Description of the string parameter.',
            value="1")
        parameters.set_integer(
            'bounded_number',
            label='Bounded number',
            description='Description of the bounded_nummber parameter.',
            value=0,
            editor=synode.editors.bounded_lineedit_editor(
                0, 4))

    In order to create editors and doing some other operations, synode
    is defined when the code is evaluated.

    Optional input port, named arg, can be used in the code. Have a look
    at the :ref:`Data type APIs<datatypeapis>` to see what methods and
    attributes are available on the data type that you are working with.

    The Evaluation context contains *parameters* of type ParameterRoot,
    *synode* - which is the module obtained from sympathy.api.node, and
    optionally *arg* which is a sympathy datatype subclass of TypeAlias or
    sybase (builtin).
    """
    name = 'Create JSON Parameters'
    author = 'Erik der Hagopian'
    version = '0.1'
    icon = 'create_json.svg'
    tags = Tags(Tag.Generic.Configuration)
    nodeid = 'org.sysess.sympathy.create.createparameters'
    inputs = Ports([Port.Custom('<a>', 'Input',
                                name='arg', n=(0, 1))])
    outputs = Ports([Port.Json('Output', name='output')])

    parameters = synode.parameters()
    parameters.set_string(
        'code',
        label='Parameters:',
        description='Python code that modifies the parameter structure.',
        value='',
        editor=synode.Util.code_editor().value())

    def execute(self, node_context):
        inputs = node_context.input.group('arg')
        arg = inputs[0] if inputs else None
        parameters = synode.parameters()
        env = {'arg': arg, 'synode': synode, 'parameters': parameters}
        try:
            base_eval(node_context.parameters['code'].value, env, mode='exec')
        except Exception:
            raise exceptions.SyUserCodeError(
                sys.exc_info(),
                'Error evaluating parameters, see underlying cause.')
        node_context.output[0].set(parameters._parameter_dict)


class ConfigureJsonParameters(synode.Node):
    """
    Configure JSON parameters.

    The input parameters are likely created by
    :ref:`Create JSON Parameters` and follows the serialization
    format used for Sympathy parameters.

    .. warning::

      The intended scope for this node, and where it will be most useful, is to
      produce static configurations. To allow configuring a set of parameters
      with static options. All the basic parameter types can be used so long
      as the choices are not intended to be dynamic and built from input data.

      For dynamic cases, where choices depend on input data, we instead
      recommend that you create a new library node. Add the parameters that
      you need and then add the Configuration output port to the node.
      If you also want to exclude it from the list of library nodes, set:

      .. code-block:: python

          tags = Tags(Hidden.Gui)

      to exclude it from the library.

    The node stores configured changes and uses them to modify the parameter
    structure from the input port.

    When data from the input port is unavailable, the stored parameters will
    be used in full.

    Execute simply outputs the resulting parameters as JSON, and by adding the
    optional output *Table Parameters*, scalar parameters from the output can
    be made available in a flat (single row) table.
    """
    name = 'Configure JSON Parameters'
    author = 'Erik der Hagopian'
    version = '0.1'
    icon = 'create_json.svg'
    tags = Tags(Tag.Generic.Configuration)

    nodeid = 'org.sysess.sympathy.create.configureparameters'
    inputs = Ports([Port.Json('Json Parameters',
                              name='json_parameters')])
    outputs = Ports(
        [Port.Json('Json Parameters',
                   name='json_parameters'),
         Port.Custom('table', 'Table Parameters',
                     name='table_parameters', n=(0, 1, 0))])
    parameters = synode.parameters()

    @classmethod
    def _update(cls, param, data):
        if param:
            if param['type'] in ['group', 'page']:
                for k, v in data.items():
                    param_ = param.get(k)
                    if param_ and isinstance(param_, dict):
                        cls._update(param_, v)
            else:
                refresh = [
                    'type', 'order', 'label', 'description', 'editor']

                if param['type'] == 'list':
                    refresh.extend(['list', 'value'])
                    list_ = list(param.get('list', []))
                    value = []
                    try:
                        value_names = data['value_names']
                        value = [list_.index(v) for v in value_names if v in list_]
                    except Exception:
                        pass
                    param['value'] = value
                    param['list'] = list_

                for k, v in data.items():
                    if k not in refresh:
                        param[k] = v

    @classmethod
    def _prune(cls, param):
        def prune_names(param):
            return set(param).difference(
                ['editor', 'order', 'description'])

        if not isinstance(param, dict):
            return param
        elif param['type'] in ['group', 'page']:
            return {k: cls._prune(param[k]) for k in prune_names(param.keys())}
        else:
            return {k: param[k] for k in prune_names(param.keys())}

    def _updated_parameters(self, node_context):
        parameters = node_context.parameters
        try:
            port_parameters_data = node_context.input[
                'json_parameters'].get()
        except exceptions.NoDataError:
            # Keep stored parameters.
            pass
        else:
            # Update port_parameters with stored parameters and
            # store updated parameters.
            port_parameters = synode.parameters(port_parameters_data)
            self._update(
                port_parameters._parameter_dict, parameters._parameter_dict)
            parameters._parameter_dict.clear()
            parameters._parameter_dict.update(port_parameters._parameter_dict)
            parameters = port_parameters
        return parameters

    def exec_parameter_view(self, node_context):
        parameters = self._updated_parameters(node_context)
        gui = parameters.gui()
        return gui

    def execute(self, node_context):

        def flat_parameter_values(parameter_dict):
            def inner(param, name):
                if param['type'] in ['group', 'page']:
                    for k, v in param.items():
                        param_ = param.get(k)
                        if param_ and isinstance(param_, dict):
                            inner(param_, k)
                else:
                    for k, v in param.items():
                        if k == 'value':
                            res[name] = v
            res = {}
            inner(parameter_dict, None)
            return sorted(res.items())

        parameters = self._updated_parameters(node_context)
        json_parameters = node_context.output.group('json_parameters')
        table_parameters = node_context.output.group('table_parameters')
        if json_parameters:
            json_parameters[0].set(self._prune(parameters._parameter_dict))
        if table_parameters:
            for key, value in flat_parameter_values(parameters._parameter_dict):
                table_parameters[0][key] = np.array([value])


class CreateJSON(synode.Node):
    """
    Manually Create JSON by writing a python expression which evaluates
    to a dictionary containing normal python values, that is, dictionaries
    lists, floats, integers, strings and booleans.

    Optional input port, named arg, can be used in the expression. Have a look
    at the :ref:`Data type APIs<datatypeapis>` to see what methods and
    attributes are available on the data type that you are working with.
    """

    name = 'Create JSON'
    author = 'Erik der Hagopian'
    version = '0.1'
    icon = 'create_json.svg'
    tags = Tags(Tag.Generic.Configuration)

    nodeid = 'org.sysess.sympathy.create.createjson'
    inputs = Ports([Port.Custom('<a>', 'Input',
                                name='arg', n=(0, 1))])
    outputs = Ports([Port.Json('Output', name='output')])

    parameters = synode.parameters()
    parameters.set_string(
        'code',
        description='Python expression that evaluates to a '
                    'json-serilizable object.',
        value='{}  # Empty dictionary.',
        editor=synode.Util.code_editor().value())

    def execute(self, node_context):
        inputs = node_context.input.group('arg')
        arg = inputs[0] if inputs else None
        env = {'arg': arg}
        dict_ = base_eval(node_context.parameters['code'].value, env)
        node_context.output[0].set(dict_)


class JSONtoText(synode.Node):
    """
    JSON to Text.
    """

    name = 'JSON to Text'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'create_json.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    nodeid = 'org.sysess.sympathy.convert.jsontotext'
    inputs = Ports([Port.Json('Input', name='input')])
    outputs = Ports([Port.Text('Output', name='output')])

    parameters = synode.parameters()

    def execute(self, node_context):
        node_context.output[0].set(
            json.dumps(node_context.input[0].get()))


class TexttoJSON(synode.Node):
    """
    Text to JSON.
    """

    name = 'Text to JSON'
    author = 'Erik der Hagopian'
    version = '1.0'
    icon = 'create_json.svg'
    tags = Tags(Tag.DataProcessing.Convert)

    nodeid = 'org.sysess.sympathy.convert.texttojson'
    inputs = Ports([Port.Text('Input', name='input')])
    outputs = Ports([Port.Json('Output', name='output')])

    parameters = synode.parameters()

    def execute(self, node_context):
        text = node_context.input[0].get()
        try:
            data = json.loads(text)
        except json.decoder.JSONDecodeError as e:
            raise exceptions.SyDataError(
                f'Unsupported json content in text. {e}.'
            )
        node_context.output[0].set(data)


@node_helper.list_node_decorator(['input'], ['output'])
class TextstoJSONs(TexttoJSON):
    name = 'Texts to JSONs'
    nodeid = 'org.sysess.sympathy.convert.textstojsons'
