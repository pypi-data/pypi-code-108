# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
import os
import re
import numpy as np
from netCDF4 import Dataset
from ....time_series import (TimeAxis)
from .. import interfaces
from .time_conversion import convert_netcdf_time
from .utils import _limit_2D, _slice_var_2D, _numpy_to_geo_ts_vec, _make_time_slice, _get_files


class WRFDataRepositoryError(Exception):
    pass


class WRFDataRepository(interfaces.GeoTsRepository):
    """
    Repository for geo located timeseries given as WRF(*) data in
    netCDF(3) files.
    NetCDF dataset assumptions:
        * Dimensions:
           Time = UNLIMITED ; // (1 currently)
           DateStrLen = 19 ;
           west_east = 73 ;
           south_north = 60 ;
           bottom_top = 29 ;
           bottom_top_stag = 30 ;
           soil_layers_stag = 4 ;
           west_east_stag = 74 ;
           south_north_stag = 61 ;
        * Variables:
          TODO: A lot.  We really want to list them here?
    (*) WRF model output is from:
        http://www2.mmm.ucar.edu/wrf/users/docs/user_guide_V3/users_guide_chap5.htm
    """

    def __init__(self, epsg, directory, filename=None, padding=5000., allow_subset=False):
        """
        Construct the netCDF4 dataset reader for data from WRF NWP model,
        and initialize data retrieval.
        Parameters
        ----------
        epsg: string
            Unique coordinate system id for result coordinates.
            Currently "32632" and "32633" are supported.
        directory: string
            Path to directory holding one or possibly more WRF data files.
            os.path.isdir(directory) should be true, or exception is raised.
        filename: string, optional
            Name of netcdf file in directory that contains spatially
            distributed input data. Can be a regex pattern as well
        padding: float, optional
            padding in meters
        allow_subset: bool
            Allow extraction of a subset of the given source fields
            instead of raising exception.
        """
        directory = os.path.expandvars(directory)
        self._directory = directory
        if filename is None:
            filename = r"wrfout_d03_(\d{4})-(\d{2})"
        self._filename = filename
        self.allow_subset = allow_subset
        if not os.path.isdir(directory):
            raise WRFDataRepositoryError("No such directory '{}'".format(directory))

        self.shyft_cs = "+init=EPSG:{}".format(epsg)
        self._padding = padding

        # Field names and mappings
        self.wrf_shyft_map = {
            "T2": "temperature",
            "HGT": "z",
            "PREC_ACC_NC": "precipitation",
            "U10": "x_wind",
            "V10": "y_wind",
            "SWDOWN": "radiation",
            "Q2": "mixing_ratio",
            "PSFC": "pressure"}

        # Fields that need an additional timeslice because the measure average values
        # self._shift_fields = ("PREC_ACC_NC", "SWDOWN")
        self._shift_fields = ()

    def get_timeseries(self, input_source_types, utc_period, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """

        filename = os.path.join(self._directory, self._filename)
        if not os.path.isfile(filename):
            if re.compile(self._filename).groups > 0:  # check if it is a filename-pattern
                filename = _get_files(self._directory, self._filename, utc_period.start, WRFDataRepositoryError)
            else:
                raise WRFDataRepositoryError("File '{}' not found".format(filename))
        with Dataset(filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types,
                                               utc_period, geo_location_criteria)

    def _calculate_rel_hum(self, T2, PSFC, Q2):
        # constants
        EZERO = 6.112
        ESLCON1 = 17.67
        ESLCON2 = 29.65
        CELKEL = 273.15
        RD = 287.
        RV = 461.6
        EPS = 0.622

        # calculation
        RH = np.empty_like(T2)
        es = EZERO*np.exp(ESLCON1*(T2 - CELKEL)/(T2 - ESLCON2))
        qvs = EPS*es/(0.01*PSFC - (1.0 - EPS)*es)
        RH = Q2/qvs
        RH[RH > 1.0] = 1.0
        RH[RH < 0.0] = 0.0
        return RH

    def _get_data_from_dataset(self, dataset, input_source_types, utc_period,
                               geo_location_criteria, ensemble_member=None):
        input_source_types_orig = list(input_source_types)
        if "wind_speed" in input_source_types:
            input_source_types = list(input_source_types)  # We change input list, so take a copy
            input_source_types.remove("wind_speed")
            input_source_types.append("x_wind")
            input_source_types.append("y_wind")

        if "relative_humidity" in input_source_types:
            input_source_types = list(input_source_types)  # We change input list, so take a copy
            input_source_types.remove("relative_humidity")
            input_source_types.append("mixing_ratio")
            input_source_types.append("pressure")
            if not "temperature" in input_source_types:
                input_source_types.append("temperature")  # Needed for rel_hum calculation

        raw_data = {}
        x_var = dataset.variables.get("XLONG", None)
        y_var = dataset.variables.get("XLAT", None)
        time = dataset.variables.get("XTIME", None)
        if not all([x_var, y_var, time]):
            raise WRFDataRepositoryError("Something is wrong with the dataset."
                                         " x/y coords or time not found.")
        time = convert_netcdf_time(time.units, time)
        data_cs_proj4 = "latlong"
        if data_cs_proj4 is None:
            raise WRFDataRepositoryError("No coordinate system information in dataset.")

        time_slice, issubset = _make_time_slice(time, utc_period, WRFDataRepositoryError)
        x, y, (x_inds, y_inds), (x_slice, y_slice) = _limit_2D(x_var[0], y_var[0], data_cs_proj4, self.shyft_cs, geo_location_criteria, self._padding, WRFDataRepositoryError, clip_in_data_cs=False)
        for k in dataset.variables.keys():
            if self.wrf_shyft_map.get(k, None) in input_source_types:
                if k in self._shift_fields and issubset:  # Add one to time slice
                    data_time_slice = slice(time_slice.start, time_slice.stop + 1)
                else:
                    data_time_slice = time_slice
                data = dataset.variables[k]
                pure_arr = _slice_var_2D(data, x_var.dimensions[2], y_var.dimensions[1], x_slice, y_slice, x_inds, y_inds, WRFDataRepositoryError,
                                         slices={'Time': data_time_slice, 'ensemble_member': ensemble_member}
                                         )
                raw_data[self.wrf_shyft_map[k]] = pure_arr, k

        if 'HGT' in dataset.variables.keys():
            data = dataset.variables['HGT']
            z = _slice_var_2D(data, x_var.dimensions[2], y_var.dimensions[1], x_slice, y_slice, x_inds, y_inds, WRFDataRepositoryError,
                              slices={'Time': 0}
                              )
        else:
            raise WRFDataRepositoryError("No elevations found in dataset.")

        # Make sure requested fields are valid, and that dataset contains the requested data.
        if not self.allow_subset and not (set(raw_data.keys()).issuperset(input_source_types)):
            raise WRFDataRepositoryError("Could not find all data fields")
        if {"x_wind", "y_wind"}.issubset(raw_data):
            x_wind, _ = raw_data.pop("x_wind")
            y_wind, _ = raw_data.pop("y_wind")
            raw_data["wind_speed"] = np.sqrt(np.square(x_wind) + np.square(y_wind)), "wind_speed"
        if {"temperature", "pressure", "mixing_ratio"}.issubset(raw_data):
            pressure, _ = raw_data.pop("pressure")
            mixing_ratio, _ = raw_data.pop("mixing_ratio")
            if "temperature" in input_source_types_orig:
                temperature, _ = raw_data["temperature"]  # Temperature input requested
            else:
                temperature, _ = raw_data.pop("temperature")  # Temperature only needed for relhum calculation
            raw_data["relative_humidity"] = self._calculate_rel_hum(temperature, pressure,
                                                                    mixing_ratio), "relative_humidity_2m"
        extracted_data = self._transform_raw(raw_data, time[time_slice], issubset=issubset)
        return _numpy_to_geo_ts_vec(extracted_data, x, y, z, WRFDataRepositoryError)

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
            return T - 273.16  # definition says -273.15, but regression test says -273.16..

        def prec_conv(p):
            # return p[1:]
            return p

        # def prec_acc_conv(p):
        #    return np.clip(p[1:] - p[:-1], 0.0, 1000.0)

        def rad_conv(r):
            # dr = r[1:] - r[:-1]
            # return np.clip(dr/(time[1] - time[0]), 0.0, 5000.0)
            return r

        convert_map = {"wind_speed": lambda x, t: (noop_space(x), noop_time(t)),
                       "relative_humidity_2m": lambda x, t: (noop_space(x), noop_time(t)),
                       "T2": lambda x, t: (air_temp_conv(x), noop_time(t)),
                       "SWDOWN": lambda x, t: (rad_conv(x), noop_time(t)),
                       "PREC_ACC_NC": lambda x, t: (prec_conv(x), noop_time(t))}
        # "precipitation_amount_acc": lambda x, t: (prec_acc_conv(x), dacc_time(t))}
        res = {}
        for k, (v, ak) in data.items():
            res[k] = convert_map[ak](v, time)
        return res
