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
import warnings

import sklearn
# Ignore a warning from numpy>=1.15.2 when importing sklearn.ensemble
# See issue #2768 for details.
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    import sklearn.ensemble

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.decisiontrees import IsolationForestDescriptor

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class IsolationForest(SyML_abstract, node.Node):
    name = 'Isolation Forest'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'isolation_forest.svg'
    description = (
        'Predicts outliers based on minimum path length of random trees with '
        'single nodes in the leafs.')
    nodeid = 'org.sysess.sympathy.machinelearning.isolation_forest'
    tags = Tags(Tag.MachineLearning.Unsupervised)

    descriptor = IsolationForestDescriptor()
    descriptor.name = name
    info = [
        [
            "Model", 
            {'name': 'n_estimators',
             'dispname': 'Number of estimators',
             'type': IntType(min_value=0, default=100)},
            {'name': 'max_samples',
             'dispname': 'Number of samples',
             'type': UnionType([
                 IntType(),
                 FloatType(),
                 StringSelectionType(['auto'])],
                               default='auto'),
             'desc': (
                 'The number of samples to draw from X to train each base '
                 'estimator  expressed as number of samples (int), or a '
                 'fraction of all samples (float). If "auto" then a maximum of '
                 '256 samples will be used (less when fewer input samples given)'
             )},
            {'name': 'contamination',
             'dispname': 'Contamination',
             'type': FloatType(min_value=0, max_value=0.5, default=0.1)},
            {'name': 'max_features',
             'dispname': 'Number of features',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0)],
                default=1.0)},
            {'name': 'bootstrap',
             'dispname': 'Bootstrap',
             'type': BoolType(default=False)},
        ],
        [
            "Solver",
            {'name': 'n_jobs',
             'dispname': 'Number of jobs',
             'type': IntType(min_value=-1, default=1)},
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([
                 IntType(), NoneType()], default=None)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.ensemble.IsolationForest)

    descriptor.set_attributes([
        {'name': 'estimators_samples_', },
        {'name': 'max_samples_'},
    ], doc_class=sklearn.ensemble.IsolationForest)

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

        from distutils.version import LooseVersion
        if LooseVersion(sklearn.__version__) < LooseVersion('0.22'):
            skl = sklearn.ensemble.IsolationForest(behaviour='new', **kwargs)
        else:
            skl = sklearn.ensemble.IsolationForest(**kwargs)

        model.set_skl(skl)
        model.save()
