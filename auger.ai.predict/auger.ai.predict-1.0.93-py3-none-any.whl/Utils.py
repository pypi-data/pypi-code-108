import dateutil
import inspect
from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
import math
import numbers
import os
import sys
import traceback
import uuid
import json

from .FSClient import *

# For calculate_scores
from auger_ml.scores.regression import *
from auger_ml.scores.classification import *

# def is_experimental_build():
#     return True

def url_encode(path):
    try:
        from urllib.parse import urlparse, parse_qs, quote
    except ImportError:
        from urlparse import urlparse, parse_qs, quote

    return quote(path, safe='#&%:/?*=\'')

def parse_url(remote_path):
    try:
        from urllib.parse import urlparse, parse_qs, quote
    except ImportError:
        from urlparse import urlparse, parse_qs, quote

    uri = urlparse(remote_path)
    params = parse_qs(uri.query)

    return uri.path, params

def get_remote_file_info(remote_path):
    from urllib.request import urlopen
    import urllib
    import codecs

    try:
        from urllib.parse import urlparse, parse_qs
    except ImportError:
        from urlparse import urlparse, parse_qs

    file_info  = {}
    try:
        remote_path1 = url_encode(remote_path)
        # logging.info("Get info for file from url: %s" % remote_path1)

        req = urlopen(remote_path1)
        #print(req.info())

        # Make local path
        contentDisp = req.getheader('Content-Disposition')
        contentType = req.getheader('Content-Type')
        fileext = ''
        if contentType:
            if contentType == 'application/x-gzip':
                fileext = '.gz'
            elif contentType == 'text/csv':
                fileext = '.csv'

        filename = ''
        if contentDisp:
            items = contentDisp.split(';')
            for item in items:
                item = item.strip()
                if item.startswith("filename=\""):
                    filename = item[10:-1]
                    break
                elif item.startswith("filename="):
                    filename = item[9:]
                    break

        if not filename:
            uri = urlparse(remote_path)
            params = parse_qs(uri.query)
            if len(params.get('id', []))>0:
                filename = params['id'][0]+fileext
            else:
                if len(uri.path)>0 and len(os.path.basename(uri.path))>0:
                    filename = os.path.basename(uri.path)
                else:
                    filename = get_uid()+fileext

        remote_file_size = 0
        try:
            remote_file_size = int(req.getheader('Content-Length'))
        except:
            pass

        remote_file_etag = ''
        try:
            remote_file_etag = req.getheader('ETag').strip("\"\'")
        except:
            pass

        req.close()

        file_info = {
            'file_name': "",
            'file_ext': "",
            'file_size': remote_file_size,
            'file_etag': remote_file_etag
        }

        dot_index = filename.find('.')
        if dot_index>=0:
            file_info['file_name'] = filename[:dot_index]
            file_info['file_ext'] = filename[dot_index:]
        else:
            file_info['file_name'] = filename

    except Exception as e:
        logging.info("Remote url '%s' cannot be open: %s"%(remote_path1, e))

    return file_info

def download_file(remote_path, local_dir, file_name=None, force_download=False, file_suffix=""):
    local_file_path = ""
    download_file = True
    remote_file_info = {}

    logging.info("download_file: %s, %s, %s, %s"%(remote_path, local_dir, file_name, force_download))
    if file_name:
        all_local_files = FSClient().listFolder(os.path.join(local_dir, file_name+".*"), wild=True, removeFolderName=True)
        #print(all_local_files)
        if all_local_files:
            local_file_path = os.path.join( local_dir, all_local_files[0])

    if not local_file_path:
        remote_file_info = get_remote_file_info(remote_path)
        if not remote_file_info:
            raise Exception("Remote path does not exist or unaccessible: %s"%(remote_path))

        if file_name:
            local_file_path = os.path.join(local_dir,
                file_name+remote_file_info.get('file_ext'))
        else:
            local_file_path = os.path.join(local_dir,
                remote_file_info.get('file_name') + file_suffix + remote_file_info.get('file_ext'))

    if FSClient().isFileExists(local_file_path):
        etag_changed = False
        file_size_changed = False

        #TODO: check etag to download new file, data_path_reloaded flag should be passed to auger_ml
        # if not remote_file_info:
        #     remote_file_info = get_remote_file_info(remote_path)

        # if remote_file_info.get('file_etag'):

        if force_download:
            logging.info("Force download file again.")

        if force_download or etag_changed or file_size_changed:
            FSClient().removeFile(local_file_path)
        else:
            download_file = False

    if download_file:
        logging.info("Download to local file path: %s"%local_file_path)
        FSClient().downloadFile(remote_path, local_file_path)

    return local_file_path

