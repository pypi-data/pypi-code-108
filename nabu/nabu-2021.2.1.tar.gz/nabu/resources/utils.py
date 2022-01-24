from ast import literal_eval
import numpy as np
from psutil import virtual_memory, cpu_count

def get_values_from_file(fname, n_values=None, shape=None, sep=None, any_size=False):
    """
    Read a text file and scan the values inside.
    This function expects one value per line, or values separated with a separator
    defined with the `sep` parameter.

    Parameters
    ----------
    fname: str
        Path of the text file
    n_values: int, optional
        If set to a value, this function will check that it scans exactly this
        number of values.
        Ignored if `shape` is provided
    shape: tuple, optional
        Generalization of n_values for higher dimensions.
    sep: str, optional
        Separator between values. Default is white space
    any_size: bool, optional
        If set to True, then the parameters 'n_values' and 'shape' are ignored.

    Returns
    --------
    arr: numpy.ndarray
        An array containing the values scanned from the text file
    """
    if not(any_size) and not((n_values is not None) ^ (shape is not None)):
        raise ValueError("Please provide either n_values or shape")
    arr = np.loadtxt(fname, ndmin=1)
    if (n_values is not None) and (arr.shape[0] != n_values):
        raise ValueError("Expected %d values, but could get %d values" % (n_values, arr.shape[0]))
    if (shape is not None) and (arr.shape != shape):
        raise ValueError("Expected shape %s, but got shape %s" % (shape, arr.shape))
    return arr


def get_memory_per_node(max_mem, is_percentage=True):
    """
    Get the available memory per node in GB.

    Parameters
    ----------
    max_mem: float
        If is_percentage is False, then number is interpreted as an absolute
        number in GigaBytes.
        Otherwise, it should be a number between 0 and 100 and is interpreted
        as a percentage.
    is_percentage: bool
        A boolean indicating whether the parameter max_mem is to be interpreted
        as a percentage of available system memory.
    """
    sys_avail_mem = virtual_memory().available / 1e9
    if is_percentage:
        return (max_mem/100.) * sys_avail_mem
    else:
        return min(max_mem, sys_avail_mem)


def get_threads_per_node(max_threads, is_percentage=True):
    """
    Get the available memory per node in GB.

    Parameters
    ----------
    max_threads: float
        If is_percentage is False, then number is interpreted as an absolute
        number of threads.
        Otherwise, it should be a number between 0 and 100 and is interpreted
        as a percentage.
    is_percentage: bool
        A boolean indicating whether the parameter max_threads is to be interpreted
        as a percentage of available system memory.
    """
    sys_n_threads = cpu_count(logical=True)
    if is_percentage:
        return (max_threads/100.) * sys_n_threads
    else:
        return min(max_threads, sys_n_threads)


def extract_parameters(params_str, sep=";"):
    """
    Extract the named parameters from a string.

    Example
    --------
    The function can be used as follows:

    >>> extract_parameters("window_width=None; median_filt_shape=(3,3); padding_mode='wrap'")
    ... {'window_width': None, 'median_filt_shape': (3, 3), 'padding_mode': 'wrap'}
    """
    if params_str in ("", None):
        return {}
    params_list = params_str.strip(sep).split(sep)
    res = {}
    for param_str in params_list:
        param_name, param_val_str = param_str.strip().split("=")
        param_name = param_name.strip()
        param_val_str = param_val_str.strip()
        param_val = literal_eval(param_val_str)
        res[param_name] = param_val
    return res


def is_hdf5_extension(ext, errors="ignore"):
    if ext.lower() in ["h5", "hdf5", "nx"]:
        return True
    else:
        if errors == "raise":
            raise ValueError("Unknown data file format: %s" % ext)
        return False
