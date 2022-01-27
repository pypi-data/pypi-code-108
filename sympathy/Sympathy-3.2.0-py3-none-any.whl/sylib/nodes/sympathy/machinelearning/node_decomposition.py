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
import sklearn.decomposition
import sklearn.cross_decomposition

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags
from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.utility import names_from_y
from sylib.machinelearning.utility import names_from_prefix
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class PrincipalComponentAnalysis(SyML_abstract, node.Node):
    name = 'Principal Component Analysis (PCA)'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'PCA.svg'
    description = (
        'Linear dimensionality reduction using Singular Value Decomposition '
        'of the data to project it to a lower dimensional space.')
    nodeid = 'org.sysess.sympathy.machinelearning.pca'
    tags = Tags(Tag.MachineLearning.DimensionalityReduction)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
            {'name': 'n_components',
             'dispname': 'Number of components to keep', 
             'type': UnionType([IntType(min_value=1), 
                               FloatType(min_value=0, max_value=1), 
                               StringSelectionType(['mle'])], default=1)},
            {'name': 'svd_solver',
             'dispname': 'Solver',
             'type': StringSelectionType(
                 ['auto', 'full', 'arpack', 'randomized'], default='auto')},
            {'name': 'tol',
             'dispname': 'Tolerance for singular values',
             'type': FloatType(default=0.0)},
            {'name': 'iterated_power',
             'dispname': 'N. of iteratins (for randomized solver)',
             'type': UnionType(
                 [IntType(min_value=0), StringSelectionType(['auto'])],
                 default='auto')},
            {'name': 'whiten',
             'dispname': 'Whiten',
             'type': BoolType(default=False)},
    ]

    descriptor.set_info(info, doc_class=sklearn.decomposition.PCA)

    descriptor.set_attributes([
        {'name': 'components_', 'cnames': names_from_x},
        {'name': 'explained_variance_'},
        {'name': 'explained_variance_ratio_'},
        {'name': 'mean_', 'cnames': names_from_x},
        {'name': 'n_components_'},
        {'name': 'noise_variance_'},
    ], doc_class=sklearn.decomposition.PCA)

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
        skl = sklearn.decomposition.PCA(**kwargs)

        model.set_skl(skl)
        model.save()


class KernelPCA(SyML_abstract, node.Node):
    name = 'Kernel Principal Component Analysis (KPCA)'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'PCA.svg'
    description = (
        'Non-linear dimensionality reduction through the use of kernels')
    nodeid = 'org.sysess.sympathy.machinelearning.kpca'
    tags = Tags(Tag.MachineLearning.DimensionalityReduction)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [
            "Model options",
            {'name': 'n_components',
             'dispname': 'Number of components',
             'type': UnionType(
                 [IntType(min_value=1), NoneType()], default=None)},
            {'name': 'kernel',
             'dispname': 'Kernel',
             'type': StringSelectionType(
                 ['linear', 'poly', 'rbf', 'sigmoid', 'cosine', 'precomputed'],
                 default='linear')},
            {'name': 'fit_inverse_transform',
             'dispname': 'Fit inverse-transform',
             'type': BoolType(default=False)},
        ],
        [
            "Advanced options",
            {'name': 'degree',
             'dispname': 'Poly kernel degree',
             'type': IntType(min_value=1, default=3)},
            {'name': 'gamma',
             'dispname': 'Kernel coefficient (poly, rbf, sigmoid)',
             'type': UnionType([
                 FloatType(min_value=0.0), NoneType()], default=None)},
            {'name': 'coef0',
             'dispname': 'Independent term (poly, sigmoid)',
             'type': FloatType(min_value=0.0, default=1)},
            {'name': 'alpha',
             'dispname': 'Ridge regression hyperparameter',
             'type': FloatType(min_value=0.0, default=1)},
            {'name': 'remove_zero_eig',
             'dispname': 'Remove components with zero eigenvalue',
             'type': BoolType(default=False)},
        ],
        [
            "Solver",
            {'name': 'eigen_solver',
             'dispname': 'Eigensolver',
             'type': StringSelectionType([
                 'auto', 'dense', 'arpack'], default='auto')},
            {'name': 'tol',
             'dispname': 'Tolerance',
             'type': FloatType(default=0.0)},
            {'name': 'max_iter',
             'dispname': 'Max iteratins',
             'type': UnionType([IntType(min_value=1), NoneType()], default=None)},
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([NoneType(), IntType()], default=None)},
            {'name': 'n_jobs',
             'dispname': 'number of jobs',
             'type': IntType(min_value=-1, default=1)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.decomposition.KernelPCA)

    descriptor.set_attributes([
        {'name': 'lambdas_'},
        {'name': 'alphas_'},
        {'name': 'dual_coef_', 'cnames': names_from_x},
        {'name': 'X_transformed_fit_'},
        {'name': 'X_fit_'},
    ], doc_class=sklearn.decomposition.KernelPCA)

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
        kwargs['copy_X'] = True
        skl = sklearn.decomposition.KernelPCA(**kwargs)

        model.set_skl(skl)
        model.save()


class PLSRegressionCrossDecomposition(SyML_abstract, node.Node):
    name = 'Partial Least Squares cross-decomposition (PLS regression)'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'PCA.svg'
    description = (
        'Finds the fundamental relations between two matrices X and Y, ie. '
        'it finds the (multidimensional) direction in X that best explains '
        'maximum multidimensional direction in Y. See also PCA-analysis')
    nodeid = 'org.sysess.sympathy.machinelearning.pls'
    tags = Tags(Tag.MachineLearning.DimensionalityReduction)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
            {'name': 'n_components',
            'dispname': 'Number of components to keep', 
            'type': IntType(min_value=1, default=2)},
            {'name': 'scale',
            'dispname': 'Scale the data', 
             'type': BoolType(default=True)},
            {'name': 'max_iter',
            'dispname': 'Max iterations', 
             'type': IntType(min_value=1, default=500)},
            {'name': 'tol',
            'dispname': 'Tolerance', 
             'type': FloatType(default=0.0)},
    ]

    descriptor.set_info(info, doc_class=sklearn.cross_decomposition.PLSRegression)

    descriptor.set_attributes([
        {'name': 'x_weights_',
         'rnames': names_from_x,
         'cnames': names_from_prefix('component ')},
        {'name': 'y_weights_',
         'rnames': names_from_y,
         'cnames': names_from_prefix('component ')},
        {'name': 'x_loadings_',
         'rnames': names_from_x,
         'cnames': names_from_prefix('component ')},
        {'name': 'y_loadings_',
         'rnames': names_from_y,
         'cnames': names_from_prefix('component ')},
        {'name': 'x_scores_',
         'cnames': names_from_prefix('component ')},
        {'name': 'y_scores_',
         'cnames': names_from_prefix('component ')},
        {'name': 'x_rotations_',
         'rnames': names_from_x,
         'cnames': names_from_prefix('component ')},
        {'name': 'y_rotations_',
         'rnames': names_from_y},
        {'name': 'coef_'},
        {'name': 'n_iter_'},
    ], doc_class=sklearn.cross_decomposition.PLSRegression)

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
        skl = sklearn.cross_decomposition.PLSRegression(**kwargs)

        model.set_skl(skl)
        model.save()
