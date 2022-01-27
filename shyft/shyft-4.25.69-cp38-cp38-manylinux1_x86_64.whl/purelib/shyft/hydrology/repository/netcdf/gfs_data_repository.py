# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
import numpy as np
from netCDF4 import Dataset
from ....time_series import (Calendar, TimeAxis)
from .. import interfaces
from .utils import _slice_var_2D, _limit_2D, _make_time_slice, _numpy_to_geo_ts_vec


class GFSDataRepositoryError(Exception):
    pass


class GFSDataRepository(interfaces.GeoTsRepository):
    """
    Repository for geo located time series given as GFS data in an OpenDAP
    server.

    Hydrologic data:
    $ hyd_ds = Dataset("http://nomads.ncep.noaa.gov:9090/dods/gens/gens20151015/gec00_00z")
    Shoud work, but does not:
    alt_ds = Dataset("http://cwcgom.aoml.noaa.gov/erddap/griddap/etopo360")

    ETOPO1 Spatial Reference System:
    urn:ogc:def:crs:EPSG::4326 urn:ogc:def:crs:EPSG::5715
    I interpret this as EPSG::4326 on land, and EPSG::5715 for sea depths.


    # This is ok:
    res = urllib2.urlopen("http://cwcgom.aoml.noaa.gov/erddap/griddap/etopo180.nc?altitude[(57):1:(71.5)][(3):1:(32)]")
    tf = open("etopo180.nc", "wb")
    tf.write(res.read())
    tf.close()
    alt_ds2 = Dataset("etopo180.nc")

    For data specification, see: http://nomads.ncdc.noaa.gov/thredds

    Specifically, we assume the following the the data set:
        * Root group has variables:
            * tmp2m: float32 array of dims (ens, time, lat, long) and units K (temperature)
            * pratesfc: float32 array of dims (ens, time, lat, long) and units kg m-2 (precip)
            *
    """

    # Constants to convert from days since 1.1.1:0:0:0 to secs since epoch
    __time_a = 3600*24.0  # utc = (t_gfs - self.time_b)*self.time_a
    __time_b = 719164.0

    def __init__(self, epsg, dem_file, padding=5000., utc=None):
        self.shyft_cs = "+init=EPSG:{}".format(epsg)
        self.dem_file = dem_file
        self.ensemble_idx = 0
        self.base_url = "http://nomads.ncep.noaa.gov:9090/dods/gens"
        if utc is not None:
            ens = 0  # Choose zero ensemble by default
            cal = Calendar()
            ymd = cal.calendar_units(utc)
            self.gfs_url = "{}/gens{:04d}{:02d}{:02d}/gec{:02d}_{:02d}z".format(self.base_url,
                                                                                ymd.year,
                                                                                ymd.month,
                                                                                ymd.day,
                                                                                ens,
                                                                                ymd.hour//6*6)
        else:
            self.gfs_url = None
        self._padding = padding
        self._gfs_shyft_map = {"ugrd10m": "x_wind",
                               "vgrd10m": "y_wind",
                               "tmp2m": "temperature",
                               "pratesfc": "precipitation",
                               "rh2m": "relative_humidity",
                               "dswrfsfc": "radiation"}

    def get_timeseries(self, input_source_types, utc_period, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        if self.gfs_url is None:
            raise GFSDataRepositoryError("Repository not initialized properly "
                                         "to call get_timeseries directly.")

        with Dataset(self.gfs_url) as dataset:
            return self._get_ensemble_data_from_dataset(dataset, input_source_types,
                                                        utc_period, geo_location_criteria)

    def _get_ensemble_data_from_dataset(self, dataset, input_source_types,
                                        utc_period, geo_location_criteria):
        if "wind_speed" in input_source_types:
            input_source_types = list(input_source_types)  # Copy the possible mutable input list
            input_source_types.remove("wind_speed")
            input_source_types.extend(["x_wind", "y_wind"])

        raw_data = {}
        lon = dataset.variables.get("lon", None)
        lat = dataset.variables.get("lat", None)
        time = dataset.variables.get("time", None)
        data_cs = "+init=EPSG:4326"  # WGS84
        if not all([lon, lat, time]):
            raise GFSDataRepositoryError("Something is wrong with the dataset."
                                         " lat/lon coords or time not found.")
        time = self.ad_to_utc(time)  # Fetch all times
        time_slice, _ = _make_time_slice(time, utc_period, GFSDataRepositoryError)
        clip_in_data_cs = True  # was false, caused problem in _limit_2D

        x, y, (x_inds, y_inds), (x_slice, y_slice) = _limit_2D(
            lon[:], lat[:], data_cs, self.shyft_cs, geo_location_criteria, self._padding, GFSDataRepositoryError,
            clip_in_data_cs=clip_in_data_cs)

        for k in dataset.variables.keys():
            if self._gfs_shyft_map.get(k, None) in input_source_types:
                data = dataset.variables[k]
                raw_data[self._gfs_shyft_map[k]] = _slice_var_2D(data, lon.name, lat.name, x_slice, y_slice, x_inds,
                                                                 y_inds, GFSDataRepositoryError,
                                                                 slices={'time': time_slice, 'ens': self.ensemble_idx})
        with Dataset(self.dem_file) as dataset:
            alts_v = dataset.variables["altitude"]
            lats_v = dataset.variables["latitude"]
            longs_v = dataset.variables["longitude"]
            lats = dataset.variables["latitude"][:]
            longs = dataset.variables["longitude"][:]
            # alts = alts_v[np.round(lats) == lats, np.round(longs) == longs]
            lats = lats[np.round(lats) == lats]
            longs = longs[np.round(longs) == longs]
            _x, _y, (x_inds, y_inds), (x_slice, y_slice) = _limit_2D(
                longs[:], lats[:], data_cs, self.shyft_cs, geo_location_criteria, self._padding, GFSDataRepositoryError,
                clip_in_data_cs=clip_in_data_cs)
            z = _slice_var_2D(alts_v, longs_v.name, lats_v.name, x_slice, y_slice, x_inds, y_inds, GFSDataRepositoryError)
            if not (np.linalg.norm(x - _x) < 1.0e-10 and np.linalg.norm(y - _y) < 1.0e-10):
                raise RuntimeError('x/y coordinates must match')
            # pts = np.dstack((x, y, z)).reshape(*(x.shape + (3,)))
        if set(("x_wind", "y_wind")).issubset(raw_data):
            x_wind = raw_data.pop("x_wind")
            y_wind = raw_data.pop("y_wind")
            raw_data["wind_speed"] = np.sqrt(np.square(x_wind) + np.square(y_wind))
        return _numpy_to_geo_ts_vec(self._transform_raw(raw_data, time[time_slice]), x, y, z, GFSDataRepositoryError)

    def get_forecast(self, input_source_types, utc_period, t_c, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        ens = 0  # Choose zero ensemble by default
        cal = Calendar()
        ymd = cal.calendar_units(t_c)
        self.gfs_url = "{}/gens{:04d}{:02d}{:02d}/gec{:02d}_{:02d}z".format(self.base_url,
                                                                            ymd.year,
                                                                            ymd.month,
                                                                            ymd.day,
                                                                            ens,
                                                                            ymd.hour//6*6)
        return self.get_timeseries(input_source_types, utc_period, geo_location_criteria)

    def get_forecast_ensemble(self, input_source_types, utc_period,
                              t_c, geo_location_criteria=None):
        """
        see shyft.repository.interfaces.GeoTsRepository
        """
        cal = Calendar()
        ymd = cal.calendar_units(t_c)
        res = []
        gfs_url = ("{}/gens{:04d}{:02d}"
                   "{:02d}/gep_all_{:02d}z".format(self.base_url,
                                                   ymd.year,
                                                   ymd.month,
                                                   ymd.day,
                                                   ymd.hour//6*6))
        with Dataset(gfs_url) as dataset:
            for ens in range(21):
                self.ensemble_idx = ens
                res.append(self._get_ensemble_data_from_dataset(dataset, input_source_types, utc_period, geo_location_criteria))
        return res

    def _transform_raw(self, data, time):

        def noop_space(x):
            return x

        def air_temp_conv(x):
            return x - 273.15

        def prec_conv(x):
            return x*3600

        convert_map = {"wind_speed": lambda x, ta: (noop_space(x), ta),
                       "radiation": lambda x, ta: (noop_space(x), ta),
                       "temperature": lambda x, ta: (air_temp_conv(x), ta),
                       "precipitation": lambda x, ta: (prec_conv(x), ta),
                       "relative_humidity": lambda x, ta: (noop_space(x), ta)}

        ta = TimeAxis(int(time[0]), int(time[1] - time[0]), len(time))
        res = {}
        for k, v in data.items():
            res[k] = convert_map[k](v, ta)
        return res

    @classmethod
    def ad_to_utc(cls, T):
        return np.array((np.asarray(T) - cls.__time_b)*cls.__time_a, dtype='int')


if __name__ == "__main__":
    utcs = GFSDataRepository.ad_to_utc([719164, 735887.0])
    cal = Calendar()
    print([cal.to_string(utc) for utc in utcs])
