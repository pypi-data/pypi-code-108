from collections import Counter
import numpy as np
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from sklearn.preprocessing import LabelEncoder
from sklearn.utils import check_random_state

from auger_ml.ensembles.utils import get_pipelines, filter_weights_and_pipelines
from auger_ml.ensembles.utils import get_score_func, labels_to_score_transform


class GreedySelection(object):    # BaseEstimator, ClassifierMixin
    def __init__(self, options, metadata, improve_eps=False, random_state=12345,
                 prune_fraction=0.0, n_best=1, n_bags=3, bag_fraction=0.5, max_bag_pipelines=3):
        self.options = options
        self.classification = True

        self.improve_eps = improve_eps
        self.random_state = random_state
        self.prune_fraction = prune_fraction
        self.n_best = n_best
        self.n_bags = n_bags
        self.bag_fraction = bag_fraction
        self.max_bag_pipelines = max_bag_pipelines

        # Set parameters
        self._y = np.asarray(metadata['source_data'][options['targetFeature']])
        self._le = LabelEncoder()

        self._score_func, self.score_name = get_score_func(options['scoring'], options['classification'])
        self._score_names = options.get('scoreNames', [])
        self._target_feature = options['targetFeature']

        keys = ('name', 'params', 'score', 'y_predicted_proba', 'uid')
        self._predictions = [{k: p[k] for k in keys} for p in metadata['predictions']]
        self._pipelines = get_pipelines(self._predictions, options)

        self._ensemble = Counter()
        self._pipelines_scores = []

        self._n_classes = 1
        if self.classification:
            self._n_classes = len(np.unique(self._y))

        self.scores = None
        self._new_weights = None
        self._new_pipelines = None

        self._check_params()

    def _check_params(self):
        num_pipelines = len(self._pipelines)
        if num_pipelines < self.n_best:
            self.n_best = num_pipelines

        min_pipelines = int(int(len(self._pipelines) * (1 - self.prune_fraction)) * self.bag_fraction)
        if min_pipelines < 1:
            self.prune_fraction = 0.0

        min_pipelines = int(int(len(self._pipelines) * (1 - self.prune_fraction)) * self.bag_fraction)
        if min_pipelines < 1:
            self.bag_fraction = 1.0

        min_pipelines = int(int(len(self._pipelines) * (1 - self.prune_fraction)) * self.bag_fraction)
        # assert min_pipelines > 0, "You feed a small number of pipelines respect to " \
        #                           "prune_fraction={} and bag_fraction={}" \
        #                           .format(self.prune_fraction, self.bag_fraction)

        min_bag_size = min(min_pipelines, self.n_best)
        # assert min_bag_size < self.max_bag_pipelines, "You should lower 'n_best' parameter or feed larger" \
        #                                               " number of pipelines respect to fraction parameters"
        if self.max_bag_pipelines > min_bag_size:
            self.max_bag_pipelines = min_bag_size

        if self.n_best == self.max_bag_pipelines:
            self.n_bags = 1

    def build(self):
        self._estimate_pipelines()
        self._build_ensemble()

        total = float(sum(self._ensemble.values()))
        for model in self._ensemble:
            self._ensemble[model] /= total

        score, weights, ensemble_probs = self._get_score_and_weights()
        self._new_weights, self._new_pipelines = filter_weights_and_pipelines(weights, self._predictions)

        self.scores = {self.score_name: score}
        self._calc_extra_scores(ensemble_probs)

        return score, {'weights': self._new_weights,
                       'pipelines': self._new_pipelines,
                       'classification': True}

    def predict_proba(self, x):
        assert self._new_weights is not None, "You should build ensemble first, before calling predict_proba"

        predicts = np.asarray([p.predict_proba(x) for p in self._new_pipelines])
        for i in range(predicts.shape[0]):
            predicts[i, :] = predicts[i, :] * self._new_weights[i]

        return np.sum(predicts, axis=0)

    def _get_score_and_weights(self):
        ensemble_weights = [0] * len(self._pipelines)
        ensemble_probs = np.zeros((self._y.shape[0], self._n_classes))

        for idx, weight in self._ensemble.items():
            ensemble_weights[idx] = weight
            ensemble_probs += np.asarray(self._predictions[idx]['y_predicted_proba']) * weight

        score = self._score_func(self._y, ensemble_probs)
        return score, ensemble_weights, ensemble_probs

    def _calc_extra_scores(self, ensemble_probs):
        for score_name in self._score_names:
            try:
                self._score_func, _ = get_score_func(score_name, self.classification)
                self.scores[score_name] = self._score_func(self._y, ensemble_probs)
            except Exception as e:
                if score_name == self._target_feature:
                    raise

                logging.error("Ensemble score %s failed to build: %s" % (score_name, str(e)))
                self.scores[score_name] = 0

    def _estimate_pipelines(self):
        """ Get score and probabilities from the given pipelines. """
        self._y = self._le.fit_transform(self._y)
        self._y = labels_to_score_transform(self.score_name, self._y, self._n_classes)

        idx_to_exclude = []
        for idx, pred in enumerate(self._predictions):
            probs = np.asarray(pred['y_predicted_proba'])
            if probs.ndim == 2 and probs[0][0] is not None:
                self._pipelines_scores.append((pred['score'], probs))
            else:
                idx_to_exclude.append(idx)

        self._predictions = [pred for idx, pred in enumerate(self._predictions) if idx not in idx_to_exclude]
        self._pipelines = [p for p in self._predictions]
        # self._pipelines = [pred for idx, pred in enumerate(self._predictions) if idx not in idx_to_exclude]
        self._check_params()

        # reorder
        new_order = list(np.argsort([p[0] for p in self._pipelines_scores]))
        self._pipelines = [self._pipelines[i] for i in new_order]
        self._pipelines_scores = [self._pipelines_scores[i] for i in new_order]

    def _build_ensemble(self):
        n_clfs = int(len(self._pipelines) * (1 - self.prune_fraction))
        bag_size = int(self.bag_fraction * n_clfs)

        bag_ensembles = []
        rs = check_random_state(self.random_state)

        for i in range(self.n_bags):
            # get bag_size elements at random
            cand_idx = sorted(rs.permutation(n_clfs)[:bag_size])
            bag_ensemble = self._ensemble_from_candidates(cand_idx)
            bag_ensembles.append(bag_ensemble)

        # combine ensembles from each bag
        for e in bag_ensembles:
            self._ensemble += e

    def _get_ensemble_score(self, idx):
        ensemble_probs = np.zeros((self._y.shape[0], self._n_classes))

        for inner_idx in idx:
            ensemble_probs += self._pipelines_scores[inner_idx][1] * inner_idx
        ensemble_probs /= len(idx)

        score = self._score_func(self._y, ensemble_probs)
        return score, ensemble_probs

    def _ensemble_from_candidates(self, idx):
        ensemble = Counter(idx[:self.n_best])
        ens_score, ens_probs = self._get_ensemble_score(idx)
        n_clfs = sum(ensemble.values())

        cand_ensembles = []
        while n_clfs < self.max_bag_pipelines:
            new_ens = []

            for inner_idx in idx:
                new_clf_proba = self._pipelines_scores[inner_idx][1]
                new_ens_proba = (ens_probs * n_clfs + new_clf_proba) / (n_clfs + 1)

                new_ens_score = self._score_func(self._y, new_ens_proba)
                new_ens.append({'score': new_ens_score, 'idx': inner_idx})

            # sort scores, so the best with index 0
            new_ens.sort(key=lambda t: t['score'], reverse=True)

            last_ens_score = ens_score
            ens_score = new_ens[0]['score']

            if self.improve_eps:
                # if score improvement is less than epsilon -> don't add & stop
                score_diff = ens_score - last_ens_score
                if score_diff < self.improve_eps:
                    break   # continue

            new_pipeline_idx = new_ens[0]['idx']
            ensemble.update({new_pipeline_idx: 1})

            if not self.improve_eps:
                # store current ensemble to select best later
                ens_copy = Counter(ensemble)
                cand = {'ens': ens_copy, 'score': ens_score}
                cand_ensembles.append(cand)

            n_clfs = sum(ensemble.values())

        if not self.improve_eps and n_clfs == self.max_bag_pipelines and cand_ensembles:
            ensemble = max(cand_ensembles, key=lambda t: t['score'])['ens']

        return ensemble
