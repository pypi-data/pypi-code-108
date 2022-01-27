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
import sklearn
import sklearn.neural_network

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.neuralnetwork import MLPClassifierDescriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class MLPRegressor(SyML_abstract, node.Node):
    name = 'Multi-Layer Perceptron Regressor'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'neuralnetwork.svg'
    description = 'Multi-layer perceptron regressor'
    nodeid = 'org.sysess.sympathy.machinelearning.mlp_regressor'
    tags = Tags(Tag.MachineLearning.Supervised)

    descriptor = MLPClassifierDescriptor()
    descriptor.name = name
    info = [
        [
            "Architecture",
            {'name': 'max_iter',
             'dispname': 'Maximum iterations',
             'type': IntType(default=200, min_value=0)},
            {'name': 'hidden_layer_sizes',
             'dispname': 'Hidden layer number and sizes',
             'type': IntListType(default=[100], min_value=1)},
            {'name': 'activation',
             'dispname': 'Activation Function',
             'type': StringSelectionType([
                 'identity', 'logistic', 'tanh', 'relu'], default='relu')},
        ],
        [
            "Solving methods",
            {'name': 'solver',
             'dispname': 'Solver',
             'type': StringSelectionType([
                 'lbfgs', 'sgd', 'adam'], default='adam')},
            {'name': 'batch_size',
             'dispname': 'Batch size',
             'type': UnionType([
                 IntType(min_value=1),
                 StringSelectionType(['auto'])
             ], default='auto')},
            {'name': 'learning_rate',
             'dispname': 'Learning rate',
             'type': StringSelectionType([
                 'constant', 'invscaling', 'adaptive'
             ])},
            {'name': 'shuffle',
             'dispname': 'Shuffle samples',
             'type': BoolType(default=True)},
            {'name': 'early_stopping',
             'dispname': 'Use early stopping',
             'type': BoolType(default=False)},
            {'name': 'validation_fraction',
             'dispname': 'Validation fraction',
             'type': FloatType(default=0.1, min_value=0.0, max_value=1.0)},
        ],
        [
            "Solver parameters",
            {'name': 'alpha',
             'dispname': 'Alpha',
             'type': FloatType(default=1e-5, min_value=0.0)},
            {'name': 'tol',
             'dispname': 'Tolerance',
             'type': FloatType(default=1e-4, min_value=0.0)},
            {'name': 'learning_rate_init',
             'dispname': 'Initial learning rate',
             'type': FloatType(default=1e-3, min_value=0.0)},
            {'name': 'power_t',
             'dispname': 'Inverse scaling learning rate exponent',
             'type': FloatType(default=0.5, min_value=0.0)},
            {'name': 'momentum',
             'dispname': 'Momentum',
             'type': FloatType(default=0.9, min_value=0.0, max_value=1.0)},
            {'name': 'nesterovs_momentum',
             'dispname': "Use Nesterov's momentum",
             'type': BoolType(default=True)},
            {'name': 'beta_1',
             'dispname': 'First moment vector decay rate',
             'type': FloatType(default=0.9, min_value=0.0, max_value=1.0)},
            {'name': 'beta_2',
             'dispname': 'Second moment vector decay rate',
             'type': FloatType(default=0.999, min_value=0.0, max_value=1.0)},
            {'name': 'epsilon',
             'dispname': 'Numberical stability',
             'type': FloatType(default=1e-8, min_value=0.0)},
        ],
        [
            "Model state",
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([NoneType(), IntType()], default=None)},
            {'name': 'warm_start',
             'dispname': 'Warm start',
             'type': BoolType(default=False)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.neural_network.MLPRegressor)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'loss_', 'coefs_', 'intercepts_', 'n_iter_',
            'n_layers_', 'n_outputs_', 'out_activation_',
        ]], doc_class=sklearn.neural_network.MLPRegressor)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([])
    outputs = Ports([ModelPort('Model', 'model')])
    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        model = node_context.output['model']
        desc = self.__class__.descriptor
        model.set_desc(desc)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        skl = sklearn.neural_network.MLPRegressor(**kwargs)

        model.set_skl(skl)
        model.save()
