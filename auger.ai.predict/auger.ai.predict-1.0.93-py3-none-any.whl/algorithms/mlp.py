from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline


class MLPClassifierBase(BaseEstimator, ClassifierMixin):
    max_num_epochs_ = 300

    def collect_params(self):
        pass

    def fit(self, X, y):
        self.collect_params()
        self.clf_ = MLPClassifier(hidden_layer_sizes=self.hidden_layer_sizes_,
                                  activation=self.activation,
                                  early_stopping=True,
                                  max_iter=self.num_epochs)
        self.clf_.fit(X, y)

        return self

    def predict(self, X):
        return self.clf_.predict(X)

    def predict_proba(self, X):
        return self.clf_.predict_proba(X)

    @property
    def classes_(self):
        return self.clf_.classes_

    @staticmethod
    def infer_additional_params(trial):
        ans = {}
        r = trial.get('ratio', 1.0)
        if r < 1.0:
            ans['num_epochs'] = int(MLPClassifierBase.max_num_epochs_ * r)

        return ans


class MLPRegressorBase(BaseEstimator, RegressorMixin):
    def collect_params(self):
        pass

    def fit(self, X, y):
        self.collect_params()
        self.clf_ = MLPRegressor(hidden_layer_sizes=self.hidden_layer_sizes_,
                                 activation=self.activation,
                                 early_stopping=True,
                                 max_iter=self.num_epochs)
        self.clf_.fit(X, y)

        return self

    def predict(self, X):
        return self.clf_.predict(X)

    @staticmethod
    def infer_additional_params(trial):
        ans = {}
        r = trial.get('ratio', 1.0)
        if r < 1.0:
            ans['num_epochs'] = int(MLPClassifierBase.max_num_epochs_ * r)

        return ans


class MLPClassifier1Layer(MLPClassifierBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1)


class MLPClassifier2Layer(MLPClassifierBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1, hidden_layer_sizes_2=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1
        self.hidden_layer_sizes_2 = hidden_layer_sizes_2

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1, self.hidden_layer_sizes_2)


class MLPClassifier3Layer(MLPClassifierBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1, hidden_layer_sizes_2=1, hidden_layer_sizes_3=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1
        self.hidden_layer_sizes_2 = hidden_layer_sizes_2
        self.hidden_layer_sizes_3 = hidden_layer_sizes_3

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1, self.hidden_layer_sizes_2, self.hidden_layer_sizes_3)


class MLPClassifier4Layer(MLPClassifierBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1, hidden_layer_sizes_2=1, hidden_layer_sizes_3=1, hidden_layer_sizes_4=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1
        self.hidden_layer_sizes_2 = hidden_layer_sizes_2
        self.hidden_layer_sizes_3 = hidden_layer_sizes_3
        self.hidden_layer_sizes_4 = hidden_layer_sizes_4

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1, self.hidden_layer_sizes_2, self.hidden_layer_sizes_3, self.hidden_layer_sizes_4)


class MLPRegressor1Layer(MLPRegressorBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1)


class MLPRegressor2Layer(MLPRegressorBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1, hidden_layer_sizes_2=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1
        self.hidden_layer_sizes_2 = hidden_layer_sizes_2

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1, self.hidden_layer_sizes_2)


class MLPRegressor3Layer(MLPRegressorBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1, hidden_layer_sizes_2=1, hidden_layer_sizes_3=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1
        self.hidden_layer_sizes_2 = hidden_layer_sizes_2
        self.hidden_layer_sizes_3 = hidden_layer_sizes_3

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1, self.hidden_layer_sizes_2, self.hidden_layer_sizes_3)


class MLPRegressor4Layer(MLPRegressorBase):
    def __init__(self, activation='relu', hidden_layer_sizes_1=1, hidden_layer_sizes_2=1, hidden_layer_sizes_3=1, hidden_layer_sizes_4=1):
        self.activation = activation
        self.hidden_layer_sizes_1 = hidden_layer_sizes_1
        self.hidden_layer_sizes_2 = hidden_layer_sizes_2
        self.hidden_layer_sizes_3 = hidden_layer_sizes_3
        self.hidden_layer_sizes_4 = hidden_layer_sizes_4

    def collect_params(self):
        self.hidden_layer_sizes_ = (self.hidden_layer_sizes_1, self.hidden_layer_sizes_2, self.hidden_layer_sizes_3, self.hidden_layer_sizes_4)


# class MyMLPClassifier(BaseEstimator):
#     def __init__(self, **kwargs):
#         for k, v in kwargs.items():
#             setattr(self, k, v)
#         self.x = 100
#
#     def fit(self, X, y):
#         print("Fit called")
#         self.hidden_sizes_ = tuple(getattr(self, k) for k in sorted([n for n in dir(self) if n.startswith("hidden_layer_sizes")]))
#         self.activation_ = getattr(self, "activation", "relu")
#
#         self.clf_ = MLPClassifier(hidden_layer_sizes=self.hidden_sizes_,
#                                   activation=self.activation_)
#
#         self.clf_.fit(X, y)
#
#         return self
#
#     def predict(self, X):
#         print("Predict called")
#         return self.clf_.predict(X)


if __name__ == "__main__":
    from sklearn.utils.estimator_checks import check_estimator

    # clf = MyMLPClassifier(hidden_sizes_1=16,
    #                       hidden_sizes_2=16,
    #                       activation='relu')
    #
    # pipeline = make_pipeline(clf)
    #
    # check_estimator(MyMLPClassifier)

    check_estimator(MLPClassifier1Layer)
    check_estimator(MLPClassifier2Layer)
    check_estimator(MLPClassifier3Layer)
    check_estimator(MLPClassifier4Layer)

