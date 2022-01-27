# This file is part of Shyft. Copyright 2015-2018 SiH, JFB, OS, YAS, Statkraft AS
# See file COPYING for more details **/
from typing import List,Dict
import os
import re
import numpy as np
import pyproj
from netCDF4 import Dataset
from shapely.ops import transform
from shapely.prepared import prep
from functools import partial
from shapely.geometry import MultiPoint, Polygon, MultiPolygon
from ....time_series import (TimeAxis,Calendar, DoubleVector, UtcPeriod, POINT_INSTANT_VALUE, POINT_AVERAGE_VALUE)
# from shyft import api
from ... import (
    RelHumSource, TemperatureSource, WindSpeedSource, RadiationSource, PrecipitationSource,
    GeoPointVector, RelHumSourceVector, TemperatureSourceVector, WindSpeedSourceVector, RadiationSourceVector, PrecipitationSourceVector,
    create_rel_hum_source_vector_from_np_array,
    create_temperature_source_vector_from_np_array,
    create_precipitation_source_vector_from_np_array,
    create_radiation_source_vector_from_np_array,
    create_wind_speed_source_vector_from_np_array
)


def fixup_init(proj_string: str, pyproj_version: str) -> str:
    if pyproj_version < '2.0.0':
        if proj_string.startswith('EPSG:'):  # add +init
            proj_string = f'+init={proj_string}'
    else:  # get rid of init (deprecated)
        if proj_string.startswith('+init='):
            proj_string = proj_string.replace('+init=', '')
    return proj_string


def make_proj(proj_string: str) -> pyproj.Proj:
    """ breaking changes before/after 2.0, we are not to use +init on latest pyproj versions """
    return pyproj.Proj(fixup_init(proj_string, pyproj.__version__))


def utm_proj(proj_string: str) -> bool:
    """ :return true if proj_string is utm"""
    return "proj=utm" in make_proj(proj_string).definition_string()


UTC = Calendar()

source_type_map = {"relative_humidity": RelHumSource,
                   "temperature": TemperatureSource,
                   "precipitation": PrecipitationSource,
                   "radiation": RadiationSource,
                   "wind_speed": WindSpeedSource,
                   "wind_speed_100m": WindSpeedSource,
                   "x_wind_10m": WindSpeedSource,
                   "y_wind_10m": WindSpeedSource,
                   "x_wind_100m": WindSpeedSource,
                   "y_wind_100m": WindSpeedSource
                   }

source_vector_map = {"relative_humidity": RelHumSourceVector,
                     "temperature": TemperatureSourceVector,
                     "precipitation": PrecipitationSourceVector,
                     "radiation": RadiationSourceVector,
                     "wind_speed": WindSpeedSourceVector,
                     "wind_speed_100m": WindSpeedSourceVector,
                     "x_wind_10m": WindSpeedSourceVector,
                     "y_wind_10m": WindSpeedSourceVector,
                     "x_wind_100m": WindSpeedSourceVector,
                     "y_wind_100m": WindSpeedSourceVector
                     }

series_type = {"relative_humidity": POINT_INSTANT_VALUE,
               "temperature": POINT_INSTANT_VALUE,
               "precipitation": POINT_AVERAGE_VALUE,
               "radiation": POINT_AVERAGE_VALUE,
               "wind_speed": POINT_INSTANT_VALUE,
               "wind_speed_100m": POINT_INSTANT_VALUE,
               "x_wind_10m": POINT_INSTANT_VALUE,
               "y_wind_10m": POINT_INSTANT_VALUE,
               "x_wind_100m": POINT_INSTANT_VALUE,
               "y_wind_100m": POINT_INSTANT_VALUE}

