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

import numpy as np
import sklearn

from sympathy.api import node
from sympathy.api.nodeconfig import Port
from sympathy.api.nodeconfig import Ports
from sympathy.api.nodeconfig import Tag
from sympathy.api.nodeconfig import Tags
from sympathy.api.exceptions import SyDataError
from sympathy.api.exceptions import sywarn

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract


class ExtractParameters(node.Node):
    name = 'Extract Parameters'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'attributes.svg'
    description = (
        'Extracts a table with current hyper-parameter values of model')
    nodeid = 'org.sysess.sympathy.machinelearning.extract_parameters'
    tags = Tags(Tag.MachineLearning.HyperParameters)

    inputs = Ports([ModelPort('Input model', 'model')])
    outputs = Ports([Port.Table('Parameters', name='parameters')])
    __doc__ = SyML_abstract.generate_docstring2(
        description, [], inputs, outputs)

    def execute(self, node_context):
        in_model = node_context.input['model']
        out_tbl = node_context.output['parameters']

        in_model.load()
        skl = in_model.get_skl()
        desc = in_model.get_desc()
        if skl is None:
            raise SyDataError("Invalid model type in input data")
        skl_params = skl.get_params()
        for name, info in desc.parameters.items():
            skl_name = info['skl_name']
            if skl_name not in skl_params:
                continue
            value = skl_params[skl_name]
            out_tbl.set_column_from_array(
                name, np.array([info['type'].to_string(value)]))


class SetParameters(node.Node):
    name = 'Set Parameters'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'set_params.svg'
    description = """Sets the model hyper parameters based on table data"""
    nodeid = 'org.sysess.sympathy.machinelearning.set_parameters'
    tags = Tags(Tag.MachineLearning.HyperParameters)

    inputs = Ports([ModelPort('Input model', 'in-model'),
                    Port.Table('Parameters', name='parameters')])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    parameters = node.parameters()
    parameters.set_boolean(
        'copy_through', value=True, label='Copy model parameters',
        description=(
            'Keeps the model parameters that are not overwritten by the input'
            'table. Otherwise default values are used.'))
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        in_model = node_context.input['in-model']
        in_tbl = node_context.input['parameters']
        out_model = node_context.output['out-model']
        copy_through = node_context.parameters['copy_through'].value

        out_model.source(in_model)
        out_model.load()
        skl = out_model.get_skl()
        desc = out_model.get_desc()
        if skl is None or not isinstance(skl, sklearn.base.BaseEstimator):
            raise SyDataError("Invalid model type in input data")
        if copy_through:
            skl_params = skl.get_params()
        else:
            skl_params = {}
        for name in in_tbl.column_names():
            if name not in desc.parameters:
                sywarn('Table column {0} is not a hyper parameter '
                       'for this model type'.format(name))
            info = desc.parameters[name]
            skl_params[info['skl_name']] = (
                info['type'].from_string(in_tbl.get_column_to_array(name)[0]))
        if not copy_through:
            for name, info in desc.parameters.items():
                if name not in in_tbl.column_names():
                    skl_params[info['skl_name']] = info['type'].default

        skl.set_params(**skl_params)
        out_model.set_skl(skl)
        out_model.save()


class SetNames(node.Node):
    name = 'Set Input and Output Names'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'set_names.svg'
    description = (
        'Sets the name of the inputs and outputs columns of this model')
    nodeid = 'org.sysess.sympathy.machinelearning.set_x_names'
    tags = Tags(Tag.MachineLearning.Apply)

    inputs = Ports([ModelPort('Input model', 'in-model')])
    outputs = Ports([ModelPort('Output model', 'out-model')])
    parameters = node.parameters()
    parameters.set_string(
        'input_names', label='Input names', value="X0|X1|X2",
        description='List of names for features separated by the | character.'
        'All whitespace is included in the final name. If empty then no '
        'names are set.')
    parameters.set_string(
        'output_names', label='Output names', value="Y0",
        description=(
            'List of names for target separated by the | character. '
            'All whitespace is included in the final name. If empty then '
            'no names are set.'))
    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        in_model = node_context.input['in-model']
        out_model = node_context.output['out-model']
        in_names = node_context.parameters['input_names'].value
        out_names = node_context.parameters['output_names'].value

        out_model.source(in_model)
        out_model.load()
        if in_names != "":
            out_model.get_desc().set_x_names(in_names.split('|'))
        if out_names != "":
            out_model.get_desc().set_y_names(out_names.split('|'))
        out_model.save()


class ParameterDistribution(node.Node):
    name = 'Parameter Distribution'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'parameter_distribution.svg'
    description = (
        'Creates a range of values giving a distribution for a parameter')
    nodeid = 'org.sysess.sympathy.machinelearning.parameter_distribution'
    tags = Tags(Tag.MachineLearning.HyperParameters)

    inputs = Ports([])
    outputs = Ports([Port.Table('Output', 'out')])
    parameters = node.parameters()
    parameters.set_string(
        'name', value='N', label='Parameter Name:',
        description='Name of generated column / parameter')
    parameters.set_float(
        'min', value=0.0, label='Minimum',
        description='Lower value in range')
    parameters.set_float(
        'max', value=1.0, label='Maximum',
        description='Upper value in range')
    parameters.set_integer(
        'N', value=10, label='Number of points',
        description='Number of point to generate / to sample')
    parameters.set_string(
        'method', value='linear', label='Distribution',
        description='Type of distribution',
        editor=node.Util.combo_editor(options=[
            'linear', 'exponential',
            ]).value())
    parameters.set_boolean(
        'as_integer', value=False, label='as integer',
        description=(
            'Forces output to be integers. Removes redundant sample points'))

    __doc__ = SyML_abstract.generate_docstring2(
        description, parameters, inputs, outputs)

    def execute(self, node_context):
        out = node_context.output['out']

        N = node_context.parameters['N'].value
        name = node_context.parameters['name'].value
        method = node_context.parameters['method'].value
        min_value = node_context.parameters['min'].value
        max_value = node_context.parameters['max'].value
        as_integer = node_context.parameters['as_integer'].value

        if method == 'linear':
            arr = np.linspace(min_value, max_value, N)
        elif method == 'exponential':
            arr = np.geomspace(min_value, max_value, N)
        else:
            raise SyDataError('Invalid method selected')

        if as_integer:
            arr = np.array(np.round(arr), dtype=int)
            arr = np.unique(arr)

        out.set_column_from_array(name, arr)
        out.set_name('parameter')
