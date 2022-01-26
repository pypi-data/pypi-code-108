import numpy as np
import re
from typing import Union, get_origin, get_args

listLike = Union[list, np.ndarray, tuple]

def _ToList(arg):

    if isinstance(arg, list):
        return np.asarray(arg)

    if not isinstance(arg, get_args(listLike)):
        return np.asarray([arg])

    else:
        return arg


def ToList(*args):
    out = []
    for arg in args:
        if not isinstance(arg, get_args(listLike)):
            out.append( [arg] )
        else:
            out.append(arg)

    if len(out) == 1: return out[0]

    return np.asarray(out)


def FormatStr(function):
    def wrapped(*args, **kwargs):
        args = (re.sub(r"\s+", "", arg.lower() ) if isinstance(arg, str) else arg for arg in args)

        kwargs = {k: re.sub(r"\s+", "", v.lower() ) if isinstance(v, str) else v for k, v in kwargs.items()}

        return function(*args, **kwargs)
    return wrapped


def FormatString(string):
    return re.sub(r"\s+", "", string.lower() )


def ConvertPolarization(Polarization):
    if Polarization is None:
        return 4242

    if isinstance(Polarization, np.ndarray):
        Polarization[Polarization==None] = 4242
        return Polarization
    else:
        return Polarization



# -
