from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import copy
import os
import pandas as pd

from auger_ml.preprocessors.space import *
from auger_ml.FSClient import FSClient
from auger_ml.data_source.data_source_api_pandas import DataSourceAPIPandas


class PreprocessorException(Exception):
    def __init__(self, name, params, cause, traceback):
        self.name = name
        self.params = params
        self.cause = cause
        self.traceback = traceback

    def __reduce__(self):
        return (self.__class__, (self.name, self.params, self.cause, self.traceback))

class AugerMLPreprocessors(object):

    def __init__(self, options):
        self.options = options
        self.warnings = []
        self.passed_preprocessors = []
        self.resample_sample_rate = None
        self.test_data_index = None
        self.data_preprocessed_name = "data_preprocessed"

    def set_test_data_index(self, test_data_index):
        self.test_data_index = test_data_index

    def preprocess_target(self, ds):
        FSClient().writeJSONFile(ds._get_datacache_path(
            "target_categoricals.json"), {}, atomic=True)
        categoricals = self.options.get('categoricalFeatures', [])
        if self.options.get('targetFeature') in categoricals:
            ds.convertToCategorical(self.options.get(
                'targetFeature'), is_target=True)
            res_categoricals = ds.categoricals
        else:
            res_categoricals = ds.getBooleanCategoricals(self.options.get('targetFeature'))

        FSClient().writeJSONFile(ds._get_datacache_path("target_categoricals.json"),
                                 res_categoricals, atomic=True)

    def update_minority_target_class(self, ds):
        res_categoricals = FSClient().readJSONFile(ds._get_datacache_path("target_categoricals.json"))
        if res_categoricals and ds.options.get('minority_target_class') is not None:
            cats_target = res_categoricals[self.options.get('targetFeature')]['categories']
            cats_target.sort()
            ds.options['minority_target_class_pos'] = cats_target.index(ds.options.get('minority_target_class'))
                    
    def get_preprocessor_params(self, pp_name):
        params = copy.deepcopy(preprocessors_space[pp_name])

        prepOptions = {}
        pp_disabled = not preprocessors_space_ex[pp_name]['auger_enabled']

        if "preprocessors" in self.options:
            short_pp_name = pp_name.split('.')[-1]
            if pp_disabled and not short_pp_name in self.options["preprocessors"]:
                return None

            prepOptions = self.options["preprocessors"].get(short_pp_name, {})
        elif 'preprocessors_space' in self.options:
            if pp_name in self.options["preprocessors_space"]:
                prepOptions = self.options["preprocessors_space"][pp_name]
            else:
                return None
        else:
            if pp_disabled:
                return None

        for name, value in params.items():
            if prepOptions and name in prepOptions:
                params[name] = prepOptions[name]

        if pp_name == 'categorical.CategoricalPreprocessor':
            params['cat_cols'] = self.options.get('categoricalFeatures', [])
            params['label_enc_cols'] = self.options.get(
                'labelEncodingFeatures', [])
            
        if pp_name == 'text.TextPreprocessor':
            params['text_cols'] = self.options.get('textFeatures', [])

        if pp_name == 'date_time.DateTimePreprocessor':
            params['datetime_cols'] = self.options.get('datetimeFeatures', [])
            params['discover_fields'] = not self.options.get('timeSeriesFeatures')

        if pp_name == 'time_series.resample.ResamplePreprocessor':
            params['datetime_col'] = self.options.get(
                'timeSeriesFeatures', [None])[0]

            if params.get('sample_rate') is None and self.resample_sample_rate is not None:
                params['sample_rate'] = self.resample_sample_rate

        return params

    def get_columns_to_load(self):
        from auger_ml.Utils import remove_dups_from_list

        selected_cols = []
        for item in self.options.get('featureColumns', []):
            selected_cols.append(str(item))

        if self.options.get('targetFeature') is not None:
            selected_cols.append(self.options.get('targetFeature'))
        if self.options.get('timeSeriesFeatures'):
            selected_cols.extend(self.options.get('timeSeriesFeatures'))

        return remove_dups_from_list(selected_cols)

    def run_preprocessors_group(self, ds, preprocessors_group):
        from auger_ml.preprocessors.space import preprocessors_groups
        import pandas as pd

        passed_preprocessors = []
        if list(preprocessors_group.keys())[0] == 'time_series':
            datetime_col = self.options.get('timeSeriesFeatures')[0]

            # run preprocessor for each column
            features, target = None, None
            for col in self.options['featureColumns'] + [self.options['targetFeature']]:
                if datetime_col is None:
                    subset_col = [col]
                else:
                    subset_col = [col, datetime_col]

                df = ds.df[subset_col]
                f, t = None, None
                for idx, pp_name in enumerate(list(preprocessors_group.values())[0]):
                    if idx < len(list(preprocessors_group.values())[0])-1:
                        df = self.run_preprocessor(df, pp_name)
                    else:
                        res = self.run_preprocessor(df, pp_name)
                        if res:
                            f, t = res

                if f is None:
                    f = ds.df[col]

                features = f if features is None else pd.concat([features, f], axis=1)

                if t is not None and col == self.options['targetFeature']:
                    self.target = t

            ds.df = features
            for pp_name in list(preprocessors_group.values())[0]:
                if type(pp_name) == dict:
                    pp_name = list(pp_name.keys())[0]

                passed_preprocessors.append({pp_name:None})
        else:
            for pp_name in list(preprocessors_group.values())[0]:
                ds.df = self.run_preprocessor(ds.df, pp_name, passed_preprocessors)

        return passed_preprocessors

    def run_fold_groups(self, ds):
        fold_groups = pspace_get_fold_groups(self.options.get('timeSeriesFeatures'))
        logging.info("Run preprocessor groups:%s"%fold_groups)
        for fold_group in fold_groups:
            self.run_fold_group(ds, fold_group)
            ds.df = None

        if self.test_data_index is not None:
            for fold_group in fold_groups:
                ds1 = DataSourceAPIPandas(self.options)
                ds1.loadFromCacheFile(os.path.join(fold_group['name'], self.data_preprocessed_name))
                ds1.df = ds1.df.head(self.test_data_index)
                ds1.saveToCacheFile(os.path.join(fold_group['name'], self.data_preprocessed_name))

        logging.info("Run preprocessor groups finished.")

    def run_split_fold_groups(self):
        if not self.options.get('split_to_folds_files', False):
            return

        fold_groups = pspace_get_fold_groups(self.options.get('timeSeriesFeatures'))
        for fold_group in fold_groups:
            self.options['fold_group'] = fold_group['name']

            ds = DataSourceAPIPandas(self.options)
            ds.loadFromCacheFile(os.path.join(fold_group['name'], self.data_preprocessed_name))

            ds.splitToFoldFiles()
            del self.options['fold_group']

    def on_finish_preprocess(self):
        if self.options.get('split_to_folds_files', False):
            fold_groups = pspace_get_fold_groups(self.options.get('timeSeriesFeatures'))

            # Check that all folds are in place and add confirm file
            for fold_group in fold_groups:
                self.options['fold_group'] = fold_group['name']
                ds = DataSourceAPIPandas(self.options)
                fold_paths = ds.getFoldPaths()
                # for fold_path in fold_paths:
                #     if not FSClient().isFileExists(fold_path):
                #         raise Exception("Preprocess data failed: split to folds file does not exist:%s"%(fold_path))

                del self.options['fold_group']

        FSClient().writeJSONFile(DataSourceAPIPandas(self.options)._get_datacache_path("preprocessors_state.json"), {"state": "completed"})

    def run_fold_group(self, ds, fold_group):
        # print(fold_group)
        self.passed_fold_groups = []
        self.passed_preprocessors = []

        if 'base_group' in fold_group:
            if not ds.loadFromCacheFile(os.path.join(fold_group['base_group'], self.data_preprocessed_name)):
                logging.info("No fold group %s files found. Run preprocessors for it."%fold_group['base_group'])
                self.run_fold_group(ds, ppspace_get_fold_group_by_name(fold_group['base_group']))
                if not ds.loadFromCacheFile(os.path.join(fold_group['base_group'], self.data_preprocessed_name)):
                    raise PreprocessorException("Fold group %s"%fold_group['base_group'], {}, "Error while preprocess base fold_group %s"%fold_group['base_group'], None)
            else:
                self.passed_fold_groups = FSClient().loadObjectFromFile(os.path.join(ds._get_datacache_path(fold_group['base_group']), "preprocessors.pkl.gz"))
        else:
            if ds.df is None:
                ds.load(self.get_columns_to_load())

        group_path = ds._get_datacache_path(fold_group['name'])
        passed_pp_groups = self.run_preprocessors_groups(ds, fold_group, fold_group['groups'])

        # Save preprocessors and data
        FSClient().createFolder(group_path)
        props = {'featureColumns': ds.columns}
        if self.options['targetFeature'] in props['featureColumns']:
            props['featureColumns'].remove(self.options['targetFeature'])
        FSClient().writeJSONFile(os.path.join(group_path, "data_preprocessed.props.json"), props)

        if self.options.get('split_to_folds_files', False):
            self.options['fold_group'] = fold_group['name']
            ds.splitToFoldFiles(test_data_index=self.test_data_index)
            #logging.info("splitToFoldFiles finished.")
            del self.options['fold_group']

        ds.saveToCacheFile(os.path.join(fold_group['name'], self.data_preprocessed_name))
        #logging.info("saveToCacheFile finished.")

        self.passed_fold_groups.append({fold_group['name']:passed_pp_groups})
        FSClient().saveObjectToFile(self.passed_fold_groups, os.path.join(group_path, "preprocessors.pkl.gz"))

    def get_saved_preprocessors_names(self):
        ds = DataSourceAPIPandas(self.options)
        preprocessors = FSClient().loadObjectFromFile(ds._get_datacache_path(self.options['fold_group']+"/preprocessors.pkl.gz"))
        pp_names = []
        for pp_group in preprocessors:
            for pp in list(pp_group.values())[0]:
                for item in list(pp.values())[0]:
                    pp_names.append({'name': list(item.keys())[0].split('.')[-1], 'params': {}})

        return pp_names

    def get_preprocessor_by_names(self, names):
        ds = DataSourceAPIPandas(self.options)
        preprocessors = FSClient().loadObjectFromFile(ds._get_datacache_path(self.options['fold_group']+"/preprocessors.pkl.gz"))

        cur_obj = preprocessors
        for name in names:
            new_cur_obj = None
            for item in cur_obj:
                if name in item.keys():
                    new_cur_obj = item[name]
                    break

            if new_cur_obj is None:
                cur_obj = None
                break

            cur_obj = new_cur_obj

        return cur_obj

    def run_preprocessors_groups(self, ds, fold_group, preprocessors_groups):
        passed_pp_groups = []

        if fold_group['name'] == 'time_series_ts_model':
            ds.sort(self.options['timeSeriesFeatures'])
            ds.drop(self.options['timeSeriesFeatures'])
        elif 'time_series' in fold_group['groups']:
            datetime_col = self.options.get('timeSeriesFeatures')[0]

            if datetime_col is not None:
                if not 'datetime64' in str(ds.df.dtypes[datetime_col]):
                    logging.info("Timeseries convert %s to datetime."%datetime_col)
                    if ds.df.dtypes[datetime_col] == 'object':
                        ds.df[datetime_col] = pd.to_datetime(ds.df[datetime_col], infer_datetime_format=True, errors='ignore', utc=True)
                    else:
                        ds.df[datetime_col] = pd.to_datetime(ds.df[datetime_col], unit='s')

                ds.df = ds.df.sort_values(datetime_col)

                # Setup ResamplePreprocessor parameters
                params = self.get_preprocessor_params('time_series.resample.ResamplePreprocessor')
                # set sample rate
                if params and params.get('sample_rate') is None:
                    self.resample_sample_rate = ds.df[datetime_col].diff().mean()

        is_ts_group = 'time_series' in fold_group['name'] and fold_group['name'] != 'time_series_ts_model'
        self.target = None
        if not is_ts_group and self.options['targetFeature'] in ds.columns:
            self.target = ds.df[self.options['targetFeature']]
            features = self.options['featureColumns']
            if 'base_group' in fold_group:
                features = ds.columns
                features.remove(self.options['targetFeature'])

            ds.select(features)

        self.options['fold_group'] = fold_group['name']
        for group_name in preprocessors_groups:
            if type(group_name) == dict:
                if len(list(group_name.values())[0]) > 0:
                    passed_pp_groups.append({list(group_name.keys())[0]: self.run_preprocessors_group(ds, group_name)})
                else:
                    passed_pp_groups.append({list(group_name.keys())[0]: self.run_preprocessors_group(ds, ppspace_get_preprocessors_group_by_name(list(group_name.keys())[0]))})
            # elif is_ts_group and group_name == 'standard':
            #     logging.info("Skip standard preprocessors for timeseries fold groups")
            else:
                passed_pp_groups.append({group_name: self.run_preprocessors_group(ds, ppspace_get_preprocessors_group_by_name(group_name))})

        del self.options['fold_group']
        if self.target is not None:
            ds.df[self.options.get('targetFeature')] = self.target

        #logging.info("Passed preprocessors groups: %s"%passed_pp_groups)
        for pp_group in passed_pp_groups:
            for item in list(pp_group.values())[0]:
                self.passed_preprocessors.append(list(item.keys())[0])

        #logging.info("Passed preprocessors: %s"%self.passed_preprocessors)
        # Check fillna:
        if fold_group.get('fillna'):
            if not set(fold_group['fillna']).issubset(self.passed_preprocessors):
                logging.info("Run fillna for fold group %s, since %s were failed."%(fold_group['name'], fold_group['fillna']))
                ds.fillna(0)

        return passed_pp_groups

    def transform_predicted_data(self, ds, model_path, target_categoricals):
        fold_groups = FSClient().loadObjectFromFile(os.path.join(model_path, self.options['fold_group'], "preprocessors.pkl.gz"))

        try:
            for fold_group in fold_groups:
                self.run_preprocessors_groups(ds, ppspace_get_fold_group_by_name(list(fold_group.keys())[0]),
                    list(fold_group.values())[0])
        except Exception as e:
            raise Exception("New Auger preprocessors version is incompatible with model. Please train again and deploy new model. Details: %s"%e)

        if target_categoricals and self.options.get('targetFeature') in target_categoricals:
            ds.convertToCategorical(self.options.get(
                'targetFeature'), is_target=True, categories=target_categoricals.get(self.options.get('targetFeature')).get('categoricalFeatures'))

    def run_preprocessor(self, df, pp_name, passed_preprocessors=None):
        import platform

        if type(pp_name) == dict:
            pp = list(pp_name.values())[0]
            if pp is None:
                pp_name = list(pp_name.keys())[0]
            else:
                res = pp.transform(df)

                if passed_preprocessors is not None:
                    passed_preprocessors.append({list(pp_name.keys())[0]: pp})

                return res

        params = self.get_preprocessor_params(pp_name)
        if params is None:
            logging.info("Skip preprocessor: %s"%pp_name)
            if 'time_series' in pp_name:
                return None
            else:
                return df

        logging.info("Run preprocessor: %s"%pp_name)
        if params.get('run_in_process', False) and platform.system().lower() != 'windows' and \
            self.options.get('tasks_run_parallel', True):
            return self.run_preprocessor_fit_transform_in_process(df, pp_name, params, passed_preprocessors)
        else:
            return self.run_preprocessor_fit_transform(df, pp_name, params, passed_preprocessors)

    def _in_process_fit_transform(self, pp_name, params):
        ds = DataSourceAPIPandas(self.options)
        ds.loadFromCacheFile(os.path.join(self.options['fold_group'], self.data_preprocessed_name))

        passed_preprocessors = []
        saved_exception = None
        try:
            ds.df = self.run_preprocessor_fit_transform(ds.df, pp_name, params, passed_preprocessors)
            ds.saveToCacheFile(os.path.join(self.options['fold_group'], self.data_preprocessed_name))
        except Exception as e:
            saved_exception = e

        FSClient().saveObjectToFile({'passed_preprocessors':passed_preprocessors,
            'warnings': self.warnings, 'saved_exception': saved_exception},
            ds._get_datacache_path(os.path.join(self.options['fold_group'], pp_name+"_preprocessor.pkl.gz")))

        # TODO: pass back exception

    def run_preprocessor_fit_transform_in_process(self, df, pp_name, params, passed_preprocessors):
        from billiard.context import Process
        import signal
        from time import sleep

        ds = DataSourceAPIPandas(self.options)
        ds.df = df
        ds.saveToCacheFile(os.path.join(self.options['fold_group'], self.data_preprocessed_name))

        max_preprocess_time_seconds = max(
            int(self.options.get("max_preprocess_time_mins", 20) * 60), 1)

        p = Process(target=self._in_process_fit_transform, args=(pp_name, params,))
        p.start()
        p.join(max_preprocess_time_seconds*1.1)

        was_timeout = False
        if p.is_alive():
            logging.info("Preprocesor %s(%s) process is still alive, try to terminate it. Timeout: %s"%(pp_name, params, max_preprocess_time_seconds))
            was_timeout = True
            p.terminate()

        nTries = 10
        while p.is_alive():
            if nTries == 0:
                logging.info("Preprocesor %s(%s) process is still alive, KILL it. Timeout: %s"%(pp_name, params, max_preprocess_time_seconds))
                os.kill(p.pid, signal.SIGKILL)
                break
            nTries = nTries-1
            sleep(1)

        if was_timeout:
            self.warnings.append({
                'name': pp_name,
                'params': params,
                'message': "timeout"
            })
            return df

        pp_file_path = ds._get_datacache_path(os.path.join(self.options['fold_group'], pp_name+"_preprocessor.pkl.gz"))
        if FSClient().isFileExists(pp_file_path):
            res = FSClient().loadObjectFromFile(pp_file_path)
            FSClient().removeFile(pp_file_path)

            if passed_preprocessors is not None:
                passed_preprocessors.extend(res['passed_preprocessors'])

            self.warnings = res['warnings']
            if res.get('saved_exception') is not None:
                raise res.get('saved_exception')

        ds.loadFromCacheFile(os.path.join(self.options['fold_group'], self.data_preprocessed_name))
        return ds.df

    def run_preprocessor_fit_transform(self, df, pp_name, params, passed_preprocessors):
        from auger_ml.Utils import create_object_by_class
        import sys
        from stopit import threading_timeoutable, TimeoutException

        skip_errors = False
        if 'skip_errors' in params:
            skip_errors = params['skip_errors']
            del params['skip_errors']
        if 'run_in_process' in params:
            del params['run_in_process']

        pp = create_object_by_class('auger_ml.preprocessors.' + pp_name, params)
        max_preprocess_time_seconds = max(
            int(self.options.get("max_preprocess_time_mins", 20) * 60), 1)

        @threading_timeoutable(default="Timeout")
        def _run_with_timeout(pp, df):
            try:
                return pp.fit_transform(df)
            except TimeoutException:
                self.warnings.append({
                    'name': pp_name,
                    'params': params,
                    'message': "timeout"
                })

            return None

        res = None
        try:
            res = _run_with_timeout(pp, df, timeout=max_preprocess_time_seconds)
            if passed_preprocessors is not None and res is not None:
                passed_preprocessors.append({pp_name: pp})
                if pp_name == 'scale.ScalePreprocessor' and self.options['targetFeature'] in pp._min:
                    self.options['pp_fold_groups_params'] = {
                        self.options['fold_group']: {
                            'scale_target_min':  pp._min[self.options['targetFeature']],
                            'scale_target_max':  pp._max[self.options['targetFeature']],
                        }
                    }

            if res is None:
                res = df

        except Exception as e:
            if skip_errors:
                self.warnings.append({
                    'name': pp_name,
                    'params': params,
                    'message': str(e)
                })
                res = df
            else:
                logging.exception("Preprocessor %s(%s) failed"%(pp_name, params))
                value, traceback = sys.exc_info()[1:]
                raise PreprocessorException(
                    pp_name, params, str(e), str(traceback))

        return res
