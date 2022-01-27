# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from os import path
import numpy as np
from netCDF4 import Dataset
from ....time_series import (Calendar,TimeAxis,deltahours)
from ... import shyftdata_dir
from .. import interfaces
from .time_conversion import convert_netcdf_time
from .utils import calc_RH, _slice_var_2D, _limit_2D, _make_time_slice, _numpy_to_geo_ts_vec


class ERAInterimDataRepositoryError(Exception):
    pass


class ERAInterimDataRepository(interfaces.GeoTsRepository):
    """
    Repository for geo located timeseries stored in netCDF files.

    """
    _G = 9.80665  # WMO-defined gravity constant to calculate the height in metres from geopotential

    def __init__(self, epsg, filename, padding=5000., allow_subset=True):
        """
        Construct the netCDF4 dataset reader for data from ERAInterim,
        and initialize data retrieval.
        """
        filename = path.expandvars(filename)
        if not path.isabs(filename):
            # Relative paths will be prepended the data_dir
            filename = path.join(shyftdata_dir, filename)
        if not path.isfile(filename):
            raise ERAInterimDataRepositoryError("No such file '{}'".format(filename))
            
        self._filename = filename # path.join(directory, filename)
        self.allow_subset = allow_subset
        self._padding = padding
        
        self.analysis_hours = [0, 12]
        self.cal = Calendar()

        self.shyft_cs = "+init=EPSG:{}".format(epsg)

        # Field names and mappings netcdf_name: shyft_name
        self._era_shyft_map = {"u10": "x_wind",
                               "v10": "y_wind",
                               "t2m": "temperature",
                               "tp": "precipitation",
                               "sp": "surface_pressure",
                               "d2m": "dewpoint_temperature",
                               "ssrd": "radiation"}

        self._shift_fields = ("tp","ssrd")
                                
    def get_timeseries(self, input_source_types, utc_period, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        filename = self._filename
        if not path.isfile(filename):
            raise ERAInterimDataRepositoryError("File '{}' not found".format(filename))
        with Dataset(filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types,
                                               utc_period, geo_location_criteria)

    def _get_data_from_dataset(self, dataset, input_source_types, utc_period,
                               geo_location_criteria):
        if "wind_speed" in input_source_types:
            input_source_types = list(input_source_types)  # Copy the possible mutable input list
            input_source_types.remove("wind_speed")
            input_source_types.extend(["x_wind", "y_wind"])
        no_temp = False
        if "temperature" not in input_source_types: no_temp = True
        if "relative_humidity" in input_source_types:
            input_source_types.remove("relative_humidity")
            input_source_types.extend(["surface_pressure", "dewpoint_temperature"])
            if no_temp: input_source_types.extend(["temperature"])

        raw_data = {}
        lon = dataset.variables.get("longitude", None)
        lat = dataset.variables.get("latitude", None)
        time = dataset.variables.get("time", None)
        data_cs = "+init=EPSG:4326" # WGS84

        if not all([lon, lat, time]):
            raise ERAInterimDataRepositoryError("Something is wrong with the dataset."
                                         " lat/lon coords or time not found.")
        time = convert_netcdf_time(time.units,time)
        time_slice, issubset = _make_time_slice(time, utc_period, ERAInterimDataRepositoryError)

        x, y, (x_inds, y_inds), (x_slice, y_slice) = _limit_2D(
            lon[:], lat[:], data_cs, self.shyft_cs, geo_location_criteria, self._padding, ERAInterimDataRepositoryError, clip_in_data_cs=True)

        for k in dataset.variables.keys():
            if self._era_shyft_map.get(k, None) in input_source_types:
                if k in self._shift_fields and issubset:  # Add one to time slice
                    data_time_slice = slice(time_slice.start, time_slice.stop + 1)
                else:
                    data_time_slice = time_slice
                data = dataset.variables[k]
                pure_arr = _slice_var_2D(data, lon.name, lat.name, x_slice, y_slice, x_inds,
                                         y_inds, ERAInterimDataRepositoryError,
                                         slices={'time': data_time_slice})
                raw_data[self._era_shyft_map[k]] = pure_arr, k
                
        if "z" in dataset.variables.keys():
            data = dataset.variables["z"]
            z = _slice_var_2D(data, lon.name, lat.name, x_slice, y_slice, x_inds, y_inds, ERAInterimDataRepositoryError)/self._G # Converting from geopotential to m
        else:
            raise ERAInterimDataRepositoryError("No elevations found in dataset")

        # Make sure requested fields are valid, and that dataset contains the requested data.
        if not self.allow_subset and not (set(raw_data.keys()).issuperset(input_source_types)):
            raise ERAInterimDataRepositoryError("Could not find all data fields")
            
        if set(("x_wind", "y_wind")).issubset(raw_data):
            x_wind, _ = raw_data.pop("x_wind")
            y_wind, _ = raw_data.pop("y_wind")
            raw_data["wind_speed"] = np.sqrt(np.square(x_wind) + np.square(y_wind)), "wind_speed"
        if set(("surface_pressure", "dewpoint_temperature")).issubset(raw_data):
            sfc_p, _ = raw_data.pop("surface_pressure")
            dpt_t, _ = raw_data.pop("dewpoint_temperature")
            if no_temp:
                sfc_t, _ = raw_data.pop("temperature")
            else:
                sfc_t, _ = raw_data["temperature"]
            raw_data["relative_humidity"] = calc_RH(sfc_t,dpt_t,sfc_p), "relative_humidity"
        return _numpy_to_geo_ts_vec(self._transform_raw(raw_data, time[time_slice], issubset=issubset), x, y, z, ERAInterimDataRepositoryError)

    def _transform_raw(self, data, time, issubset=False):
        """
        We need full time if deaccumulating
        """

        def noop_time(t):
            t0 = int(t[0])
            t1 = int(t[1])
            return TimeAxis(t0, t1 - t0, len(t))

        def dacc_time(t):
            t0 = int(t[0])
            t1 = int(t[1])
            return noop_time(t) if issubset else TimeAxis(t0, t1 - t0, len(t) - 1)

        def noop_space(x):
            return x

        def air_temp_conv(T):
            return T - 273.15

        def prec_acc_conv(p):
            indx = np.nonzero([self.cal.calendar_units(int(ti)).hour in self.analysis_hours for ti in time])[0]
            f = 1000.*int(deltahours(1))/(int(time[1]) - int(time[0])) # conversion from m/delta_t to mm/1hour
            dp = np.clip((p[1:] - p[:-1])*f, 0.0, 10000.) # np.clip b/c negative values may occur after deaccumulation
            dp[indx] = p[indx+1]*f
            return dp

        def rad_conv(r):
            indx = np.nonzero([self.cal.calendar_units(int(ti)).hour in self.analysis_hours for ti in time])[0]
            dr = np.clip((r[1:] - r[:-1])/(time[1] - time[0]), 0.0, 10000.) # np.clip b/c negative values may occur after deaccumulation
            dr[indx] = r[indx+1]/(time[1] - time[0])
            return dr

        convert_map = {"wind_speed": lambda x, t: (noop_space(x), noop_time(t)),
                       "relative_humidity": lambda x, t: (noop_space(x), noop_time(t)),
                       "t2m": lambda x, t: (air_temp_conv(x), noop_time(t)),
                       "ssrd": lambda x, t: (rad_conv(x), dacc_time(t)),
                       "tp": lambda x, t: (prec_acc_conv(x), dacc_time(t))}
        res = {}
        for k, (v, ak) in data.items():
            res[k] = convert_map[ak](v, time)
        return res
