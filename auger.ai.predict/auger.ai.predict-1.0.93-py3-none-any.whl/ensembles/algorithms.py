import copy
import sklearn.base
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from auger_ml.ensembles import load_data
from auger_ml.ensembles.build import EnsembleSelection
from auger_ml.ensembles.base import Ensemble, Voting, Averaging
from auger_ml.ensembles.greedy_selection import GreedySelection
from auger_ml.ensembles.super_learner import SuperLearner
from auger_ml.ensembles.deep_super_learner import DeepSuperLearner
from auger_ml.ensembles.deep_ensemble import DeepEnsemble


class ShowEnsemble(object):
    def __init__(self, name, algorithms):
        self._params = {'ensemble': name, 'algorithms': algorithms}

    def get_params(self, deep=False):
        return self._params


class EnsembleOptimizer(object):
    def __init__(self, optimizer_params, options, _trialsQueue=None):
        self.optimizer_params = optimizer_params
        self.options = options

        # logging.info("Init optimizer: %s(%s). Algotithm: %s" % (self.options['optimizer_name'], self.options['optimizer_params'], self.options.get('optimizer_algorithm', '')))

    def get_next_trials(self):
        return [{'algorithm_name': self.options['optimizer_algorithm'][0], 'algorithm_params': self.options['optimizer_algorithm'][1],
                 'trialClass': 'auger_ml.core.AugerMLTrial.AugerMLTrialEnsemble'}], None



class BaseEnsembleAlgorithm(sklearn.base.BaseEstimator):
    def fit(self, x, y):
        self._ensemble.fit(x, y)
        return self

    def predict(self, x):
        return self._ensemble.predict(x)

    def get_params(self, deep=False):
        return self._params

    def _create_ensemble(self, params, options):
        return Ensemble(options, **params)

    def _init_steps(self, params, options):
        self._ensemble = self._create_ensemble(params, options)
        show_ensemble = ShowEnsemble(type(self).__name__, [p['name'].split('.')[-1] for p in params['pipelines']])
        self.steps = [(type(self).__name__.lower(), show_ensemble)]

    def predict_proba(self, x):
        return self._ensemble.predict_proba(x)

    @property
    def classes_(self):
        return self._ensemble.classes_

    @property
    def feature_importances_(self):
        return self._ensemble.feature_importances_

    @property
    def coef_(self):
        return self._ensemble.coef_


class _SuperLearnerAlgorithm(BaseEnsembleAlgorithm):
    def __init__(self, method, opt_trials, trim_eps, num_pipelines,
                 classification, _steps_params, options):
        self._params = dict(
            method=method,
            opt_trials=opt_trials,
            trim_eps=trim_eps,
            num_pipelines=num_pipelines,
            _steps_params=_steps_params,
            options=options
        )
        self._learner_params = dict(method=method, opt_trials=opt_trials, trim_eps=trim_eps)
        self._ensemble = None
        self.steps = []
        self._estimator_type = 'classifier' if classification else 'regressor'
        if _steps_params is not None:
            self._init_steps(_steps_params, options)

    @staticmethod
    def infer_additional_params(trial):
        return {'options': copy.copy(trial)}

    def build_ensemble_and_update_algorithm_params(self, options, algorithm_params):
        d = load_data.load(options)
        ens = SuperLearner(options, d, **self._learner_params)
        score, params = ens.build()
        self._init_steps(params, options)
        algorithm_params['_steps_params'] = params
        return score, ens.scores


class DeepSuperLearnerAlgorithm(BaseEnsembleAlgorithm):
    def __init__(self, method='slsqp', k_folds=3, opt_trials=3, trim_eps=1e-6, max_iters=12, num_pipelines=5,
                 classification=True, _steps_params=None):
        self._params = dict(
            method=method,
            k_folds=k_folds,
            opt_trials=opt_trials,
            trim_eps=trim_eps,
            max_iters=max_iters,
            num_pipelines=num_pipelines,
            classification=classification,
            _steps_params=_steps_params
        )
        self._learner_params = dict(method=method, opt_trials=opt_trials, trim_eps=trim_eps,
                                    max_iters=max_iters, num_pipelines=num_pipelines)
        self._ensemble = None
        self.steps = []
        self._estimator_type = 'classifier'  # if classification else 'regressor'
        if _steps_params is not None:
            self._init_steps(_steps_params)

    def build_ensemble_and_update_algorithm_params(self, options, algorithm_params):
        d = load_data.load(options)
        ens = DeepSuperLearner(options, d, **self._learner_params)
        score, params = ens.build()

        self._init_steps(params, {})
        algorithm_params['_steps_params'] = params
        return score, ens.scores

    def _create_ensemble(self, params, options):
        return DeepEnsemble(**params)


