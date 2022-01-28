import datetime
import os
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from auger_ml.Utils import get_uid, get_uid4, sort_arrays
from auger_ml.FSClient import FSClient
from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas


class ModelHelper(object):

    @staticmethod
    def get_root_paths(s3_bucket):
        if s3_bucket:
            root_dir = os.path.join("s3://", s3_bucket)
            local_tmp_dir = "/tmp"
        else:
            root_dir = ""
            local_tmp_dir = "./tmp"

        root_tmp_dir = os.path.join(root_dir, 'temp')

        if not os.environ.get('AUGER_LOCAL_TMP_DIR'):
            os.environ["AUGER_LOCAL_TMP_DIR"] = local_tmp_dir

        return root_dir, root_tmp_dir

    @staticmethod
    def get_project_path(s3_bucket, project_name):
        root_dir, root_tmp_dir = ModelHelper.get_root_paths(s3_bucket)
        return os.path.join(root_dir, 'workspace/projects', project_name)

    @staticmethod
    def get_models_path(project_path):
        return os.path.join(project_path, "models")

    @staticmethod
    def get_model_path(model_id, project_path):
        if model_id:
            return os.path.join(ModelHelper.get_models_path(project_path), model_id)

    @staticmethod
    def get_metrics_path(params):
        s3_bucket = params.get('augerInfo').get('s3_bucket')
        project_path = params.get('augerInfo', {}).get('project_path')

        return os.path.join(project_path, "channels", params['augerInfo']['experiment_id'],
            "project_runs", params['augerInfo']['experiment_session_id'], "metrics")

    @staticmethod
    def get_metric_path(params, metric_id=None):
        if not metric_id:
            metric_id = params.get('augerInfo').get('pipeline_id')

        if not metric_id:
            metric_id = params.get('uid')

        return os.path.join(ModelHelper.get_metrics_path(params), metric_id)

    @staticmethod
    def get_feature_importances(params, metric_id):
        cache_path = ModelHelper.get_metric_path(params, metric_id)

        importance_data = None
        if cache_path:
            importance_data = FSClient().readJSONFile(os.path.join(cache_path, "metrics.json")).get('feature_importance_data')
            if not importance_data:
                importance_data = FSClient().readJSONFile(os.path.join(cache_path, "metric_names_feature_importance.json")).get('feature_importance_data')

        if importance_data:
            if importance_data.get('features_orig') and importance_data.get('scores_orig'):
                return importance_data['features_orig'], importance_data['scores_orig']
            else:
                return importance_data['features'], importance_data['scores']
        else:
            logging.warn("No feature importance in cache: for model %s" % (cache_path))
            return [], []

    @staticmethod
    def calculate_scores(options, y_test, X_test=None, estimator=None, y_pred=None, raise_main_score=True,
            test_roi_data=None):
        from sklearn.metrics import get_scorer
        from sklearn.model_selection._validation import _score
        import numpy as np
        import inspect

        if options.get('fold_group') == 'time_series_standard_model':
            pp_fold_groups_params = options.get('pp_fold_groups_params', {}).get(options['fold_group'], {})
            if pp_fold_groups_params.get('scale_target_min') and pp_fold_groups_params.get('scale_target_max'):
                corr_min = pp_fold_groups_params['scale_target_min']
                corr_max = pp_fold_groups_params['scale_target_max']

                if estimator:
                    y_pred = estimator.predict(X_test)

                y_test = y_test * corr_max + corr_min
                if isinstance(y_pred, list):
                    y_pred = np.array(y_pred)

                y_pred = y_pred * corr_max + corr_min
            else:
                logging.error("calculate_scores: no scaling found for target fold group: %s"%options['fold_group'])

        if y_pred is None and (options.get("score_top_count") or options.get('scoring')=='roi'):
            y_pred = estimator.predict(X_test)

        if options.get("score_top_count"):
            y_pred, y_test = sort_arrays(y_pred, y_test, options.get("score_top_count"))

        all_scores = {}
        scoreNames = options.get('scoreNames', [])
        if options.get('scoring') and not options.get('scoring') in scoreNames:
            scoreNames += [options.get('scoring')]

        for scoring in scoreNames:
            try:
                if options.get('task_type') == "timeseries":
                    from auger_ml.preprocessors.space import ppspace_is_timeseries_model

                    if ppspace_is_timeseries_model(options.get('algorithm_name')) and \
                        scoring != options.get('scoring'):
                        continue

                #TODO: translate score names to sklearn:
                # Classification : accuracy, AUC_weighted, average_precision_score_weighted, norm_macro_recall, precision_score_weighted
                # Regression,  Time Series Forecasting: spearman_correlation, normalized_root_mean_squared_error, r2_score, normalized_mean_absolute_error

                if scoring == 'roi':
                    all_scores[scoring] = ModelHelper.calculate_roi(options, test_roi_data, y_test, y_pred)
                else:
                    scorer = get_scorer(scoring)
                    if options.get('minority_target_class_pos') is not None:
                        argSpec = inspect.getfullargspec(scorer._score_func)
                        if 'pos_label' in argSpec.args:
                            scorer._kwargs['pos_label'] = options.get('minority_target_class_pos')
                            #logging.info("Use minority class to calculate score: %s"%scorer._kwargs)

                    if y_pred is not None:
                        all_scores[scoring] = scorer._sign * scorer._score_func(y_test, y_pred, **scorer._kwargs)
                    else:
                        all_scores[scoring] = _score(estimator, X_test, y_test, scorer)
                        #all_scores['scoring'] = scorer(estimator, X_test, y_test)


                    if np.isnan(all_scores[scoring]):
                        all_scores[scoring] = 0

            except Exception as e:
                #logging.exception("Score failed.")
                if scoring == options.get('scoring', None) and raise_main_score:
                    raise

                logging.error("Score %s for algorithm %s failed to build: %s" % (
                    scoring, options.get('algorithm_name'), str(e)))
                all_scores[scoring] = 0

        return all_scores

    @staticmethod
    def calculate_roi(options, test_roi_data, y_test, y_pred):
        from auger_ml.roi.calculator import Calculator as RoiCalculator

        if not options.get('roi_metric'):
            return 0

        if test_roi_data is None:
            logging.error("calculate_roi failed: roi data is none.")
            return 0

        known_vars = test_roi_data.columns.tolist()

        test_roi_data['a2ml_actual'] = y_test
        test_roi_data['a2ml_predicted'] = y_pred

        vars_mapping = {
            "A": "a2ml_actual",
            "actual": "a2ml_actual",
            "P": 'a2ml_predicted',
            "prediction": 'a2ml_predicted',
        }

        for known_var in known_vars:
            vars_mapping["$" + known_var] = known_var

        calc = RoiCalculator(
            filter=options['roi_metric']['filter'],
            revenue=options['roi_metric']['revenue'],
            investment=options['roi_metric']['investment'],
            known_vars=known_vars,
            vars_mapping=vars_mapping,
        )

        res = calc.calculate(test_roi_data)
        #logging.info("ROI result: %s"%res)
        return res["roi"]

    @staticmethod
    def preprocess_target(model_path, data_path=None, records=None, features=None):
        ds = DataSourceAPIPandas.create_dataframe(data_path, records, features)

        return ModelHelper.preprocess_target_ds(model_path, ds)

    @staticmethod
    def preprocess_target_ds(model_path, ds):
        import numpy as np

        options = FSClient().readJSONFile(os.path.join(model_path, "options.json"))
        target_categoricals = FSClient().readJSONFile(os.path.join(model_path, "target_categoricals.json"))
        y_true =  None

        if not options.get('targetFeature') or not options.get('targetFeature') in ds.columns:
            return y_true, target_categoricals

        if options.get('timeSeriesFeatures'):
            y_true = np.ravel(ds.df[options.get('targetFeature')].astype(np.float64, copy=False), order='C')
        else:
            if target_categoricals and options.get('targetFeature') in target_categoricals:
                ds.convertToCategorical(options.get('targetFeature'), is_target=True,
                    categories=target_categoricals.get(options.get('targetFeature')).get('categories'))

            y_true = np.ravel(ds.df[options.get('targetFeature')], order='C')

        return y_true, target_categoricals

    @staticmethod
    def process_prediction(ds, results, results_proba, proba_classes,
                           threshold, minority_target_class, targetFeature, target_categories):

        if results_proba is not None:
            proba_classes_orig = None
            if target_categories:
                proba_classes_orig = ModelHelper.revertCategories(proba_classes, target_categories)

            results = ModelHelper.calculate_proba_target(
                results_proba, proba_classes, proba_classes_orig,
                threshold, minority_target_class)

            if proba_classes_orig is not None:
                proba_classes = proba_classes_orig

        try:
            results = list(results)
        except Exception as e:
            results = [results]

        if target_categories:
            results = ModelHelper.revertCategories(results, target_categories)

        # drop target
        if targetFeature in ds.columns:
            ds.drop([targetFeature])

        try:
            results = list(results)
        except Exception as e:
            results = [results]

        result_cols = [targetFeature]
        ds.df[targetFeature] = results
        if results_proba is not None:
            for idx, name in enumerate(proba_classes):
                col_name = 'proba_'+str(name)
                ds.df[col_name] = list(results_proba[:, idx])
                result_cols.append(col_name)

        return result_cols
                
    @staticmethod
    def save_prediction(ds, prediction_id,
        json_result, count_in_result, prediction_date, model_path, model_id, output=None,
        gzip_predict_file=False):

        path_to_predict = ds.options.get('data_path')
        # Id for whole prediction (can contains many rows)
        if not prediction_id:
            prediction_id = get_uid()

        result = {}
        if path_to_predict and not json_result:
            if output:
                predict_path = output
            else:
                parent_path = os.path.dirname(path_to_predict)
                file_name = os.path.basename(path_to_predict)
                predict_path = os.path.join(parent_path, "predictions",
                    os.path.splitext(file_name)[0] + "_%s_%s_predicted.csv" % (prediction_id, model_id))

                if gzip_predict_file:
                    predict_path += ".gz"

            ds.saveToFile(predict_path)

            if count_in_result:
                result = {'result_path': predict_path, 'count': ds.count()}
            else:
                result = predict_path
        else:
            if json_result:
                result = ds.df.to_json(orient='split', index=False)
            elif ds.loaded_columns:
                predicted = ds.df.to_dict('split')
                result = {'data': predicted.get('data', []), 'columns': predicted.get('columns')}
            else:
                result = ds.df.to_dict('records')

        return result

    @staticmethod
    def revertCategories(results, categories):
        def get_cat_index(value):
            idx = int(value)
            if idx < 0:
                return 0
            if idx >= len(categories):
                return len(categories)-1

            return idx

        return list(map(lambda x: categories[get_cat_index(x)], results))

    @staticmethod
    def calculate_proba_target(results_proba, proba_classes, proba_classes_orig,
                               threshold, minority_target_class=None):
        import json
        results = []

        if type(threshold) == str:
            try:
                threshold = float(threshold)
            except:
                try:
                    threshold = json.loads(threshold)
                except Exception as e:
                    raise Exception("Threshold '%s' should be float or hash with target classes. Error: %s" % (
                        threshold, str(e)))

        if not proba_classes_orig:
            proba_classes_orig = proba_classes

        if type(threshold) != dict:
            if minority_target_class is None:
                minority_target_class = proba_classes_orig[-1]

            threshold = {minority_target_class: threshold}

        mapped_threshold = {}

        for name, value in threshold.items():
            idx_class = None
            for idx, item in enumerate(proba_classes_orig):
                if item == name:
                    idx_class = idx
                    break

            if idx_class is None:
                raise Exception("Unknown target class in threshold: %s, %s" % (
                    name, proba_classes_orig))

            mapped_threshold[idx_class] = value

        for item in results_proba:
            proba_idx = None
            for idx, value in mapped_threshold.items():
                if item[idx] >= value:
                    proba_idx = idx
                    break

            # Find class with value > threshold from the last
            if proba_idx is None and len(mapped_threshold) == 1:
                threshold_value = list(mapped_threshold.values())[0]
                for idx, value in enumerate(item):
                    if item[len(item)-idx-1] >= threshold_value:
                        proba_idx = len(item)-idx-1
                        break

            # Find any class not minority_target_class  from the last
            if proba_idx is None:
                proba_idx = len(item)-1
                for idx, value in enumerate(item):
                    if len(item)-idx-1 not in mapped_threshold:
                        proba_idx = len(item)-idx-1
                        break

            results.append(proba_classes[proba_idx])

        return results
