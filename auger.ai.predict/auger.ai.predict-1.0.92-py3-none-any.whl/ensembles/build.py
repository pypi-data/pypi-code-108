import numpy as np
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from sklearn.preprocessing import LabelEncoder
from auger_ml.ensembles.utils import get_score_func, preds_accumulator
from auger_ml.Utils import remove_dups_from_list
from auger_ml.model_helper import ModelHelper


class EnsembleSelection(object):
    def __init__(self, options, metadata, max_pipelines=3):
        self.max_pipelines = max_pipelines
        self.classification = options['classification']

        self._y = metadata['source_data'][options['targetFeature']].values
        self._preds, self._y_pred = self._init_preds(metadata['predictions'])

        #self._score_func, self.score_name = get_score_func(options['scoring'], options['classification'])
        self.options = options
        self.metadata = metadata
        self._score_names = options.get('scoreNames', [])
        self._target_feature = options['targetFeature']

        self._scores = []
        self.scores = None

        self._n_classes = 1
        if self.classification:
            self._get_scores = self._get_cl_scores
            self._n_classes = len(np.unique(self._y))
        else:
            self._get_scores = self._get_reg_scores

    @staticmethod
    def _init_preds(metadata):
        keys = ('name', 'params', 'score', 'y_predicted', 'y_predicted_proba', 'uid')
        preds = [{k: p[k] for k in keys} for p in metadata]

        y_pred = []
        idx_to_exclude = []

        for idx, model in enumerate(preds):
            # pred = np.squeeze(np.asarray(model['y_predicted']))
            pred = np.reshape(np.asarray(model['y_predicted']), (-1,))
            if pred[0] is not None:
                y_pred.append(pred)
            else:
                idx_to_exclude.append(idx)

        return [pred for idx, pred in enumerate(preds) if idx not in idx_to_exclude], y_pred

    def select(self):
        if len(self._preds) < self.max_pipelines:
            idx = np.arange(len(self._preds))
            self.max_pipelines = len(self._preds)
        else:
            self._get_scores()
            idx = self._get_best_models()
        preds = np.asarray(self._preds)[idx]

        score = self._calc_scores(preds)
        pipelines = [{'name': p['name'], 'params': p['params'], 'uid': p['uid']} for p in preds]

        return score, pipelines

    def _calc_scores(self, preds):
        preds_cnt = max(1, len(preds))

        if self.classification:
            # self._y = LabelEncoder().fit_transform(self._y)
            y_pred = np.zeros((self._y.shape[0], self._n_classes))

            for p in preds:
                pred = np.asarray(p['y_predicted_proba'])
                y_pred, preds_cnt = preds_accumulator(pred, y_pred, preds_cnt)
        else:
            y_pred = np.zeros((self._y.shape[0], ))
            for p in preds:
                # pred = np.squeeze(np.asarray(p['y_predicted']))
                pred = np.reshape(np.asarray(p['y_predicted']), (-1,))
                y_pred, preds_cnt = preds_accumulator(pred, y_pred, preds_cnt)

        y_pred = y_pred / float(preds_cnt)

        if self.options['scoring'] == 'roi':
            score_name = 'roi'
            if y_pred.ndim == 1:
                score = ModelHelper.calculate_roi(self.options, self.metadata['test_roi_data'], self._y, y_pred)
            else:
                score = 0 #TODO: support roi for classification                
        else:    
            _score_func, score_name = get_score_func(self.options['scoring'], self.options['classification'])
            score = _score_func(self._y, y_pred)

        self.scores = {score_name: score}

        for score_name in self._score_names:
            try:
                if score_name == 'roi':
                    if y_pred.ndim == 1:
                        self.scores[score_name] = ModelHelper.calculate_roi(self.options, 
                            self.metadata['test_roi_data'], self._y, y_pred)
                    else:
                        score = 0 #TODO: support roi for classification                        
                else:    
                    _score_func, _ = get_score_func(score_name, self.classification)
                    self.scores[score_name] = _score_func(self._y, y_pred)
            except Exception as e:
                if score_name == self._target_feature:
                    raise

                logging.error("Ensemble score %s failed to build: %s" % (score_name, str(e)))
                self.scores[score_name] = 0

        return score

    def _get_cl_scores(self):
        for i, y_pred in enumerate(self._y_pred):
            cur_corr = []
            for j in range(i + 1, len(self._y_pred)):
                match = (y_pred == self._y_pred[j])
                cur_corr.append(match.sum() / float(match.size))
            if cur_corr:
                decorr = 1.0 - np.asarray(cur_corr)
                scores = [el['score'] for el in self._preds[i + 1:]]
                inner_score = (self._preds[i]['score'] + np.asarray(scores)) / 2.
                self._scores.append(decorr + inner_score)

    def _get_reg_scores(self):
        scores = []
        corrs = []
        for i, y_pred in enumerate(self._y_pred):
            cur_corr = []
            for j in range(i + 1, len(self._y_pred)):
                match = np.abs(y_pred - self._y_pred[j])
                cur_corr.append(np.sum(match) / match.shape[0])
            if cur_corr:
                mate_scores = [el['score'] for el in self._preds[i + 1:]]
                scores.append((self._preds[i]['score'] + np.asarray(mate_scores)) / 2.)
                corrs.append(np.asarray(cur_corr))

        scores_normalized = self.__normalize(np.concatenate(scores))
        size = len(scores)
        for idx, el in enumerate(scores):
            idx_start = idx * (size - idx)
            res = corrs[idx] + scores_normalized[idx_start:idx_start + len(el)]
            self._scores.append(res)

    def _get_best_models(self):  # by idx for now
        scores = np.concatenate(self._scores)
        best_pair_idx = np.argmax(scores)
        best_models_idx = self.__get_models_by_idx(best_pair_idx)

        for idx in range(self.max_pipelines - 1):
            scores[best_pair_idx] = 0.
            best_pair_idx = np.argmax(scores)
            best_models_idx += self.__get_models_by_idx(best_pair_idx)

        best_models_idx = remove_dups_from_list(best_models_idx)
        return best_models_idx[:self.max_pipelines]

    def __get_models_by_idx(self, idx):
        first = -1
        size = len(self._scores)
        while idx > 0:
            idx -= size
            first += 1
            size -= 1
        return [first, idx + size]

    @staticmethod
    def __normalize(vec, eps=1e-8):
        vec = np.asarray(vec)
        norm = np.linalg.norm(vec, ord=1)
        if norm < eps:
            norm = np.finfo(vec.dtype).eps
        return vec / norm
