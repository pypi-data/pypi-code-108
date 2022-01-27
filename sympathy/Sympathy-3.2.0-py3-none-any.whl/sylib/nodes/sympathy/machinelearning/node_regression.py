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
import sklearn.linear_model
import sklearn.kernel_ridge

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.utility import names_from_y
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class LinearRegression(SyML_abstract, node.Node):
    name = 'Linear Regression'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'linear_regression.svg'
    description = 'Ordinary linear regression'
    nodeid = 'org.sysess.sympathy.machinelearning.linearregression'
    tags = Tags(Tag.MachineLearning.Regression)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        {'name': 'fit_intercept',
         'dispname': 'Fit intercept',
         'type': BoolType(default=True)},
        {'name': 'normalize',
         'dispname': 'Normalize regressors',
         'type': BoolType(default=False)},
        {'name': 'n_jobs',
         'dispname': 'Number of jobs',
         'type': IntType(min_value=1, default=1)},
    ]

    descriptor.set_info(info, doc_class=sklearn.linear_model.LinearRegression)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'coef_', 'intercept_', 'residues_',
        ]], doc_class=sklearn.linear_model.LinearRegression)

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
        skl = sklearn.linear_model.LinearRegression(**kwargs)

        model.set_skl(skl)
        model.save()


class LogisticRegression(SyML_abstract, node.Node):
    name = 'Logistic Regression'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'logistic_regression.svg'
    description = 'Logistic regression of a categorical dependent variable'
    nodeid = 'org.sysess.sympathy.machinelearning.logisticregression'
    tags = Tags(Tag.MachineLearning.Supervised)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [   
            'Options',
            {'name': 'penalty',
             'dispname': 'Penalty',
             'type': StringSelectionType(['l1', 'l2'], default='l2')},
            {'name': 'dual',
             'dispname': 'Dual Formulation',
             'type': BoolType(default=False)},
            {'name': 'C',
             'dispname': 'C',
             'type': FloatType(min_value=0, default=1.0)},
            {'name': 'fit_intercept',
             'dispname': 'Fit intercept',
             'type': BoolType(default=True)},
            {'name': 'intercept_scaling',
             'dispname': 'Intercept scaling',
             'type': FloatType(default=1.0)},
            {'name': 'class_weight',
             'dispname': 'Class weights',
             'type': UnionType([
                 NoneType(), StringSelectionType(['balanced'])], default=None)},
            {'name': 'tol',
             'dispname': 'Tolerance',
             'type': FloatType(default=1e-4)},
            {'name': 'multi_class',
             'dispname': 'Multiclass',
             'type': StringSelectionType(['ovr', 'multinomial'], default='ovr')}
        ],
        [   
            'Solver',
            {'name': 'max_iter',
             'dispname': 'Maximum iterations',
             'type': IntType(min_value=0, default=100)},
            {'name': 'solver',
             'dispname': 'Solver',
             'type': StringSelectionType(
                 ['newton-cg', 'lbfgs', 'liblinear', 'sag'],
                 default='liblinear')},
            {'name': 'n_jobs',
             'dispname': 'Number of jobs',
             'desc': (
                 'Number of CPU cores used when parallelizing over classes if '
                 'multi_class="ovr". Ignored when the solver is set to '
                 '"liblinear" regardless of multi_class. If given -1 then all '
                 'cores are used'),
             'type': IntType(min_value=-1, default=1)}
        ],
        [   
            'Model state',
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([NoneType(), IntType()], default=None)},
            {'name': 'warm_start',
             'dispname': 'Warm start',
             'type': BoolType(default=False)}
        ],
    ]

    descriptor.set_info(info, doc_class=sklearn.linear_model.LogisticRegression)

    descriptor.set_attributes([
        {'name': 'n_iter_'},
        {'name': 'coef_', 'cnames': names_from_x},
        {'name': 'intercept_'},
    ], doc_class=sklearn.linear_model.LogisticRegression)

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
        skl = sklearn.linear_model.LogisticRegression(**kwargs)

        model.set_skl(skl)
        model.save()


class KernelRidge(SyML_abstract, node.Node):
    name = 'Kernel Ridge Regression'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'kernel_ridge.svg'
    description = (
        'Kernel Ridge based classifier combining ridge regression '
        '(linear least-squares L2-norm) regression with the kernel trick')
    nodeid = 'org.sysess.sympathy.machinelearning.kernel_ridge'
    tags = Tags(Tag.MachineLearning.Regression)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [   
            "Model", 
            {'name': 'alpha',
             'dispname': 'Alpha',
             'type': FloatType(min_value=0, default=1.0)},
            {'name': 'kernel',
             'dispname': 'Kernel',
             'type': StringSelectionType(
                 ['linear', 'rbf', 'poly', 'sigmoid', 'cosine',
                  'laplacian', 'chi2'], default='rbf')},
        ],
        [   
            "Advanced",
            {'name': 'gamma',
             'dispname': 'Gamma',
             'type': UnionType([NoneType(), FloatType()], default=None)},
            {'name': 'coef0',
             'dispname': 'Zero coefficient',
             'type': FloatType(default=1.0)},
            {'name': 'degree',
             'dispname': 'Degree',
             'type': IntType(min_value=1, default=3)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.kernel_ridge.KernelRidge)

    descriptor.set_attributes([
        {'name': 'dual_coef_', 'cnames': names_from_y},
        {'name': 'X_fit_', 'cnames': names_from_x},
    ], doc_class=sklearn.kernel_ridge.KernelRidge)

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
        skl = sklearn.kernel_ridge.KernelRidge(**kwargs)

        model.set_skl(skl)
        model.save()


class SupportVectorRegression(SyML_abstract, node.Node):
    name = 'Epsilon Support Vector Regression'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'svm.svg'
    description = 'Support vector machine based regressor (SVR)'
    nodeid = 'org.sysess.sympathy.machinelearning.svr'
    tags = Tags(Tag.MachineLearning.Regression)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [   
            "Options",
             {'name': 'C',
              'dispname': 'Penalty',
              'type': FloatType(default=1.0)},
             {'name': 'kernel',
              'dispname': 'Kernel',
              'type': StringSelectionType(
                  ['linear', 'rbf', 'poly', 'sigmoid'], default='rbf')},
             {'name': 'epsilon',
              'dispname': 'Epsilon',
              'type': FloatType(default=0.1)},
        ],
        [   
            "Advanced",
             {'name': 'gamma',
              'dispname': 'Gamma',
              'type': UnionType([
                  StringSelectionType(['auto']), FloatType()], default='auto')},
             {'name': 'degree',
              'dispname': 'Polynomial Degree',
              'type': IntType(default=3)},
             {'name': 'coef0',
              'dispname': 'Independent term in kernel function',
              'type': FloatType(default=0.0)},
        ],
        [   
            "Solver",
              {'name': 'max_iter',
              'dispname': 'Maximum iterations',
              'type': IntType(default=-1)},
             {'name': 'tol',
              'dispname': 'Tolerance',
              'type': FloatType(default=1e-3)},
             {'name': 'shrinking',
              'dispname': 'Shrinking',
              'type': BoolType(default=True)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.svm.SVR)

    descriptor.set_attributes([
        {'name': 'support_', },
        {'name': 'support_vectors_', 'cnames': names_from_x},
        {'name': 'dual_coef_'},
        {'name': 'intercept_'},
        {'name': 'coef_', 'cnames': names_from_x},
    ], doc_class=sklearn.svm.SVR)

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
        skl = sklearn.svm.SVR(**kwargs)

        model.set_skl(skl)
        model.save()
