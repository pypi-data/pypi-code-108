import pickle
import orjson
import numpy as np 
from pathlib import Path
import os

def orjson_load(filename):
    return orjson.loads(open(filename, "rb").read())


def orjson_dump(data, filename):
    open(filename, "wb").write(orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS))

def pickle_load(filename):
    return pickle.load(open(filename,'rb'))

def pickle_dump(data, filename):
    pickle.dump(data,open(filename,'wb'))

def np_load(filename):
    return np.load(filename)
def np_dump(data, filename):
    np.save(filename,data)


def prepare_filename(filename):
    if isinstance(filename, Path):
        filename = str(filename)
    if '~' in filename:
        filename = os.path.expanduser(filename)
    return filename

def sload(filename):
    filename = prepare_filename(filename)
    if filename.endswith('json'):
        return orjson_load(filename)
    elif filename.endswith('pkl'):
        return pickle_load(filename)
    elif filename.endswith('npy'):
        return np_load(filename)
    else:
        raise NotImplementedError(f"File format not supported: {filename.split('.')[-1]}")
    
def sdump(data, filename, makedirs=False):
    filename = prepare_filename(filename)
    if makedirs:
        os.makedirs(Path(filename).parent, exist_ok=True)
    if filename.endswith('json'):
        return orjson_dump(data, filename)
    elif filename.endswith('pkl'):
        return pickle_dump(data, filename)
    elif filename.endswith('npy'):
        return np_dump(data, filename)
    else:
        raise NotImplementedError(f"File format not supported: {filename.split('.')[-1]}")


