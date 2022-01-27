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
import sklearn.preprocessing
from sklearn.impute import SimpleImputer

from sympathy.api import node
from sympathy.api.nodeconfig import Ports, Tag, Tags

from sylib.machinelearning.model import ModelPort
from sylib.machinelearning.preprocessing import StandardScalerDescriptor
from sylib.machinelearning.preprocessing import RobustScalerDescriptor
from sylib.machinelearning.preprocessing import MaxAbsScalerDescriptor
from sylib.machinelearning.preprocessing import OneHotEncoderDescriptor
from sylib.machinelearning.preprocessing import PolynomialFeaturesDescriptor
from sylib.machinelearning.preprocessing import LabelBinarizerDescriptor
from sylib.machinelearning.preprocessing import CategoryEncoderDescriptor
from sylib.machinelearning.preprocessing import CategoryEncoder
from sylib.machinelearning.utility import names_from_x
from sylib.machinelearning.utility import names_from_y

from sylib.machinelearning.abstract_nodes import SyML_abstract
from sylib.machinelearning.descriptors import Descriptor

from sylib.machinelearning.descriptors import BoolListType
from sylib.machinelearning.descriptors import BoolType
from sylib.machinelearning.descriptors import FloatListType
from sylib.machinelearning.descriptors import FloatType
from sylib.machinelearning.descriptors import IntListType
from sylib.machinelearning.descriptors import IntType
from sylib.machinelearning.descriptors import StringType
from sylib.machinelearning.descriptors import NoneType
from sylib.machinelearning.descriptors import StringSelectionType
from sylib.machinelearning.descriptors import UnionType


class StandardScaler(SyML_abstract, node.Node):
    name = 'Standard Scaler'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'scaler.svg'
    description = """
Standardize features by removing the mean and scaling to unit variance.

Centering and scaling happen independently on each feature by
computing the relevant statistics on the samples in the training
set. Mean and standard deviation are then stored to be used on later
data using the transform method.  Standardization of a dataset is a
common requirement for many machine learning estimators: they might
behave badly if the individual feature do not more or less look like
standard normally distributed data (e.g. Gaussian with 0 mean and unit
variance)."""
    nodeid = 'org.sysess.sympathy.machinelearning.standard_scaler'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = StandardScalerDescriptor()
    descriptor.name = name
    info = [
             {'name': 'with_mean',
              'dispname': 'Center the data before scaling', 
              'type': BoolType(default=True)},
             {'name': 'with_std',
              'dispname': 'Scale to unit variance',
              'type': BoolType(default=True)},
    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.StandardScaler)

    descriptor.set_mirroring()
    descriptor.set_attributes([
        {'name': 'scale_', 'cnames': names_from_x},
        {'name': 'mean_', 'cnames': names_from_x},
        {'name': 'var_', 'cnames': names_from_x},
        {'name': 'n_samples_seen_'},
    ], doc_class=sklearn.preprocessing.StandardScaler)

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
        skl = sklearn.preprocessing.StandardScaler(**kwargs)

        model.set_skl(skl)
        model.save()