def open_file_reader(remote_path, download_as_utf8=True):
    from urllib.request import urlopen
    import codecs

    remote_path1 = url_encode(remote_path)
    logging.info("Open file reader from url: %s" % remote_path1)

    req = urlopen(remote_path1)
    #print(req.info())

    if download_as_utf8:
        return codecs.getreader('utf-8')(req, errors='replace')
    else:
        return req

def read_file_local_or_remote(local_path, remote_path):
    file_reader = None
    full_path = local_path
    if FSClient().isFileExists(local_path):
        file_reader = FSClient().open(local_path, "rb")
    else:
        if not remote_path:
            raise Exception(
                "File '%s' does not exist and there is no remote path." % local_path)

        #full_path = os.path.join(remote_path, os.path.basename(local_path))
        full_path = '/'.join([remote_path, os.path.basename(local_path)])
        file_reader = open_file_reader(full_path, download_as_utf8=True)

    return file_reader, full_path


def process_arff_line(line, date_attrs):
    if "@attribute" in line.lower():
        parts = line.split(maxsplit=3)
        if len(parts) > 2 and parts[2].lower() == 'date':
            line = parts[0]+ ' ' + parts[1] + ' string\n'
            date_field = parts[1].strip("\"\'")
            date_format = parts[3].strip("\"\'\n")

            date_attrs[date_field] = date_format

    return line

def load_arff_header(arff_path, arff_folder_url=None):
    import arff

    file_reader, arff_path = read_file_local_or_remote(
        arff_path, arff_folder_url)
    strHeader = ""
    date_attrs = {}
    for line in file_reader:
        line = process_arff_line(line, date_attrs)
        strHeader += line
        if "@data" in line.lower():
            break

    file_reader.close()

    dataArff = arff.loads(strHeader)
    features = []
    feature_types = []
    categoricals = {}

    for attr in dataArff['attributes']:
        features.append(str(attr[0]))
        feature_types.append(attr[1])
        if type(attr[1]) == list:
            categoricals[str(attr[0])] = attr[1]
        elif attr[1].lower() == 'string':
            if not str(attr[0]) in date_attrs:
                categoricals[str(attr[0])] = []

    return arff_path, features, feature_types, categoricals, date_attrs

# def freeze_value(v):
#     if isinstance(v, dict):
#         return frozenset((k, freeze_value(v_)) for k, v_ in v.items())
#     if isinstance(v, (tuple, list)):
#         return tuple(freeze_value(v_) for v_ in v)
#     return v

# def get_pipeline_key(algorithm_name, algorithm_parameters):
#     #logging.info("get_pipeline_key: %s, %s"%(algorithm_name, algorithm_parameters))
#     return freeze_value((algorithm_name, algorithm_parameters))


# def hex_hash(key):
#     return '%016X' % (hash(key) % (2 * (sys.maxsize + 1)))


def get_uid():
    return uuid.uuid4().hex[:15].upper()


def get_uid4():
    return str(uuid.uuid4())


def remove_fields_from_dict(obj, fields_to_delete):
    for field in fields_to_delete:
        if field in obj:
            del obj[field]


def dict_equal_fields(dict1, dict2, names):
    for name in names:
        if dict1.get(name) != dict2.get(name):
            return False

    return True


