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
import inspect
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
from sylib.machinelearning.decisiontrees import RandomForestDescriptor
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class RandomForestClassifier(SyML_abstract, node.Node):
    name = 'Random Forest Classifier'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'forest.svg'
    description = (
        'A random forest is a meta estimator that fits a number of decision '
        'tree classifiers on various sub-samples of the dataset and use '
        'averaging to improve the predictive accuracy and control '
        'over-fitting. The sub-sample size is always the same as the original '
        'input sample size but the samples are drawn with replacement if '
        'bootstrap is True (default).')
    nodeid = 'org.sysess.sympathy.machinelearning.random_forest_classifier'
    tags = Tags(Tag.MachineLearning.Supervised)

    # Test for existance of 'impurity_decrease' parameter (scikit-learn 0.19+)
    param_impurity_decrease = (
        'min_impurity_decrease' in inspect.signature(
            sklearn.ensemble.RandomForestClassifier).parameters
    )

    descriptor = RandomForestDescriptor()
    descriptor.name = name
    info = [
        [
            "Basic",
            {'name': 'n_estimators',
             'dispname': 'Trees in forest',
             'type': IntType(min_value=1, default=3)},
            {'name': 'criterion',
             'dispname': 'Split quality criterion',
             'type': StringSelectionType(['gini', 'entropy'])},
            {'name': 'bootstrap',
             'dispname': 'Bootstrap',
             'type': BoolType(default=True)},
            {'name': 'oob_score',
             'dispname': 'Use out-of-bad samples',
             'type': BoolType(default=True)},
            {'name': 'n_jobs',
             'dispname': 'Number of jobs',
             'type': IntType(min_value=-1, default=1)},
        ],
        [
            "Node growth",
            {'name': 'max_features',
             'dispname': 'Maximum number of features',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0),
                 StringSelectionType([
                     'auto', 'sqrt', 'log2']),
                 NoneType()], default="None")},
            {'name': 'max_depth',
             'dispname': 'Maximum tree depth',
             'type': UnionType([IntType(min_value=1), NoneType()])},
            {'name': 'min_samples_split',
             'dispname': 'Minimum samples for split',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0)
             ], default="2")},
            {'name': 'min_samples_leaf',
             'dispname': 'Minimum number of samples for leaf node',
             'type': UnionType([
                 IntType(min_value=1),
                 FloatType(min_value=0.0, max_value=1.0)
             ], default="1")},
            {'name': 'min_weight_fraction_leaf',
             'dispname': 'Minimum leaf weight fraction',
             'type': FloatType(min_value=0.0, default=0.0)},
            {'name': 'max_leaf_nodes',
             'dispname': 'Maximum leaf nodes',
             'type': UnionType([IntType(min_value=0),
                                NoneType()], default="None")},
            {'name': 'min_impurity_split',
             'dispname': 'Growth threshold',
             'type': FloatType(min_value=0.0, default=1e-7),
             'deprecated': param_impurity_decrease},
        ],
        [
            "Model state",
            {'name': 'random_state',
             'dispname': 'Random Seed',
             'type': UnionType([NoneType(), IntType()], default=None)},
            {'name': 'warm_start',
             'dispname': 'Warm start',
             'type': BoolType(default=False)},
        ],
    ]
    if param_impurity_decrease:
        info[1].append({'name': 'min_impurity_decrease',
                        'dispname': 'Minimum impurity decrease',
                        'type': FloatType(default=0)})
    descriptor.set_info(info,
                        doc_class=sklearn.ensemble.RandomForestClassifier)

    descriptor.set_attributes([
        {'name': 'classes_'},
        {'name': 'feature_importances_', 'cnames': names_from_x},
        {'name': 'n_classes_'},
        {'name': 'n_features_'},
        {'name': 'n_outputs_'},
        {'name': 'oob_score_'},
        {'name': 'oob_decision_function_'},
    ], doc_class=sklearn.ensemble.RandomForestClassifier)

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
        skl = sklearn.ensemble.RandomForestClassifier(**kwargs)

        model.set_skl(skl)
        model.save()
