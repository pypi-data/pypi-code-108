from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import numpy as np
import os

from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas
from auger_ml.FSClient import FSClient


class _ComputationData(object):
    def __init__(self, options):
        self.data = {'options': options, 'predictions': [], 'source_data': None}

        ds = DataSourceAPIPandas(options)
        if options.get('fold_group') is not None:
            ds.loadFromCacheFile(options.get('fold_group') + "/data_preprocessed", features=[options['targetFeature']])
        else:
            ds.load(features=[options['targetFeature']], use_cache=False)

        self.data['source_data'] = ds.df

        if options.get('roi_metric'):
            ds_roi = DataSourceAPIPandas(options).load_roi_features()
            self.data['test_roi_data'] = ds_roi.df
            
        self.load_trials_and_predictions(options)

    def load_trials_and_predictions(self, options):
        from auger_ml.core.trials_history import TrialsHistory

        predictions = self.data['predictions']
        for trial in TrialsHistory(options).get_top_pipelines_for_ensembles():
            prediction = {
                'name': trial['algorithm_name'],
                'params': trial['algorithm_params'],
                'uid': trial['uid'],
                'score': trial['score'],

                'y_predicted': np.zeros(shape=(len(self.data['source_data']),), dtype=np.float32),
                'y_predicted_proba': None,
                'idx': []
            }

            prediction_path = os.path.join(options['augerInfo']['predictionsPath'],
                                           "%s_*.npz" % (trial['uid']))
            prediction_files = FSClient().listFolder(prediction_path, wild=True)
            for file in prediction_files:
                fold_content = \
                    FSClient().loadNPObjectFromFile(os.path.join(options['augerInfo']['predictionsPath'], file))
                self.append_fold_to_prediction(prediction, fold_content)

            predictions.append(prediction)

    @staticmethod
    def append_fold_to_prediction(prediction, fold_content):
        test_index = fold_content['test_index']
        y_predicted_proba = fold_content['y_predicted_proba']

        if test_index is not None and test_index.any():
            prediction['idx'].append(test_index)
            prediction['y_predicted'][test_index] = fold_content['y_predicted']

        if y_predicted_proba.any():
            if prediction['y_predicted_proba'] is None:
                shape = (prediction['y_predicted'].shape[0], y_predicted_proba.shape[1])
                prediction['y_predicted_proba'] = np.zeros(shape=shape, dtype=np.float32)

            try:
                if test_index is not None and test_index.any():
                    prediction['y_predicted_proba'][test_index] = y_predicted_proba
            except (IndexError, TypeError, ValueError) as e:
                logging.info("Erorr while accumulating predict: {}".format(str(e)))


def load(options):
    return _ComputationData(options).data