class RobustScaler(SyML_abstract, node.Node):
    name = 'Robust Scaler'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'scaler.svg'
    description = """
Scale features using statistics that are robust to outliers.

This Scaler removes the median and scales the data according to the
quantile range (defaults to IQR: Interquartile Range). The IQR is the
range between the 1st quartile (25th quantile) and the 3rd quartile
(75th quantile). Centering and scaling happen independently on each
feature (or each sample, depending on the axis argument) by computing
the relevant statistics on the samples in the training set. Median and
interquartile range are then stored to be used on later data using the
transform method. Standardization of a dataset is a common requirement
for many machine learning estimators. Typically this is done by
removing the mean and scaling to unit variance. However, outliers can
often influence the sample mean / variance in a negative way. In such
cases, the median and the interquartile range often give better
results.  """
    nodeid = 'org.sysess.sympathy.machinelearning.robust_scaler'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = RobustScalerDescriptor()
    descriptor.name = name
    descriptor.set_mirroring()
    info = [
        {'name': 'with_centering',
         'dispname': 'Center the data before scaling',
         'type': BoolType(default=True)},
        {'name': 'with_scaling',
         'dispname': 'Scale to interquantile range',
         'type': BoolType(default=True)},
        {'name': 'quantile_range',
         'dispname': 'IQR Quantile range',
         'type': FloatListType(default=[25.0, 75.0], 
                               min_length=2, 
                               max_length=2, 
                               min_value=0.0, 
                               max_value=100.0)},
    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.RobustScaler)

    descriptor.set_attributes([
        {'name': 'center_', 'cnames': names_from_x},
        {'name': 'scale_', 'cnames': names_from_x},
    ], doc_class=sklearn.preprocessing.RobustScaler)

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
        skl = sklearn.preprocessing.RobustScaler(**kwargs)

        model.set_skl(skl)
        model.save()


class MaxAbsScaler(SyML_abstract, node.Node):
    name = 'Max Abs Scaler'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'scaler.svg'
    description = """
Scale each feature by its maximum absolute value.

This estimator scales and translates each feature individually such
that the maximal absolute value of each feature in the training set
will be 1.0. It does not shift/center the data, and thus does not
destroy any sparsity.
"""
    nodeid = 'org.sysess.sympathy.machinelearning.maxabs_scaler'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = MaxAbsScalerDescriptor()
    descriptor.name = name
    descriptor.set_info([])
    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'scale_', 'cnames': names_from_x},
        {'name': 'max_abs_', 'cnames': names_from_x},
        {'name': 'n_samples_seen_'},
    ], doc_class=sklearn.preprocessing.MaxAbsScaler)

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
        skl = sklearn.preprocessing.MaxAbsScaler(**kwargs)

        model.set_skl(skl)
        model.save()


class Normalizer(SyML_abstract, node.Node):
    name = 'Normalizer'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'normalizer.svg'
    description = """
Normalize samples individually to unit norm.

Each sample (i.e. each row of the data matrix) with at least one non
zero component is rescaled independently of other samples so that its
norm (l1, l2 or max) equals one."""
    nodeid = 'org.sysess.sympathy.machinelearning.normalizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        {'name': 'norm',
         'dispname': 'Norm',
         'type': StringSelectionType(options=['l1', 'l2', 'max'], default='l2')
        }
    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.Normalizer)

    descriptor.set_mirroring()

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
        skl = sklearn.preprocessing.Normalizer(**kwargs)

        model.set_skl(skl)
        model.save()


class Binarizer(SyML_abstract, node.Node):
    name = 'Binarizer'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'binarizer.svg'
    description = """
Binarize data (set feature values to 0 or 1) according to a threshold.

Values greater than the threshold map to 1, while values less than or
equal to the threshold map to 0. With the default threshold of 0, only
positive values map to 1. Binarization is a common operation on text
count data where the analyst can decide to only consider the presence
or absence of a feature rather than a quantified number of occurrences
for instance. It can also be used as a pre-processing step for
estimators that consider boolean random variables (e.g. modelled using
the Bernoulli distribution in a Bayesian setting)."""
    nodeid = 'org.sysess.sympathy.machinelearning.binarizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        {'name': 'threshold',
         'dispname': 'Threshold',
         'type': FloatType(default=0.0)}
    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.Binarizer)

    descriptor.set_mirroring()

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
        skl = sklearn.preprocessing.Binarizer(**kwargs)

        model.set_skl(skl)
        model.save()


