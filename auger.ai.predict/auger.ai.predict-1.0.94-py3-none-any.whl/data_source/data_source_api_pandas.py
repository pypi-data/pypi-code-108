from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
#import arff
#import gzip
#from imblearn.over_sampling import *
import math
import numpy as np
import os
import pandas as pd
import sklearn
import warnings
from functools import wraps
import copy

from auger_ml.FSClient import FSClient
from auger_ml.Utils import get_uid, remove_dups_from_list, dict_keys_to_string, parse_url


#To avoid warnings for inplace operation on datasets
pd.options.mode.chained_assignment = None

class DataSourceAPIPandas(object):
    BOOLEAN_WORDS_TRUE = ['yes', 't']
    BOOLEAN_WORDS_FALSE = ['no', 'f']

    def __init__(self, options):
        self.options = options
        self.categoricals = {}
        self.transforms_log = [[],[],[],[]]
        self.df = None
        self.dataset_name = None
        self.loaded_columns = None

    # @staticmethod
    # def load_columns_from_file(path):
    #     with FSClient().open(path, 'r') as f:
    #         if path.endswith('.csv'):
    #             for line in f:
    #                 return line.strip().split(',')
    #             else:
    #                 raise RuntimeError('empty CSV file')

    #         if path.endswith('.arff'):
    #             obj = arff.load(f, return_type=arff.COO)
    #             return [a[0] for a in obj['attributes']]

    #         raise NotImplementedError

    def _get_compression(self, extension):
        compression = self.options.get('data_compression', 'infer')
        if extension.endswith('.gz') or extension.endswith('.gzip'):
            compression = 'gzip'
        elif extension.endswith('.bz2'):
            compression = 'bz2'
        elif extension.endswith('.zip'):
            compression = 'zip'
        elif extension.endswith('.xz'):
            compression = 'xz'

        return compression

    @staticmethod
    def create_dataframe(data_path=None, records=None, features=None, reset_index=False):
        if data_path is not None:
            if isinstance(data_path, pd.DataFrame):
                ds = DataSourceAPIPandas({})
                ds.df = data_path
            elif isinstance(data_path, DataSourceAPIPandas):
                ds = data_path
            elif isinstance(data_path, list):
                ds = DataSourceAPIPandas({})
                ds.load_records(data_path)
            elif isinstance(data_path, dict):
                ds = DataSourceAPIPandas({})

                if 'data' in data_path and 'columns' in data_path:
                    ds.load_records(data_path['data'], features=data_path['columns'])
                else:
                    ds.load_records(data_path)
            else:
                ds = DataSourceAPIPandas({'data_path': data_path})
                ds.load(features = features, use_cache=False)
        else:
            ds = DataSourceAPIPandas({})
            ds.load_records(records, features=features)

        if reset_index and ds.df is not None:
            ds.df.reset_index(drop=True, inplace=True)

        return ds

    @staticmethod
    def load_from_files(files, features=None):
        for file in files:
            path = file if type(file) == str else file['path']
            df = DataSourceAPIPandas.create_dataframe(path, None, features)
            yield (file, df)

    def load_from_file(self, path, features=None, nrows=None):
        from collections import OrderedDict

        if not FSClient().isAbsPath(path) and 'augerInfo' in self.options:
            path = os.path.join(self.options['augerInfo']['project_path'], path)

        extension = path
        if self.options.get('data_extension', 'infer') != 'infer':
            extension = self.options['data_extension']

        if self.options.get('content_type') == 'multipart':
            FSClient().merge_folder_files(path)

        #logging.info("load_from_file path: %s, extension: %s"%(path, extension))
        if extension.endswith('.arff') or extension.endswith('.arff.gz'):
            from auger_ml.Utils import process_arff_line
            import arff
            
            #TODO: support nrows  in arff
            arffFile = None
            class ArffFile:
                def __init__(self, file):
                    self.file = file
                    self.date_attrs = {}

                def __iter__(self):
                    return self

                def __next__(self):
                    line = process_arff_line(next(self.file), self.date_attrs)
                    return line

            try:

                with FSClient().open(path, 'r') as f:
                    arffFile = ArffFile(f)
                    arff_data = arff.load(arffFile, return_type=arff.COO)

                convert_arff = DataSourceAPIPandas._convert_arff_coo
            except arff.BadLayout:
                with FSClient().open(path, 'r') as f:
                    arffFile = ArffFile(f)
                    arff_data = arff.load(arffFile, return_type=arff.DENSE)

                convert_arff = DataSourceAPIPandas._convert_arff_dense

            columns = [a[0] for a in arff_data['attributes']]
            series = convert_arff(features, columns, arff_data['data'])

            res = pd.DataFrame.from_dict(OrderedDict(
                (c, s) for c, s in zip(columns, series) if s is not None
            ))
            for date_field, fmt in arffFile.date_attrs.items():
                #print(date_field, fmt)
                res[date_field] = pd.to_datetime(res[date_field], infer_datetime_format=True, errors='ignore', utc=True)

            return res
        elif extension.endswith('.pkl') or extension.endswith('.pkl.gz'):
            #TODO: support nrows  in pkl file
            return self.loadFromBinFile(path, features)
        elif extension.endswith('.json') or extension.endswith('.json.gz'):
            with FSClient().s3fs_open(path) as f:
                res = pd.read_json(f, orient=self.options.get('json_orient',None))

            if features:
                res = res[features]
            return res
        elif extension.endswith('.xlsx') or extension.endswith('.xls'):
            with FSClient().s3fs_open(path) as f:
                return pd.read_excel(f, usecols=features)
        elif extension.endswith('.feather') or extension.endswith('.feather.gz') or extension.endswith('.feather.zstd') or extension.endswith('.feather.lz4'):
            return self.loadFromFeatherFile(path, features=features)
        elif extension.endswith('.parquet'):
            return self.loadFromParquetFile(path, features=features)

        csv_with_header = self.options.get('csv_with_header', True)
        header = 0 if csv_with_header else None
        prefix = None if csv_with_header else 'c'

        compression = self._get_compression(extension)
        res_df = None
        try:
            with FSClient().s3fs_open(path) as f:
                res_df = pd.read_csv( f,
                        encoding='utf-8',
                        escapechar="\\",
                        usecols=features,
                        na_values=['?'],
                        header=header,
                        prefix=prefix,
                        sep = ',',
                        nrows=nrows,
                        low_memory=False,
                        compression=compression
                    )
        except Exception as e:
            if 'Usecols do not match columns' in str(e):
                raise

            logging.error("read_csv failed: %s"%e)
            with FSClient().s3fs_open(path) as f:
                res_df = pd.read_csv( f,
                    encoding='utf-8',
                    escapechar="\\",
                    usecols=features,
                    na_values=['?'],
                    header=header,
                    prefix=prefix,
                    sep = '|',
                    nrows=nrows,
                    low_memory=False,
                    compression=compression
                )

        return res_df

    def load(self, features=None, use_cache=True, nrows=None):
        self.categoricals = {}
        self.transforms_log = [[],[],[],[]]

        if use_cache and self.loadFromCacheFile("data_transformed",
            features, self.options.get("datetimeFeatures", None)):
            transformations_path = self._get_datacache_path("transformations.json")
            if FSClient().isFileExists(transformations_path):
                self.transforms_log = FSClient().readJSONFile(transformations_path)
        else:
            import csv
            from io import StringIO

            path = self.options['data_path']
            if isinstance(path, StringIO):
                path.seek(0)
                self.df = pd.read_csv(path, #parse_dates=self.options.get("datetimeFeatures", None),
                    encoding='utf-8', escapechar="\\", usecols=features, na_values=['?'], nrows=nrows)
                if self.options.get("targetFeature") in self.df.columns:
                    self.dropna([self.options["targetFeature"]])
            else:
                if path.startswith("jdbc:"):
                    import psycopg2
                    from psycopg2.extensions import parse_dsn

                    path = path.replace('sslfactory=org.postgresql.ssl.NonValidatingFactory&', '')
                    path, params = parse_url(path)

                    self.dbconn_args = parse_dsn(path)
                    conn = psycopg2.connect(**self.dbconn_args)
                    sql_cmd = "select " + (",".join(features) if features else "*") +" from %s"%params['tablename'][0]
                    if 'limit' in params:
                        sql_cmd += " LIMIT %s"%params['limit'][0]

                    if 'offset' in params:
                        sql_cmd += " OFFSET %s"%params['offset'][0]

                    logging.info("Read data from remote DB: %s"%sql_cmd)
                    self.df = pd.read_sql(sql_cmd, con=conn)
                else:
                    path, remote_path = self._check_remote_path()
                    try:
                        self.df = self.load_from_file(path, features=features, nrows=nrows)
                    except:
                        if remote_path:
                            logging.exception("Loading local file failed. Download it again...")
                            self.options['data_path'] = remote_path
                            path, remote_path = self._check_remote_path(force_download=True)
                            self.df = self.load_from_file(path, features=features, nrows=nrows)
                        else:
                            raise

                    self.dataset_name = os.path.basename(path)

                if self.options.get("targetFeature") in self.df.columns:
                    self.dropna([self.options["targetFeature"]])

                #self._update_dataset_manifest({'name': self.dataset_name, 'statistics': {'stat_data':[]}}, skip_if_exists=True)

        if self.df is not None and self.options.get('discover_datetime', False):
            for name, value in self.df.dtypes.items():
                if value == 'object':
                    self.df[name] = pd.to_datetime(self.df[name], infer_datetime_format=True, errors='ignore', utc=True)

        return self

    def _check_remote_path(self, force_download=False):
        from auger_ml.Utils import download_file
        from auger_ml.LocalFSClient import LocalFSClient

        remote_path = None
        if self.options['data_path'].startswith("http:") or self.options['data_path'].startswith("https:"):
            local_dir = self.options.get('augerInfo', {}).get('dataTmpPath', LocalFSClient().get_temp_folder())
            file_name = self.options.get('augerInfo', {}).get('project_file_id', "")
            if not file_name:
                file_name = self.options.get('data_id', "")

            local_file_path = download_file(self.options['data_path'],
                local_dir=local_dir, file_suffix="_" + str(file_name), force_download=force_download)

            remote_path = self.options['data_path']
            self.options['data_path'] = local_file_path

        return self.options['data_path'], remote_path

    def _update_dataset_manifest(self, manifest, create_new_manifest=False):
        from auger_ml.core.auger_messenger import AugerMessenger
        old_manifest = {}
        if 'datacachePath' in self.options.get('augerInfo', {}):
            old_manifest = FSClient().readJSONFile(self._get_datacache_path("current_dataset_manifest.json"))

        manifest['data_path'] = self.options.get('data_path')
        manifest['experiment_id'] = self.options['augerInfo'].get('experiment_id')

        if create_new_manifest:
            manifest['id'] = get_uid()
        else:
            manifest['id'] = self.options['augerInfo'].get('dataset_manifest_id')

        # if remove_stat_if_exists and old_manifest.get('statistics'):
        #     del manifest['statistics']

        if 'datacachePath' in self.options.get('augerInfo', {}):
            if 'name' in old_manifest:
                manifest['name'] = old_manifest['name']

            for key, value in manifest.items():
                old_manifest[key] = value

            FSClient().writeJSONFile(self._get_datacache_path("current_dataset_manifest.json"), old_manifest)

        if create_new_manifest:
            AugerMessenger(self.options).send_create_dataset_manifest(manifest)
        else:
            AugerMessenger(self.options).send_update_dataset_manifest(manifest)

    def get_dataset_manifest_id(self):
        manifest = self.get_dataset_manifest()
        uid = manifest.get('id')
        if not uid:
            uid = get_uid()

        return uid

    def get_dataset_manifest(self):
        if 'datacachePath' in self.options.get('augerInfo', {}):
            return FSClient().readJSONFile(self._get_datacache_path("current_dataset_manifest.json"))
        else:
            return {}

    def load_records(self, records, features=None):
        self.categoricals = {}
        self.transforms_log = [[],[],[],[]]

        if features:
            self.df = pd.DataFrame.from_records(records, columns=features)
            self.loaded_columns = features
        else:
            self.df = pd.DataFrame(records) #dict

        return self

    def saveToFile(self, path):
        if path.endswith('.feather') or path.endswith('.feather.gz') or path.endswith('.feather.zstd') or path.endswith('.feather.lz4'):
            self.saveToFeatherFile(path)
        elif path.endswith('.parquet'):
            self.saveToParquetFile(path)
        else:
            self.saveToCsvFile(path, compression="infer")

    def saveToCsvFile(self, path, compression="gzip"):
        FSClient().removeFile(path)
        FSClient().createParentFolder(path)

        with FSClient().save_local(path) as local_path:
            self.df.to_csv(local_path, index=False, compression=compression, encoding='utf-8')

    def saveToParquetFile(self, path, compression="gzip"):
        FSClient().removeFile(path)
        FSClient().createParentFolder(path)

        with FSClient().save_local(path) as local_path:
            self.df.to_parquet(local_path, index=False, compression=compression)

    def saveToBinFile(self, path):
        FSClient().saveObjectToFile(self.df, path)

    def loadFromBinFile(self, path, features=None):
        self.df = FSClient().loadObjectFromFile(path)

        if features:
            self.df =  self.df[features]

        return self.df

    def saveToFeatherFile(self, path):
        FSClient().saveObjectToFile(self.df, path, fmt="feather")

    def loadFromFeatherFile(self, path, features=None):
        self.df = FSClient().loadDBFromFeatherFile(path, features)
        return self.df

    def loadFromParquetFile(self, path, features=None):
        self.df = FSClient().loadDBFromParquetFile(path, features)
        return self.df

    def saveToCacheFile(self, name):
        path = self._get_datacache_path(name + ".pkl.gz")
        uid_path = self._get_datacache_path(name + ".uid.json")
        FSClient().removeFile(uid_path)

        self.saveToBinFile(path)
        FSClient().writeJSONFile(uid_path, {'uid': get_uid()})

        return path

    def loadFromCacheFile(self, name, features=None, parse_dates=None):
        if self.options.get('augerInfo', {}).get('datacachePath') is not None:
            path = self._get_datacache_path(name + ".pkl.gz")
            try:
                if FSClient().isFileExists(path):
                    self.df = self.loadFromBinFile(path, features)
                    return True
            except:
                logging.exception("Failed to load cache file: %s"%path)

        return False

    def has_cached_data(self):
        if self.options.get('augerInfo', {}).get('datacachePath') is not None:
            path = self._get_datacache_path("data_transformed.pkl.gz")
            if FSClient().isFileExists(path):
                return True

        return False

    def count(self):
        if self.df is not None:
            return len(self.df)
        else:
            return 0

    def getCategoricalsInfo(self):
        return self.categoricals

    @property
    def columns(self):
        return self.df.columns.tolist()

    def _map_dtypes(self, dtype):
        dtype_map = {'int64': 'integer', 'float64':'double', 'object': 'string',
            'categorical':'categorical', 'datetime64[ns]': 'datetime', 'bool': 'boolean'}
        if dtype_map.get(dtype, None):
            return dtype_map[dtype]

        if dtype and (dtype.startswith('int') or dtype.startswith('uint')):
            return 'integer'

        if dtype and dtype.startswith('float'):
            return 'float'

        if dtype and dtype.startswith('double'):
            return 'double'

        if dtype and dtype.startswith('datetime64'):
            return 'datetime'

        return dtype

    @property
    def dtypes(self):
        types_list = []
        columns_list = self.columns
        for idx, dtype in enumerate(self.df.dtypes):
            types_list.append((columns_list[idx], self._map_dtypes(dtype.name)))

        return types_list

    @property
    def dtypes_dict(self):
        types_dict = {}
        columns_list = self.columns
        for idx, dtype in enumerate(self.df.dtypes):
            types_dict[columns_list[idx]] = self._map_dtypes(dtype.name)

        return types_dict

    def get_text_cols(self):
        text_cols = []

        for item in self.dtypes:
            if item[1] == 'string':
                text_cols.append(item[0])

        return text_cols

    def getOptions(self):
        return self.options

    def setOptions(self, value):
        self.options = value

    def select(self, features):
        self.df = self.df[features]
        return self

    def select_and_limit(self, features, limit):
        res = []
        if features:
            if limit > 0:
                res = self.df[features].head(limit)
            else:
                res = self.df[features]
        else:
            if limit > 0:
                res = self.df.head(limit)
            else:
                res = self.df

        return res.values.tolist()

    def sort(self, columns, ascending=True):
        self.df.sort_values(columns, ascending = ascending, inplace=True)

    def drop(self, columns):
        self.df.drop(columns, inplace=True, axis=1)

    def drop_duplicates(self, columns=None):
        self.df.drop_duplicates(subset=columns, inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        return self

    def dropna(self, columns=None):
        self.df.dropna(subset=columns, inplace=True, axis=0)
        self.df.reset_index(drop=True, inplace=True)
        return self

    def fillna(self, value):
        if isinstance(value, dict):
            value = value.copy()
            for item in self.dtypes:
                if list(value.keys())[0] == item[0]:
                    if item[1] == 'string':
                        value[list(value.keys())[0]] = str(list(value.values())[0])
                    elif item[1] == 'integer':
                        value[list(value.keys())[0]] = int(list(value.values())[0])
                    else:
                        value[list(value.keys())[0]] = float(list(value.values())[0])

        #print(value)
        self.df.fillna(value, inplace=True)
        return self

    @staticmethod
    def encode_feature_list(list_features_arg):
        from urllib.parse import quote

        list_features = list_features_arg.copy()
        for idx, name in enumerate(list_features):
            encoded_name = quote(name)
            if encoded_name != name:
                list_features[idx] = encoded_name

        return list_features

    def encode_features(self):
        from urllib.parse import quote

        rename_cols = {}
        feature_names = self.columns

        for name in feature_names:
            encoded_name = quote(name)
            if encoded_name != name:
                rename_cols[name] = encoded_name

        self.df.rename(columns=rename_cols, inplace=True)

    def convertToCategorical(self, col_names, is_target = False, categories = None):
        #print("convertToCategorical:%s"%col_names)
        if not isinstance(col_names, list):
            col_names = [col_names]

        if is_target:
            for col in col_names:
                if col in self.columns and self.categoricals.get(col, None) is None:
                    self.df[col] = pd.Categorical(self.df[col], categories=categories)
                    self.categoricals[col] = {'categories': list(self.df[col].cat.categories)}
                    self.df[col] = self.df[col].cat.codes
        else:
            cols_to_process = []
            cols = self.columns
            for col in col_names:
                if col in cols:
                    cols_to_process.append(col)

            #print(cols_to_process)
            if cols_to_process:
                self.df = pd.get_dummies(self.df, columns=cols_to_process)
                new_cols = self.columns

                for col in cols_to_process:
                    generated_cols = []
                    for new_col in new_cols:
                        if new_col.startswith(col+'_'):
                            generated_cols.append(new_col)

                    self.categoricals[col] = {'columns': generated_cols}

        return self

    def expandCategoricalFeatures(self, features):
        res = []
        for feature in features:
            if self.categoricals.get(feature):
                if self.categoricals[feature].get('columns'):
                    res.extend(self.categoricals[feature].get('columns'))
                else:
                    res.append(feature)
            else:
                res.append(feature)

        return res

    def getSummary(self):
        types_list = []
        columns_list = self.df.columns.tolist()
        for idx, dtype in enumerate(self.df.dtypes):
            types_list.append((columns_list[idx], self._map_dtypes(dtype.name)))

        info = {"dtypes": self.dtypes, "count": self.count(), 'columns_count': len(self.columns),'data_path': self.options['data_path']}
        stat_data = []
        for x in info['dtypes']:
            cname = str(x[0])
            ctype = x[1]
            children = []

            if ctype == 'string':
                children = self._check_for_json(cname)

            # add children or just add row
            if children:
                stat_data = stat_data + children
            else:
                item = {
                    'column_name': cname,
                    'orig_datatype': ctype,
                    'datatype': ctype,
                }

                if ctype == 'integer' or ctype == 'float' or ctype == 'double':
                    mean = self.__format_number_for_serialization(self.df[cname].mean())
                    if mean:
                        item['avg'] = mean

                    std = self.__format_number_for_serialization(self.df[cname].std())
                    if std:
                        item['std_dev'] = std

                stat_data.append(item)

        #TODO : remove from UI isTarget and use
        lef = set(self.options.get('labelEncodingFeatures', []))
        tf = self.options.get('targetFeature', "")
        fc = set(self.options.get('featureColumns', []))
        tsf = set(self.options.get('timeSeriesFeatures', []))
        dtf = self.options.get('datetimeFeatures', [])
        if dtf is None:
            dtf = []

        for row in stat_data:
            row['isTarget'] = False
            row['use'] = False

            cname = row['column_name']
            if row['datatype'] == 'string':
                row['datatype'] = 'hashing' if cname in lef else 'categorical'

            if cname == tf:
                row['isTarget'] = True
            if cname in fc:
                row['use'] = True
            if cname in tsf:
                row['datatype'] = 'timeseries'
            if cname in dtf:
                row['datatype'] = 'datetime'

        info['stat_data'] = stat_data
        del info['dtypes']

        return info

    def getStatistics(self, create_new_manifest=False, update_manifest=True):
        summary = self.getSummary()
        describe = None
        try:
            describe = self.df.describe(include='all')
        except:
            logging.exception("describe failed.")

        c = set(self.columns)
        lef = set(self.options.get('labelEncodingFeatures', []))
        cf = set(self.options.get('categoricalFeatures', []))
        fc = set(self.options.get('featureColumns', []))
        histogram_count = 0
        cat_value_counts = 0
        for row in summary['stat_data']:
            try:
                if row['column_name'] in c:
                    row['unique_values'] = 0
                    if describe is not None:
                        count = describe[row['column_name']]['count']
                        if not np.isnan(count) and summary['count'] - int(count) > 0:
                            row['missing_values'] = summary['count'] - int(count)

                        if not np.isnan(describe[row['column_name']].get('min',np.nan)):
                            min_value = "{0:.2f}".format(float(describe[row['column_name']]['min']))
                            max_value = "{0:.2f}".format(float(describe[row['column_name']]['max']))

                            row['range'] = [min_value, max_value]

                        if 'unique' in describe[row['column_name']] and not np.isnan(describe[row['column_name']]['unique']):
                            row['unique_values'] = describe[row['column_name']]['unique']
                        elif row['datatype'] == 'integer' or row['datatype'] == 'float' or row['datatype'] == 'double' \
                            or row['datatype'] == 'categorical' or row['datatype'] == 'hashing' or row['datatype'] == 'boolean':
                            row['unique_values'] = self.df[row['column_name']].nunique()
                    elif row['datatype'] == 'integer' or row['datatype'] == 'float' or row['datatype'] == 'double' \
                        or row['datatype'] == 'categorical' or row['datatype'] == 'hashing' or row['datatype'] == 'boolean':
                        row['unique_values'] = self.df[row['column_name']].nunique()

                    if row['datatype'] == 'integer' or row['datatype'] == 'float' or row['datatype'] == 'double' \
                        or row['datatype'] == 'categorical' or row['datatype'] == 'hashing' or row['datatype'] == 'boolean':
                        try:
                            if histogram_count < self.options.get('max_histogram_count', 50):
                                hist, bin_edges = np.histogram(self.df[row['column_name']], bins=self.options.get('histogram_bins', 10))
                                row['histogram'] = {'hist': list(hist), 'bin_edges': list(bin_edges)}
                                histogram_count += 1
                            #print(row['column_name'], row['histogram'])
                        except Exception as e:
                            #print(e)
                            pass

                    if row.get('missing_values'):
                        row['unique_values'] = row.get('unique_values', 0) + 1

                    if row['column_name'] in lef:
                        row['datatype'] = 'hashing'
                    elif row['column_name'] in cf:
                        row['datatype'] = 'categorical'
                    elif row['datatype'] == 'categorical':
                        if row['unique_values'] > self.options.get('max_categoricals_nunique', 50):
                            row['datatype'] = 'hashing'
                        # elif row['unique_values'] == 2 and row['orig_datatype'] == 'string' and row.get('value_counts'):
                        #     is_bool = True
                        #     for key in row['value_counts'].keys():
                        #         if key and not (key.lower() in BOOLEAN_WORDS_TRUE or key.lower() in BOOLEAN_WORDS_FALSE):
                        #             is_bool = False

                        #     if is_bool:
                        #         row['datatype'] = 'boolean'

                    # elif row.get('unique_values', 0) < self.options.get('min_categoricals_nunique', 10) and \
                    #      row.get('unique_values', 0) > 1:
                    #     if  row['datatype'] != 'boolean':
                    #         if (row['datatype'] == 'integer' or row['datatype'] == 'float' or row['datatype'] == 'double') and \
                    #             row.get('unique_values') == 2 and row.get('range'):
                    #             if row['range'][0] == '0.00' and row['range'][1] == '1.00':
                    #                 row['datatype'] = 'boolean'
                    #             else:
                    #                 row['datatype'] = 'categorical'
                    #         else:
                    #             row['datatype'] = 'categorical'

                    if row['datatype'] == 'categorical' and cat_value_counts < self.options.get('max_cat_value_counts', 50):
                        row['value_counts'] = self.df[row['column_name']].value_counts().to_dict()
                        if row['orig_datatype'] == 'datetime' or row['orig_datatype'] == 'string':
                            row['value_counts'] = dict_keys_to_string(row['value_counts'])

                        cat_value_counts += 1

                    if row['datatype'] == 'categorical':
                        if row['unique_values'] == 2 and row['orig_datatype'] == 'string' and row.get('value_counts'):
                            is_bool = True
                            for key in row['value_counts'].keys():
                                if key and not (key.lower() in DataSourceAPIPandas.BOOLEAN_WORDS_TRUE or key.lower() in DataSourceAPIPandas.BOOLEAN_WORDS_FALSE):
                                    is_bool = False

                            if is_bool:
                                row['datatype'] = 'boolean'

                    if row['datatype'] == 'boolean' and not row.get('value_counts'):
                        row['value_counts'] = self.df[row['column_name']].value_counts().to_dict()

                    if len(fc) == 0 and row['datatype'] != 'string':
                        if not row.get('unique_values') or row.get('unique_values') > 1:
                            if row['datatype'] == 'datetime' or row['datatype'] == 'timeseries':
                                row['use'] = True
                            elif row.get('unique_values', 0) < self.count():
                                row['use'] = True

                    if row.get('value_counts'):
                        row['value_counts_ex'] = []
                        for key, value in row['value_counts'].items():
                            row['value_counts_ex'].append({"value": key, "count": value})

            except Exception as e:
                logging.exception("getStatistics failed for field: %s."%(row['column_name']))

        if update_manifest:
            self._update_dataset_manifest({'statistics': summary}, create_new_manifest)

        return summary

    def error_decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                logging.exception("DataSourceAPIPandas method: %s failed."%str(method))
                return {}

        return wrapper

    def getMetaFeatures(self, create_new_manifest=False):
        statistics = self.getStatistics(update_manifest=False)
        manifest = {'statistics': statistics}
        manifest['metafeatures'] = self._doMetaFeatures(statistics)
        #logging.info(manifest['metafeatures'])
        self._update_dataset_manifest(manifest, create_new_manifest)

        return manifest

    #@error_decorator
    def _doMetaFeatures(self, data):
        from scipy.stats import kurtosis, skew, entropy
        from sklearn.metrics import mutual_info_score
        from sklearn.preprocessing import LabelEncoder
        from collections import Counter

        numeric_dtypes = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

        features = {}

        if data:
            all_features = self.options['featureColumns']
        else:
            all_features = self.columns

        target_name = self.options['targetFeature']

        if target_name in self.columns:
            df_target = self.df[target_name]
            if target_name in all_features:
                all_features.remove(target_name)

        df_data = self.df[all_features]

        categoricals = list(self.options.get('categoricalFeatures', []))
        is_target_categorical = False
        if target_name in categoricals:
            is_target_categorical = True
            categoricals.remove(target_name)

        categoricals = [x for x in categoricals if x in all_features]

        #numerics = list(set(all_features) - set(categoricals))
        df_numeric = df_data.select_dtypes(include=numeric_dtypes)

        num_features = df_data.shape[1]
        num_instances = df_data.shape[0]
        num_numeric = df_numeric.shape[1]
        num_categorical = len(categoricals)

        if num_instances > 0:
            features['Dimensionality'] = float(num_features) / float(num_instances)
            features['NumberOfInstances'] = num_instances
            features['NumberOfFeatures'] = num_features
            features['NumberOfClasses'] = df_target.unique().size

            counts = df_data.count(axis='columns')

            # df_data.isnull().values.ravel().sum()
            features['NumberOfMissingValues'] = df_data.size - counts.sum()

            # df_data.shape[0] - df_data.dropna().shape[0]
            features['NumberOfInstancesWithMissingValues'] = (counts < len(df_data.columns)).sum()

            features['NumberOfNumericFeatures'] = num_numeric
            features['NumberOfSymbolicFeatures'] = num_categorical
            features['NumberOfBinaryFeatures'] = 0

            features['PercentageOfNumericFeatures'] = float(num_numeric) / float(num_features) if num_features > 0 else 0
            features['PercentageOfSymbolicFeatures'] = float(num_categorical) / float(num_features) if num_features > 0 else 0
            features['PercentageOfBinaryFeatures'] = 0

            values_size = df_data.size
            features['PercentageOfMissingValues'] = float(features['NumberOfMissingValues']) / values_size if values_size else 0
            features['PercentageOfInstancesWithMissingValues'] = float(features['NumberOfInstancesWithMissingValues']) / num_instances

            #print("PercentageOfMissingValues = {}".format(features['PercentageOfMissingValues']))
            #print("PercentageOfInstancesWithMissingValues = {}".format(features['PercentageOfInstancesWithMissingValues']))

            means_among_numeric_list = df_numeric.mean().dropna().values
            std_numeric_list = df_numeric.std().dropna().values
            # df_numeric.apply(lambda x: x.unique().size).values
            numeric_num_uniq_list = df_numeric.nunique().values
            numeric_kurtosis_list = df_numeric.apply(lambda x: kurtosis(x.dropna(), nan_policy='omit')).dropna().values
            numeric_skew_list = df_numeric.apply(lambda x: skew(x.dropna(), nan_policy='omit')).dropna().values

            if len(means_among_numeric_list) == 0:
                means_among_numeric_list = [0]
                std_numeric_list = [0]
                numeric_num_uniq_list = [0]
                numeric_kurtosis_list = [0]
                numeric_skew_list = [0]

            categorical_num_uniq_list = []
            nominal_entropies_list = []
            nominal_mutual_info_list = []

            if len(categoricals) > 0:
                le = LabelEncoder()
                df_categorical = df_data[categoricals]
                for col in categoricals:
                    df_col = df_categorical[col]
                    cat_item = {}
                    for item in data.get('stat_data', []):
                        if item['column_name'] == col:
                            cat_item = item
                    # logger.debug("col_name: {}, col_values: {}".format(col, df_col))
                    try:
                        if data.get('stat_data'):
                            categorical_num_uniq_list.append(cat_item.get("unique_values", 0))
                        else:
                            categorical_num_uniq_list.append(df_col.unique().size)

                        ent = entropy(list(Counter(df_col.values).values()), base=2)
                        nominal_entropies_list.append(ent)

                        mi = 0
                        if is_target_categorical:
                            td = self.df[[col, target_name]].dropna()
                            if len(td):
                                p = le.fit_transform(td[col]).astype(np.int64)
                                t = le.fit_transform(td[target_name]).astype(np.int64)
                                mi = auger_mutual_info_score(t, p)
                                # logging.info("col: {}, labels: {}, MI: {}".format(col, td[col].unique(), mi))
                        nominal_mutual_info_list.append(mi)
                    except Exception as e:
                        #logging.error("Warning! Column {} is empty (all values are missing)!".format(col))
                        logging.exception("Categorical processing failed for: {}\n{}".format(col, repr(e)))

            if not categorical_num_uniq_list:
                categorical_num_uniq_list = [0]
            if not nominal_entropies_list:
                nominal_entropies_list = [0]
            if not nominal_mutual_info_list:
                nominal_mutual_info_list = [0]

            features['MinAttributeEntropy'] = min(nominal_entropies_list)
            features['MaxAttributeEntropy'] = max(nominal_entropies_list)
            features['MeanAttributeEntropy'] = np.mean(nominal_entropies_list)
            features['MedianAttributeEntropy'] = np.median(nominal_entropies_list)
            features['Quartile1AttributeEntropy'] = np.percentile(nominal_entropies_list, 25)
            features['Quartile2AttributeEntropy'] = np.percentile(nominal_entropies_list, 50)
            features['Quartile3AttributeEntropy'] = np.percentile(nominal_entropies_list, 75)

            # MeansOfNumericAtts
            features['MinMeansOfNumericAtts'] = min(means_among_numeric_list)
            features['MaxMeansOfNumericAtts'] = max(means_among_numeric_list)
            features['MeanMeansOfNumericAtts'] = np.mean(means_among_numeric_list)
            features['MedianMeansOfNumericAtts'] = np.median(means_among_numeric_list)
            features['Quartile1MeansOfNumericAtts'] = np.percentile(means_among_numeric_list, 25)
            features['Quartile2MeansOfNumericAtts'] = np.percentile(means_among_numeric_list, 50)
            features['Quartile3MeansOfNumericAtts'] = np.percentile(means_among_numeric_list, 75)

            # StdDevOfNumericAtts
            if list(std_numeric_list):
                features['MinStdDevOfNumericAtts'] = min(std_numeric_list)
                features['MaxStdDevOfNumericAtts'] = max(std_numeric_list)
                features['MeanStdDevOfNumericAtts'] = np.mean(std_numeric_list)
                features['MedianStdDevOfNumericAtts'] = np.median(std_numeric_list)
                features['Quartile1StdDevOfNumericAtts'] = np.percentile(std_numeric_list, 25)
                features['Quartile2StdDevOfNumericAtts'] = np.percentile(std_numeric_list, 50)
                features['Quartile3StdDevOfNumericAtts'] = np.percentile(std_numeric_list, 75)
            else:
                features['MinStdDevOfNumericAtts'] = 0
                features['MaxStdDevOfNumericAtts'] = 0
                features['MeanStdDevOfNumericAtts'] = 0
                features['MedianStdDevOfNumericAtts'] = 0
                features['Quartile1StdDevOfNumericAtts'] = 0
                features['Quartile2StdDevOfNumericAtts'] = 0
                features['Quartile3StdDevOfNumericAtts'] = 0

            # CardinalityOfNumericAttributes
            features['MinCardinalityOfNumericAttributes'] = min(numeric_num_uniq_list)
            features['MaxCardinalityOfNumericAttributes'] = max(numeric_num_uniq_list)
            features['MeanCardinalityOfNumericAttributes'] = np.mean(numeric_num_uniq_list)
            features['MedianCardinalityOfNumericAttributes'] = np.median(numeric_num_uniq_list)
            features['Quartile1CardinalityOfNumericAttributes'] = np.percentile(numeric_num_uniq_list, 25)
            features['Quartile2CardinalityOfNumericAttributes'] = np.percentile(numeric_num_uniq_list, 50)
            features['Quartile3CardinalityOfNumericAttributes'] = np.percentile(numeric_num_uniq_list, 75)

            # KurtosisOfNumericAtts
            features['MinKurtosisOfNumericAtts'] = min(numeric_kurtosis_list)
            features['MaxKurtosisOfNumericAtts'] = max(numeric_kurtosis_list)
            features['MeanKurtosisOfNumericAtts'] = np.mean(numeric_kurtosis_list)
            features['MedianKurtosisOfNumericAtts'] = np.median(numeric_kurtosis_list)
            features['Quartile1KurtosisOfNumericAtts'] = np.percentile(numeric_kurtosis_list, 25)
            features['Quartile2KurtosisOfNumericAtts'] = np.percentile(numeric_kurtosis_list, 50)
            features['Quartile3KurtosisOfNumericAtts'] = np.percentile(numeric_kurtosis_list, 75)

            # SkewnessOfNumericAtts
            features['MinSkewnessOfNumericAtts'] = min(numeric_skew_list)
            features['MaxSkewnessOfNumericAtts'] = max(numeric_skew_list)
            features['MeanSkewnessOfNumericAtts'] = np.mean(numeric_skew_list)
            features['MedianSkewnessOfNumericAtts'] = np.median(numeric_skew_list)
            features['Quartile1SkewnessOfNumericAtts'] = np.percentile(numeric_skew_list, 25)
            features['Quartile2SkewnessOfNumericAtts'] = np.percentile(numeric_skew_list, 50)
            features['Quartile3SkewnessOfNumericAtts'] = np.percentile(numeric_skew_list, 75)

            # CardinalityOfNominalAttributes
            features['MinCardinalityOfNominalAttributes'] = min(categorical_num_uniq_list)
            features['MaxCardinalityOfNominalAttributes'] = max(categorical_num_uniq_list)
            features['MeanCardinalityOfNominalAttributes'] = np.mean(categorical_num_uniq_list)
            features['MedianCardinalityOfNominalAttributes'] = np.median(categorical_num_uniq_list)
            features['Quartile1CardinalityOfNominalAttributes'] = np.percentile(categorical_num_uniq_list, 25)
            features['Quartile2CardinalityOfNominalAttributes'] = np.percentile(categorical_num_uniq_list, 50)
            features['Quartile3CardinalityOfNominalAttributes'] = np.percentile(categorical_num_uniq_list, 75)

            # NominaAttributesDistinctValues
            features['MinNominalAttDistinctValues'] = features['MinCardinalityOfNominalAttributes']
            features['MaxNominalAttDistinctValues'] = features['MaxCardinalityOfNominalAttributes']
            features['MeanNominalAttDistinctValues'] = features['MeanCardinalityOfNominalAttributes']
            features['StdvNominalAttributesDistinctValues'] = np.std(categorical_num_uniq_list)

            # Class-related features
            class_counts = Counter(df_target.values)
            majority_count = class_counts.most_common(1)[0][1]
            minority_count = class_counts.most_common()[-1][1]

            features['MinorityClassSize'] = minority_count
            features['MajorityClassSize'] = majority_count
            features['MinorityClassPercentage'] = minority_count / float(num_instances)
            features['MajorityClassPercentage'] = majority_count / float(num_instances)

            features['ClassEntropy'] = entropy(list(Counter(df_target.values).values()), base=2)

            order_chnages = 0
            # TODO: change to support regression
            for i in range(1, df_target.size):
                cur = df_target.values[i]
                prev = df_target.values[i - 1]

                # Regression:
                # order_chnages += prev - cur

                # Classification:
                order_chnages += 0 if prev == cur else 1

            features['AutoCorrelation'] = (num_instances - 1 - order_chnages) / (num_instances - 1) if num_instances > 1 else 0

            features['MeanMutualInformation'] = np.mean(nominal_mutual_info_list)
            features['MaxMutualInformation'] = np.max(nominal_mutual_info_list)
            features['MinMutualInformation'] = np.min(nominal_mutual_info_list)
            features['Quartile1MutualInformation'] = np.percentile(nominal_mutual_info_list, 25)
            features['Quartile2MutualInformation'] = np.percentile(nominal_mutual_info_list, 50)
            features['Quartile3MutualInformation'] = np.percentile(nominal_mutual_info_list, 75)

            ena = 0
            snr = 0

            if features['MeanMutualInformation'] <= 0:
                ena = -1
                snr = -1
            else:
                ena = features['ClassEntropy'] / features['MeanMutualInformation']
                snr = (features['MeanAttributeEntropy'] - features['MeanMutualInformation']) / features['MeanMutualInformation']

            features['EquivalentNumberOfAtts'] = ena
            features['MeanNoiseToSignalRatio'] = snr

        return features
        # # Check types
        # features_safe_pairs = []
        # for k, v in features.items():
        #     if type(v) in [np.int32, np.int64]:
        #         features_safe_pairs.append((k, int(v)))
        #     elif type(v) in [np.float32, np.float64]:
        #         features_safe_pairs.append((k, float(v)))
        #     else:
        #         features_safe_pairs.append((k, v))

        # return dict(features_safe_pairs)

    def filter_ex(self, params, conditions):
        cond_map = {'OR': '|', 'AND': "&"}

        query_text = ""
        for index, item in enumerate(params):
            cond_str = item.split(",")

            if conditions and index > 0:
                query_text += " " + cond_map[conditions[index-1]] + " " + " ".join(cond_str)
            else:
                query_text = " ".join(cond_str)

        # print(query_text)
        self.df.query(query_text, inplace=True)

        return self

    def search(self, params, features, limit):
        for key in params:
            tpl = params[key]
            val = tpl[0]
            op = tpl[1]

            if val == 'null':
                if op == '==':
                    query_text = key + "!=" + key
                else:
                    query_text = key + "==" + key
            else:
                query_text = key + " " + op + " " + str(val)

            self.df.query(query_text, inplace=True)

        return self.select_and_limit(features, limit)

    def calculateFeaturesCorrelation(self, model_features, target_feature):
        fields = self.dtypes_dict
        result = []
        cols_to_process = []

        if target_feature in fields and fields[target_feature] == 'string':
            self.convertToCategorical(target_feature, is_target=True)

        fields = self.dtypes_dict
        for col in model_features:
            if col in fields and fields[col] != 'string' and fields[col] != 'datetime':
                cols_to_process.append(col)

        if cols_to_process:
            res_corr = self.df[cols_to_process].corrwith(self.df[target_feature]).values
            for idx, col in enumerate(cols_to_process):
                if col != target_feature:
                    result.append( (col, format(res_corr[idx], '.2f') ) )

        manifest = {
            'correlation_to_target': result,
            'featureColumns': cols_to_process,
            'targetFeature': target_feature
        }

        self._update_dataset_manifest(manifest)
        return manifest

    def calculateAllFeaturesCorrelation(self, names):
        cols = self.columns
        cols_to_process = []
        result = []
        for col in names:
            if col in cols:
                cols_to_process.append(col)

        if cols_to_process:
            df_corr = self.df[cols_to_process].corr()
            result = self._convert_floats_to_str(df_corr)
            cols_to_process = df_corr.columns.tolist()

        manifest = {
            'correlation_matrix': result,
            'featureColumns': cols_to_process
        }

        self._update_dataset_manifest(manifest)
        return manifest

    def _isNumericType(self, col_type):
        if col_type.lower() == 'double' or col_type.lower() == 'float' or \
            col_type.lower() == 'integer' or col_type.lower() == 'boolean' or col_type.lower() == 'short' or col_type.lower() == 'byte' \
            or col_type.lower() == 'long' or col_type.lower() == 'decimal':
            return True

        return False

    def withJsonColumn(self, col_name, json_col_name, child_name, col_type):
        import json
        from auger_ml.Utils import convertStringsToUTF8

        def get_json_value(json_value, child_name, col_type):
            result = []
            for item in json_value:
                try:
                    #print(item)
                    res = json.loads(item, object_hook=convertStringsToUTF8)
                    if col_type.lower() == 'double' or col_type.lower() == 'float':
                        result.append(float(res[child_name]))
                    elif col_type.lower() == 'integer' or col_type.lower() == 'boolean' or col_type.lower() == 'short' or col_type.lower() == 'byte' \
                        or col_type.lower() == 'long' or col_type.lower() == 'decimal':
                        result.append(int(res[child_name]))
                    else:
                        result.append(res[child_name])
                except Exception as e:
                    #logging.exception("withJsonColumn failed for child name: %s."%(child_name))

                    if self._isNumericType(col_type):
                        result.append(0)
                    else:
                        result.append("")

            return result

        try:
            self.df[col_name] = get_json_value(self.df[json_col_name], child_name, col_type)
        except Exception as e:
            raise Exception("Extract from json field '%s'.'%s' to '%s' of type '%s' failed: %s"%(col_name, json_col_name, child_name, col_type, str(e)))
        return self

    def withNumericColumn(self, col_name):
        import re

        if not col_name in self.columns:
            return

        non_decimal = re.compile(r'[^\d.]+')
        field_type = self._map_dtypes(self.df[col_name].dtype.name)

        try:
            if field_type == 'string':
                self.df[col_name] = self.df[col_name].str.replace(non_decimal, '').astype(float)
            else:
                self.df[col_name] = self.df[col_name].astype(float)
        except Exception as e:
            logging.exception("withNumericColumn failed.")

            raise Exception("Cannot convert field '%s' from type '%s' to '%s': %s"%(col_name,
                field_type, 'double', str(e)))
        return self

    def withBooleanColumn(self, col_name):
        import re

        if not col_name in self.columns:
            return

        field_type = self._map_dtypes(self.df[col_name].dtype.name)

        try:
            def convert_to_boolean(col_name, x):
                x_lower = x.lower()
                if x_lower in DataSourceAPIPandas.BOOLEAN_WORDS_TRUE:
                    return 1

                if x_lower in DataSourceAPIPandas.BOOLEAN_WORDS_FALSE:
                    return 0

                raise Exception("Cannot convert field '%s' with value '%s' to Boolean"%(col_name, x))

            if field_type == 'string':
                self.df[col_name] = self.df[col_name].apply(lambda x: convert_to_boolean(col_name, x))
            else:
                self.df[col_name] = self.df[col_name].astype(bool)

        except Exception as e:
            logging.exception("withNumericColumn failed.")

            raise Exception("Cannot convert field '%s' from type '%s' to '%s': %s"%(col_name,
                field_type, 'double', str(e)))
        return self

    def withColumn(self, col_name, expra):
        #self.df = self.df.withColumn(col_name, expr(expra))
        return self

    def withCustomColumn(self, col_name, eval_text):
        #self.df = self.df.withColumn(col_name, eval(eval_text))
        return self

    def _convert_floats_to_str(self, data, precision='.2f'):
        str_res = []
        if len(data.shape) > 1:
            for res_row in data.values:
                result = [format(res, precision) for res in res_row]
                str_res.append(result)
        else:
            str_res = [format(res, precision) for res in data.values]

        return str_res

    def _check_for_json(self, cname):
        import json
        from auger_ml.Utils import convertStringsToUTF8

        rows = self.df[cname][(self.df[cname] != '[]') & (self.df[cname] != '{}')].values
        if rows is None or len(rows) == 0:
            return []
        else:
            row = rows[0]

        try:
            data = json.loads(row, object_hook=convertStringsToUTF8)
            children = []
            for key in data:
                name = str(key) + '_' + cname
                dtype = type(data[key]).__name__
                if dtype == 'unicode':
                    dtype = 'string'
                #cast_type = self.sparkTypes[dtype] + "Type()"

                # self.df = self.df.withColumn(name, get_json_object(
                #     self.df[cname], '$.%s' % str(key)).cast(eval(cast_type)))
                children.append({'column_name': name, 'orig_column_name': str(key), 'child': cname, 'orig_datatype': dtype, 'datatype': dtype})

            return children
        except Exception as e:
            return []

    @staticmethod
    def saveToFileFoldFunc(options, fold_idx, X_train, y_train,
            test_index, X_test, y_test, test_roi_data):
        path = options['data_folds_path_prefix'] + "%d" % fold_idx + ".pkl.gz"
        # np.savez_compressed(
        # path, X_train=X_train, y_train=y_train, test_index=test_index, X_test=X_test, y_test=y_test)
        FSClient().saveObjectToFile(
            {
                'X_train': X_train, 'y_train': y_train,
                'test_index': test_index, 'X_test': X_test, 'y_test': y_test,
                'test_roi_data': test_roi_data
            },
            path
        )
        return path

    @staticmethod
    def loadFoldFile_s(options, nFold=0, fold_path=None):
        if not fold_path:
            fold_path = str(options['data_folds_path'][nFold])
        # if 'data_folds_path' in options:
        #     fold_path = str(options['data_folds_path'][nFold])
        # else:
        #     fold_path = DataSourceAPIPandas.get_datacache_path_s(options, "traindata_fold")+ "%d.npz" % nFold

        # data_fold = np.load(fold_path)
        data_fold = FSClient().loadObjectFromFile(fold_path)

        return (data_fold['X_train'], data_fold['y_train'], data_fold['X_test'], data_fold['y_test'])

    def loadFoldFile(self, nFold=0, fold_path=None):
        return self.loadFoldFile_s(self.options, nFold, fold_path)

    def splitToFoldFiles(self, fold_name=None, test_data_index=None):
        if fold_name is None:
            fold_name="traindata_fold"

        #print(self.df)
        path = self._get_datacache_path(os.path.join(self.options.get('fold_group', ''), fold_name))
        FSClient().removeFile(path+"*", wild=True)
        self.options['data_folds_path_prefix'] = path

        return self.splitToFolds(DataSourceAPIPandas.saveToFileFoldFunc, test_data_index)

    @staticmethod
    def getFoldPath_s(options, nFold=0):
        return DataSourceAPIPandas.get_datacache_path_s(options, options.get('fold_group', '') + "/traindata_fold")+ "%d" % nFold + ".pkl.gz"

    def getFoldPath(self, nFold=0):
        return self.getFoldPath_s(self.options, nFold)

    def getFoldPaths(self):
        return [self.getFoldPath(nFold) for nFold in range(0, self.options.get('crossValidationFolds', 2))]

    def getFoldGroup_XY(self, fold_group_name):
        from auger_ml.data_splitters.XYNumpyDataPrep import XYNumpyDataPrep

        if self.options.get('test_data_path') or self.options.get('crossValidationFolds', 2) == 1:
            fold_path = self.getFoldPath(0)
            logging.info("Use train data to fit exported model: %s"%fold_path)
            X_train, y_train, X_test, y_test = self.loadFoldFile(fold_path=fold_path)

            return X_train, y_train
        else:
            old_fold_group_name = self.options.get('fold_group')
            self.options['fold_group'] = fold_group_name
            self.loadFromCacheFile(fold_group_name + "/data_preprocessed")
            X_train, y_train = XYNumpyDataPrep(self.options).split_training(self.df)
            res = self.oversamplingFit(X_train, y_train)
            self.options['fold_group'] = old_fold_group_name

            return res

    def call_fold_func(self, fold_func, fold_idx, **kfold_func_args):
        fold_file = self.options['data_folds_path'][fold_idx]
        data_fold = FSClient().loadObjectFromFile(str(fold_file), self.options.get('use_local_cache', False))
        return fold_func(self.options, fold_idx, data_fold['X_train'], data_fold['y_train'],
                        data_fold['test_index'], data_fold['X_test'], data_fold['y_test'],
                        data_fold.get('test_roi_data'),
                        **kfold_func_args)

    def load_roi_features(self, use_cache=True):
        from auger_ml.roi.calculator import Calculator as RoiCalculator

        roi_features = RoiCalculator(
            filter = self.options['roi_metric'].get('filter'),
            revenue = self.options['roi_metric'].get('revenue'),
            investment = self.options['roi_metric'].get('investment')
        ).get_var_names()
        logging.info("ROI features loaded from dataset: %s"%roi_features)
        return self.load(features = roi_features, use_cache=use_cache)

    @staticmethod
    def load_test_dataset(options):    
        test_options = copy.deepcopy(options)
        test_options['data_path'] = test_options['test_data_path']
        if test_options.get('test_data_compression'):
            test_options['data_compression'] = test_options['test_data_compression']
        elif  'data_compression' in test_options:
            del test_options['data_compression']

        if test_options.get('test_data_extension'):
            test_options['data_extension'] = test_options['test_data_extension']
        elif  'data_extension' in test_options:
            del test_options['data_extension']

        return DataSourceAPIPandas(test_options)

    def splitToFolds(self, fold_func, test_data_index, **kfold_func_args):
        from auger_ml.data_splitters.XYNumpyDataPrep import XYNumpyDataPrep
        from sklearn.utils import indexable
        from sklearn.utils import _safe_indexing
        from sklearn.model_selection._split import check_cv
        from sklearn.model_selection import train_test_split
        from sklearn.model_selection import StratifiedShuffleSplit, ShuffleSplit, StratifiedKFold, KFold, TimeSeriesSplit, GroupKFold, GroupShuffleSplit
        import gc
        from .group_splits import GroupTimeSeriesSplit, StratifiedGroupKFold

        result = []

        if self.options.get('data_folds_path', None):
            # print(self.options['data_folds_path'])
            for fold_idx, fold_file in enumerate(self.options['data_folds_path']):
                res = self.call_fold_func(fold_func, fold_idx)
                result.append(res)
        else:
            # self.fillna(0)
            data_shape = None
            features, target = XYNumpyDataPrep(self.options).split_training(self.df)

            logging.info("splitOptions: %s; test_data_index: %s" % (self.options.get('splitOptions', {}), test_data_index))

            if test_data_index is not None:
                test_roi_data = None

                if self.options.get('roi_metric'):
                    ds_roi = DataSourceAPIPandas.load_test_dataset(self.options).load_roi_features(use_cache=False)
                    test_roi_data = ds_roi.df

                X_train = features.head(test_data_index)
                y_train = target[:test_data_index]
                X_test = features.tail(self.count()-test_data_index)
                y_test = target[test_data_index:]

                X_train, y_train = self.oversamplingFit(X_train, y_train)
                res = fold_func(self.options, 0, X_train, y_train,
                                None, X_test, y_test, test_roi_data, **kfold_func_args)

                data_shape = features.shape
                result.append(res)
            else:
                cv_num = self.options.get('crossValidationFolds', 2)
                groups_col = self.options.get('splitOptions', {}).get('groups_col')
                groups = None
                if groups_col:
                    if groups_col in self.columns:
                        logging.info("Group column found in dataset: %s"%groups_col)
                        groups = self.df[groups_col]
                    else:
                        ds_groups = DataSourceAPIPandas(self.options)
                        logging.info("Group column loaded from full dataset: %s"%groups_col)
                        ds_groups.load(features = [groups_col])
                        groups = ds_groups.df[groups_col]


                features, target, groups = indexable(features, target, groups)
                cv = None

                trainSplitRatio = self.options.get('splitOptions', {}).get('trainRatio', None)
                randomSeed = self.options.get('splitOptions', {}).get('randomSeed', cv_num)
                shuffleData = self.options.get('splitOptions', {}).get('shuffleData', True)
                tsSplit = self.options.get('splitOptions', {}).get('timeseriesSplit', False)
                test_size_limit = self.options.get('splitOptions', {}).get('test_size_limit', None)
                if len(self.options.get('timeSeriesFeatures', [])) > 0 or tsSplit:
                    if groups is not None:
                        cv = GroupTimeSeriesSplit(n_splits=max(cv_num, 2), max_train_size=len(self.df)-test_size_limit)
                    else:
                        cv = TimeSeriesSplit(n_splits=max(cv_num, 2), test_size=test_size_limit)
                else:
                    if trainSplitRatio is not None:
                        if shuffleData:
                            if self.options.get('classification', True):
                                if groups is not None:
                                    cv = GroupShuffleSplit(n_splits=cv_num, train_size=float(trainSplitRatio),
                                                                random_state=randomSeed)
                                else:
                                    cv = StratifiedShuffleSplit(n_splits=cv_num, train_size=float(trainSplitRatio),
                                                                random_state=randomSeed)
                            else:
                                if groups is not None:
                                    cv = GroupShuffleSplit(n_splits=cv_num, train_size=float(trainSplitRatio),
                                                  random_state=randomSeed)
                                else:
                                    cv = ShuffleSplit(n_splits=cv_num, train_size=float(trainSplitRatio),
                                                  random_state=randomSeed)
                        else:
                            logging.info("Make 1 train/test split without Stratified, since shuffleData is false.")
                            #self.options['crossValidationFolds'] = 1

                            if groups is not None:
                                gs = GroupShuffleSplit(n_splits=2, train_size=float(trainSplitRatio), random_state=randomSeed)
                                train_ix, test_ix = next(gs.split(features, target, groups=groups))

                                X_train = _safe_indexing(features, train_ix)
                                y_train = _safe_indexing(target, train_ix)

                                X_test = _safe_indexing(features, test_ix)
                                y_test = _safe_indexing(target, test_ix)
                            else:
                                X_train, X_test, y_train, y_test = \
                                    train_test_split(features, target,
                                        train_size=float(trainSplitRatio),
                                        shuffle=False, random_state=randomSeed)

                            X_train, y_train = self.oversamplingFit(X_train, y_train)

                            res = fold_func(self.options, 0, X_train, y_train, None, X_test, y_test, None, **kfold_func_args)
                            data_shape = X_train.shape
                            result.append(res)
                    else:
                        if self.options.get('classification', True):
                            if groups is not None:
                                cv = StratifiedGroupKFold(n_splits=max(cv_num, 2), random_state=randomSeed, shuffle=shuffleData)
                            else:
                                cv = StratifiedKFold(n_splits=max(cv_num, 2), random_state=randomSeed, shuffle=shuffleData)
                        else:
                            if groups is not None:
                                cv = GroupKFold(n_splits=max(cv_num, 2))
                            else:
                                cv = KFold(n_splits=max(cv_num, 2), random_state=randomSeed, shuffle=shuffleData)

                if cv is not None:
                    cv_iter = list(cv.split(features, target, groups))

                    ds_roi = None
                    if self.options.get('roi_metric'):
                        ds_roi = DataSourceAPIPandas(self.options).load_roi_features()

                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore')

                        for fold_idx, (train_index, test_index) in enumerate(cv_iter):
                            if fold_idx >= cv_num:
                                break

                            X_train = _safe_indexing(features, train_index)
                            y_train = _safe_indexing(target, train_index)
                            X_train, y_train = self.oversamplingFit(X_train, y_train)

                            X_test = _safe_indexing(features, test_index)
                            y_test = _safe_indexing(target, test_index)

                            test_roi_data = None
                            if ds_roi is not None:
                                test_roi_data = _safe_indexing(ds_roi.df, test_index)

                            res = fold_func(self.options, fold_idx, X_train, y_train,
                                test_index, X_test, y_test, test_roi_data, **kfold_func_args)

                            if fold_idx == 0:
                                data_shape = X_train.shape

                            result.append(res)

            if data_shape is not None:
                self.options['dataset_ncols'] = data_shape[1]
                self.options['dataset_nrows'] = data_shape[0]

        return result

    def splitToFiles(self, save_to_csv=False):
        from sklearn.model_selection import train_test_split

        split_options = self.options.get('splitOptions', {})
        if self.options.get('classification') and self.options.get('targetFeature'):
            train, test = train_test_split(self.df, train_size=split_options.get('trainRatio', 0.8), random_state=split_options.get("randomSeed", 123),
                                           stratify=self.df[[self.options.get('targetFeature')]],
                                           shuffle=split_options.get('shuffleData', True))
        else:
            train, test = train_test_split(self.df, train_size=split_options.get('trainRatio', 0.8),
                                           random_state=split_options.get("randomSeed", 123),
                                           shuffle=split_options.get('shuffleData', True))

        path = self._get_datacache_path("")

        file_prefix = ""
        if self.dataset_name:
            file_prefix = self.dataset_name.split(".")[0] + "_"

        train.reset_index(drop=True, inplace=True)
        test.reset_index(drop=True, inplace=True)

        dsTrain = DataSourceAPIPandas({})
        dsTrain.df = train

        dsTest = DataSourceAPIPandas({})
        dsTest.df = test

        train_path = os.path.join(path, file_prefix+"training")
        test_path = os.path.join(path, file_prefix+"test")

        if save_to_csv:
            train_path += ".csv.gz"
            test_path += ".csv.gz"
            dsTrain.saveToCsvFile(train_path)
            dsTest.saveToCsvFile(test_path)
        else:
            train_path += ".pkl.gz"
            test_path += ".pkl.gz"
            dsTrain.saveToBinFile(train_path)
            dsTest.saveToBinFile(test_path)

        # train_path = os.path.join(path, file_prefix+"training.csv.gz")
        # test_path = os.path.join(path, file_prefix+"test.csv.gz")

        # FSClient().removeFile(train_path)
        # FSClient().removeFile(test_path)
        # train.to_csv(train_path, index=False, encoding='utf-8', compression="gzip")
        # test.to_csv(test_path, index=False, encoding='utf-8', compression="gzip")

        return train_path, test_path

    @staticmethod
    def get_datacache_path_s(options, suffix):
        if 'augerInfo' in options:
            path = options['augerInfo']["datacachePath"]
            FSClient().createFolder(path)

            return os.path.join(path, suffix)

        return ""

    def _get_datacache_path(self, suffix):
        return self.get_datacache_path_s(self.options, suffix)

    @staticmethod
    def oversampling_shuffling_augment_data(x, y, augmentations=2):
        xs, xn = [], []
        for i in range(augmentations):
            mask = y > 0
            x1 = x[mask].copy()
            ids = np.arange(x1.shape[0])
            for c in range(x1.shape[1]):
                np.random.shuffle(ids)
                x1[:, c] = x1[ids][:, c]
            xs.append(x1)

        for i in range(augmentations//2):
            mask = y == 0
            x1 = x[mask].copy()
            ids = np.arange(x1.shape[0])
            for c in range(x1.shape[1]):
                np.random.shuffle(ids)
                x1[:, c] = x1[ids][:, c]
            xn.append(x1)

        xs = np.vstack(xs)
        xn = np.vstack(xn)
        ys = np.ones(xs.shape[0])
        yn = np.zeros(xn.shape[0])
        x = np.vstack([x, xs, xn])
        y = np.concatenate([y, ys, yn])

        return x, y

    def oversamplingFit(self, X_train, y_train):
        from importlib import import_module
        from auger_ml.preprocessors.space import pspace_is_fold_group_allow_oversampling
        from auger_ml.Utils import get_app_node_cpu
        import inspect
        import multiprocessing as mp

        if self.options.get('oversampling') and self.options['oversampling'].get('name'):
            if not pspace_is_fold_group_allow_oversampling(self.options['fold_group']):
                logging.info("Oversampling is not applied to this group of algorithms: %s"%self.options['fold_group'])
            else:
                try:
                    logging.info("START oversampling: %s"%self.options['oversampling'])

                    if self.options['oversampling']['name'] == 'auger_shuffling_augment':
                        x, y_train = self.oversampling_shuffling_augment_data(X_train.values[:], y_train, **self.options['oversampling'].get('params', {}))
                    else:
                        if 'SMOTEENN' in self.options['oversampling']['name'] or \
                           'SMOTETomek' in self.options['oversampling']['name']:
                            over_sampler_class = getattr(import_module("imblearn.combine"),
                                self.options['oversampling']['name'])
                        else:
                            over_sampler_class = getattr(import_module("imblearn.over_sampling"),
                                self.options['oversampling']['name'])

                        params = copy.deepcopy(self.options['oversampling'].get('params', {}))
                        if 'ratio' in params:
                            params['sampling_strategy'] = params['ratio']
                            del params['ratio']
                        if 'kind' in params:
                            del params['kind']

                        argSpec = inspect.getfullargspec(over_sampler_class.__init__)
                        if 'n_jobs' in argSpec.args:
                            params['n_jobs'] = get_app_node_cpu()
                            mp.current_process().daemon = False

                        logging.info("oversampling n_jobs: %s"%params.get('n_jobs'))

                        over_sampler = over_sampler_class(**params)
                        x, y_train = over_sampler.fit_resample(X_train.values[:], y_train)

                    X_train = pd.DataFrame(data=x, columns=X_train.columns.tolist())
                    logging.info("END oversampling")
                    return X_train, y_train

                except Exception as e:
                    msg = "Oversampling method %s(%s) run with error: %s"%(
                        self.options['oversampling']['name'], self.options['oversampling'].get('params', {}), str(e))
                    logging.exception(msg)
                    raise Exception(msg)

        return X_train, y_train

    def update_options_by_dataset_statistics(self):
        transforms = []
        categoricals = []
        hashings = []
        timeseries = []
        selected_features = []
        target_feature = None
        binaryClassification = None
        minority_target_class = None
        datetimeFeatures = []
        text_features = []

        #logging.info(self.options.get('dataset_statistics'))
        for item in self.options.get('dataset_statistics', {}).get('stat_data', []):
            if item.get('isTarget'):
                target_feature = item['column_name']
                if (self.options.get('model_type', '') == 'classification' or self.options.get('classification')):
                    binaryClassification = item.get('unique_values', 0) == 2

                    #Find minority target class
                    if item.get('value_counts_ex'):
                        minority_target_class = item['value_counts_ex'][0]['value']
                        minority_target_count = item['value_counts_ex'][0]['count']
                        for vc in item['value_counts_ex']:
                            if vc['count'] < minority_target_count:
                                minority_target_class = vc['value']
                                minority_target_count = vc['count']

            if item.get('use') and not item.get('isTarget'):
                selected_features.append(item['column_name'])

            if item['datatype'] == 'text':
                text_features.append(item['column_name'])

            if item.get('use') or item.get('isTarget'):
                if item['orig_datatype'] == 'string':
                    if item['datatype'] == 'integer' or item['datatype'] == 'double':
                        transforms.append({"withNumericColumn":{"col_name":item['column_name']}})
                    if item['datatype'] == 'boolean':
                        transforms.append({"withBooleanColumn":{"col_name":item['column_name']}})

                if item['datatype'] == 'categorical':
                    categoricals.append(item['column_name'])
                if item['datatype'] == 'hashing':
                    categoricals.append(item['column_name'])
                    hashings.append(item['column_name'])
                if item['datatype'] == 'timeseries':
                    timeseries.append(item['column_name'])
                if item['datatype'] == 'datetime':
                    datetimeFeatures.append(item['column_name'])

        if categoricals:
            self.options['categoricalFeatures'] = categoricals
        if hashings:
            self.options['labelEncodingFeatures'] = hashings
        if text_features:
            self.options['textFeatures'] = text_features
        if timeseries:
            self.options['timeSeriesFeatures'] = timeseries
        if selected_features:
            self.options['featureColumns'] = selected_features
        if target_feature:
            self.options['targetFeature'] = target_feature
        if datetimeFeatures:
            self.options['datetimeFeatures'] = datetimeFeatures
        if binaryClassification is not None:
            self.options['binaryClassification'] = binaryClassification
        if minority_target_class is not None and self.options.get('minority_target_class') is None and \
            self.options.get('use_minority_target_class'):
            self.options['minority_target_class'] = minority_target_class
            # if isinstance(self.options['minority_target_class'], bool):
            #     self.options['minority_target_class_pos'] = 1 if self.options['minority_target_class'] else 0

        if not 'datasource_transforms' in self.options:
            self.options['datasource_transforms'] = []

        self.options['datasource_transforms'] = [transforms]

        # if  'dataset_statistics' in self.options:
        #     del self.options['dataset_statistics']

        #logging.info(self.options)

    def getBooleanCategoricals(self, feature):
        res = {}
        values = []

        for item in self.options.get('dataset_statistics', {}).get('stat_data', []):
            if item['column_name'] == feature:
                if item['datatype'] == 'boolean':
                    values = [False, True]
                    # for vc in item.get('value_counts_ex', []):
                    #     key = vc['value']
                    #     if isinstance(key, str):
                    #         if key.lower() in self.BOOLEAN_WORDS_TRUE:
                    #             values.append(key)
                    #         else:
                    #             values.insert(0, key)
                    #     else:
                    #         values.append(key)
                break

        if values:
            #values.sort()
            res[feature] = {'categories': values}

        return res

    def transform(self, transforms, cache_to_file=True):
        ordered_trans = [[], [], [], []]
        for group in transforms:
            for item in group:
                if list(item.keys())[0] == 'withJsonColumn':
                    ordered_trans[0].append(item)
                elif list(item.keys())[0] == 'fillna':
                    ordered_trans[1].append(item)
                elif list(item.keys())[0] == 'filter_ex':
                    ordered_trans[2].append(item)
                else:
                    ordered_trans[3].append(item)

        #TODO: implement comparing lists
        # if len(self.transforms_log) == len(ordered_trans):
        #     return
        # if  cmp(self.transforms_log, ordered_trans) == 0:
        #     #logging.info("Same transformations.Skip transform")
        #     return

        if self.transforms_log != [[], [], [], []]:
            logging.info("New transformations.Re-load data")
            self.load(use_cache=False)

        for group in ordered_trans:
            for item in group:
                name = list(item.keys())[0]
                args = list(item.values())[0]
                getattr(self, name)(**args)
                if name == "convertToCategorical" and args.get('is_target', False) and self.categoricals.get(args.get('col_names')):
                    args['categories'] = self.categoricals[args.get('col_names')]['categories']

        self.transforms_log = ordered_trans

        if cache_to_file:
            path = self._get_datacache_path("transformations.json")
            FSClient().removeFile(path)
            FSClient().writeJSONFile(path, self.transforms_log, atomic=True)

            self.saveToCacheFile("data_transformed")

    @staticmethod
    def revertTargetCategories(results, transforms):
        target_categories = []
        for group in transforms:
            for item in group:
                name = list(item.keys())[0]
                args = list(item.values())[0]
                if name == "convertToCategorical" and args.get('is_target', False):
                    target_categories = args['categories']
                    break

        if len(target_categories) == 0:
            return results

        return map(lambda x: target_categories[int(x)], results)

    # @staticmethod
    # def revertCategories(results, categories):
    #     return list(map(lambda x: categories[int(x)], results))

    @staticmethod
    def _convert_arff_coo(features, columns, arff_data_data):
        if features is None:
            data = [([], []) for _ in columns]
        else:
            fset = remove_dups_from_list(features)
            data = [([], []) if c in fset else None for c in columns]

        for v, i, j in zip(*arff_data_data):
            d = data[j]
            if d is not None:
                indices, values = d
                if indices:
                    assert indices[-1] < i
                indices.append(i)
                values.append(v)

        max_i = -1
        for d in data:
            if d is not None and len(d[0]) > 0:
                max_i = max(max_i, d[0][-1])
        height = max_i + 1

        series = []
        for d in data:
            if d is None:
                s = None
            else:
                keys, values = d
                sa = pd.SparseArray(
                    values,
                    sparse_index=pd._libs.sparse.IntIndex(height, keys),
                    fill_value=0
                )
                s = pd.Series(sa)
            series.append(s)

        return series

    @staticmethod
    def _convert_arff_dense(features, columns, arff_data_data):
        # for idx, item in enumerate(arff_data_data):
        #     arff_data_data[idx] = [pd.np.nan if x is None else x for x in item]

        if features is None or set(features) == set(columns):
            return zip(*arff_data_data)

        fset = remove_dups_from_list(features)
        return [
            [row[i] for row in arff_data_data] if c in fset else None
            for i, c in enumerate(columns)
        ]

    def __format_number_for_serialization(self, v):
        if v != v or math.isinf(v):
            return None
        else:
            return round(v, 6)



def auger_mutual_info_score(labels_true, labels_pred, contingency=None):
    from scipy import sparse as sp
    """
    Refer to sklearn function mutual_info_score
    This is corrected implementation to account for overflow in 'outer = pi.take(nzx) * pj.take(nzy)' calculation
    :param labels_true:
    :param labels_pred:
    :param contingency:
    :return:
    """
    if contingency is None:
        labels_true, labels_pred = sklearn.metrics.cluster._supervised.check_clusterings(labels_true, labels_pred)
        contingency = sklearn.metrics.cluster.contingency_matrix(labels_true,
                                                                            labels_pred,
                                                                            sparse=True).astype(np.float64)
    else:
        contingency = sklearn.utils.check_array(contingency,
                                                accept_sparse=['csr', 'csc', 'coo'],
                                                dtype=[int, np.int32, np.int64])

    if isinstance(contingency, np.ndarray):
        # For an array
        nzx, nzy = np.nonzero(contingency)
        nz_val = contingency[nzx, nzy]
    elif sp.issparse(contingency):
        # For a sparse matrix
        nzx, nzy, nz_val = sp.find(contingency)
    else:
        raise ValueError("Unsupported type for 'contingency': %s" %
                         type(contingency))

    contingency_sum = contingency.sum()
    pi = np.ravel(contingency.sum(axis=1))
    pj = np.ravel(contingency.sum(axis=0))
    log_contingency_nm = np.log(nz_val)
    contingency_nm = nz_val / contingency_sum
    # Don't need to calculate the full outer product, just for non-zeroes
    outer = pi.take(nzx) * pj.take(nzy)
    log_outer = -np.log(outer) + np.log(pi.sum()) + np.log(pj.sum())
    mi = (contingency_nm * (log_contingency_nm - np.log(contingency_sum)) +
          contingency_nm * log_outer)
    return mi.sum()
