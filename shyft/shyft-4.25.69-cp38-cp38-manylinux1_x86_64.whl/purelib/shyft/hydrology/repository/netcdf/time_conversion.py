# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from ....hydrology import parse_cf_time
import numpy as np


def convert_netcdf_time(time_spec: str, t:np.array)->np.array:
    """
    Converts supplied numpy array to  shyft time given netcdf time_spec.
    Throws exception if time-unit is not supported, i.e. not part of delta_t_dic
    as specified in this file.

    Parameters
    ----------
        time_spec: string
           from netcdef  like 'hours since 1970-01-01 00:00:00'
        t: numpy array
    Returns
    -------
        numpy array type int64 with new shyft time units (seconds since 1970utc)
    """
    r = parse_cf_time(time_spec)
    if not r.valid():
        raise RuntimeError(f"Ill-formed netcdf time_spec {time_spec}")
    t_origin = np.int64(int(r.start))
    delta_t = np.int64(int(r.timespan()))
    return t_origin + delta_t * t[:].astype(np.int64)