class LabelBinarizer(SyML_abstract, node.Node):
    name = 'Label Binarizer'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'label_binarizer.svg'
    description = """
Binarize labels in a one-vs-all fashion.

Several regression and binary classification algorithms are available
in the scikit. A simple way to extend these algorithms to the
multi-class classification case is to use the so-called one-vs-all
scheme. At learning time, this simply consists in learning one
regressor or binary classifier per class. In doing so, one needs to
convert multi-class labels to binary labels (belong or does not belong
to the class). LabelBinarizer makes this process easy with the
transform method. At prediction time, one assigns the class for which
the corresponding model gave the greatest confidence. LabelBinarizer
makes this easy with the inverse_transform method """
    nodeid = 'org.sysess.sympathy.machinelearning.label_binarizer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = LabelBinarizerDescriptor()
    descriptor.name = name
    info = [
        {'name': 'pos_label',
         'dispname': 'Positive label',
         'type': IntType(default=1)},
        {'name': 'neg_label',
         'dispname': 'Negative label',
         'type': IntType(default=0)},
        {'name': 'sparse_output',
         'dispname': 'Transformed array in sparse format',
         'desc': """
Will generate sparse matrix if true.
Warning: sparse matrices are not handled by all Sympathy nodes and may be
silently converted to non-sparse arrays""",
         'type': BoolType(default=False)},
    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.LabelBinarizer)

    descriptor.set_attributes([
        {'name': 'classes_', 'rnames': names_from_y},
        {'name': 'y_type_', },
    ], doc_class=sklearn.preprocessing.LabelBinarizer)

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
        skl = sklearn.preprocessing.LabelBinarizer(**kwargs)

        model.set_skl(skl)
        model.save()


class OneHotEncoder(SyML_abstract, node.Node):
    name = 'One-Hot Encoder'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'label_binarizer.svg'
    description = """
Encode categorical integer features using a one-hot aka one-of-K scheme.

For each categorical input feature, a number of output features will
be given of which exactly one is marked as true and the rest as
false. This encoding is needed for feeding categorical data to many
scikit-learn estimators, notably linear models and SVMs with the
standard kernels. Note: a one-hot encoding of y labels should use a
LabelBinarizer instead. Also note: categories for the input data are
generated automatically (as in category='auto' keyword in scikit-learn)"""
    nodeid = 'org.sysess.sympathy.machinelearning.one_hot_encoder'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = OneHotEncoderDescriptor()
    descriptor.name = name
    info = [
        #{'name': 'n_values',
        # 'dispname': 'Number of values per feature',
        # 'type': UnionType([StringSelectionType(["auto"]),
        #                    IntType(min_value=0),
        #                    IntListType(min_length=1, min_value=0)],
        #                    default='auto')},
        #{'name': 'categorical_features',
        # 'dispname': 'Which features are categorical',
        # 'type': UnionType([
        #     StringSelectionType(["all"]),
        #     IntListType(min_length=1, min_value=0),
        #     BoolListType(min_length=1)], default='all')},
        {'name': 'handle_unknown',
         'dispname': 'Handle unknown',
         'desc': 'How to handle unknown categories during (non-fit) transform',
         'type': StringSelectionType(['error', 'ignore'])},
        {'name': 'sparse',
         'dispname': 'Transformed array in sparse format',
         'desc': """
Will generate sparse matrix if true.
Warning: sparse matrices are not handled by all Sympathy nodes and may be
silently converted to non-sparse arrays""",
         'type': BoolType(default=False)},
    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.OneHotEncoder)

    descriptor.set_attributes([
        {'name': 'active_features_'},
        {'name': 'feature_indices_', 'cnames': names_from_x},
        {'name': 'n_values_', 'cnames': names_from_x},
        {'name': 'categories_', 'cnames': names_from_x},
    ], doc_class=sklearn.preprocessing.OneHotEncoder)

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
        skl = sklearn.preprocessing.OneHotEncoder(categories='auto', **kwargs)

        model.set_skl(skl)
        model.save()