# by default value from other dict overwrites value in d
def merge_dicts(d, other, concat_func=lambda v, ov: ov):
    from collections import Mapping

    for k, v in other.items():
        d_v = d.get(k)
        if isinstance(v, Mapping) and isinstance(d_v, Mapping):
            merge_dicts(d_v, v, concat_func)
        else:
            if k in d:
                d[k] = concat_func(d[k], v)
            else:
                d[k] = v

    return d


def convertStringsToUTF8(params):
    # if params is None:
    #     return params

    # if type(params) is dict:
    #     for key, value in params.items():
    #         new_key = key.encode('utf-8')
    #         del params[key]
    #         params[new_key] = convertStringsToUTF8(value)
    # elif type(params) is list:
    #     for idx, value in enumerate(params):
    #         params[idx] = convertStringsToUTF8(value)
    # elif type(params) is str:
    #     params = params.encode('utf-8')

    return params

def convert_to_date(date):
    if type(date) is str:
        return dateutil.parser.parse(date).date()
    elif type(date) is time.time:
        return date.date()
    else:
        return date


def dict_keys_to_string(params):
    if params is None or type(params) is not dict:
        return params

    result = {}
    for key, value in params.items():
        result[str(key)] = value

    return result

def remove_dups_from_list(ar):
    from collections import OrderedDict
    return list(OrderedDict.fromkeys(ar))


def create_object_by_class(full_name, *args):
    import importlib

    module_name, class_name = full_name.rsplit('.', 1)
    cls = getattr(importlib.import_module(module_name), class_name)
    return cls(*args)


def parse_cluster_cpus(cpu_string, do_ceil=True):
    res = 1

    if not cpu_string:
        return res

    try:
        #logging.info("parse_cluster_cpus: %s"%cpu_string)

        if cpu_string.endswith('n'):
            res = float(cpu_string[:-1])
            res = res / 1e9
        elif cpu_string.endswith('u'):
            res = float(cpu_string[:-1])
            res = res / 1e6
        elif cpu_string.endswith('m'):
            res = float(cpu_string[:-1])
            res = res / 1e3
        else:
            res = float(cpu_string)

        if do_ceil:
            res = math.ceil(res)
        else:
            res = math.floor(res)

    except:
        logging.exception("parse_cluster_cpus failed: %s" % cpu_string)

    return max(int(res), 1)

def parse_cluster_ram_mb(ram_string):
    res = 0

    if not ram_string:
        return res
    else:
        ram_string = ram_string.lower()

    try:
        if ram_string.endswith('ki'):
            res = float(ram_string[:-2])
            res = res / 1024
        elif ram_string.endswith('mi'):
            res = float(ram_string[:-2])
        elif ram_string.endswith('gi'):
            res = float(ram_string[:-2])
            res = res * 1024
        else:
            res = float(ram_string) / 1e6
    except:
        logging.exception("parse_cluster_ram failed: %s" % ram_string)

    return int(res)

def is_nan(x):
    import numpy as np

    return (x is np.nan or x != x)

def convert_simple_numpy_type(obj):
    import numpy as np

    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
        np.int16, np.int32, np.int64, np.uint8,
        np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32,
        np.float64)):
        return float(obj)
    elif isinstance(obj,np.bool_):
        return bool(obj)
    # elif isinstance(obj,(np.ndarray,)): #### This is the fix
    #     return obj.tolist()

    return None

class NumpyJSONEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        res = convert_simple_numpy_type(obj)
        if res is not None:
            return res

        return json.JSONEncoder.default(self, obj)

def convert_nan_inf(params):
    if params is None:
        return params

    if type(params) is dict:
        for key, value in params.items():
            params[key] = convert_nan_inf(value)
    elif type(params) is list:
        for idx, value in enumerate(params):
            params[idx] = convert_nan_inf(value)
    else:
        if isinstance(params, numbers.Number) and math.isinf(params):
            params = None
        if is_nan(params):
            params = None

    return params