create_geo_ts_type_map = {"relative_humidity": create_rel_hum_source_vector_from_np_array,
                          "temperature": create_temperature_source_vector_from_np_array,
                          "precipitation": create_precipitation_source_vector_from_np_array,
                          "radiation": create_radiation_source_vector_from_np_array,
                          "wind_speed": create_wind_speed_source_vector_from_np_array,
                          "wind_speed_100m": create_wind_speed_source_vector_from_np_array,
                          "x_wind_10m": create_wind_speed_source_vector_from_np_array,
                          "y_wind_10m": create_wind_speed_source_vector_from_np_array,
                          "x_wind_100m": create_wind_speed_source_vector_from_np_array,
                          "y_wind_100m": create_wind_speed_source_vector_from_np_array
                          }


def _numpy_to_geo_ts_vec(data:Dict[np.ndarray,List[TimeAxis]], x:np.ndarray, y:np.ndarray, z:np.ndarray, err):
    """
    Convert timeseries from numpy structures to shyft.hydrology geo-timeseries vector.
    Parameters
    ----------
    data: dict of tuples (np.ndarray, (list of)Time Axis)
        array with shape
        (nb_forecasts, nb_lead_times, nb_ensemble_members, nb_points) or
        (nb_lead_times, nb_ensemble_members, nb_points) or
        (nb_lead_times, nb_points)
        one time axis of size nb_lead_times for each forecast
    x: np.ndarray
        X coordinates in meters in cartesian coordinate system, with array shape = (nb_points)
    y: np.ndarray
        Y coordinates in meters in cartesian coordinate system, with array shape = (nb_points)
    z: np.ndarray
        elevation in meters, with array shape = (nb_points)
    Returns
    -------
    timeseries: dict
        Time series arrays keyed by type
    """
    geo_pts = GeoPointVector.create_from_x_y_z(*[DoubleVector.from_numpy(arr) for arr in [x, y, z]])
    shape = list(data.values())[0][0].shape
    ndim = len(shape)
    if ndim == 4:
        nb_forecasts = shape[0]
        nb_ensemble_members = shape[2]
        geo_ts = [[{key: create_geo_ts_type_map[key](ta[i], geo_pts, arr[i, :, j, :].transpose(), series_type[key])
                    for key, (arr, ta) in data.items()}
                   for j in range(nb_ensemble_members)] for i in range(nb_forecasts)]
    elif ndim == 3:
        nb_ensemble_members = shape[1]
        geo_ts = [{key: create_geo_ts_type_map[key](ta, geo_pts, arr[:, j, :].transpose(), series_type[key])
                   for key, (arr, ta) in data.items()}
                  for j in range(nb_ensemble_members)]
    elif ndim == 2:
        geo_ts = {key: create_geo_ts_type_map[key](ta, geo_pts, arr[:, :].transpose(), series_type[key])
                  for key, (arr, ta) in data.items()}
    else:
        raise err("Number of dimensions, ndim, of Numpy array to be converted to shyft GeoTsVector not 2<=ndim<=4.")
    return geo_ts


def _validate_geo_location_criteria(geo_location_criteria, err):
    """
    Validate geo_location_criteria.
    """
    if geo_location_criteria is not None:
        if not isinstance(geo_location_criteria, (Polygon, MultiPolygon)):
            raise err("Unrecognized geo_location_criteria. "
                      "It should be one of these shapley objects: (Polygon, MultiPolygon).")