class Imputer(SyML_abstract, node.Node):
    name = 'Imputer'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'imputer.svg'
    description = (
        'Replaces missing values in a data set with a computed value infered '
        'from the remained of the data set. If there are missing data in the '
        'data set, those needs to be removed or replaced first.')
    nodeid = 'org.sysess.sympathy.machinelearning.imputer'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    info = [
        {'name': 'missing_values',
         'dispname': 'Placeholder for missing values',
         'type': UnionType([FloatType(),
                            StringType(), 
                            NoneType()],
                            default=np.nan)},
        {'name': 'strategy',
         'dispname': 'Imputing strategy',
         'type': StringSelectionType([
             "mean", "median", "most_frequent"], default="mean")},
    ]

    descriptor.set_info(info, doc_class=SimpleImputer)

    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'statistics_', 'cnames': names_from_x},
    ], doc_class=SimpleImputer)

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
        skl = SimpleImputer(**kwargs)

        model.set_skl(skl)
        model.save()


class PolynomialFeatures(SyML_abstract, node.Node):
    name = 'Polynomial Features'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'polynomial.svg'
    description = (
        'Generate a new feature matrix consisting of all polynomial '
        'combinations of the features with less than a given degree')
    nodeid = 'org.sysess.sympathy.machinelearning.polynomial_features'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = PolynomialFeaturesDescriptor()
    descriptor.name = name
    info = [
        {'name': 'degree',
         'dispname': 'Degree',
         'type': IntType(min_value=0, default=2)},
        {'name': 'interaction_only',
         'dispname': 'Only interaction features produced',
         'type': BoolType(default=False)},
        {'name': 'include_bias',
         'dispname': 'Include bias',
         'type': BoolType(default=True)},
        #{'name': 'order',
        # 'dispname': 'Order of output array',
        # 'type': StringSelectionType(['C', 'F'], default='C')},

    ]

    descriptor.set_info(info, doc_class=sklearn.preprocessing.PolynomialFeatures)

    descriptor.set_attributes([
        {'name': 'n_input_features_', },
        {'name': 'n_output_features_', },
        {'name': 'powers_', 'cnames': names_from_x, 'rnames': names_from_y},
    ])

    descriptor.set_info(info, doc_class=sklearn.preprocessing.PolynomialFeatures)

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
        skl = sklearn.preprocessing.PolynomialFeatures(**kwargs)

        model.set_skl(skl)
        model.save()


class LabelEncoder(SyML_abstract, node.Node):
    name = 'Label Encoder'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'label_encoder.svg'
    description = (
        'Encode single string labels with value between 0 and n_classes-1.')
    nodeid = 'org.sysess.sympathy.machinelearning.label_encoder'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = Descriptor()
    descriptor.name = name
    
    descriptor.set_info([])

    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'classes_'},
    ], doc_class=sklearn.preprocessing.LabelEncoder)

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
        skl = sklearn.preprocessing.LabelEncoder(**kwargs)

        model.set_skl(skl)
        model.save()


class CategoryEncoderNode(SyML_abstract, node.Node):
    name = 'Categorical Encoder'
    author = 'Mathias Broxvall'
    version = '0.1'
    icon = 'categorical_encoder.svg'
    description = (
        'Encodes all inputs into integer features, assumes '
        'that all inputs are Categorical ')
    nodeid = 'org.sysess.sympathy.machinelearning.category_encoder'
    tags = Tags(Tag.MachineLearning.Processing)

    descriptor = CategoryEncoderDescriptor()
    descriptor.name = name
    descriptor.set_info([
        {'name': 'max_categories',
         'dispname': 'Maximum categories',
         'type': UnionType([NoneType(), IntType(min_value=1)], default=None),
         'desc': (
             'Maximum number of categories for any feature. '
             'Remaining values are encoded as 0. '
             'If None then no upper bound on number of features')},
    ])
    descriptor.set_mirroring()

    descriptor.set_attributes([
        {'name': 'categories_',
         'desc': (
             'List of dictionaries that map each input feature into '
             'a categorical integer')},
        {'name': 'inv_categories_',
         'desc': (
             'List of dictionaries that map each output value into '
             'an corresponding input value')}
        ])

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
        skl = CategoryEncoder(**kwargs)

        model.set_skl(skl)
        model.save()