def convert_numpy_types(params):
    if params is None:
        return params

    if type(params) is dict:
        for key, value in params.items():
            params[key] = convert_numpy_types(value)
    elif type(params) is list:
        for idx, value in enumerate(params):
            params[idx] = convert_numpy_types(value)
    else:
        if isinstance(params, numbers.Number) and math.isinf(params):
            params = None
        elif is_nan(params):
            params = None
        else:
            res = convert_simple_numpy_type(params)
            if res is not None:
                params = res

    return params

def json_dumps_np(data, allow_nan=False):
    if not allow_nan:
        data = convert_nan_inf(data)

    return json.dumps(data, cls=NumpyJSONEncoder, allow_nan=allow_nan)

def calculate_scores(options, y_test, X_test=None, estimator=None, y_pred=None, raise_main_score=True):
    from .model_helper import ModelHelper
    return ModelHelper.calculate_scores(options, y_test, X_test, estimator, y_pred, raise_main_score)

def convert_time_from_str(time_arg):
    from datetime import datetime

    time_res = time_arg
    if time_arg and type(time_arg) == str:
        dt_format = '%Y-%m-%d %H:%M:%S.%f'
        time_res = (datetime.strptime(time_arg, dt_format)-datetime.utcfromtimestamp(0)).total_seconds()

    if time_res is None:
        time_res = 0

    return time_res

def get_app_node_cpu():
    try:
        if os.environ.get('AUGER_WORKER_CPU_LIMIT'):
            cpu_per_node = parse_cluster_cpus(os.environ.get('AUGER_WORKER_CPU_LIMIT'))
        else:
            cpu_per_node = 8
    except:
        logging.exception("get_app_node_cpu failed.")

    return max(cpu_per_node, 1)

def get_app_node_ram_mb():
    try:
        if os.environ.get('AUGER_WORKER_RAM_LIMIT'):
            ram_per_node = parse_cluster_ram_mb(os.environ.get('AUGER_WORKER_RAM_LIMIT'))
        else:
            ram_per_node = 8
    except:
        logging.exception("get_app_node_ram failed.")

    return max(ram_per_node, 1024)

def sort_arrays(ar1, ar2, top_n=None, desc=True):
    p = ar1.argsort()
    if desc:
        p = p[::-1]
    if top_n:
        p = p[:top_n]

    return ar1[p], ar2[p]

# def load_arff_df_ex(path, csv_path=None):
#     import arff
#     import csv
#     fs_client = FSClient()
#     if csv_path is None:
#         csv_path = path + '.csv'
#     else:
#         fs_client.createFolder(csv_path)
#         csv_path = os.path.join(csv_path, os.path.basename(path) + '.csv')

#     if fs_client.isFileExists(csv_path):
#         return csv_path

#     strData = fs_client.readTextFile(path)
#     dataArff = arff.loads(strData, return_type=arff.COO)
#     strData = None
#     features = []
#     categorical = {}
#     maxCategories = 0

#     for attr in dataArff['attributes']:
#         features.append(attr[0])
#         if type(attr[1]) == list:
#             categorical[attr[0]] = attr[1]
#             if len(attr[1]) > maxCategories:
#                 maxCategories = max(len(attr[1]), maxCategories)

#     with fs_client.open(csv_path, mode="w") as csv_file:
#         csv_writer = csv.writer(csv_file, delimiter=',', escapechar="\\", quoting=csv.QUOTE_NONE)
#         csv_writer.writerow(features)

#         for item in dataArff['data']:
#             csv_writer.writerow(item)

#     return csv_path #, maxCategories, categorical

# def log_traceback(ex, ex_traceback=None):
#     if ex_traceback is None:
#         ex_traceback = ex.__traceback__
#     tb_lines = [line.rstrip('\n') for line in
#                 traceback.format_exception(ex.__class__, ex, ex_traceback)]
#     for l in tb_lines:
#         print(l)