def _limit_2D(x, y, data_cs, target_cs, geo_location_criteria, padding, err, clip_in_data_cs=True):
    """
    Parameters
    ----------
    x: np.ndarray
        X coordinates in meters in cartesian coordinate system
        specified by data_cs
    y: np.ndarray
        Y coordinates in meters in cartesian coordinate system
        specified by data_cs
    data_cs: string
        Proj4 string specifying the cartesian coordinate system
        of x and y
    target_cs: string
        Proj4 string specifying the target coordinate system
    Returns
    -------
    x: np.ndarray
        Coordinates in target coordinate system
    y: np.ndarray
        Coordinates in target coordinate system
    x_mask: np.ndarray
        Boolean index array
    y_mask: np.ndarray
        Boolean index array
    """
    _validate_geo_location_criteria(geo_location_criteria, err)
    # Get coordinate system for arome data
    data_cs_ = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", data_cs)  # TODO: remove this workaround when Proj allows for +e=0  # TODO: remove this workaround when Proj allows for +e=0
    if data_cs.startswith('+'):
        data_proj = make_proj(data_cs_)
    else:
        data_proj = pyproj.Proj(proj=data_cs_)  # bw compat, should work pre&post 2.0
    target_cs_ = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", target_cs)  # TODO: remove this workaround when Proj allows for +e=0
    target_proj = make_proj(target_cs_)

    if x.shape != y.shape:
        err("x and y coords do not have the same dimensions.")
    if not (1 <= len(x.shape) <= 2):
        err("x and y coords should have one or two dimensions.")

    if len(x.shape) == 1:
        if geo_location_criteria is None:  # get all geo_pts in dataset
            x_mask = np.ones(np.size(x), dtype=bool)
            y_mask = np.ones(np.size(y), dtype=bool)
            x_indx = np.nonzero(x_mask)[0]
            y_indx = np.nonzero(y_mask)[0]
            xy_in_poly = np.dstack(np.meshgrid(x, y)).reshape(-1, 2)
            yi, xi = np.unravel_index(np.arange(len(xy_in_poly), dtype=int), (y_indx.shape[0], x_indx.shape[0]))
        else:
            poly = geo_location_criteria.buffer(padding)
            if clip_in_data_cs:
                # Find bounding polygon in data coordinate system
                project = partial(pyproj.transform, target_proj, data_proj)
                # poly = geo_location_criteria.buffer(padding)
                # poly_prj = transform(project, poly)
                poly = transform(project, poly)
                # p_poly = prep(poly_prj)
            else:
                # p_poly = prep(poly)
                x, y = pyproj.transform(data_proj, target_proj, x, y)

            p_poly = prep(poly)
            # Extract points in poly envelop
            xmin, ymin, xmax, ymax = poly.bounds
            x_mask = ((x > xmin) & (x < xmax))
            y_mask = ((y > ymin) & (y < ymax))
            x_indx = np.nonzero(x_mask)[0]
            y_indx = np.nonzero(y_mask)[0]
            x_in_box = x[x_indx]
            y_in_box = y[y_indx]
            xy_in_box = np.dstack(np.meshgrid(x_in_box, y_in_box)).reshape(-1, 2)
            if len(xy_in_box) == 0:
                raise err("No points in dataset which are within the bounding box of the geo_location_criteria polygon.")
            pts_in_box = MultiPoint(xy_in_box)
            pt_in_poly = np.array(list(map(p_poly.contains, pts_in_box)))
            # Create the index for the points in the buffer polygon
            yi, xi = np.unravel_index(np.nonzero(pt_in_poly)[0], (y_indx.shape[0], x_indx.shape[0]))
            xy_in_poly = xy_in_box[pt_in_poly]
            if len(xy_in_poly) == 0:
                raise err("No points in dataset which are within the geo_location_criteria polygon.")

        if clip_in_data_cs:
            # Transform from source coordinates to target coordinates
            x_in_poly, y_in_poly = pyproj.transform(data_proj, target_proj, xy_in_poly[:, 0],
                                                    xy_in_poly[:, 1])  # in Shyft coord sys
        else:
            x_in_poly, y_in_poly = xy_in_poly[:, 0], xy_in_poly[:, 1]

        return x_in_poly, y_in_poly, (xi, yi), (slice(x_indx[0], x_indx[-1] + 1), slice(y_indx[0], y_indx[-1] + 1))
    else:
        if geo_location_criteria is None:  # get all geo_pts in dataset
            x_mask = np.ones(np.size(x), dtype=bool)
            y_mask = np.ones(np.size(y), dtype=bool)
            x_indx = np.nonzero(x_mask)[0]
            y_indx = np.nonzero(y_mask)[0]
            xy_in_poly = np.dstack(np.meshgrid(x, y)).reshape(-1, 2)
            yi, xi = np.unravel_index(np.arange(len(xy_in_poly), dtype=int), (y_indx.shape[0], x_indx.shape[0]))
        else:
            poly = geo_location_criteria.buffer(padding)
            if clip_in_data_cs:
                # Find bounding polygon in data coordinate system
                project = partial(pyproj.transform, target_proj, data_proj)
                # poly = geo_location_criteria.buffer(padding)
                # poly_prj = transform(project, poly)
                poly = transform(project, poly)
                # p_poly = prep(poly_prj)
            else:
                # p_poly = prep(poly)
                x, y = pyproj.transform(data_proj, target_proj, x, y)

            p_poly = prep(poly)
            # Extract points in poly envelop
            xmin, ymin, xmax, ymax = poly.bounds
            # x_mask = ((x > xmin) & (x < xmax))
            # y_mask = ((y > ymin) & (y < ymax))
            # x_indx = np.nonzero(x_mask)[0]
            # y_indx = np.nonzero(y_mask)[0]
            # x_in_box = x[x_indx]
            # y_in_box = y[y_indx]
            # xy_in_box = np.dstack(np.meshgrid(x_in_box, y_in_box)).reshape(-1, 2)
            mask = ((x >= xmin) & (x <= xmax) & (y >= ymin) & (y <= ymax))
            a = np.argwhere(mask)
            (ystart, xstart), (ystop, xstop) = a.min(0), a.max(0) + 1
            xy_in_box = np.dstack((x, y))[ystart:ystop, xstart:xstop, :].reshape(-1, 2)
            if len(xy_in_box) == 0:
                raise err("No points in dataset which are within the bounding box of the geo_location_criteria polygon.")
            pts_in_box = MultiPoint(xy_in_box)
            pt_in_poly = np.array(list(map(p_poly.contains, pts_in_box)))
            # Create the index for the points in the buffer polygon
            # yi, xi = np.unravel_index(np.nonzero(pt_in_poly)[0], (y_indx.shape[0], x_indx.shape[0]))
            yi, xi = np.unravel_index(np.nonzero(pt_in_poly)[0], (ystop - ystart, xstop - xstart))
            xy_in_poly = xy_in_box[pt_in_poly]
            if len(xy_in_poly) == 0:
                raise err("No points in dataset which are within the geo_location_criteria polygon.")

        if clip_in_data_cs:
            # Transform from source coordinates to target coordinates
            x_in_poly, y_in_poly = pyproj.transform(data_proj, target_proj, xy_in_poly[:, 0],
                                                    xy_in_poly[:, 1])  # in Shyft coord sys
        else:
            x_in_poly, y_in_poly = xy_in_poly[:, 0], xy_in_poly[:, 1]

        return x_in_poly, y_in_poly, (xi, yi), (slice(xstart, xstop), slice(ystart, ystop))


