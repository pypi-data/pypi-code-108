import warnings
from distutils.version import LooseVersion

import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
from shap import Explainer, Explanation
from shap.explainers._tree import TreeEnsemble
from shap import _cext
from shap import maskers
from shap.plots import colors
from shap.utils import assert_import, safe_isinstance
from shap.utils._legacy import DenseData

output_transform_codes = {
    "identity": 0,
    "logistic": 1,
    "logistic_nlogloss": 2,
    "squared_loss": 3
}

feature_perturbation_codes = {
    "interventional": 0,
    "tree_path_dependent": 1,
    "global_path_dependent": 2
}

labels = {
    'MAIN_EFFECT': "SHAP main effect value for\n%s",
    'INTERACTION_VALUE': "SHAP interaction value",
    'INTERACTION_EFFECT': "SHAP interaction value for\n%s and %s",
    'VALUE': "SHAP value (impact on model output)",
    'GLOBAL_VALUE': "mean(|SHAP value|) (average impact on model output magnitude)",
    'VALUE_FOR': "SHAP value for\n%s",
    'PLOT_FOR': "SHAP plot for %s",
    'FEATURE': "Feature %s",
    'FEATURE_VALUE': "Feature value",
    'FEATURE_VALUE_LOW': "Low",
    'FEATURE_VALUE_HIGH': "High",
    'JOINT_VALUE': "Joint SHAP value",
    'MODEL_OUTPUT': "Model output value"
}


def summary_legacy(shap_values, features):
    num_features = shap_values.shape[1]
    max_display = 20
    feature_names = np.array(
        [labels['FEATURE'] % str(i) for i in range(num_features)])

    # order features by the sum of their effect magnitudes
    feature_order = np.argsort(np.sum(np.abs(shap_values), axis=0))
    feature_order = feature_order[-min(max_display, len(feature_order)):]

    row_height = 0.4
    pl.gcf().set_size_inches(8, len(feature_order) * row_height + 1.5)
    pl.axvline(x=0, color="#999999", zorder=-1)

    for pos, i in enumerate(feature_order):
        pl.axhline(y=pos, color="#cccccc", lw=0.5, dashes=(1, 5), zorder=-1)

        shaps = shap_values[:, i]
        inds = np.arange(len(shaps))
        np.random.shuffle(inds)
        values = features[inds, i]
        shaps = shaps[inds]

        N = len(shaps)
        nbins = 100
        quant = np.round(nbins * (shaps - np.min(shaps)) / (
                np.max(shaps) - np.min(shaps) + 1e-8))
        inds = np.argsort(quant + np.random.randn(N) * 1e-6)
        layer = 0
        last_bin = -1
        ys = np.zeros(N)
        for ind in inds:
            if quant[ind] != last_bin:
                layer = 0
            ys[ind] = np.ceil(layer / 2) * ((layer % 2) * 2 - 1)
            layer += 1
            last_bin = quant[ind]
        ys *= 0.9 * (row_height / np.max(ys + 1))

        # if i != 2: #
        #     continue #
        # print(shaps)
        # print(ys)

        pl.scatter(shaps, pos + ys,
                   cmap=colors.red_blue, s=16, c=values, linewidth=0,
                   zorder=3, rasterized=len(shaps) > 500)

    pl.gca().xaxis.set_ticks_position('bottom')
    pl.gca().yaxis.set_ticks_position('none')
    pl.gca().spines['right'].set_visible(False)
    pl.gca().spines['top'].set_visible(False)
    pl.gca().spines['left'].set_visible(False)
    pl.gca().tick_params(color="#333333", labelcolor="#333333")
    pl.yticks(range(len(feature_order)),
              [feature_names[i] for i in feature_order], fontsize=13)
    pl.gca().tick_params('y', length=20, width=0.5, which='major')
    pl.gca().tick_params('x', labelsize=11)
    pl.ylim(-1, len(feature_order))
    pl.xlabel(labels['VALUE'], fontsize=13)
    pl.show()


