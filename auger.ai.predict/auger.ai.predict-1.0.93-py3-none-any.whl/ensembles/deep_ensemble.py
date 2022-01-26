import numpy as np
from scipy.optimize import fmin_l_bfgs_b, nnls, fmin_slsqp

from sklearn import clone
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import log_loss

from auger_ml.ensembles.base import BaseEnsemble


class DeepEnsemble(BaseEnsemble):
    def __init__(self, pipelines, method='slsqp', k_folds=3,
                 opt_trials=3, trim_eps=1e-6, max_iters=12,
                 classification=True):
        super(DeepEnsemble, self).__init__(
            pipelines=pipelines,
            classification=classification,
            params=dict(
                pipelines=pipelines,
                classification=classification
            )
        )

        self.method = method
        self.k_folds = k_folds
        self.opt_trials = opt_trials
        self.trim_eps = trim_eps
        self.max_iters = max_iters

        self._n_classes = 1
        if self.classification:
            self._loss = 'nloglike'
        else:
            self._loss = 'l2'

        self._weights_per_iteration = None
        self._fitted_models_per_iteration = None

    def fit(self, x, y):
        x = np.asarray(x)
        y = np.asarray(y)

        if self.classification:
            y = self.le.fit_transform(y)
            self._n_classes = len(np.unique(y))

        weights_per_iteration = []
        fitted_models_per_iteration = []
        latest_loss = np.finfo(np.double).max

        for iter in range(self.max_iters):
            fitted_models_per_fold = np.empty(shape=(self.k_folds, len(self.pipelines)), dtype=np.object)
            y_pred_mat = np.zeros(shape=(y.shape[0], len(self.pipelines), self._n_classes))
            # regression

            folds = StratifiedKFold(n_splits=self.k_folds, shuffle=False)
            for fold_i, fold_idx in enumerate(folds.split(x, y)):

                train_idx, test_idx = fold_idx
                x_train, x_test = x[train_idx], x[test_idx]
                y_train, y_test = y[train_idx], y[test_idx]

                for p_i, p in enumerate(self.pipelines):
                    model = clone(p)
                    model.fit(x_train, y_train)

                    fitted_models_per_fold[fold_i, p_i] = model
                    y_pred_mat[test_idx, p_i, :] = self._get_predictions(model, x_test)

            fitted_models_per_iteration.append(fitted_models_per_fold)
            tmp_weights = self._get_weights(y, y_pred_mat)
            avg_probs = self._get_weighted_prediction(y_pred_mat, tmp_weights)
            loss = self._get_loss(y, avg_probs)
            weights_per_iteration.append(tmp_weights)

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

    def _get_weights(self, y, y_pred_cv):
        def init():
            return np.array([1. / len(self.pipelines)] * len(self.pipelines)), \
                [(0, 1)] * len(self.pipelines)

        def ff(x):
            return self._get_loss(y, self._get_weighted_prediction(y_pred_cv, x))

        if self.method == 'lbfgs':
            c, maxls = 0, 20
            x0, bounds = init()
            for i in range(self.opt_trials):
                coef_init, b, c = fmin_l_bfgs_b(ff, x0, bounds=bounds, approx_grad=True, maxls=maxls)
                c = c['warnflag']
                if c is 0:
                    break
                else:
                    maxls *= 2
                    print('Optimization procedure is failed -> it tries one more time...')
            assert c is 0, "Error code {}: -> " \
                           "fmin_l_bfgs_b failed when trying to calculate coefficients".format(c)

        elif self.method == 'nnls':
            coef_init, b = nnls(y_pred_cv, y)

        elif self.method == 'slsqp':
            def constr(x):
                return np.array([np.sum(x) - 1])

            d, iter = 0, 100
            x0, bounds = init()
            for i in range(self.opt_trials):
                coef_init, b, c, d, e = fmin_slsqp(ff, x0, f_eqcons=constr, bounds=bounds,
                                                   disp=0, full_output=True, iter=iter)
                if d is 0:
                    break
                else:
                    iter *= 2
                    print('Optimization procedure is failed -> it tries one more time...')
            assert d is 0, "Error code {}: -> " \
                           "fmin_slsqp failed when trying to calculate coefficients".format(d)

        coef_init = np.array(coef_init)
        coef_init[coef_init < np.sqrt(np.finfo(np.double).eps)] = 0
        s = np.sum(coef_init)
        if s == 0:
            coef_init[:] = 1.0
            s = np.sum(coef_init)
        return coef_init / s

    def _get_weighted_prediction(self, y_pred_mat, coef):
        if self._loss == 'l2':
            return np.dot(y_pred_mat, coef)
        elif self._loss == 'nloglike':
            y_pred_mat = np.clip(y_pred_mat, self.trim_eps, 1 - self.trim_eps)
            for idx in range(coef.shape[0]):
                y_pred_mat[:, idx, :] = y_pred_mat[:, idx, :] * coef[idx]
            return np.sum(y_pred_mat, axis=1)

    def _get_loss(self, y, y_pred, sample_weight=None):
        if self._loss == 'l2':
            return np.mean((y - y_pred) ** 2)
        elif self._loss == 'nloglike':
            return log_loss(y, y_pred, eps=self.trim_eps, sample_weight=sample_weight)

    def predict(self, x):
        if self.classification:
            return self.le.inverse_transform(np.argmax(self.predict_proba(x), axis=-1))
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
            y_pred_mat = np.zeros(shape=(x.shape[0], len(self.pipelines), j))
            fitted_models_per_fold = self._fitted_models_per_iteration[iter]

            for model_i in range(len(self.pipelines)):
                model_probs_per_fold = np.empty(shape=(self.k_folds, x.shape[0], j))

                for fold_i in range(self.k_folds):
                    model = fitted_models_per_fold[fold_i, model_i]
                    model_probs_per_fold[fold_i, :, :] = self._get_predictions(model, x)

                model_avg_probs = np.mean(model_probs_per_fold, axis=0)
                y_pred_mat[:, model_i, :] = model_avg_probs

            optimized_weights = self._weights_per_iteration[iter]
            avg_probs = self._get_weighted_prediction(y_pred_mat, optimized_weights)
            x = np.hstack((x, avg_probs))

        return avg_probs