def _limit_1D(x, y, data_cs, target_cs, geo_location_criteria, padding, err, clip_in_data_cs=True):
    """
    Project coordinates from data_cs to target_cs, identify points defined by geo_location_criteria as mask and find
    limiting slice

    Parameters
    ----------
    x: np.ndarray
        X coordinates in meters in cartesian coordinate system
        specified by data_cs
    y: np.ndarray
        Y coordinates in meters in cartesian coordinate system
        specified by data_cs
    data_cs: string
        Proj4 string specifying the cartesian coordinate system
        of x and y
    target_cs: string
        Proj4 string specifying the target coordinate system

    Returns
    -------
    xx: np.ndarray
        Coordinates in target coordinate system
    yy: np.ndarray
        Coordinates in target coordinate system
    xy_mask: np.ndarray
        Boolean index array
    """
    _validate_geo_location_criteria(geo_location_criteria, err)
    # Get coordinate system for netcdf data
    data_cs_ = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", data_cs)  # TODO: remove this workaround when Proj allows for +e=0
    if data_cs.startswith('+'):
        data_proj = make_proj(data_cs_)
    else:
        data_proj = pyproj.Proj(proj=data_cs_)
    target_cs_ = re.sub(r'\+e=[-+]?0*.?0+', "+e=1e-100", target_cs)  # TODO: remove this workaround when Proj allows for +e=0
    target_proj = make_proj(target_cs_)

    if geo_location_criteria is None:  # get all geo_pts in dataset
        xy_mask = np.ones(np.size(x), dtype=bool)
    else:
        poly = geo_location_criteria.buffer(padding)
        if clip_in_data_cs:
            # Find bounding polygon in data coordinate system
            project = partial(pyproj.transform, target_proj, data_proj)
            # poly = geo_location_criteria.buffer(padding)
            poly_prj = transform(project, poly)
            p_poly = prep(poly_prj)
        else:
            p_poly = prep(poly)
            x, y = pyproj.transform(data_proj, target_proj, x, y)

        pts_in_file = MultiPoint(np.dstack((x, y)).reshape(-1, 2))
        xy_mask = np.array(list(map(p_poly.contains, pts_in_file)))

    # Check if there is at least one point extaracted and raise error if there isn't
    if not xy_mask.any():
        raise err("No points in dataset which are within the geo_location_criteria polygon.")
    xy_inds = np.nonzero(xy_mask)[0]
    if clip_in_data_cs:
        # Transform from source coordinates to target coordinates
        xx, yy = pyproj.transform(data_proj, target_proj, x[xy_mask], y[xy_mask])
    else:
        xx, yy = x[xy_mask], y[xy_mask]
    return xx, yy, xy_mask, slice(xy_inds[0], xy_inds[-1] + 1)