class Tree(Explainer):
    def __init__(self, model, data=None, model_output="raw",
                 feature_perturbation="interventional"):
        super(Tree, self).__init__(model, data)
        self.data = data
        if self.data is None:
            feature_perturbation = "tree_path_dependent"
        self.data_missing = None if self.data is None else pd.isna(self.data)
        self.feature_perturbation = feature_perturbation
        self.expected_value = None
        self.model = TreeEnsemble(model, self.data, self.data_missing, model_output)
        self.model_output = model_output
        # self.model_output = self.model.model_output # this allows the TreeEnsemble to translate model outputs types by how it loads the model

        # compute the expected value if we have a parsed tree for the cext
        if data is not None:
            self.expected_value = self.model.predict(self.data).mean(0)
            if hasattr(self.expected_value, '__len__') and len(
                    self.expected_value) == 1:
                self.expected_value = self.expected_value[0]
        elif hasattr(self.model, "node_sample_weight"):
            self.expected_value = self.model.values[:, 0].sum(0)
            if self.expected_value.size == 1:
                self.expected_value = self.expected_value[0]
            self.expected_value += self.model.base_offset

        # if our output format requires binary classification to be represented as two outputs then we do that here
        if self.model.model_output == "probability_doubled" and self.expected_value is not None:
            self.expected_value = [1 - self.expected_value,
                                   self.expected_value]

    def shap_values(self, X, y=None, tree_limit=None, approximate=False):
        print("self.expected_value", self.expected_value)
        print("self.feature_perturbation", self.feature_perturbation)
        print("self.model.model_output", self.model.model_output)
        print("self.model.num_outputs", self.model.num_outputs)
        print("self.model.model_type", self.model.model_type)
        print("self.model.tree_limit", self.model.tree_limit)
        """
        self.expected_value [-1.78200922  0.5         0.5       ]
        self.feature_perturbation interventional
        self.model.model_output raw
        self.model.num_outputs 3
        self.model.model_type xgboost
        self.model.tree_limit 100
        """


        tree_limit = -1 if self.model.tree_limit is None else self.model.tree_limit

        # shortcut using the C++ version of Tree SHAP in XGBoost, LightGBM, and CatBoost
        if self.feature_perturbation == "tree_path_dependent" and self.model.model_type != "internal" and self.data is None:
            phi = None
            if self.model.model_type == "xgboost":
                import xgboost
                if not isinstance(X, xgboost.core.DMatrix):
                    X = xgboost.DMatrix(X)
                if tree_limit == -1:
                    tree_limit = 0
                try:
                    phi = self.model.original_model.predict(
                        X, ntree_limit=tree_limit, pred_contribs=True,
                        approx_contribs=approximate, validate_features=False
                    )
                except ValueError as e:
                    raise ValueError(
                        "This reshape error is often caused by passing a bad data matrix to SHAP. " \
                        "See https://github.com/slundberg/shap/issues/580") from e

            # note we pull off the last column and keep it as our expected_value
            if phi is not None:
                if len(phi.shape) == 3:
                    self.expected_value = [phi[0, i, -1] for i in range(phi.shape[1])]
                    out = [phi[:, i, :-1] for i in range(phi.shape[1])]
                else:
                    self.expected_value = phi[0, -1]
                    out = phi[:, :-1]

                return out

        flat_output = False
        if len(X.shape) == 1:
            flat_output = True
            X = X.reshape(1, X.shape[0])
        if X.dtype != self.model.input_dtype:
            X = X.astype(self.model.input_dtype)
        X_missing = np.isnan(X, dtype=np.bool)

        tree_limit = -1
        if tree_limit < 0 or tree_limit > self.model.values.shape[0]:
            tree_limit = self.model.values.shape[0]

        transform = self.model.get_transform()

        # run the core algorithm using the C extension
        phi = np.zeros((X.shape[0], X.shape[1] + 1, self.model.num_outputs))

        # print("self.model.children_left", self.model.children_left)
        # print("self.model.children_right", self.model.children_right)
        # print("self.model.children_default", self.model.children_default)
        # print("self.model.features", self.model.features)
        # print("self.model.thresholds", self.model.thresholds)
        print("self.model.max_depth", self.model.max_depth)
        # print("self.model.values", self.model.values)

        _cext.dense_tree_shap(
            self.model.children_left, self.model.children_right,
            self.model.children_default,
            self.model.features, self.model.thresholds, self.model.values,
            self.model.node_sample_weight,
            self.model.max_depth, X, X_missing, y, self.data,
            self.data_missing, tree_limit,
            self.model.base_offset, phi,
            feature_perturbation_codes[self.feature_perturbation],
            output_transform_codes[transform], False
        )

        print(phi.shape)
        print(phi[0, :-1, 0])
        print(phi[0, :-1, 1])

        # note we pull off the last column and keep it as our expected_value
        if self.model.num_outputs == 1:
            if self.expected_value is None and self.model.model_output != "log_loss":
                self.expected_value = phi[0, -1, 0]
            if flat_output:
                out = phi[0, :-1, 0]
            else:
                out = phi[:, :-1, 0]
        else:
            if self.expected_value is None and self.model.model_output != "log_loss":
                self.expected_value = [phi[0, -1, i] for i in
                                       range(phi.shape[2])]
            if flat_output:
                out = [phi[0, :-1, i] for i in range(self.model.num_outputs)]
            else:
                out = [phi[:, :-1, i] for i in range(self.model.num_outputs)]
        return out


if __name__ == "__main__":
    import shap
    from sklearn.datasets import load_iris, load_boston
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from xgboost import XGBClassifier

    iris = load_iris()
    boston = load_boston()
    X, y = iris.data, iris.target
    X, y = boston.data, boston.target
    model = RandomForestClassifier(n_estimators=10, random_state=0)
    model = RandomForestRegressor(n_estimators=10, random_state=0)
    # model = XGBClassifier(random_state=0)
    model.fit(X, y)

    # table = Table("iris")
    # X = table.X
    # y = table.Y

    # xgbmodel = XGBClassifier(random_state=0)(table)
    # import xgboost
    #
    # d_train = xgboost.DMatrix(X, label=y)
    # xgbmodel = xgboost.train({"random_state": 0}, d_train)

    explainer = shap.TreeExplainer(model, data=X)
    explainer = shap.TreeExplainer(model, data=shap.sample(X, 100))
    shap_values = explainer.shap_values(X, check_additivity=False)
    # shap_values = Tree(
    #     model,
    #     data=shap.sample(X, 100)
    # ).shap_values(X)
    summary_legacy(shap_values, X)

    # i = 1
    # shap.force_plot(explainer.expected_value, shap_values[1, :], matplotlib=True)
