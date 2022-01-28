"""Methods for saving outputs to files.

Currently just uses pickles until HDF is working.
"""

import h5py
import numpy as np
import pickle
import warnings
import json
from collections import defaultdict
import importlib
import os.path

HDF_EXTENSIONS = [".h5", ".hdf5", ".hdf"]
PICKLE_EXTENSIONS = [".pkl", ".pickle"]
EXTENSIONS = HDF_EXTENSIONS + PICKLE_EXTENSIONS
FORMAT_OPTIONS = ["hdf", "pickle"]


def type_to_json(_type):
    if not isinstance(_type, type):
        raise TypeError(f"Not a type: {_type}")
    if hasattr(_type, "__module__"):
        return f"{_type.__module__}.{_type.__name__}"
    else:
        return _type.__name__


def type_from_json(data):
    # Grab the class name and figure out what type of object
    # to instantiate
    cls_name, *module = data.rsplit(".", maxsplit=1)[::-1]
    if len(module) == 0:  # builtin
        return getattr(__builtins__, cls_name)
    else:
        module = importlib.import_module(module[0])
        return getattr(module, cls_name)


def np_dtype_to_json(dtype):
    """Converts a numpy dtype into a json string format."""
    if not isinstance(dtype, np.dtype):
        raise TypeError(f"Not a dtype {dtype}")
    return json.dumps(tuple((a, b, tuple(c)) for a, b, *c in dtype.descr))


def np_dtype_from_json(data):
    data = json.loads(data)

    def process(a, b, c):
        a = a.strip()
        f = (
            lambda x: ()
            if len(x) == 0
            else tuple(np.atleast_1d(np.squeeze(x)).tolist())
        )
        c = f(c)
        if len(c) == 0:
            return (
                a,
                b,
            )
        else:
            return (a, b, c)

    # multiple checks needed to remove extra information stored during
    # the storage stage. If no name or shapes are given then we have
    # to go back to a single dtype string, rather than a tuple otherwise
    # you get a record array and an auto generated name for the column
    descr = [process(a, b, c) for a, b, *c in data]
    if len(descr) == 1 and len(descr[0]) == 2 and len(descr[0][0]) == 0:
        descr = descr[0][1]
    return np.dtype(descr)


def dict_to_json(d):
    return json.dumps(d)


def object_to_hdf(obj):
    pkl = pickle.dumps(obj, protocol=5)
    return np.void(pkl)


def create_object_dataset(grp, key, obj):
    d = grp.create_dataset(key, data=object_to_hdf(obj))
    d.attrs["type"] = type_to_json(type(obj))


def str_array_to_hdf(s):
    return np.string_(s)


def to_generic_hdf(obj, grp):
    """Used to convert a generic Python class into a HDF group.

    Scalar values (as determined by np.isscalar) are added as HDF group attributes. This
    includes class attributes that are int, float, strings, etc. Attributes that are
    representable with a numpy array are written as datasets within the group. Any
    attribute that does not fit in the above will be pickled and added as a byte stream
    dataset.
    """
    if not hasattr(obj, "__dict__"):
        warnings.warn(f"Nothing to write for {repr(obj)}")
        return

    for key, value in obj.__dict__.items():
        try:
            arr = np.asarray(value)
            if np.isscalar(value):
                # Write scalars as attributes to the group
                grp.attrs[key] = value
            elif arr.dtype.char == "U":  # array of strings
                grp.create_dataset(key, data=str_array_to_hdf(value))
            elif arr.dtype.char == "O":  # Object
                create_object_dataset(grp, key, value)
            else:  # Otherwise just try and dump the numpy array
                grp.create_dataset(key, data=value)
        except Exception as ex:
            raise Exception(f"Error writing {key}:{value} to HDF", ex)


def dump_solution_hdf(sol, filename):
    def _dump(grp, obj):
        grp.attrs["__solution__.name"] = obj.name
        grp.attrs["__solution__.type"] = type_to_json(type(obj))
        dumpfunc = dump_mapping.get(type(obj), to_generic_hdf)
        grp.attrs["__solution__.dumper"] = f"{dumpfunc.__module__}.{dumpfunc.__name__}"
        dumpfunc(obj, grp)

    data = defaultdict(list)
    data[sol.name].append(sol)
    for _ in sol.get_all_children():
        data[_.get_path()].append(_)
    with h5py.File(filename, "w") as f:

        # Every solution object has its own group
        for path, sols in data.items():
            grp = f.create_group(path)
            if len(sols) > 1:
                # Then we have multiple solutions with the same name at this level
                for i, s in enumerate(sols):
                    g = grp.create_group(str(i))
                    _dump(g, s)
            else:
                _dump(grp, sols[0])


