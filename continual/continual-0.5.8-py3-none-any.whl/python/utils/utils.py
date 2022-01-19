import base64
import sys
import logging
from typing import List, Tuple
from google.protobuf.timestamp_pb2 import Timestamp

import pandas as pd

from continual.rpc.management.v1 import types

base64_encode_prefix = "continual_"


def get_parent(name: str) -> str:
    parts = name.split("/")
    if len(parts) < 2:
        return ""
    return "/".join(parts[:-2])


def parse_project_name(project_name):
    # projects/<project>
    items = project_name.split("/")
    if len(items) != 2 or items[0] != "projects" or not items[1]:
        raise Exception("Error parsing project name [{}]".format(project_name))
    return items[1]


def parse_model_version_name(model_version_name):
    # projects/<project>/models/<model>/versions/<model_version>
    items = model_version_name.split("/")
    if (
        len(items) != 6
        or items[0] != "projects"
        or items[2] != "models"
        or items[4] != "versions"
        or not items[1]
        or not items[3]
        or not items[5]
    ):
        raise Exception(
            "Error parsing model version name [{}]".format(model_version_name)
        )

    return (items[1], items[3], items[5])


def parse_experiment_name(experiment_name):
    # projects/<project>/models/<model>/versions/<model_version>/experiments/<experiment>
    items = experiment_name.split("/")
    if (
        len(items) != 8
        or items[0] != "projects"
        or items[2] != "models"
        or items[4] != "versions"
        or items[6] != "experiments"
        or not items[1]
        or not items[3]
        or not items[5]
        or not items[7]
    ):
        raise Exception("Error parsing experiment name [{}]".format(experiment_name))

    return (items[1], items[3], items[5], items[7])


def validate_experiment_name(experiment_name):
    # projects/<project>/versions/<model_version>/experiments/<experiment>
    items = experiment_name.split("/")
    if (
        len(items) != 8
        or items[0] != "projects"
        or items[2] != "models"
        or items[4] != "versions"
        or items[6] != "experiments"
        or not items[1]
        or not items[3]
        or not items[5]
        or not items[7]
    ):
        raise Exception("Error parsing experiment name [{}]".format(experiment_name))
    return


def is_integer_value(val):
    try:
        int(val)
    except ValueError:
        return False
    return True


def get_experiment_id_from_name(experiment_name):
    validate_experiment_name(experiment_name)

    # The last field is the experiment ID
    return experiment_name.split("/")[-1]


def validate_project_name(project_name):
    # projects/<project_id>
    items = project_name.split("/")
    if len(items) != 2 or items[0] != "projects" or not items[1]:
        raise Exception("Error parsing project name [{}]".format(project_name))
    return


def validate_model_version_name(model_version_name):
    parse_model_version_name(model_version_name)
    return


def get_project_name(project_id):
    # projects/<project_id>
    if not project_id:
        raise Exception("project ID should not be an empty string")
    return "projects/{}".format(project_id)


def parse_model_name(model_name: str) -> Tuple[str, str]:
    # projects/:project_id/models/:model_id
    items = model_name.split("/")
    if (
        len(items) != 4
        or items[0] != "projects"
        or items[2] != "models"
        or not items[1]
        or not items[3]
    ):
        raise Exception("Error parsing model name [{}]".format(model_name))
    return items[1], items[3]


def parse_batch_prediction_job_name(batch_prediction_job_name):
    # projects/<project>/models/<model>/batchPredictions/<batch_prediction_job_id>
    items = batch_prediction_job_name.split("/")
    if (
        len(items) != 6
        or items[0] != "projects"
        or items[2] != "models"
        or items[4] != "batchPredictions"
        or not items[1]
        or not items[3]
        or not items[5]
    ):
        raise Exception(
            "Error parsing batch prediction job name [{}]".format(
                batch_prediction_job_name
            )
        )

    return (items[1], items[3], items[5])


def validate_model_name(model_name):
    parse_model_name(model_name)
    return


def get_model_version_name(model_name, model_version_id):
    validate_model_name(model_name)
    return "{}/versions/{}".format(model_name, model_version_id)


def get_featureset_name(project_name, feature_set_id):
    return "{}/featureSets/{}".format(project_name, feature_set_id)


def get_experiment_name(model_version_name, experiment_id):
    return "{}/experiments/{}".format(model_version_name, experiment_id)


def get_featureset_from_modelversion(model_version_name):
    project_id, model_id, _ = parse_model_version_name(model_version_name)
    entity = model_id.split(":")[0]
    fs_name = get_featureset_name(get_project_name(project_id), entity)
    return fs_name


def _get_float_replacement(val, name, mapper):
    if mapper.get(name, None) is not None:
        return mapper[name]
    return val


float_dict = {"inf": sys.float_info.max, "-inf": sys.float_info.min}


