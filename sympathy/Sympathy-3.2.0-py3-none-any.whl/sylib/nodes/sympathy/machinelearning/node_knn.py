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
import sklearn.neighbors

from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import StringType
from sylib.machinelearning.model import ModelPort
from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags


class KNeighborsClassifier(SyML_abstract, node.Node):
    name = 'k-Nearest Neighbors Classifier'
    author = 'Alexander Aschikhin'
    version = '0.1'
    icon = 'knn.svg'
    description = 'Classifier based on the k-nearest neighbors algorithm'
    nodeid = 'org.sysess.sympathy.machinelearning.knn'
    tags = Tags(Tag.MachineLearning.Supervised)

    inputs = Ports([])
    outputs = Ports([ModelPort('Output model', name='out-model')])

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [
            'Model',
            {'name': 'n_neighbors',
             'dispname': 'Number of neighbors',
             'type': IntType(min_value=1, default=5)},
            {'name': 'weights',
             'dispname': 'Weights',
             'type': StringSelectionType(['uniform', 'distance'], default='uniform')},
            {'name': 'algorithm',
             'dispname': 'Algorithm',
             'type': StringSelectionType(['ball_tree', 'kd_tree', 'brute', 'auto'], default='auto')},
        ],
        [
            'Advanced options',
            {'name': 'leaf_size',
             'dispname': 'Leaf size (for ball_tree or kd_tree)',
             'type': IntType(min_value=1, default=30)},
            {'name': 'metric',
             'dispname': 'Metric',
             'type': StringType(default='minkowski')},
            {'name': 'p',
             'dispname': 'Power parameter for the Minkowski metric',
             'type': IntType(default=2)},
        ],
        [
            'Solver',
            {'name': 'n_jobs',
             'dispname': 'Number of jobs',
             'type': IntType(min_value=-1, default=1)},
        ]
    ]


    descriptor.set_info(info, doc_class=sklearn.neighbors.KNeighborsClassifier)

    descriptor.set_attributes([], doc_class=sklearn.neighbors.KNeighborsClassifier)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    __doc__ = SyML_abstract.generate_docstring(
        description, descriptor.info, descriptor.attributes, inputs, outputs)

    def execute(self, node_context):
        model = node_context.output['out-model']
        desc = self.__class__.descriptor
        model.set_desc(desc)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        #ap = kwargs.pop('additional_params')
        skl = sklearn.neighbors.KNeighborsClassifier(**kwargs)

        model.set_skl(skl)
        model.save()
