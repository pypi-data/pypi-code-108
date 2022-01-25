import json
import numbers
import pathlib

import dclab
import h5py


def append_history(path, hdict):
    """Append DCKit history to an .rtdc file

    Parameters
    ----------
    path: str or pathlib.Path
        Path to .rtdc file
    hdict: dict
        History element (not the full history)
    """
    path = pathlib.Path(path)
    hlist = read_history(path)
    hlist.append(hdict)
    write_history(path, hlist)


def default_json_converter(obj):
    """is a function that should return a serializable version
    of obj or raise TypeError.
    """
    if isinstance(obj, numbers.Integral):
        return int(obj)
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")
    else:
        raise TypeError(
            "Object of type '{}' is not JSON serializable".format(type(obj)))


def read_history(path):
    """Read DCKit history from an .rtdc file

    Parameters
    ----------
    path: str or pathlib.Path
        Path to .rtdc file

    Returns
    -------
    hlist: list of dicts
        Full history (containing history elements)
    """
    path = pathlib.Path(path)
    with dclab.new_dataset(path) as ds:
        if "dckit-history" in ds.logs:
            hdump = ds.logs["dckit-history"]
            hlist = json.loads("\n".join(hdump))
        else:
            hlist = []
    return hlist


def write_history(path, hlist):
    """Write DCKit history to .rtdc file

    Parameters
    ----------
    path: str or pathlib.Path
        Path to .rtdc file
    hlist: list of dicts
        Full history (containing history elements)
    """
    path = pathlib.Path(path)
    # remove previous log
    with h5py.File(path, "a") as h5:
        if "dckit-history" in h5["logs"]:
            del h5["logs"]["dckit-history"]
    # dump json log
    hlog = json.dumps(hlist,
                      sort_keys=True,
                      indent=2,
                      default=default_json_converter,
                      ).split("\n")
    # write dump as log
    with dclab.RTDCWriter(path) as hw:
        hw.store_log("dckit-history", hlog)
