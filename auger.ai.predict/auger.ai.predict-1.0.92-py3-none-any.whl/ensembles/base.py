import numpy as np

# from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import LabelEncoder

from auger_ml.ensembles.utils import get_pipelines


class BaseEnsemble(object):
    """ Base class for all Ensemble classes.

    Note: this class should not be used directly -> Use derived classes instead.

    Parameters
    ----------
    pipelines : list of pipelines, which is used for ensemble.
    """
    def __init__(self, options, pipelines, classification, params):
        self.pipelines = get_pipelines(pipelines, options)

        self.classification = classification
        self._params = params
        self.le = LabelEncoder()
        self.options = options
        self.is_fitted = False
        self._num_features = None

    def get_pipelines_fold_group(self):
        from auger_ml.preprocessors.space import pspace_get_fold_group        

        pipelines_fold_group = []
        for p in self.pipelines:
            name = type(p).__name__
            res = pspace_get_fold_group(name, self.options.get('timeSeriesFeatures'))
            pipelines_fold_group.append(res)
           
        return pipelines_fold_group
            
    def fit(self, x, y):
        """ Fit defined pipelines.

        Parameters
        ----------
        x : {array-like, matrix}, shape = [n_samples, n_features].

        y : array-like, shape = [n_samples] -> target values.

        Returns
        -------
        self : object
        """
        from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas

        res = []
        pipelines_fold_group = self.get_pipelines_fold_group()
        self._num_features = x[pipelines_fold_group[0]].shape[1]
        process_lightgbm = False
        while True:
            for idx, p in enumerate(self.pipelines):
                if process_lightgbm != ('lightgbm' in str(type(p))):
                    #logging.info("Pass:%s"%type(p))
                    continue

                x_fold = x[pipelines_fold_group[idx]]
                y_fold = y[pipelines_fold_group[idx]]
                if self.classification:
                    y_fold = self.le.fit_transform(y_fold)

                if 'lightgbm' in str(type(p)):
                    ds = DataSourceAPIPandas({})
                    ds.df = x_fold
                    ds.encode_features()

                res.append(p.fit(x_fold, y_fold))

            if process_lightgbm:
                break

            process_lightgbm = True

        self.pipelines = res
        self.is_fitted = True
        return self

    def get_params(self, deep=False):
        return self._params

    def _predict(self, x):
        """ Collect predictions as labels for defined pipelines
        within an array-like, shape = [n_pipelines, n_samples]. """
        res = []
        pipelines_fold_group = self.get_pipelines_fold_group()

        for idx, p in enumerate(self.pipelines):
            x_fold = x[pipelines_fold_group[idx]]
            pred = p.predict(x_fold)
            if len(np.asarray(pred).shape) > 0:
                res.append(pred)

        return np.asarray(res)

    def _predict_proba(self, x):
        """ Collect predictions as probabilities for defined pipelines
        within an array-like, shape = [n_pipelines, n_samples, n_classes]. """
        res = []
        pipelines_fold_group = self.get_pipelines_fold_group()

        for idx, p in enumerate(self.pipelines):
            x_fold = x[pipelines_fold_group[idx]]
            try:
                res.append(p.predict_proba(x_fold))
            except AttributeError as e:
                res.append(p._predict_proba(x_fold))
                        
        return np.asarray(res)

    def __len__(self):
        """ Returns the number of pipelines within the ensemble."""
        return len(self.pipelines)

    def __getitem__(self, index):
        """ Returns the index'th pipeline in the ensemble."""
        return self.pipelines[index]

    def __iter__(self):
        """ Returns iterator over list of pipelines within the ensemble."""
        return iter(self.pipelines)

    @property
    def classes_(self):
        p = self.pipelines[0]
        if hasattr(p, 'classes_'):
            return p.classes_
        else:
            return NotImplementedError

    @property
    def feature_importances_(self):
        from auger_ml.model_helper import ModelHelper

        values = None
        cnt = 0
        fi_names = None
        if not self._num_features:
            for pipeline in self._params['pipelines']:
                fi_names_, fi_data_ = ModelHelper.get_feature_importances(self.options, pipeline['uid'])
                if fi_names is None:
                    fi_names = fi_names_

                fi_data = [0.0]*len(fi_names)
                for idx, name in enumerate(fi_names_):
                    if name in fi_names:
                        idx_name = fi_names.index(name)
                        fi_data[idx_name] = fi_data_[idx]

                if values is None:
                    values = np.asarray(fi_data, dtype=float)
                else:    
                    values += np.asarray(fi_data, dtype=float)
                cnt += 1
        else:        
            #values = np.zeros(shape=(self._num_features,))
            cnt = 0
            for p in self.pipelines:
                if hasattr(p, 'feature_importances_'):
                    if values is None:
                        values = np.asarray(p.feature_importances_, dtype=float)
                    else:    
                        values += np.asarray(p.feature_importances_, dtype=float)
                    cnt += 1

        if cnt > 0:
            values /= cnt
        if fi_names:
            return {'names': fi_names, 'scores': values.tolist()}

        return values.tolist()


