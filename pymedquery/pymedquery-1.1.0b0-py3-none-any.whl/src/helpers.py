from pymedquery.config.logger_object import Logger

from typing import Iterable, Any
import gzip
import numpy as np
from functools import wraps
from time import time
import json
import csv
import pickle as pkl
import joblib
from psycopg2.extensions import AsIs
from collections import defaultdict

log = Logger(__name__)


def timer(orig_func):
    """This is custom timer decorator.
    Parameters
    ----------
    orig_func : object
        The `orig_func` is the python function which is decorated.
    Returns
    -------
    type
        elapsed runtime for the function.
    """

    @wraps(orig_func)
    def wrapper(*args, **kwargs):
        t1 = time()
        result = orig_func(*args, **kwargs)
        t2 = time() - t1
        print("Runtime for {}: {} sec".format(orig_func.__name__, t2))
        return result

    return wrapper


def write_type(fname):
    ext = fname.split(".")[-1]
    return "w" + ("b" if ext in ["pkl", "gz"] else "")


def assert_records_len(records: list, batch: bool = True):
    if batch:
        assert len(records) > 1, log.error(
            "records have to be a list with multiple tuples representing the rows to insert",
            exc_info=True,
        )
    else:
        assert len(records == 1), log.error(
            "records have to contain one tuple representing the row to insert",
            exc_info=True,
        )


def adapt_numpy_nan(numpy_nan):
    return "'NaN'"


def adapt_numpy_inf(numpy_inf):
    return "'Infinity'"


def adapt_numpy_ndarray(numpy_ndarray: np.ndarray):
    return AsIs(numpy_ndarray.tolist())


# def addapt_numpy_array(numpy_array: np.ndarray, multi_dim: bool = True):
#     if multi_dim:
#         return AsIs(map(tuple, numpy_array))
#     else:
#         return AsIs(tuple(numpy_array))


def addapt_dict(dict: dict):
    return AsIs(tuple(dict))


def batch_maker(iterable: Iterable[Any], batch_size: int = 10):
    iterable_length = len(iterable)
    for idx in range(0, iterable_length, batch_size):
        yield iterable[idx: min(idx + batch_size, iterable_length)]


def read_data_file(fname: str, jlib=False):
    """
    Description
    ===========
    Function that reads in either a dataframe, dictionary or csv
    Setup
    ===========
    :param fname: the filepath for where object is stored
    :return data: the dataframe of interest
    """

    if not fname:
        raise ValueError(
            "please specifiy the filepath for where the object is to be saved"
        )

    with open(fname, "rb") as filepath:
        if jlib:
            log.info(f"Reading file from {fname} with joblib")
            data = joblib.load(filepath)
        else:
            if ".gz" in fname:
                log.failure("please set jlib=True when reading gzip files")
            if ".pkl" in fname or ".pickle" in fname:
                log.info(f"Reading a pickle file from {fname} with joblib")
                data = pkl.load(filepath)
            if ".json" in fname:
                log.info(f"Reading a json file from {fname} with joblib")
                data = json.load(filepath)
        log.success("Loading done, happy coding!")
    return data


def save_data_file(obj, fname: str, jlib: bool = False):
    """
    Function that saves either a pickle, json, gzip or csv
    Parameters
    ----------
    obj : object
        the object that is to be saved `obj`.
    fname : str
        `fname` is the filepath for where object is to be stored.
    jlib : bool
        `jlib` is a boolean to indicate whether or not to use the joblib library(the default is False).
    Returns
    -------
    None
    """
    EXT_WRITETYPE_DICT = {
        "pkl": "wb",
        "pickle": "w",
        "json": "w",
        "csv": "w",
        "gz": "wb",
    }
    EXTENSIONS = EXT_WRITETYPE_DICT.keys()
    if not fname:
        raise ValueError(
            "please specifiy the filepath for where the object is to be saved"
        )

    if not any((fname.endswith(ext) for ext in EXTENSIONS)):
        raise ValueError(
            f"please pass one of the following file EXTENSIONS: {EXTENSIONS}"
        )

    # TODO: refactor with a dict and a loop
    with open(fname, write_type(fname)) as filepath:
        if jlib:
            log.info(f"Saving with joblib to {fname}")
            joblib.dump(obj, filepath)
        else:
            if fname.endswith(".pkl") or fname.endswith(".pickle"):
                log.info(f"Saving a pickle file to {fname}")
                pkl.dump(obj, filepath, protocol=pkl.HIGHEST_PROTOCOL)
            if ".gz" in fname:
                log.info(f"Saving with gzip compression level 9 to {fname}")
                joblib.dump(obj, filepath, compress="gzip")
            if fname.endswith(".json"):
                log.info(f"Saving a json file to {fname}")
                json.dump(obj, filepath)
            if fname.endswith(".csv"):
                log.info(f"Saving a csv file to {fname}")
                writer = csv.writer(filepath, quoting=csv.QUOTE_ALL)
                writer.writerows(obj)
    log.success("Saving done, happy coding!")


def nested_dict():
    """Reacursive dict function for making nested dicts."""
    return defaultdict(nested_dict)


def payload_to_dict(payload, colnames: tuple, dct: dict = None) -> dict:
    if not dct:
        dct = defaultdict(list)
    for lzt in payload:
        for idx, col in enumerate(colnames):
            dct[col].append(lzt[idx])
    return dct


def payload_transform(payload: bytes, shape_str: str, dtype_str: str) -> dict:
    # decompress the payload
    payload_decomp = gzip.decompress(payload)
    # get the image shape from the metadata of the http header
    img_shape = tuple(int(i) for i in shape_str[1:-1].split(","))

    # reshape the image to the original
    flat_img = np.frombuffer(payload_decomp, dtype=dtype_str, count=-1)
    img = flat_img.reshape(img_shape)

    return img


class ObjWrap:
    """ObjWrap is a simple wrapping class to help
    delete objects that are yielded in a loop but still
    kept in scope.
    """

    def __init__(self, obj):
        self.obj = obj

    def unlink(self):
        obj = self.obj
        self.obj = None
        return obj
