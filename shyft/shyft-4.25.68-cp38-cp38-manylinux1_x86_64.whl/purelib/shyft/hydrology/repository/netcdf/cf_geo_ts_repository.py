# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from os import path
import numpy as np
from netCDF4 import Dataset
from ... import shyftdata_dir
from ....time_series import (TimeAxis, UtcTimeVector)
from .. import interfaces
from .time_conversion import convert_netcdf_time
from .utils import _limit_1D, _numpy_to_geo_ts_vec, _make_time_slice, _slice_var_1D


class CFDataRepositoryError(Exception):
    pass


class CFDataRepository(interfaces.GeoTsRepository):
    """
    Repository for geo located timeseries stored in netCDF files.

    """

    def __init__(self, epsg, filename, padding=5000.):
        filename = path.expandvars(filename)

        if not path.isabs(filename):
            # Relative paths will be prepended the data_dir
            filename = path.join(shyftdata_dir, filename)
        if not path.isfile(filename):
            raise CFDataRepositoryError("No such file '{}'".format(filename))

        self._filename = filename
        self.allow_subset = True  # allow_subset

        self.shyft_cs = f"+init=EPSG:{epsg}"
        self._padding = padding

        # Field names and mappings netcdf_name: shyft_name
        self._nc_shyft_map = {"relative_humidity": "relative_humidity",
                              "temperature": "temperature",
                              "z": "z",
                              "precipitation": "precipitation",
                              "precipitation_amount_acc": "precipitation",
                              "wind_speed": "wind_speed",
                              "global_radiation": "radiation",
                              "discharge": "discharge"}

        self._shift_fields = ("precipitation_amount_acc",
                              "integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time")

    def get_timeseries(self, input_source_types, utc_period, geo_location_criteria=None):
        """
        see interfaces.GeoTsRepository
        """

        with Dataset(self._filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types,
                                               utc_period, geo_location_criteria)

    def _get_data_from_dataset(self, dataset, input_source_types, utc_period,
                               geo_location_criteria):

        x = dataset.variables.get("x", None)
        y = dataset.variables.get("y", None)
        time = dataset.variables.get("time", None)
        dim_nb_series = [dim.name for dim in dataset.dimensions.values() if dim.name != 'time'][0]
        if not all([x, y, time]):
            raise CFDataRepositoryError("Something is wrong with the dataset."
                                        " x/y coords or time not found.")
        time = convert_netcdf_time(time.units, time)
        data_cs = dataset.variables.get("crs", None)
        if data_cs is None:
            raise CFDataRepositoryError("No coordinate system information in dataset.")

        time_slice, issubset = _make_time_slice(time, utc_period, CFDataRepositoryError)

        x, y, m_xy, xy_slice = _limit_1D(x[:], y[:], data_cs.proj4, self.shyft_cs, geo_location_criteria, self._padding, CFDataRepositoryError)

        raw_data = {}
        for k in dataset.variables.keys():
            if self._nc_shyft_map.get(k, None) in input_source_types:
                if k in self._shift_fields and issubset:  # Add one to time slice
                    data_time_slice = slice(time_slice.start, time_slice.stop + 1)
                else:
                    data_time_slice = time_slice
                data = dataset.variables[k]
                pure_arr = _slice_var_1D(data, dim_nb_series, xy_slice, m_xy, slices={'time': data_time_slice})
                raw_data[self._nc_shyft_map[k]] = pure_arr, k

        if "z" in dataset.variables.keys():
            data = dataset.variables["z"]
            # dims = data.dimensions
            # data_slice = len(data.dimensions)*[slice(None)]
            # data_slice[dims.index("dim_nb_series")] = m_xy
            # z = data[data_slice]
            z = data[m_xy]
        else:
            raise CFDataRepositoryError("No elevations found in dataset")

        # Make sure requested fields are valid, and that dataset contains the requested data.
        if not self.allow_subset and not (set(raw_data.keys()).issuperset(input_source_types)):
            raise CFDataRepositoryError("Could not find all data fields")

        extracted_data = self._transform_raw(raw_data, time[time_slice], issubset=issubset)
        return _numpy_to_geo_ts_vec(extracted_data, x, y, z, CFDataRepositoryError)

    def _transform_raw(self, data, time, issubset=False):
        """
        We need full time if deaccumulating
        """

        def noop_time(t):
            return TimeAxis(UtcTimeVector.from_numpy(t.astype(int)), int(2*t[-1] - t[-2]))

        def dacc_time(t):
            return noop_time(t) if issubset else TimeAxis(UtcTimeVector.from_numpy(t.astype(int)))

        def noop_space(x):
            return x

        def air_temp_conv(T):
            return T - 273.15

        def prec_conv(p):
            return p[1:]

        def prec_acc_conv(p):
            return np.clip(p[1:] - p[:-1], 0.0, 1000.0)

        def rad_conv(r):
            dr = r[1:] - r[:-1]
            return np.clip(dr/(time[1] - time[0]), 0.0, 5000.0)

        # Unit- and aggregation-dependent conversions go here
        convert_map = {"wind_speed": lambda x, t: (noop_space(x), noop_time(t)),
                       "relative_humidity": lambda x, t: (noop_space(x), noop_time(t)),
                       "temperature": lambda x, t: (noop_space(x), noop_time(t)),
                       "global_radiation": lambda x, t: (noop_space(x), noop_time(t)),
                       "precipitation": lambda x, t: (noop_space(x), noop_time(t)),
                       "precipitation_amount_acc": lambda x, t: (prec_acc_conv(x), dacc_time(t)),
                       "discharge": lambda x, t: (noop_space(x), noop_time(t))}
        res = {}
        for k, (v, ak) in data.items():
            res[k] = convert_map[ak](v, time)
        return res