def _make_time_slice(time, utc_period, err):
    if utc_period is None:
        # If period is None set period to be from start to end of dataset time dimension
        utc_period = UtcPeriod(int(time[0]), int(time[-1]))
    idx_min = np.argmin(time <= utc_period.start) - 1  # raise error if result is -1
    idx_max = np.argmax(time >= utc_period.end)  # raise error if result is 0
    if idx_min < 0:
        raise err(
            "The earliest time in repository ({}) is later than the start of the period for which data is "
            "requested ({})".format(UTC.to_string(int(time[0])), UTC.to_string(utc_period.start)))
    if idx_max == 0:
        raise err(
            "The latest time in repository ({}) is earlier than the end of the period for which data is "
            "requested ({})".format(UTC.to_string(int(time[-1])), UTC.to_string(utc_period.end)))

    issubset = True if idx_max < len(time) - 1 else False
    time_slice = slice(idx_min, idx_max + 1)
    return time_slice, issubset


def _slice_var_1D(nc_var, xy_var_name, xy_slice, xy_mask, slices={}):  # , time_slice=None, ensemble_member=None):
    dims = nc_var.dimensions
    data_slice = len(nc_var.dimensions)*[slice(None)]
    # if time_slice is not None and "time" in dims:
    #     data_slice[dims.index("time")] = time_slice
    # if ensemble_member is not None and "ensemble_member" in dims:
    #     data_slice[dims.index("ensemble_member")] = ensemble_member
    for k, v in slices.items():
        if k in dims and v is not None:
            data_slice[dims.index(k)] = v
    data_slice[dims.index(xy_var_name)] = xy_slice
    # data_slice[dims.index("time")] = time_slice  # data_time_slice
    xy_slice_mask = [xy_mask[xy_slice] if dim == xy_var_name else slice(None) for dim in dims]
    pure_arr = nc_var[data_slice][tuple(xy_slice_mask)]
    if isinstance(pure_arr, np.ma.core.MaskedArray):
        # print(pure_arr.fill_value)
        pure_arr = pure_arr.filled(np.nan)
    return pure_arr


