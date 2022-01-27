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
import sklearn
import sklearn.tree

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.decisiontrees import DecisionTreeDescriptor
from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.utility import names_from_x

from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class DecisionTreeClassifier(SyML_abstract, node.Node):
    name = 'Decision Tree Classifier'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'tree.svg'
    description = (
        'Decision Trees (DTs) are a non-parametric supervised learning method'
        'used for classification and regression. The goal is to create a model'
        'that predicts the value of a target variable by learning simple'
        'decision rules inferred from the data features.')
    nodeid = 'org.sysess.sympathy.machinelearning.decision_tree_classifier'
    tags = Tags(Tag.MachineLearning.Supervised)

    # Test for existance of 'impurity_decrease' parameter (scikit-learn 0.19+)
    param_impurity_decrease = (
        'min_impurity_decrease' in inspect.signature(
            sklearn.tree.DecisionTreeClassifier.__init__).parameters
    )

    descriptor = DecisionTreeDescriptor()
    descriptor.name = name
    info = [
        [
            "Tree options",
            {'name': 'max_depth',
             'dispname': 'Maximum tree depth',
             'type': UnionType([IntType(min_value=1), NoneType()], default=3)},
            {'name': 'criterion',
             'dispname': 'Split quality criterion',
             'type': StringSelectionType(['gini', 'entropy'])},
            {'name': 'max_features',
             'dispname': 'Number of features to consider',
             'type': UnionType([IntType(min_value=1),
                               FloatType(min_value=0, max_value=1),
                               NoneType(), 
                               StringSelectionType(['auto', 'sqrt', 'log2'])],
                               default=None)},
            {'name': 'min_samples_split',
             'dispname': 'Minimum samples required to split',
             'type': UnionType([IntType(min_value=0), FloatType(min_value=0, max_value=1)], default=2)},
            {'name': 'min_samples_leaf',
             'dispname': 'Minimum samples required for leaf node',
             'type': UnionType([IntType(min_value=0), FloatType(min_value=0, max_value=1)], default=1)},
            {'name': 'max_leaf_nodes',
             'dispname': 'Maximum of leaf nodes',
             'type': UnionType([IntType(min_value=0), NoneType()], default=None)},
        ],
        [
            "Advanced options",
            {'name': 'min_weight_fraction_leaf',
             'dispname': 'Min. weighted fraction of weights for leaf node',
             'type': FloatType(default=0.)},
            {'name': 'splitter',
             'dispname': 'Splitting strategy',
             'type': StringSelectionType(['best', 'random'])},
            {'name': 'min_impurity_decrease',
             'dispname': 'Node splitting threshold',
             'type': FloatType(default=0.)},
        ],
        [
            "Model state",
            #{'name': 'presort',
            # 'dispname': 'Presort data',
            # 'type': BoolType(default=False)},
            {'name': 'random_state',
             'dispname': 'Random seed',
             'type': UnionType([NoneType(), IntType()], default=None)},
        ]
    ]

    descriptor.set_info(info, doc_class=sklearn.tree.DecisionTreeClassifier)

    descriptor.set_attributes([
        { 'name': 'classes_' },
        { 'name': 'feature_importances_', 'cnames': names_from_x },
        { 'name': 'max_features_' },
        { 'name': 'n_classes_' },
        { 'name': 'n_features_' },
        { 'name': 'n_outputs_' },
    ], doc_class=sklearn.tree.DecisionTreeClassifier)

    parameters = node.parameters()
    SyML_abstract.generate_parameters(parameters, descriptor)

    inputs = Ports([])
    outputs = Ports([ModelPort('Model', 'model')])
    __doc__ = SyML_abstract.generate_docstring(description, descriptor.info,
                                               descriptor.attributes, inputs,
                                               outputs)

    def execute(self, node_context):
        model = node_context.output['model']
        desc = self.__class__.descriptor
        model.set_desc(desc)

        kwargs = self.__class__.descriptor.get_parameters(
            node_context.parameters)
        skl = sklearn.tree.DecisionTreeClassifier(**kwargs)
        model.set_skl(skl)
        model.save()
