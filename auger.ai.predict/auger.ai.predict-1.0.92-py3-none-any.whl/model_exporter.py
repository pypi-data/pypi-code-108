import copy
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import math
import numpy as np
import os
import pandas as pd
import datetime
import time

from auger_ml.FSClient import FSClient
from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas
from auger_ml.data_splitters.XYNumpyDataPrep import XYNumpyDataPrep
from auger_ml.Utils import remove_dups_from_list, get_uid, get_uid4, convert_to_date, merge_dicts
from .model_helper import ModelHelper


class ModelExporter(object):
    def __init__(self, options):
        self.options = options

    def load_model(self, model_path):
        from auger_ml.preprocessors.space import ppspace_is_timeseries_model

        model = FSClient().loadObjectFromFile(os.path.join(model_path, "model.pkl.gz"))

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        timeseries_model = options.get('timeSeriesFeatures') and ppspace_is_timeseries_model(options.get('algorithm_name'))

        return model, timeseries_model

    def preprocess_target(self, model_path, data_path=None, records=None, features=None):
        return ModelHelper.preprocess_target(model_path, data_path, records, features)

    def preprocess_target_ds(self, model_path, ds):
        return ModelHelper.preprocess_target_ds(model_path, ds)

    def preprocess_data(self, model_path, data_path=None, records=None, features=None, predict_value_num=None):
        from auger_ml.AugerMLPreprocessors import AugerMLPreprocessors
        from auger_ml.preprocessors.space import ppspace_is_timeseries_model, pspace_get_fold_group_names

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        fold_group_props = FSClient().readJSONFile(os.path.join(model_path, options['fold_group'], "data_preprocessed.props.json"))

        if fold_group_props and 'featureColumns' in fold_group_props:
            train_features = copy.deepcopy(fold_group_props['featureColumns'])
        else:
            train_features = copy.deepcopy(options['featureColumns'])

        options['featureColumns'] = options.get('originalFeatureColumns')
        data_features = options['featureColumns'][:]
        if options.get('timeSeriesFeatures'):
            data_features.extend(options.get('timeSeriesFeatures'))
            data_features.append(options.get('targetFeature'))

        data_features = remove_dups_from_list(data_features)

        if features is None:
            features = data_features

        ds = DataSourceAPIPandas.create_dataframe(data_path, records, features)

        if set(data_features).issubset(set(ds.columns)):
            if options.get('targetFeature') in ds.columns and not options.get('targetFeature') in data_features:
                data_features.append(options.get('targetFeature'))

            ds.df = ds.df[data_features]
        else:
            raise Exception("Prediction data missing columns:%s"%(set(data_features)-set(ds.columns)))

        transforms = FSClient().readJSONFile(os.path.join(model_path, "transformations.json"))
        ds.transform(transforms, cache_to_file=False)

        target_categoricals = FSClient().readJSONFile(os.path.join(model_path, "target_categoricals.json"))

        X_test, Y_test = None, None
        if options.get('timeSeriesFeatures'):

            if predict_value_num is not None:
                if predict_value_num == len(ds.df):
                    return None, None, None, None

                ds.df = ds.df.iloc[:(predict_value_num + 1)]  # truncate dataset

            pp = AugerMLPreprocessors(options)
            pp.transform_predicted_data(ds, model_path, target_categoricals)

            X_test, Y_test = XYNumpyDataPrep(options).split_predict_timeseries(ds.df, train_features)

        else:
            X_test = {}
            if options.get('ensemble', False):
                fold_groups = pspace_get_fold_group_names(options.get('timeSeriesFeatures'))
                for fold_group in fold_groups:
                    options['fold_group'] = fold_group

                    ds2 = DataSourceAPIPandas(options)
                    ds2.df = ds.df.copy()

                    pp = AugerMLPreprocessors(options)
                    pp.transform_predicted_data(ds2, model_path, target_categoricals)
                    fold_group_props_1 = FSClient().readJSONFile(os.path.join(model_path, fold_group, "data_preprocessed.props.json"))

                    fold_group_features = train_features
                    if fold_group_props_1 and 'featureColumns' in fold_group_props_1:
                        fold_group_features = fold_group_props_1['featureColumns']

                    X_test[fold_group], Y_test = XYNumpyDataPrep(options).split_predict(ds2.df, fold_group_features)
            else:
                pp = AugerMLPreprocessors(options)
                pp.transform_predicted_data(ds, model_path, target_categoricals)
                X_test, Y_test = XYNumpyDataPrep(options).split_predict(ds.df, train_features)

        return X_test, Y_test, target_categoricals, data_features

    def check_model_path(self):
        from auger_ml.core.AugerML import AugerML

        if not self.options.get('model_path'):
            params = copy.deepcopy(self.options)
            params = AugerML.update_task_params(params)
            self.options['model_path'] = self._build_model_path(params['augerInfo']['pipeline_id'], params)
            # if 'augerInfo' in self.options:
            #     del self.options['augerInfo']

        return self

    def _build_model_path(self, pipeline_id, params=None):
        from auger_ml.core.AugerML import AugerML

        if pipeline_id:
            if not params:
                params = copy.deepcopy(self.options)
                params = AugerML.update_task_params(params)

            return os.path.join(params['augerInfo']['modelsPath'], pipeline_id)

    def predict_by_model(self, model_path, path_to_predict=None, records=None, features=None,
        threshold=None, predict_value_num=None, json_result=False, count_in_result=False,
        prediction_date=None, prediction_id=None, no_features_in_result=None, output=None):

        ds, options = self.predict_by_model_to_ds(model_path, path_to_predict, records, features,
            threshold, predict_value_num, no_features_in_result=no_features_in_result)
        if ds is None:
            return None

        gzip_predict_file = False

        if ds.count() > options.get('max_predict_records_to_gzip', 1000):
            gzip_predict_file = True

        return ModelHelper.save_prediction(ds, prediction_id, json_result, count_in_result,
            prediction_date, model_path, options.get('uid'), gzip_predict_file=gzip_predict_file,
            output=output)

    def predict_by_model_to_ds(self, model_path, path_to_predict=None, records=None, features=None,
        threshold=None, predict_value_num=None, no_features_in_result=None):

        from auger_ml.preprocessors.space import ppspace_is_timeseries_model

        X_test, Y_test, target_categoricals, data_features = self.preprocess_data(model_path,
            data_path=path_to_predict, records=records, features=features, predict_value_num=predict_value_num)

        # print("Start loading model: %s"%datetime.datetime.utcnow())
        model, timeseries_model = self.load_model(model_path)
        # print("End loading model: %s"%datetime.datetime.utcnow())

        if X_test is None:
            return None, {}

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        if threshold and not options.get('classification', True):
            logging.warning("Threshold only applied to classification and will be ignored.")
            threshold = None

        result_cols = [options['targetFeature']]
        ds = DataSourceAPIPandas.create_dataframe(path_to_predict, records, features)
        if options.get('timeSeriesFeatures'):
            if ppspace_is_timeseries_model(options.get('algorithm_name')):
                results = model.predict((X_test, Y_test, False))[-1:]
            else:
                results = model.predict(X_test.iloc[-1:])

            ds.df = pd.DataFrame({
                options['targetFeature']: results,
                options['timeSeriesFeatures'][0]: X_test.index[-1:]
            })
        else:
            results = None
            results_proba = None
            proba_classes = None
            if threshold:
                try:
                    if hasattr(model, 'predict_proba') and callable(getattr(model, 'predict_proba')):
                        try:
                            results_proba = model.predict_proba(X_test)
                        except AttributeError as e:
                            logging.info("predict_proba is property, try _predict_proba")
                            results_proba = model._predict_proba(X_test)

                    elif hasattr(model, 'decision_function'):
                        results_proba = model.decision_function(X_test)

                    if results_proba is not None:
                        proba_classes = list(model.classes_)
                except:
                    logging.exception("predict_proba failed.")

            if results_proba is None:
                results = model.predict(X_test)

            target_categories = None
            if options['targetFeature'] in target_categoricals:
                target_categories = target_categoricals[options['targetFeature']]['categories']

            result_cols = ModelHelper.process_prediction(ds,
                results, results_proba, proba_classes,
                threshold, options.get('minority_target_class'),
                options['targetFeature'], target_categories)

        if no_features_in_result:
            ds.df = ds.df[result_cols]

        return ds, options

    def predict_by_model_ts_recursive(self, model_path, path_to_predict=None, records=None, features=None,
                                      start_prediction_num=None):
        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        targetFeature = options['targetFeature']

        i = start_prediction_num
        result = []
        while True:
            res = self.predict_by_model(model_path, path_to_predict, records, features, predict_value_num=i)
            if res is None:
                break

            if path_to_predict is not None:
                ds = DataSourceAPIPandas({'data_path': res})
                ds.load(features = [targetFeature], use_cache = False)
                res = ds.df
                #res = pd.read_csv(res, encoding='utf-8', escapechar='\\', usecols=[targetFeature])

            #assert len(res) == 1
            result.append(res[targetFeature][0])
            i += 1

        return result

    def score_by_model(self, model_path, predict_path=None, test_path=None,
            records=None, features=None, test_records=None, test_features=None,
            start_prediction_num=20, predictions=None):
        from .model_helper import ModelHelper

        res = {}
        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        y_pred = None

        if options.get('timeSeriesFeatures'):
            y_pred = self.predict_by_model_ts_recursive(model_path,
                path_to_predict=predict_path, records=records, features=features, start_prediction_num=start_prediction_num)
        else:
            if predictions is None:
                predictions = self.predict_by_model(model_path, path_to_predict=predict_path,
                    records=records, features=features)

            if predict_path:
                y_pred, target_categoricals = self.preprocess_target(model_path, data_path=predictions)
            else:
                y_pred, target_categoricals = self.preprocess_target(model_path, records=predictions, features=[options.get('targetFeature')])

            #TODO: support proba scores and threshold

        if test_path is None and test_records is None:
            test_path = predict_path

        y_true, target_categoricals = self.preprocess_target(model_path, data_path=test_path,
            records=test_records, features=test_features)

        if predict_path is not None and test_path == predict_path:
            y_true = y_true[:len(y_pred)]

        test_roi_data = None
        if options.get('scoring')=='roi':
            test_roi_data = DataSourceAPIPandas.create_dataframe(data_path=test_path,
                records=test_records, features=test_features).df

        res['all_scores'] = ModelHelper.calculate_scores(options, y_test=y_true, y_pred=y_pred, raise_main_score=False,
            test_roi_data=test_roi_data)

        return res
