import numpy as np

from sklearn import clone
from sklearn.model_selection import StratifiedKFold

from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas
from auger_ml.data_splitters.XYNumpyDataPrep import XYNumpyDataPrep

from auger_ml.ensembles.super_learner import SuperLearner
from auger_ml.ensembles.utils import labels_to_score_transform


class DeepSuperLearner(SuperLearner):
    def __init__(self, options, metadata, method='slsqp', opt_trials=3, trim_eps=1e-6,
                 max_iters=12, num_pipelines=5):
        super(DeepSuperLearner, self).__init__(options, metadata, method, opt_trials, trim_eps, num_pipelines)

        self.max_iters = max_iters
        self._k_folds = options['crossValidationFolds']

        ds = DataSourceAPIPandas(options)
        ds.loadFromCacheFile("data_preprocessed")
        # ds.fillna(0)
        x_train, y_train = XYNumpyDataPrep(options).split_training(ds.df)
        self._x, self._y = ds.oversamplingFit(x_train, y_train)

        self._weights_per_iteration = None
        self._fitted_models_per_iteration = None

        self._params = dict(
            method=method,
            k_folds=self._k_folds,
            opt_trials=opt_trials,
            trim_eps=trim_eps,
            max_iters=max_iters
        )

    def build(self):
        self.fit(self._x, self._y)

        if self.classification:
            y_pred_weighted = self.predict_proba(self._x)
            self._y = self._le.fit_transform(self._y)
            y = labels_to_score_transform(self.score_name, self._y, self._n_classes)
        else:
            y_pred_weighted = self.predict(self._x)
            y = self._y

        main_score = self._score_func(y, y_pred_weighted)
        self.scores = {self.score_name: main_score}
        self._calc_extra_scores(y_pred_weighted)

        pipelines = []
        for i in self._indices:
            pipelines.append({k: self._predictions[i][k] for k in ['name', 'params']})
        self._params.update({'pipelines': pipelines, 'classification': self.classification})
        return main_score, self._params

    def fit(self, x, y):
        x = np.asarray(x)
        y = np.asarray(y)

        if self.classification:
            y = self._le.fit_transform(y)
            self._n_classes = len(np.unique(y))
        else:
            self._n_classes = 1

        weights_per_iteration = []
        fitted_models_per_iteration = []
        latest_loss = np.finfo(np.double).max

        for iter in range(self.max_iters):
            fitted_models_per_fold = np.empty(shape=(self._k_folds, self.num_pipelines), dtype=np.object)
            y_pred_mat = np.zeros(shape=(y.shape[0], self.num_pipelines, self._n_classes))
            # regression

            folds = StratifiedKFold(n_splits=self._k_folds, shuffle=False)
            for fold_i, fold_idx in enumerate(folds.split(x, y)):

                train_idx, test_idx = fold_idx
                x_train, x_test = x[train_idx], x[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]

                for p_i, p in enumerate(self._pipelines):
                    model = clone(p)
                    model.fit(x_train, y_train)

                    fitted_models_per_fold[fold_i, p_i] = model
                    y_pred_mat[test_idx, p_i, :] = self._get_predictions(model, x_test)

            fitted_models_per_iteration.append(fitted_models_per_fold)
            tmp_weights = self._get_weights(y, y_pred_mat)
            avg_probs = self._get_weighted_prediction(y_pred_mat, tmp_weights)
            loss = self._get_loss(y, avg_probs)
            weights_per_iteration.append(tmp_weights)

            # print("Iteration: {} Loss: {}".format(iter, loss))
            # print("Weights: ", tmp_weights)
            if loss < latest_loss:
                latest_loss = loss
                x = np.hstack((x, avg_probs))
            else:
                weights_per_iteration = weights_per_iteration[:-1]
                fitted_models_per_iteration = fitted_models_per_iteration[:-1]
                break

        self._weights_per_iteration = weights_per_iteration
        self._fitted_models_per_iteration = fitted_models_per_iteration
        return self

    def _get_predictions(self, model, x):
        if self.classification:
            if hasattr(model, "predict_proba"):
                pred = model.predict_proba(x)
            else:
                raise Exception("predict_proba method isn't found for {}"
                                .format(model.__class__.__name__))
        else:
            pred = np.reshape(model.predict(x), newshape=(-1, 1))
        return pred

    def predict(self, x):
        if self.classification:
            return self._le.inverse_transform(np.argmax(self.predict_proba(x), axis=-1))
        else:
            return np.argmax(self.predict_proba(x), axis=-1)

    def predict_proba(self, x):
        iters = len(self._weights_per_iteration)
        if iters < 0:
            raise Exception("DeepSuperLearner wasn't fitted!")

        x = np.asarray(x)
        j = self._n_classes
        avg_probs = np.zeros(shape=(x.shape[0], j))

        for iter in range(iters):
            y_pred_mat = np.zeros(shape=(x.shape[0], self.num_pipelines, j))
            fitted_models_per_fold = self._fitted_models_per_iteration[iter]

            for model_i in range(self.num_pipelines):
                model_probs_per_fold = np.empty(shape=(self._k_folds, x.shape[0], j))

                for fold_i in range(self._k_folds):
                    model = fitted_models_per_fold[fold_i, model_i]
                    model_probs_per_fold[fold_i, :, :] = self._get_predictions(model, x)

                model_avg_probs = np.mean(model_probs_per_fold, axis=0)
                y_pred_mat[:, model_i, :] = model_avg_probs

            optimized_weights = self._weights_per_iteration[iter]
            avg_probs = self._get_weighted_prediction(y_pred_mat, optimized_weights)
            x = np.hstack((x, avg_probs))

        return avg_probs