def _slice_var_2D(nc_var, x_var_name, y_var_name, x_slice, y_slice, x_inds, y_inds, err, slices={}):  # , time_slice=None, ensemble_member=None):
    dims = nc_var.dimensions
    data_slice = len(nc_var.dimensions)*[slice(None)]
    # if time_slice is not None and "time" in dims:
    #     data_slice[dims.index("time")] = time_slice
    # if ensemble_member is not None and "ensemble_member" in dims:
    #     data_slice[dims.index("ensemble_member")] = ensemble_member
    for k, v in slices.items():
        if k in dims and v is not None:
            data_slice[dims.index(k)] = v
    # from the whole dataset, slice pts within the polygons's bounding box
    data_slice[dims.index(x_var_name)] = x_slice  # m_x
    data_slice[dims.index(y_var_name)] = y_slice  # m_y
    # from the points within the bounding box, slice pts within the polygon
    new_slice = len(nc_var.dimensions)*[slice(None)]
    new_slice[dims.index(x_var_name)] = x_inds
    new_slice[dims.index(y_var_name)] = y_inds
    new_slice = [s for i, s in enumerate(new_slice) if not isinstance(data_slice[i], int)]
    # identify the height dimension, which should have a length of 1 and set its slice to 0
    # hgt_dim_nm = [nm for nm in dims if nm not in ['time', 'ensemble_member', x_var_name, y_var_name]][0]
    dim_nms = [x_var_name, y_var_name] + list(slices.keys())
    extra_dim = [nm for nm in dims if nm not in dim_nms]
    if len(extra_dim) == 1:
        hgt_dim_nm = [nm for nm in dims if nm not in dim_nms][0]
        if "ensemble_member" in dims:
            dims_flat = [d for d in dims if d != x_var_name]
            slc = [0 if d == hgt_dim_nm else slice(None) for d in dims_flat]
            return nc_var[data_slice][new_slice][slc]
        else:
            new_slice[dims.index(hgt_dim_nm)] = 0
            return nc_var[data_slice][tuple(new_slice)]
    elif len(extra_dim) == 0:
        return nc_var[data_slice][tuple(new_slice)]
    else:
        raise err("Variable '{}' has more dimensions than required.".format(nc_var.name))


def _get_files(_directory, _filename, t_c, err):
    file_names = [g for g in os.listdir(_directory) if re.findall(_filename, g)]
    if len(file_names) == 0:
        raise err('No matches found for file_pattern = {} and t_c = {} '.format(_filename, UTC.to_string(t_c)))
    match_files = []
    match_times = []
    for fn in file_names:

        t = UTC.time(*[int(x) for x in re.search(_filename, fn).groups()])
        if t <= t_c:
            match_files.append(fn)
            match_times.append(t)
    if match_files:
        return os.path.join(_directory, match_files[np.argsort(match_times)[-1]])
    raise err("No matches found for file_pattern = {} and t_c = {} ".format(_filename, UTC.to_string(t_c)))


def calc_RH(T, Td, p):
    """ Calculates relative humidity from air_temperature, dew_point_temperature and pressure."""
    # Constants used in RH calculation
    __a1_w = 611.21  # Pa
    __a3_w = 17.502
    __a4_w = 32.198  # K

    __a1_i = 611.21  # Pa
    __a3_i = 22.587
    __a4_i = -20.7  # K

    __T0 = 273.16  # K
    __Tice = 205.16  # K

    def calc_q(T, p, alpha):
        e_w = __a1_w*np.exp(__a3_w*((T - __T0)/(T - __a4_w)))
        e_i = __a1_i*np.exp(__a3_i*((T - __T0)/(T - __a4_i)))
        q_w = 0.622*e_w/(p - (1 - 0.622)*e_w)
        q_i = 0.622*e_i/(p - (1 - 0.622)*e_i)
        return alpha*q_w + (1 - alpha)*q_i

    def calc_alpha(T):
        alpha = np.zeros(T.shape, dtype='float')
        # alpha[T<=Tice]=0.
        alpha[T >= __T0] = 1.
        indx = (T < __T0) & (T > __Tice)
        alpha[indx] = np.square((T[indx] - __Tice)/(__T0 - __Tice))
        return alpha

    alpha = calc_alpha(T)
    qsat = calc_q(T, p, alpha)
    q = calc_q(Td, p, alpha)
    return q/qsat