class GreedySelectionAlgorithm(BaseEnsembleAlgorithm):
    def __init__(
        self,
        improve_eps=False,
        random_state=12345,
        prune_fraction=0.0,
        n_best=1,
        n_bags=3,
        bag_fraction=0.5,
        max_bag_pipelines=3,
        _steps_params=None,
        options=None
    ):
        self._params = dict(
            improve_eps=improve_eps,
            random_state=random_state,
            prune_fraction=prune_fraction,
            n_best=n_best,
            n_bags=n_bags,
            bag_fraction=bag_fraction,
            max_bag_pipelines=max_bag_pipelines,
            _steps_params=_steps_params,
            options=options
        )
        self._selection_params = dict(
            improve_eps=improve_eps,
            random_state=random_state,
            prune_fraction=prune_fraction,
            n_best=n_best,
            n_bags=n_bags,
            bag_fraction=bag_fraction,
            max_bag_pipelines=max_bag_pipelines
        )
        self._ensemble = None
        self.steps = []
        self._estimator_type = 'classifier'
        if _steps_params is not None:
            self._init_steps(_steps_params, options)

    @staticmethod
    def infer_additional_params(trial):
        return {'options': copy.copy(trial)}

    def build_ensemble_and_update_algorithm_params(self, options, algorithm_params):
        d = load_data.load(options)
        ens = GreedySelection(options, d, **self._selection_params)
        score, params = ens.build()
        self._init_steps(params, options)
        algorithm_params['_steps_params'] = params
        return score, ens.scores


class VotingAlgorithm(BaseEnsembleAlgorithm):
    def __init__(self, n_best=3, weights=None, voting='soft', _steps_params=None, options=None):
        self._params = dict(
            n_best=n_best,
            weights=weights,
            voting=voting,
            _steps_params=_steps_params,
            options=options
        )
        self._n_best = n_best
        self._weights = weights
        self._voting = voting
        self._ensemble = None
        self.steps = []
        self._estimator_type = 'classifier'
        if _steps_params is not None:
            self._init_steps(_steps_params, options)

    @staticmethod
    def infer_additional_params(trial):
        return {'options': copy.copy(trial)}

    def build_ensemble_and_update_algorithm_params(self, options, algorithm_params):
        d = load_data.load(options)
        selector = EnsembleSelection(options, d, max_pipelines=self._n_best)
        score, pipelines = selector.select()
        params = dict(
            pipelines=pipelines,
            weights=self._weights,
            n_best=self._n_best,
            voting=self._voting
        )
        self._init_steps(params, options)
        algorithm_params['_steps_params'] = params
        return score, selector.scores

    def _create_ensemble(self, params, options):
        return Voting(options, **params)


class _AveragingAlgorithm(BaseEnsembleAlgorithm):
    def __init__(self, n_best, weights, classification, _steps_params, options):
        self._params = dict(
            n_best=n_best,
            weights=weights,
            _steps_params=_steps_params,
            options=options
        )
        self._n_best = n_best
        self._weights = weights
        self._classification = classification
        self._ensemble = None
        self.steps = []
        self._estimator_type = 'classifier' if classification else 'regressor'
        if _steps_params is not None:
            self._init_steps(_steps_params, options)

    @staticmethod
    def infer_additional_params(trial):
        return {'options': copy.copy(trial)}

    def build_ensemble_and_update_algorithm_params(self, options, algorithm_params):
        d = load_data.load(options)
        selector = EnsembleSelection(options, d, max_pipelines=self._n_best)
        score, pipelines = selector.select()
        params = dict(
            pipelines=pipelines,
            weights=self._weights,
            n_best=self._n_best,
            classification=self._classification
        )
        self._init_steps(params, options)
        algorithm_params['_steps_params'] = params
        return score, selector.scores

    def _create_ensemble(self, params, options):
        return Averaging(options, **params)


class AveragingAlgorithmRegressor(_AveragingAlgorithm):
    def __init__(self, n_best=3, weights=None, _steps_params=None, options=None):
        super(AveragingAlgorithmRegressor, self).__init__(
            n_best=n_best,
            weights=weights,
            classification=False,
            _steps_params=_steps_params,
            options=options
        )


class AveragingAlgorithmClassifier(_AveragingAlgorithm):
    def __init__(self, n_best=3, weights=None, _steps_params=None, options=None):
        super(AveragingAlgorithmClassifier, self).__init__(
            n_best=n_best,
            weights=weights,
            classification=True,
            _steps_params=_steps_params,
            options=options
        )


class SuperLearnerAlgorithmRegressor(_SuperLearnerAlgorithm):
    def __init__(self, method='slsqp', opt_trials=3, trim_eps=1e-6, num_pipelines=5,
                 _steps_params=None, options=None):
        super(SuperLearnerAlgorithmRegressor, self).__init__(
            method=method,
            opt_trials=opt_trials,
            trim_eps=trim_eps,
            num_pipelines=num_pipelines,
            classification=False,
            _steps_params=_steps_params,
            options=options
        )


class SuperLearnerAlgorithmClassifier(_SuperLearnerAlgorithm):
    def __init__(self, method='slsqp', opt_trials=3, trim_eps=1e-6, num_pipelines=5,
                 _steps_params=None, options=None):
        super(SuperLearnerAlgorithmClassifier, self).__init__(
            method=method,
            opt_trials=opt_trials,
            trim_eps=trim_eps,
            num_pipelines=num_pipelines,
            classification=True,
            _steps_params=_steps_params,
            options=options
        )

