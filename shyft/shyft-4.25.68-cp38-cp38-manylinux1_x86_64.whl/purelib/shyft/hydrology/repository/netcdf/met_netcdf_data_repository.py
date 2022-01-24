# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from builtins import range
import os
import numpy as np
from netCDF4 import Dataset
from ....time_series import (Calendar, TimeAxis, UtcTimeVector)
from .. import interfaces
from .time_conversion import convert_netcdf_time
from .utils import (calc_P, calc_RH, _slice_var_2D, _limit_2D, _make_time_slice, _numpy_to_geo_ts_vec, _get_files, utm_proj)

UTC = Calendar()


class MetNetcdfDataRepositoryError(Exception):
    pass


class MetNetcdfDataRepository(interfaces.GeoTsRepository):
    """
    Repository for geo located timeseries given as Arome(*) or EC(**) data in
    netCDF files.

    NetCDF dataset assumptions:
        * Root group has variables:
            * time: timestamp (int) array with seconds since epoc
                    (1970.01.01 00:00, UTC) for each data point
            * x: float array of latitudes
            * y: float array of longitudes
        * Root group has subset of variables:
            * relative_humidity_2m: float array of dims (time, 1, y, x)
            * air_temperature_2m: float array of dims (time, 1, y, x)
            * altitude: float array of dims (y, x)
            * precipitation_amount: float array of dims (time, y, x)
            * x_wind_10m: float array of dims (time, y, x)
            * y_wind_10m: float array of dims (time, y, x)
            * integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time:
              float array of dims (time, 1, y, x)
            * All variables are assumed to have the attribute grid_mapping
              which should be a reference to a variable in the root group
              that has an attribute named proj4. Example code:
                ds = netCDF4.Dataset(arome_file)
                var = "precipitation_amount"
                mapping = ds.variables[var].grid_mapping
                proj = ds.variables[mapping].proj4


    (*) Arome NWP model output is from:
        http://thredds.met.no/thredds/catalog/meps25files/catalog.html
    (**) EC model output is from:
        https://thredds.met.no/thredds/catalog/ecmwf/atmo/catalog.html
        Contact:
            Name: met.no
            Organization: met.no
            Email: thredds@met.no
            Phone: +47 22 96 30 00

    """

    _G = 9.80665  # WMO-defined gravity constant to calculate the height in metres from geopotential

    def __init__(self, epsg, directory, filename=None, ensemble_member=0,
                 padding=5000., elevation_file=None, allow_subset=False):
        """
        Construct the netCDF4 dataset reader for data from Arome or EC NWP model,
        and initialize data retrieval.

        Parameters
        ----------
        epsg: string
            Unique utm-coordinate system id for result coordinates.
        directory: string
            Path to directory holding one or possibly more arome data files.
            os.path.isdir(directory) should be true, or exception is raised.
        filename: string, optional
            Name of netcdf file in directory that contains spatially
            distributed input data. Can be a regex pattern as well, in case
            it is used for forecasts or ensambles.
        padding: float, optional
            padding in meters
        elevation_file: string, optional
            Name of netcdf file of same dimensions in x and y, subject to
            constraints given by bounding box and padding, that contains
            elevation that should be used in stead of elevations in file.
        allow_subset: bool
            Allow extraction of a subset of the given source fields
            instead of raising exception.
        """
        # directory = directory.replace('${SHYFTDATA}', os.getenv('SHYFTDATA', '.'))
        self.ensemble_member = ensemble_member
        self._directory = directory
        if directory is not None:
            self._directory = os.path.expandvars(directory)
        else:
            filename = os.path.expandvars(filename)
        self._filename = filename
        if filename is None:
            self._filename = r"(\d{4})(\d{2})(\d{2})[T_](\d{2})Z?.nc$"
        self.allow_subset = allow_subset
        if not os.path.isfile(filename):
            if not os.path.isdir(self._directory):
                raise MetNetcdfDataRepositoryError("No such directory '{}'".format(self._directory))

        if elevation_file is not None:
            self.elevation_file = os.path.join(self._directory, elevation_file)
            if not os.path.isfile(self.elevation_file):
                raise MetNetcdfDataRepositoryError(
                    "Elevation file '{}' not found".format(self.elevation_file))
        else:
            self.elevation_file = None

        self.shyft_cs = "+init=EPSG:{}".format(epsg)
        if not utm_proj(self.shyft_cs):
            raise MetNetcdfDataRepositoryError(f"Coordinate system EPSG:{epsg} is not UTM-type")
        self._padding = padding

        # Field names and mappings
        self._arome_shyft_map = {
            'dew_point_temperature_2m': 'dew_point_temperature_2m',
            'surface_air_pressure': 'surface_air_pressure',
            'sea_level_pressure': 'sea_level_pressure',
            "relative_humidity_2m": "relative_humidity",
            "air_temperature_2m": "temperature",
            # "altitude": "z",
            "precipitation_amount": "precipitation",
            "precipitation_amount_acc": "precipitation",
            "x_wind_10m": "x_wind",
            "y_wind_10m": "y_wind",
            "integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time": "radiation"}

        self.var_units = {"air_temperature_2m": ['K'],
                          "relative_humidity_2m": ['1'],
                          "precipitation_amount_acc": ['kg/m^2', 'Mg/m^2', 'm', 'mm'],
                          "precipitation_amount": ['kg/m^2', 'Mg/m^2', 'm', 'mm'],
                          "x_wind_10m": ['m/s'],
                          "y_wind_10m": ['m/s'],
                          "integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time": ['W s/m^2'],
                          'dew_point_temperature_2m': ['K'],
                          'surface_air_pressure': ['Pa'],
                          'sea_level_pressure': ['Pa'],
                          }

        self._shift_fields = ("precipitation_amount", "precipitation_amount_acc",
                              "integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time")

    def get_timeseries(self, input_source_types, utc_period, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        if self._directory is not None:
            filename = os.path.join(self._directory, self._filename)
        else:
            filename = self._filename
        if not os.path.isfile(filename):
            raise MetNetcdfDataRepositoryError("File '{}' not found".format(filename))
        with Dataset(filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types,
                                               utc_period, geo_location_criteria, ensemble_member=self.ensemble_member)

    def get_timeseries_ensemble(self, input_source_types, utc_period, geo_location_criteria=None):
        """
        Parameters
        ----------
        see interfaces.GeoTsRepository

        Returns
        -------
        see interfaces.GeoTsRepository
        """
        if self._directory is not None:
            filename = os.path.join(self._directory, self._filename)
        else:
            filename = self._filename
        if not os.path.isfile(filename):
            raise MetNetcdfDataRepositoryError("File '{}' not found".format(filename))
        with Dataset(filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types,
                                               utc_period, geo_location_criteria)

    def get_forecast(self, input_source_types, utc_period, t_c, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        filename = _get_files(self._directory, self._filename, t_c, MetNetcdfDataRepositoryError)
        with Dataset(filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types, utc_period,
                                               geo_location_criteria, ensemble_member=self.ensemble_member)

    def get_forecast_ensemble(self, input_source_types, utc_period,
                              t_c, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        filename = _get_files(self._directory, self._filename, t_c, MetNetcdfDataRepositoryError)
        with Dataset(filename) as dataset:
            return self._get_data_from_dataset(dataset, input_source_types, utc_period,
                                               geo_location_criteria, ensemble_member=None)

    def _check_and_get_coord_vars(self, dataset, var_types):
        cs = []
        coord_names = []
        for k, v in self._arome_shyft_map.items():
            if v in var_types and k in dataset.variables:
                cs.append(dataset.variables[k].getncattr('grid_mapping'))
                coord_names.append([d for d in dataset.variables[k].dimensions if d in ['time', 'x', 'y', 'latitude', 'longitude']])
        if not all(elem == cs[0] for elem in cs):
            MetNetcdfDataRepositoryError('Requested vars have different coord_sys. Do index extraction per var.')
        if not all(elem == coord_names[0] for elem in coord_names):
            MetNetcdfDataRepositoryError('Requested vars have different coords. Do index extraction per var.')
        time = dataset.variables.get("time", None)
        if not time:
            raise MetNetcdfDataRepositoryError("Time variable not found in dataset.")
        time = convert_netcdf_time(time.units, time)

        if 'y' in coord_names[0]:
            x = dataset.variables.get("x", None)
            y = dataset.variables.get("y", None)
        elif 'latitude' in coord_names[0]:
            x = dataset.variables.get("longitude", None)
            y = dataset.variables.get("latitude", None)
        else:
            MetNetcdfDataRepositoryError('No recognized coordinate dimension names found.')

        if not all([x, y]):
            raise MetNetcdfDataRepositoryError("Spatial Coordinate variables not found in dataset.")
        if 'y' in coord_names[0]:
            if not all([var.units in ['km', 'm'] for var in [x, y]]) and x.units == y.units:
                raise MetNetcdfDataRepositoryError("The unit for x and y coordinates should be either m or km.")
        else:
            if not (y.units == 'degrees_north' and x.units == 'degrees_east'):
                raise MetNetcdfDataRepositoryError("The unit for latitude and longitude coordinates should be "
                                                   "'degrees_north' and 'degrees_east' repectively.")
        coord_conv = 1.
        if y.units == 'km':
            coord_conv = 1000.

        data_cs = dataset.variables.get(cs[0], None)
        if data_cs is None:
            raise MetNetcdfDataRepositoryError("No coordinate system information in dataset.")
        return time, x, y, data_cs, coord_conv

    def _get_data_from_dataset(self, dataset, input_source_types, utc_period,
                               geo_location_criteria, ensemble_member=None):

        if "wind_speed" in input_source_types:
            input_source_types = list(input_source_types)  # We change input list, so take a copy
            input_source_types.remove("wind_speed")
            input_source_types.append("x_wind")
            input_source_types.append("y_wind")

        no_temp = False
        if "temperature" not in input_source_types: no_temp = True
        # To handel the empty relative_humidity_2m variable included in netcdf files created from ecmwf data flow
        # if "relative_humidity_2m" in dataset.variables:
        #     rh = dataset.variables['relative_humidity_2m'][:]
        #     ecmwf_fetching_error = isinstance(rh, np.ma.core.MaskedArray)
        # else:
        #     ecmwf_fetching_error = False
        # if "relative_humidity" in input_source_types and ("relative_humidity_2m" not in dataset.variables or ecmwf_fetching_error):

        # estimate from surface_air_preasure...
        if "relative_humidity" in input_source_types and all([var in dataset.variables for var in ["surface_air_pressure", "dew_point_temperature_2m"]]):
            if not isinstance(input_source_types, list):
                input_source_types = list(input_source_types)  # We change input list, so take a copy
            input_source_types.remove("relative_humidity")
            input_source_types.extend(["surface_air_pressure", "dew_point_temperature_2m"])
            if no_temp: input_source_types.extend(["temperature"])
        # ...or from sea_level_preasure
        if "relative_humidity" in input_source_types and all([var in dataset.variables for var in ["sea_level_pressure", "dew_point_temperature_2m"]]):
            if not isinstance(input_source_types, list):
                input_source_types = list(input_source_types)  # We change input list, so take a copy
            input_source_types.remove("relative_humidity")
            input_source_types.extend(["sea_level_pressure", "dew_point_temperature_2m"])
            if no_temp: input_source_types.extend(["temperature"])

        # Check for presence and consistency of coordinate variables
        time, x_var, y_var, data_cs, coord_conv = self._check_and_get_coord_vars(dataset, input_source_types)
        # Check units of meteorological variables
        unit_ok = {k: dataset.variables[k].units in self.var_units[k]
                   for k in dataset.variables.keys() if self._arome_shyft_map.get(k, None) in input_source_types}
        if not all(unit_ok.values()):
            raise MetNetcdfDataRepositoryError("The following variables have wrong unit: {}.".format(
                ', '.join([k for k, v in unit_ok.items() if not v])))
        # Make temporal slilce
        time_slice, issubset = _make_time_slice(time, utc_period, MetNetcdfDataRepositoryError)
        # Make spatial slice
        x, y, (x_inds, y_inds), (x_slice, y_slice) = _limit_2D(x_var[:]*coord_conv, y_var[:]*coord_conv,
                                                               data_cs.proj4, self.shyft_cs, geo_location_criteria,
                                                               self._padding, MetNetcdfDataRepositoryError)
        raw_data = {}
        for k in dataset.variables.keys():
            if self._arome_shyft_map.get(k, None) in input_source_types:
                # if k in self._shift_fields and issubset:  # Add one to time slice
                #     data_time_slice = slice(time_slice.start, time_slice.stop + 1)  # to supply the extra value that is needed for accumulated variables
                # else:
                #     data_time_slice = time_slice
                data = dataset.variables[k]
                pure_arr = _slice_var_2D(data, x_var.name, y_var.name, x_slice, y_slice, x_inds,
                                         y_inds, MetNetcdfDataRepositoryError,
                                         # slices={'time': data_time_slice, 'ensemble_member': ensemble_member})
                                         slices={'time': time_slice, 'ensemble_member': ensemble_member})
                raw_data[self._arome_shyft_map[k]] = pure_arr, k, data.units

        if self.elevation_file is not None:
            _x, _y, z = self._read_elevation_file(self.elevation_file, x_var.name, y_var.name, geo_location_criteria)
            if not (np.linalg.norm(x - _x) < 1.0e-10 and np.linalg.norm(y - _y) < 1.0e-10):
                raise RuntimeError('x/y coordinates must match')
        elif any([nm in dataset.variables.keys() for nm in ['altitude', 'surface_geopotential']]):
            var_nm = ['altitude', 'surface_geopotential'][[nm in dataset.variables.keys() for nm in ['altitude', 'surface_geopotential']].index(True)]
            z_data = dataset.variables[var_nm]
            z = _slice_var_2D(z_data, x_var.name, y_var.name, x_slice, y_slice, x_inds, y_inds, MetNetcdfDataRepositoryError)
            if var_nm == 'surface_geopotential':
                z /= self._G
        else:
            raise MetNetcdfDataRepositoryError("No elevations found in dataset"
                                               ", and no elevation file given.")

        # Make sure requested fields are valid, and that dataset contains the requested data.
        if not self.allow_subset and not (set(raw_data.keys()).issuperset(input_source_types)):
            raise MetNetcdfDataRepositoryError("Could not find all data fields")

        if set(("x_wind", "y_wind")).issubset(raw_data):
            x_wind = raw_data.pop("x_wind")[0]
            y_wind = raw_data.pop("y_wind")[0]
            raw_data["wind_speed"] = np.sqrt(np.square(x_wind) + np.square(y_wind)), "wind_speed", 'm/s'
        if set(("surface_air_pressure", "dew_point_temperature_2m")).issubset(raw_data):
            sfc_p = raw_data.pop("surface_air_pressure")[0]
            dpt_t = raw_data.pop("dew_point_temperature_2m")[0]
            if no_temp:
                sfc_t = raw_data.pop("temperature")[0]
            else:
                sfc_t = raw_data["temperature"][0]
            raw_data["relative_humidity"] = calc_RH(sfc_t, dpt_t, sfc_p), "relative_humidity_2m", '1'
        if set(("sea_level_pressure", "dew_point_temperature_2m")).issubset(raw_data):
            sea_p = raw_data.pop("sea_level_pressure")[0]
            dpt_t = raw_data.pop("dew_point_temperature_2m")[0]
            if no_temp:
                sfc_t = raw_data.pop("temperature")[0]
            else:
                sfc_t = raw_data["temperature"][0]
            raw_data["relative_humidity"] = calc_RH(sfc_t, dpt_t, calc_P(z, sea_p)), "relative_humidity_2m", '1'
        # print(data.dimensions)
        # time_slice = slice(time_slice.start, time_slice.stop + 1)  # to supply the extra time that is needed for accumulated variables
        if ensemble_member is None and 'ensemble_member' in data.dimensions:
            dims_flat = [d for d in data.dimensions if d in ['time', 'ensemble_member', x_var.name]]
            ens_dim_idx = dims_flat.index('ensemble_member')
            ens_slice = len(dims_flat)*[slice(None)]
            returned_data = []
            for i in range(dataset.dimensions['ensemble_member'].size):
                ens_slice[ens_dim_idx] = i
                # print([(k, raw_data[k][0].shape) for k in raw_data])
                ensemble_raw = {k: (raw_data[k][0][ens_slice], raw_data[k][1], raw_data[k][2]) for k in raw_data.keys()}
                # print([(k,ensemble_raw[k][0].shape) for k in ensemble_raw])
                returned_data.append(_numpy_to_geo_ts_vec(self._transform_raw(ensemble_raw, time[time_slice]),  # , issubset=issubset)
                                                          x, y, z, MetNetcdfDataRepositoryError))
        else:
            returned_data = _numpy_to_geo_ts_vec(self._transform_raw(raw_data, time[time_slice]),  # , issubset=issubset),
                                                 x, y, z, MetNetcdfDataRepositoryError)
        return returned_data

    def _read_elevation_file(self, filename, x_var_name, y_var_name, geo_location_criteria):
        with Dataset(filename) as dataset:
            elev = dataset.variables["altitude"]
            if "altitude" not in dataset.variables.keys():
                raise interfaces.InterfaceError(
                    "File '{}' does not contain altitudes".format(filename))
            x, y, (x_inds, y_inds), (x_slice, y_slice) = _limit_2D(dataset.variables[x_var_name][:], dataset.variables[y_var_name][:],
                                                                   dataset.variables[elev.grid_mapping].proj4, self.shyft_cs, geo_location_criteria,
                                                                   self._padding, MetNetcdfDataRepositoryError)
            z = _slice_var_2D(elev, x_var_name, y_var_name, x_slice, y_slice, x_inds, y_inds, MetNetcdfDataRepositoryError)
            return x, y, z

    def _transform_raw(self, data, time):  # , issubset=False):
        """
        We need full time if deaccumulating
        """

        def noop_time(t):
            # if issubset:
            #     t = t[:-1]
            dt_last = int(t[-1] - t[-2])
            if np.all(t[1:] - t[:-1] == dt_last):  # fixed_dt time axis
                return TimeAxis(int(t[0]), dt_last, len(t))
            else:  # point_type time axis
                return TimeAxis(UtcTimeVector.from_numpy(t.astype(int)), int(t[-1] + dt_last))

        def dacc_time(t):
            dt_last = int(t[-1] - t[-2])
            if np.all(t[1:] - t[:-1] == dt_last):  # fixed_dt time axis
                return TimeAxis(int(t[0]), dt_last, len(t) - 1)
            else:
                return TimeAxis(UtcTimeVector.from_numpy(t[:-1].astype(int)), int(t[-1]))

        def noop_space(x):
            return x

        def air_temp_conv(T):  # from kelvin to degree_celcius
            return T - 273.15

        def prec_conv(p, unit):
            factor = 1.
            if unit in ['Mg/m^2', 'm']:  # from m (Mg/m2) to mm (kg/m2)
                factor = 1000.
            return factor*p[1:]

        def prec_acc_conv(p, t, unit):
            factor = 1.
            if unit in ['Mg/m^2', 'm']:  # from m (Mg/m2) to mm (kg/m2) and from mm/delta_t to mm/1hour
                factor = 1000.
            f = factor*3600./(t[1:] - t[:-1])  # assume t is in units of second
            return np.clip((p[1:, :] - p[:-1, :])*f[:, np.newaxis], 0.0, 1000.0)

        def rad_acc_conv(r, t):  # from W s/m2 to W/m2
            return np.clip((r[1:, :] - r[:-1, :])/(t[1:] - t[:-1])[:, np.newaxis], 0.0, 5000.0)

        convert_map = {"wind_speed": lambda x, t, u: (noop_space(x), noop_time(t)),
                       "relative_humidity_2m": lambda x, t, u: (noop_space(x), noop_time(t)),
                       "air_temperature_2m": lambda x, t, u: (air_temp_conv(x), noop_time(t)),
                       "integral_of_surface_downwelling_shortwave_flux_in_air_wrt_time":
                           lambda x, t, u: (rad_acc_conv(x, t), dacc_time(t)),
                       "precipitation_amount": lambda x, t, u: (prec_conv(x, u), dacc_time(t)),
                       "precipitation_amount_acc": lambda x, t, u: (prec_acc_conv(x, t, u), dacc_time(t))}

        return {k: convert_map[ak](v, time, unit) for k, (v, ak, unit) in data.items()}