def calc_P(elev, seaLevelPressure=101325):
    """
    Compute surface pressure at a particular altitude given a sea level pressure

    elev: meters
    seaLevelPressure: pa
    """
    g = 9.80665  # m/s2
    T0 = 288.15  # K
    L = -0.0065  # K/m
    M = 0.0289644  # kg/mol
    R = 8.3144598  # J/mol/K
    value = seaLevelPressure*(T0/(T0 + L*(elev))) ** (g*M/(R*L))
    return value


def _clip_ensemble_of_geo_timeseries(ensemble, utc_period, err=None, allow_shorter_period=False):
    """
    Clip ensemble og source-keyed dictionaries of geo-ts according to utc_period

    Parameters
    ----------
    ensemble: list
        List of dictionaries keyed by time series type, where values are
        api vectors of geo located time series over the same time axis
    utc_period: UtcPeriod
        The utc time period that should (as a minimum) be covered.
    allow_shorter_period: bool, optional
        may return ts for shorter period if time_axis does not cover utc_period

    Returns
    -------
        List of dictionaries keyed by time series type, where values are
        api vectors of geo located time series that cover the utc_period
    """
    if utc_period is None:
        return ensemble
    if err is None:
        err = Exception

    # Check time axis of first ensemble member/geo_point and if required create new time axis to use for clipping
    member = ensemble[0]
    i0 = {}
    n = {}
    is_optimal = {}
    for key, geo_ts in member.items():
        ta = geo_ts[0].ts.time_axis
        point_type = geo_ts[0].ts.point_interpretation() == POINT_INSTANT_VALUE
        # If POINT_INSTANT_VALUE we need at least one value (i.e. two time_points) at time >= utc_period.end
        if ta.total_period().start >= utc_period.end or ta.time_points[-1 - point_type] <= int(utc_period.start):
            raise err("Found time axis that does not intersect utc_period.")
        if ta.total_period().start > utc_period.start or not ta.time_points[-1 - point_type] >= int(utc_period.end):
            if not allow_shorter_period:
                raise err("Found time axis that does not cover utc_period.")
            else:
                period_start = max(ta.time_points[0], int(utc_period.start))
                period_end = min(ta.time_points[-1 - point_type], int(utc_period.end))
        else:
            period_start = utc_period.start
            period_end = utc_period.end
        idx_start = np.argmax(ta.time_points > period_start) - 1
        idx_end = np.argmax(ta.time_points >= period_end) + point_type
        if idx_start > 0 or idx_end < len(ta.time_points) - 1:
            is_optimal[key] = False
        else:
            is_optimal[key] = True
        i0[key] = idx_start
        n[key] = int(idx_end - idx_start)
    if all(list(is_optimal.values())):
        res = ensemble  # No need to clip if all are optimal
    else:
        res = []
        for f in ensemble:
            d = {}
            for key, geo_ts in f.items():
                source_vector = source_vector_map[key]()
                for s in geo_ts:
                    source_vector.append(source_type_map[key](s.mid_point(), s.ts.evaluate().slice(int(i0[key]), n[key])))
                d[key] = source_vector
            res.append(d)
    return res


def create_ncfile(data_file, variables, dimensions, ncattrs=None):
    """
    Create a ncfile ready for accepting shyft geo data.

    Parameters
    -----------

    data_file: netcdf filename to create **will be overwritten**

    dimensions: a dictionary keyed by 'dimensions'

    variables: a dictionary keyed by 'variable_name' with a list
        containing: [datatype, dimension tuple, and a dict of attributes]

    ncattrs: a dictionary keyed by nc file attributes

    Returns
    -------
    a netcdf file object handle to be filled with data

    """

    with Dataset(data_file, 'w') as dset:

        if ncattrs:
            dset.setncatts(ncattrs)

        for dimension, size in dimensions.items():
            dset.createDimension(dimension, size)

        for name, content in variables.items():
            dtype, dims, attrs = content
            dset.createVariable(name, dtype, dims)
            dset[name].setncatts(attrs)

        # dset.close()