def load_solution_hdf(filename):
    def _load_group(data, parent=None):
        groups = list(filter(lambda x: type(x[1]) == h5py.Group, data.items()))
        datasets = list(filter(lambda x: type(x[1]) == h5py.Dataset, data.items()))
        new_sol = None

        if "__solution__.type" in data.attrs:
            sol_type = data.attrs["__solution__.type"]
            sol_name = data.attrs["__solution__.name"]
            # Grab the class name and figure out what type of object
            # to instantiate
            cls_name, *module = sol_type.rsplit(".", maxsplit=1)[::-1]
            if len(module) == 0:  # builtin
                stype = getattr(__builtins__, cls_name)
            else:
                module = importlib.import_module(module[0])
                stype = getattr(module, cls_name)
            # Try and make a new object
            if stype in load_mapping:
                # Need to do more complicated mapping
                # this function should do all the attr
                # and dataset reading from the group
                # into the new object
                new_sol = load_mapping[stype](data, parent)
                if new_sol not in parent.children:
                    parent.add(new_sol)
                if type(new_sol) is not stype:
                    raise TypeError(
                        f"Excepted {load_mapping[stype]} to return an object of type {stype} not {new_sol}"
                    )
            else:
                # assume the most basic of interface for BaseSolution
                new_sol = stype(sol_name, parent=parent)
                # Set any scalar like attrs
                for attr in data.attrs:
                    if not attr.startswith("__solution__"):  # Ignore any metadata
                        setattr(new_sol, attr, data.attrs[attr])
                for name, ds in datasets:
                    setattr(new_sol, name, ds[()])

            parent = new_sol  # new parent to use as creating a new solution
        # Now load any other sub-groups which will be other solutions/groups
        for _, value in groups:
            _load_group(value, parent=parent)
        if new_sol:
            return new_sol

    with h5py.File(filename, "r") as f:
        groups = list(filter(lambda x: type(x[1]) == h5py.Group, f.items()))
        datasets = list(filter(lambda x: type(x[1]) == h5py.Dataset, f.items()))
        if len(datasets):
            warnings.warn("Found datasets in root which wasn't expected")
        if len(groups) != 1:
            raise Exception("Unexpected number of groups in root")
        return _load_group(groups[0][1], None)


def save(obj, filename, format=None):
    f"""Saves a Finesse solution object to a file. Two options are available: HDF5 and Pickle.

    Parameters
    ----------
    obj : Solution
        Solution object generated by a Finesse simulation
    filename : str
        A path and filename to save the output. If the path does not exist it will
        be created.
    formation : str, optional
        For HDF files use one of {HDF_EXTENSIONS} or
        pickle files use one of {PICKLE_EXTENSIONS}.
        If `None` then the extension of the `filename` is used.
    """
    if format is None:
        _, ext = os.path.splitext(filename)
        if ext in HDF_EXTENSIONS:
            format = "hdf"
        elif ext in PICKLE_EXTENSIONS:
            format = "pickle"
        elif ext is None:
            raise ValueError(
                "No file extension was provided, could not automatically choose format to use."
            )
        else:
            raise ValueError(
                f"{ext} not a supported file extension. Valid extensions are {EXTENSIONS}"
            )
    elif format not in FORMAT_OPTIONS:
        raise ValueError(f"format options are {FORMAT_OPTIONS}")

    a, _ = os.path.split(filename)
    if not os.path.exists(a):
        os.mkdir(a)

    if format == "pickle":
        pickle.dump(obj, open(filename, "wb"), protocol=5)
    elif format == "hdf":
        dump_solution_hdf(obj, filename)


def load(filename, format=None):
    if format is None:
        _, ext = os.path.splitext(filename)
        if ext in HDF_EXTENSIONS:
            format = "hdf"
        elif ext in PICKLE_EXTENSIONS:
            format = "pickle"
        elif ext is None:
            raise ValueError(
                "No file extension was provided, could not automatically choose format to use."
            )
        else:
            raise ValueError(
                f"{ext} not a supported file extension. Valid extensions are {EXTENSIONS}"
            )
    elif format not in FORMAT_OPTIONS:
        raise ValueError(f"format options are {FORMAT_OPTIONS}")

    if format == "pickle":
        return pickle.load(open(filename, "rb"))
    elif format == "hdf":
        return load_solution_hdf(filename)


# object type to HDF data map
dump_mapping = {}
# HDF data to object type map
load_mapping = {}
