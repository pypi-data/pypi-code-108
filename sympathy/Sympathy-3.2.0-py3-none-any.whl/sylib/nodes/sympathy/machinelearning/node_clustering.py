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
import sklearn.cluster

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType

from distutils.version import LooseVersion
sklearn_version = LooseVersion(sklearn.__version__)


def _kmeans_clustering_info():
    # Test for deprecation of n_jobs and precomputed_distances arguments
    # (scikit-learn 0.23+)
    params_023 = sklearn_version >= LooseVersion('0.23.0')

    model_info = [
        "Model",
        {'name': 'n_clusters',
         'dispname': 'Number of clusters/centroids',
         'type': IntType(default=8)},
        {'name': 'n_init',
         'dispname': 'Number of runs',
         'type': IntType(default=10)},
        {'name': 'init',
         'dispname': 'Initialization method',
         'type': StringSelectionType(
             ['k-means++', 'random'], default='k-means++')},
        {'name': 'algorithm',
         'dispname': 'K-means algorithm',
         'type': StringSelectionType(
             ['auto', 'full', 'elkan'], default='auto')},
    ]

    solver_info = [
        "Solver",
        {'name': 'max_iter',
            'dispname': 'Maximum number of iterations',
            'type': IntType(default=300)},
        {'name': 'tol',
            'dispname': 'Tolerance',
            'type': FloatType(min_value=0, default=1e-4)},
    ]
    if not params_023:
        solver_info.extend([
            {'name': 'precompute_distances',
             'dispname': 'Precompute distances',
             'type': UnionType([
                 StringSelectionType(['auto']), BoolType()], default='auto')},
            {'name': 'n_jobs',
             'dispname': 'Number of jobs',
             'type': IntType(min_value=-1, default=1)},
        ])
    solver_info.append(
        {'name': 'random_state',
         'dispname': 'Random seed',
         'type': UnionType([NoneType(), IntType()], default=None)},
    )

    return [model_info, solver_info]


class KMeansClustering(SyML_abstract, synode.Node):
    name = 'K-means Clustering'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'dataset_blobs.svg'
    description = (
        'Clusters data by trying to separate samples in n groups of equal '
        'variance')
    nodeid = 'org.sysess.sympathy.machinelearning.k_means'
    tags = Tags(Tag.MachineLearning.Unsupervised)

    descriptor = Descriptor()
    descriptor.name = name
    info = _kmeans_clustering_info()

    descriptor.set_info(info, doc_class=sklearn.cluster.KMeans)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'cluster_centers_', 'labels_', 'inertia_'
        ]], doc_class=sklearn.cluster.KMeans)

    parameters = synode.parameters()
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
        skl = sklearn.cluster.KMeans(**kwargs)

        model.set_skl(skl)
        model.save()


class MiniBatchKMeansClustering(SyML_abstract, synode.Node):
    name = 'Mini-batch K-means Clustering'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'dataset_blobs.svg'
    description = (
        'Variant of the KMeans algorithm which uses mini-batches to reduce the'
        ' computation time')
    nodeid = 'org.sysess.sympathy.machinelearning.mini_batch_k_means'
    tags = Tags(Tag.MachineLearning.Unsupervised)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        [
            "Model",
            {'name': 'n_clusters',
             'dispname': 'Number of clusters/centroids',
             'type': IntType(default=8)},
            {'name': 'max_no_improvement',
             'dispname': 'Consecutive batches without improvement',
             'type': UnionType([IntType(), NoneType()], default=10)},
            {'name': 'batch_size',
             'dispname': 'Mini-batch size',
             'type': IntType(default=100, min_value=1)},
            {'name': 'init',
             'dispname': 'Initialization method',
             'type': StringSelectionType(
                 ['k-means++', 'random'], default='k-means++')},
            {'name': 'compute_labels',
             'dispname': 'Compute label assignment',
             'type': BoolType(default=True)},
        ],
        [
            "Solver",
            {'name': 'max_iter',
             'dispname': 'Maximum number of iterations',
             'type': IntType(default=300)},
            {'name': 'tol',
             'dispname': 'Tolerance',
             'type': FloatType(min_value=0, default=1e-4)},
            {'name': 'init_size',
             'dispname': 'Number of random samples',
             'type': IntType(default=300, min_value=1)},
            {'name': 'n_init',
             'dispname': 'Number of random initializations',
             'type': IntType(default=3)},
            {'name': 'reassignment_ratio',
             'dispname': 'Reassignment ratio',
             'type': FloatType(default=0.01)},
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([NoneType(), IntType()], default=None)},

        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.cluster.MiniBatchKMeans)

    descriptor.set_attributes([
        {'name': attr_name} for attr_name in [
            'cluster_centers_', 'labels_', 'inertia_'
        ]], doc_class=sklearn.cluster.MiniBatchKMeans)

    parameters = synode.parameters()
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
        skl = sklearn.cluster.MiniBatchKMeans(**kwargs)

        model.set_skl(skl)
        model.save()
