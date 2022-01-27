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
from sylib.machinelearning.descriptors import Descriptor

import numpy as np

import sklearn
import distutils

sklearn_version = distutils.version.LooseVersion(
    sklearn.__version__).version[:3]


class StandardScalerDescriptor(Descriptor):
    pass


class RobustScalerDescriptor(Descriptor):
    pass


class MaxAbsScalerDescriptor(Descriptor):
    pass


class LabelBinarizerDescriptor(Descriptor):

    def post_fit(self, skl):
        """Assign the model classes as Y parameter names"""
        self.set_y_names(skl.classes_)


class OneHotEncoderDescriptor(Descriptor):

    def post_fit(self, skl):
        """Compute labels for each output from the OneHotEncoder"""
        if self.x_names is None:
            return
        y_names = []

        if sklearn_version <= [0, 20, 0]:
            indices = skl.feature_indices_
            feature_idx = 0
            for feature, (start, stop) in enumerate(
                    zip(indices[:-1], indices[1:])):
                feature_name = self.x_names[feature]
                for i in range(stop - start):
                    if feature_idx in skl.active_features_:
                        y_names.append("{0}_{1}".format(feature_name, i))
                    feature_idx = feature_idx + 1
            # TODO - logic to compute the names for columns that are
            # not "categorial" and just passed through the SKL node
        else:
            for x_name, cat in zip(self.x_names, skl.categories_):
                for i, active_feature in enumerate(cat):
                    y_names.append(f"{x_name}_{i}")
                    # TODO - change the column names to reflect the discrete
                    # values in skl.categories_
        self.set_y_names(y_names)


class PolynomialFeaturesDescriptor(Descriptor):

    def post_fit(self, skl):
        y_names = []
        x_names = self.x_names or ["X{0}".format(i) for i in range(skl.n_input_features_)]
        for row in range(skl.n_output_features_):
            name=""
            for col in range(skl.n_input_features_):
                power = skl.powers_[row,col]
                if power > 0:
                    if name != "": name += " * "
                    name += x_names[col]
                if power > 1:
                    name += "^{0}".format(power)
            if name == "": name = "bias"
            y_names.append(name)
        self.set_y_names(y_names)

class  CategoryEncoderDescriptor(Descriptor):

    def __init__(self):
        super(CategoryEncoderDescriptor, self).__init__()

class  CategoryEncoder(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):

    def __init__(self, max_categories=None):
        super(CategoryEncoder, self).__init__()
        self.max_categories = max_categories

    def fit(self, X):
        self.categories_ = []
        self.inv_categories_ = []
        for col in range(X.shape[1]):
            all_values = np.array(list(set(X[:,col])))
            if self.max_categories is not None:
                count = np.array([np.sum(X[:,col] == val) for val in all_values], dtype=int)
                s = np.argsort(-count)
                all_values = all_values[s]
                all_values = all_values[:self.max_categories]
            all_values.sort()
            cats = {val: pos+1 for pos,val in enumerate(all_values)}
            self.categories_.append(cats)
            inv_cats = {pos+1: val for pos,val in enumerate(all_values)}
            self.inv_categories_.append(inv_cats)

    def transform(self, X):
        result = np.full(X.shape, 0, dtype=int)
        for col in range(X.shape[1]):
            dct = self.categories_[col]
            for key, val in dct.items():
                result[:, col][X[:, col] == key] = val
        return result

    def inverse_transform(self, X):
        result = np.zeros(X.shape, dtype='O')
        maxlen = 1
        for col in range(X.shape[1]):
            dct = self.inv_categories_[col]
            for key, val in dct.items():
                maxlen = max(maxlen, len(str(val)))
                result[:, col][X[:, col] == key] = str(val)
        try:
            result = result.astype(int)
        except ValueError:
            try:
                result = result.astype(float)
            except ValueError:
                result = result.astype('S{}'.format(maxlen))
        return np.array(result)

    def fit_transform(self, X, y=None):
        self.fit(X)
        return self.transform(X)

    def get_params(self, deep=False):
        return {}

    def set_params(self, **params):
        pass
