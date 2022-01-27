import hashlib
import numbers
import pathlib

import h5py
import numpy as np


def hashobj(obj):
    """Compute md5 hex-hash of a Python object"""
    return hashlib.md5(obj2bytes(obj)).hexdigest()


def obj2bytes(obj):
    """String representation of an object for hashing"""
    if isinstance(obj, str):
        return obj.encode("utf-8")
    elif isinstance(obj, pathlib.Path):
        return obj2bytes(str(obj))
    elif isinstance(obj, (bool, numbers.Number)):
        return str(obj).encode("utf-8")
    elif obj is None:
        return b"none"
    elif isinstance(obj, np.ndarray):
        return obj.tobytes()
    elif isinstance(obj, tuple):
        return obj2bytes(list(obj))
    elif isinstance(obj, list):
        return b"".join(obj2bytes(o) for o in obj)
    elif isinstance(obj, dict):
        return obj2bytes(sorted(obj.items()))
    elif hasattr(obj, "identifier"):
        return obj2bytes(obj.identifier)
    elif isinstance(obj, h5py.Dataset):
        return obj2bytes(obj[0])
    else:
        raise ValueError("No rule to convert object '{}' to string.".
                         format(obj.__class__))


def get_valid_filename(value):
    """
    Return the given string converted to a string that can be used
    for a clean filename.
    """
    ret = ""

    valid = "abcdefghijklmnopqrstuvwxyz" \
            + "ABCDEFGHIJKLMNOPQRSTUVWXYZ" \
            + "0123456789" \
            + "._-()"
    replace = {
        " ": "_",
        "[": "(",
        "]": ")",
        "µ": "u",
    }

    for ch in value:
        if ch in valid:
            ret += ch
        elif ch in replace:
            ret += replace[ch]
        else:
            ret += "?"

    ret = ret.strip(".")
    return ret
