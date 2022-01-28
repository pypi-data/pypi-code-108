from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
from collections import Counter

import numpy as np
from scipy.optimize import fmin_l_bfgs_b, nnls, fmin_slsqp
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import log_loss

from auger_ml.ensembles.utils import get_pipelines, filter_weights_and_pipelines
from auger_ml.ensembles.utils import get_score_func, labels_to_score_transform
from auger_ml.model_helper import ModelHelper


class SuperLearner(object):
    _param_choices = {
        'loss': ['l2', 'nloglike'],
        'method': ['slsqp', 'lbfgs', 'nnls']
    }

    _default_pipelines_shallow = ['catboostclassifier', 'xgbclassifier', 'lgbmclassifier',
                                  'randomforestclassifier', 'extratreesclassifier', 'linearsvc']

    _default_groups = Counter({'boost': 3, 'trees': 2, 'nns': 1, 'linear': 1, 'svm': 1})
    _default_groups_map = {'boost': ['catboostclassifier', 'xgbclassifier', 'lgbmclassifier',
                                     'gradientboostingclassifier', 'adaboostclassifier'],
                           'trees': ['randomforestclassifier', 'extratreesclassifier',
                                     'decisiontreeclassifier'],
                           'nns': ['shapeddeepneuralnetworkclassifier'],
                           'linear': ['linearsvc', 'logisticregression'],
                           'svm': ['svc']}

    def __init__(self, options, metadata, method='slsqp', opt_trials=3, trim_eps=1e-6, num_pipelines=6,
                 shallow=False):
        self.options = options

        self.method = method.lower()
        self.opt_trials = opt_trials
        self.trim_eps = trim_eps
        self.num_pipelines = num_pipelines

        self.classification = options['classification']
        if self.classification:
            self._loss = 'nloglike'
            keys = ('name', 'params', 'y_predicted_proba', 'uid')
        else:
            self._loss = 'l2'
            keys = ('name', 'params', 'y_predicted', 'uid')

        self._check_params()

        self._y = np.asarray(metadata['source_data'][options['targetFeature']])
        self._predictions = [{k: p[k] for k in keys} for p in metadata['predictions']]
        self._backup = {k: metadata['predictions'][0][k] for k in ('name', 'params', 'score')}

        #self._score_func, self.score_name = get_score_func(options['scoring'], options['classification'])
        self.score_name = options['scoring']
        self.options = options
        self.metadata = metadata
        self._score_names = options.get('scoreNames', [])
        self._target_feature = options['targetFeature']

        self._n_classes = 1
        if self.classification:
            self._indices = []
            self._le = LabelEncoder()
            self._n_classes = len(np.unique(self._y))
            self._get_indices = self._get_full
            if shallow:
                self._get_indices = self._get_shallow
            self._pipelines = self._get_pipelines()

        self.scores = None
        self._new_weights = None
        self._new_pipelines = None

    def _check_params(self):
        losses = SuperLearner._param_choices['loss']
        methods = SuperLearner._param_choices['method']

        assert self._loss in losses, \
            "Defined loss type {} isn't fit to allowed one {}".format(self._loss, losses)

        assert self.method in methods, \
            "Defined method type {} isn't fit to allowed one {}".format(self.method, methods)

        if self._loss == 'nloglike':
            assert self.method != 'nnls', \
                "Defined loss type {} isn't allowed for defined method {}".format(self._loss, self.method)

    def _get_pipelines(self):
        if self.num_pipelines > len(self._predictions):
            self.num_pipelines = len(self._predictions)
        # assert self.num_pipelines <= len(self._predictions), \
        #     "Number of provided pipelines is lower than desired num_pipelines"

        pipelines = get_pipelines(self._predictions, self.options)
        self._get_indices()

        idx = 0
        while len(self._indices) < self.num_pipelines:
            if idx not in self._indices:
                self._indices.append(idx)
            idx += 1

        self._predictions = [self._predictions[i] for i in self._indices]
        return [pipelines[i] for i in self._indices]

    def _get_shallow(self):
        default = SuperLearner._default_pipelines_shallow[:]

        for idx, p in enumerate(self._predictions):
            name = p['name'].lower()
            if name in default:
                self._indices.append(idx)
                del default[default.index(name)]

    def _get_full(self):
        groups = SuperLearner._default_groups
        group_names = SuperLearner._default_groups_map

        for idx, p in enumerate(self._predictions):
            if sum(groups.values()) == 0:
                break
            name = p['name'].lower()
            for group in groups:
                if name in group_names[group]:
                    if groups[group] > 0:
                        self._indices.append(idx)
                        # print(name, groups[group])
                        groups[group] -= 1

    def _restore(self):
        main_score = self._backup['score']
        self.scores = {self.score_name: main_score}
        return main_score, {'weights': [1.0],
                            'pipelines': [{k: self._backup[k] for k in ('name', 'params')}],
                            'classification': self.classification}

    def build(self):
        if self.classification:
            self._y = self._le.fit_transform(self._y)
            y_pred_cv = np.zeros(shape=(len(self._y), len(self._pipelines), self._n_classes))
        else:
            self._pipelines = get_pipelines(self._predictions, self.options)
            y_pred_cv = np.zeros(shape=(len(self._y), len(self._pipelines)))

        if not self._pipelines:
            return self._restore()

        if self.classification:
            for idx, p in enumerate(self._predictions):
                preds = np.asarray(p['y_predicted_proba'])
                if preds.ndim == 2 and preds[0][0] is not None:
                    y_pred_cv[:, idx, :] = preds
        else:
            for idx, p in enumerate(self._predictions):
                # y_pred_cv[:, idx] = np.squeeze(np.asarray(p['y_predicted']))
                y_pred_cv[:, idx] = np.reshape(np.asarray(p['y_predicted']), (-1,))

        weights = self._get_weights(self._y, y_pred_cv)
        main_score, y_pred_weighted = self._get_score(y_pred_cv, weights)

        self.scores = {self.score_name: main_score}
        self._calc_extra_scores(y_pred_weighted)

        self._new_weights, self._new_pipelines = filter_weights_and_pipelines(weights, self._predictions)
        return main_score, {'weights': self._new_weights,
                            'pipelines': self._new_pipelines,
                            'classification': self.classification}

    def predict_proba(self, x):
        assert self._new_weights is not None, "You should build ensemble first, before calling predict_proba"

        predicts = np.asarray([p.predict_proba(x) for p in self._new_pipelines])
        for i in range(predicts.shape[0]):
            predicts[i, :] = predicts[i, :] * self._new_weights[i]

        return np.sum(predicts, axis=0)

    def _get_score(self, y_pred_cv, weights):
        if self.classification:
            y = labels_to_score_transform(self.score_name, self._y, self._n_classes)
        else:
            y = self._y

        y_pred_weighted = self._get_weighted_prediction(y_pred_cv, weights)

        if self.score_name == 'roi':
            if y_pred_weighted.ndim == 1:
                score = ModelHelper.calculate_roi(self.options, self.metadata['test_roi_data'], y, y_pred_weighted)
            else:
                score = 0 #TODO: support roi for classification    
        else:        
            _score_func, _ = get_score_func(self.score_name, self.options['classification'])
            score = _score_func(y, y_pred_weighted)

        return score, y_pred_weighted

    def _calc_extra_scores(self, y_pred_weighted):
        for score_name in self._score_names:
            try:
                if self.score_name == 'roi':
                    if y_pred_weighted.ndim == 1:
                        self.scores[score_name] = ModelHelper.calculate_roi(self.options, 
                            self.metadata['test_roi_data'], self._y, y_pred_weighted)
                    else:
                        score = 0 #TODO: support roi for classification                        
                else:        
                    _score_func, _ = get_score_func(score_name, self.classification)
                    self.scores[score_name] = _score_func(self._y, y_pred_weighted)
            except Exception as e:
                if score_name == self._target_feature:
                    raise

                logging.error("Ensemble score %s failed to build: %s" % (score_name, str(e)))
                self.scores[score_name] = 0

    def _get_weights(self, y, y_pred_cv):
        def init():
            return np.array([1. / len(self._pipelines)] * len(self._pipelines)), \
                [(0, 1)] * len(self._pipelines)

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
