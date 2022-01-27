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
from distutils.version import LooseVersion

import sklearn
import sklearn.svm

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class SupportVectorClassifier(SyML_abstract, node.Node):
    name = 'Support Vector Classifier'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'svm.svg'
    description = 'Support vector machine (SVM) based classifier'
    nodeid = 'org.sysess.sympathy.machinelearning.svc'
    tags = Tags(Tag.MachineLearning.Supervised)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [
            "Model",
            {'name': 'C',
             'dispname': 'Penalty parameter C',
             'type': FloatType(min_value=0.0, default=1.0)},
            {'name': 'kernel',
             'dispname': 'Kernel',
             'type': StringSelectionType([
                  'rbf', 'linear', 'poly', 'sigmoid', 'precomputed'],
                default='rbf')},
        ],
        [
            "Advanced",
            {'name': 'degree',
             'dispname': 'Polynomial kernel degree',
             'type': IntType(min_value=1, default=3)},
            {'name': 'gamma',
             'dispname': 'Kernel coefficient',
             'type': UnionType([
                 FloatType(), StringSelectionType(['auto'])],
                default='auto')},
            {'name': 'coef0',
             'dispname': 'Independent kernel function term',
             'type': FloatType(default=0.0)},
            {'name': 'probability',
             'dispname': 'Enable probability estimates',
             'type': BoolType(default=False)},
            {'name': 'shrinking',
             'dispname': 'Use shrinking heuristic',
             'type': BoolType(default=True)},
            {'name': 'class_weight',
             'dispname': 'Class weight',
             'type': UnionType([NoneType(), StringSelectionType(['balanced'])],
                               default=None)},

        ],
        [
            "Solver",
            {'name': 'tol',
             'dispname': 'Tolerance',
             'type': FloatType(default=1e-3)},
            {'name': 'max_iter',
             'dispname': 'Hard iteration limit',
             'type': IntType(min_value=-1)},
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([IntType(), NoneType()], default=None)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.svm.SVC)

    descriptor.set_attributes([
        {'name': 'support_', },
        {'name': 'support_vectors_', 'cnames': names_from_x},
        {'name': 'n_support_'},
        {'name': 'dual_coef_'},
        {'name': 'coef_', 'cnames': names_from_x},
        {'name': 'intercept_'},
    ], doc_class=sklearn.svm.SVC)

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
        skl = sklearn.svm.SVC(**kwargs)

        model.set_skl(skl)
        model.save()


def _one_class_svm_info():
    model_info = [
        "Model",
        {'name': 'kernel',
         'dispname': 'Kernel',
         'type': StringSelectionType(
             ['rbf', 'linear', 'poly', 'sigmoid', 'precomputed'],
             default='rbf')},
        {'name': 'nu',
         'dispname': 'Upper/lower fraction bound',
         'type': FloatType(min_value=0, max_value=1, default=0.5)},
    ]
    advanced_info = [
        "Advanced",
        {'name': 'degree',
         'dispname': 'Polynomial kernel degree',
         'type': IntType(min_value=1, default=3)},
        {'name': 'gamma',
         'dispname': 'Kernel coefficient',
         'type': UnionType([
             FloatType(), StringSelectionType(['auto'])],
                           default='auto')},
        {'name': 'coef0',
         'dispname': 'Independent kernel function term',
         'type': FloatType(default=0.0)},
        {'name': 'shrinking',
         'dispname': 'Use shrinking heuristic',
         'type': BoolType(default=True)},
    ]
    solver_info = [
        "Solver",
        {'name': 'tol',
            'dispname': 'Tolerance',
            'type': FloatType(default=1e-3)},
        {'name': 'max_iter',
            'dispname': 'Hard iteration limit',
            'type': IntType(min_value=-1)},
    ]

    # Earlier versions of sklearn and sympathy supported the random_state
    # parameter. It is deprecated and ignored in sklearn>=0.20 and removed in
    # sklearn>=0.22.
    if LooseVersion(sklearn.__version__) < LooseVersion('0.20'):
        solver_info.append({
            'name': 'random_state',
            'dispname': 'Random seed',
            'type': UnionType([IntType(), NoneType()], default=None),
        })

    return [model_info, advanced_info, solver_info]


class OneClassSVM(SyML_abstract, node.Node):
    name = 'One Class Support Vector Machines'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'outliers.svg'
    description = (
        'Unsupervised outlier detection based on support vector machines'
    )
    nodeid = 'org.sysess.sympathy.machinelearning.one_class_svm'
    tags = Tags(Tag.MachineLearning.Unsupervised)

    descriptor = Descriptor()
    descriptor.name = name
    info = _one_class_svm_info()

    descriptor.set_info(info, doc_class=sklearn.svm.OneClassSVM)

    descriptor.set_attributes([
        {'name': 'support_', },
        {'name': 'support_vectors_', 'cnames': names_from_x},
        {'name': 'dual_coef_'},
        {'name': 'coef_', 'cnames': names_from_x},
        {'name': 'intercept_'},
    ], doc_class=sklearn.svm.OneClassSVM)

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
        skl = sklearn.svm.OneClassSVM(**kwargs)

        model.set_skl(skl)
        model.save()