class Ensemble(BaseEnsemble):
    def __init__(self, options, pipelines, weights=None, classification=False):
        super(Ensemble, self).__init__(
            options=options,
            pipelines=pipelines,
            classification=classification,
            params=dict(
                pipelines=pipelines,
                weights=weights,
                classification=classification
            )
        )
        self.weights = weights

        if weights is None:
            length = len(self.pipelines)
            self.weights = np.asarray([1 / float(length)] * length)

    def _assemble_predicts(self, predicts):
        for i in range(predicts.shape[0]):
            predicts[i, :] = predicts[i, :] * self.weights[i]

        return np.sum(predicts, axis=0)

    def predict(self, x):
        if self.classification:  # soft_labels
            predicts = self.predict_proba(x)
        else:
            predicts = self._assemble_predicts(self._predict(x))

        if self.classification:
            predicts = self.le.inverse_transform(np.argmax(predicts, axis=1))
        return predicts

    def predict_proba(self, x):
        return self._assemble_predicts(self._predict_proba(x))


class Voting(BaseEnsemble):
    """ Voting ensemble for classification based on Majority/Weighted rule.
    It uses pipelines, where the last estimator should be an classifier.

    Parameters
    ----------
    pipelines : list of pipelines for classification.

    voting : str, {'hard', 'soft'} (default='soft')
        If 'hard', uses predicted class labels for majority rule voting.
        Else if 'soft', predicts the class label based on the argmax of
        the sums of the predicted probabilities.

    weights : array-like, shape = [n_pipelines], optional (default=`None`)
        Sequence of weights (`float` or `int`) to weight the occurrences of
        predicted class labels (`hard` voting) or class probabilities
        before averaging (`soft` voting). Uses uniform weights if `None`.
    """
    def __init__(self, options, pipelines, weights=None, n_best=3, voting='soft'):
        super(Voting, self).__init__(
            options=options,
            pipelines=pipelines[:n_best],
            classification=True,
            params=dict(
                pipelines=pipelines,
                weights=weights,
                n_best=n_best,
                voting=voting
            )
        )
        self.voting = voting
        self.weights = weights

    def predict(self, x):
        """ Predict class labels for x.

        Parameters
        ----------
        x : {array-like, matrix}, shape = [n_samples, n_features].

        Returns
        ----------
        predictions : array-like, shape = [n_samples] -> predicted class labels.
        """
        # check_is_fitted(self, 'pipelines')

        if self.voting == 'soft':
            avg = self.predict_proba(x)
            predictions = np.argmax(avg, axis=1)

        else:  # 'hard' voting
            predictions = np.apply_along_axis(
                lambda lbl: np.argmax(np.bincount(lbl, weights=self.weights)),
                axis=0, arr=self._predict(x)
            )
        return self.le.inverse_transform(predictions)

    def predict_proba(self, x):
        return np.average(self._predict_proba(x), axis=0, weights=self.weights)


class Averaging(BaseEnsemble):
    """ Averaging ensemble for classification and regression tasks.

    Parameters
    ----------
    pipelines : list of pipelines for classification.

    classification : bool, (default=False)
        If True, uses predicted class probabilities for averaging within them.
        If False, uses averaging over raw predicted values.

    weights : array-like, shape = [n_pipelines], optional (default=`None`)
        Sequence of weights (`float` or `int`) to weight the class probabilities (for `classification`)
        or values (for `regression`) before averaging. Uses uniform weights if `None`.
    """
    def __init__(self, options, pipelines, weights=None, n_best=3, classification=False):
        super(Averaging, self).__init__(
            options=options,
            pipelines=pipelines[:n_best],
            classification=classification,
            params=dict(
                pipelines=pipelines,
                weights=weights,
                n_best=n_best,
                classification=classification
            )
        )
        self.weights = weights

    def predict(self, x):
        """ Predict class labels for x.

        Parameters
        ----------
        x : {array-like, matrix}, shape = [n_samples, n_features].

        Returns
        ----------
        predictions : array-like, shape = [n_samples] -> predicted class labels or values.
        """

        if self.classification:
            avg = self.predict_proba(x)
            predictions = self.le.inverse_transform(np.argmax(avg, axis=1))

        else:  # 'regression' task_type
            predictions = np.average(self._predict(x), axis=0, weights=self.weights)

        return predictions

    def predict_proba(self, x):
        return np.average(self._predict_proba(x), axis=0, weights=self.weights)