def renormalize_floats(obj, mapper):
    if isinstance(obj, list):
        out = []
        for val in obj:
            out.append(renormalize_floats(val, mapper))
        return out
    if isinstance(obj, dict):
        for key, val in obj.items():
            obj[key] = renormalize_floats(val, mapper)
        return obj
    if isinstance(obj, float):
        if obj == float("inf"):
            obj = _get_float_replacement(obj, "inf", mapper)
        elif obj == float("-inf"):
            obj = _get_float_replacement(obj, "-inf", mapper)
        elif obj == float("nan"):
            obj = _get_float_replacement(obj, "nan", mapper)
        return obj
    return obj


def parse_feature_set_name(name):
    """
    Splits name string such as 'projects/<project>/featureSets/<featureset>@<version>' to a dict like:
     {
       'projects' : <project>,
       'featureSets' : <featureset>s
     }
    """
    retmap = {}
    splits = name.split("/")
    i = 0
    while i < len(splits):
        retmap[splits[i]] = None
        if i + 1 < len(splits):
            retmap[splits[i]] = splits[i + 1]
        i = i + 2

    return retmap


def get_current_time():
    ts = Timestamp()
    ts.GetCurrentTime()
    return ts


def get_model_name(project_name, model_id, validate_fields=True):
    # projects/project_id/models/model_id
    if validate_fields:
        validate_project_name(project_name)
    return "{}/models/{}".format(project_name, model_id)


def encode_featurename_base64(name):
    continual_name = bytes(base64_encode_prefix + name, encoding="utf-8")
    out_bytes = base64.urlsafe_b64encode(continual_name)
    out = str(out_bytes, encoding="utf-8")
    return out.rstrip("=")


def encode_featurename_list(names_lst):
    out = []
    for name in names_lst:
        out.append(encode_featurename_base64(name))
    return out


def decode_featurename_base64(base64val):
    if not isinstance(base64val, str):
        return base64val
    base64str = base64val
    n = len(base64str)
    pad_str = ((4 - n % 4) % 4) * "="
    padded_base64str = base64str + pad_str
    try:
        out_bytes = base64.urlsafe_b64decode(bytes(padded_base64str, encoding="utf-8"))
        out = str(out_bytes, encoding="utf-8")
        if not out.startswith(base64_encode_prefix):
            return base64str
        return out[len(base64_encode_prefix) :]
    except Exception:
        return base64str
    return base64str


def decode_base64_obj(base64obj):
    if isinstance(base64obj, list):
        out_list = []
        for item in base64obj:
            out_list.append(decode_base64_obj(item))
        return out_list
    if isinstance(base64obj, dict):
        out_dict = {}
        for key, val in base64obj.items():
            key = decode_featurename_base64(key)
            out_dict[key] = decode_base64_obj(val)
        return out_dict
    if isinstance(base64obj, str):
        return decode_featurename_base64(base64obj)
    return base64obj


# This is an in-place encode of column names in df
def encode_df_column_names(df):
    columns = [encode_featurename_base64(column_name) for column_name in df.columns]
    df.columns = columns
    return


# This is an in-place decode of column names in df
def decode_df_column_names(df):
    columns = [decode_featurename_base64(column_name) for column_name in df.columns]
    df.columns = columns
    return


def split_name(name):
    splits = name.split("/")
    i = 0
    name_map = {}
    while i < len(splits):
        name_map[splits[i]] = splits[i + 1]
        i = i + 2
    return splits[len(splits) - 1], name_map


def dot_get(obj, path, raise_error=True):
    ret = None
    paths, current = path.split("."), obj
    for p in paths:
        if p not in current:
            if raise_error:
                raise KeyError("Could not find key in object")

            break
        elif p in current:
            current = current[p]
            ret = current

    return ret


def read_csv(file_path, chunksize=None):
    encoding = "utf-8"
    try:
        with open(file_path, "r") as f:
            logging.info("File ({}) has encoding: {}".format(file_path, f.encoding))
            encoding = f.encoding
    except Exception as e:
        logging.info(
            "Failed to open file locally: file_path={}, error: {}".format(
                file_path, str(e)
            )
        )

    try:
        return pd.read_csv(
            file_path, encoding=encoding, low_memory=False, chunksize=chunksize
        )
    except UnicodeDecodeError:
        logging.info(
            "Ran into unicode decode error with encoding ({}) — retrying with latin-1".format(
                encoding
            )
        )
        return pd.read_csv(
            file_path, encoding="latin-1", low_memory=False, chunksize=chunksize
        )


def generate_field_mask_paths(obj: dict) -> List[str]:
    paths = []

    q = list(obj.keys())
    while q:
        path = q.pop()

        value = dot_get(obj, path, raise_error=False)
        if value is not None and type(value) is dict:
            if len(value.keys()) == 0:
                paths.append(path)
            else:
                for k in value.keys():
                    q.append(f"{path}.{k}")
        else:
            paths.append(path)

    return paths


def generate_datastore_field_paths(data_store: types.DataStore) -> List[str]:
    paths = []
    if type(data_store) is not dict:
        data_store = data_store.to_dict()
    for path in generate_field_mask_paths(data_store):
        qualified_path = f"data_store.config.{path}"
        paths.append(qualified_path)
        if qualified_path.endswith(".username"):
            paths.append(qualified_path.replace(".username", ".user"))
    return paths
