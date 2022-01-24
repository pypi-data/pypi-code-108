# need to create the `__all__` attribute for documentation.
# if you want sphinx-apidoc to autodoc a module/class it should be
# included below.
# generate using ipython: from `shyft.hydrology._api import *` and `dir()`, then clean
# concatenate several lists from this file and from the list you create:

__all__ = [
           'GeoCellDataServer',
           'GeoCellDataClient',
           'GeoCellDataModel',
           'parse_cf_time',
           'np_array',
           'StrGeoCellData',
           'ABS_DIFF',
           'ARegionEnvironment',
           'ActualEvapotranspirationCalculate_step',
           'ActualEvapotranspirationParameter',
           'ActualEvapotranspirationResponse',
           'BTKParameter',
           'CELL_CHARGE',
           'CatchmentPropertyType',
           'CellEnvironment',
           'CellStateId',
           'DISCHARGE',
           'EXPONENTIAL',
           'FlowAdjustResult',
           'GAUSSIAN',
           'GammaSnowCalculator',
           'GammaSnowParameter',
           'GammaSnowResponse',
           'GammaSnowState',
           'GeoCellData',
           'GeoCellDataVector',
           'GeoPoint',
           'GeoPointSource',
           'GeoPointSourceVector',
           'GeoPointVector',
           'GlacierMeltParameter',
           'HbvActualEvapotranspirationParameter',
           'HbvActualEvapotranspirationResponse',
           'HbvPhysicalSnowCalculator',
           'HbvPhysicalSnowParameter',
           'HbvPhysicalSnowResponse',
           'HbvPhysicalSnowState',
           'HbvSnowCalculator',
           'HbvSnowParameter',
           'HbvSnowResponse',
           'HbvSnowState',
           'HbvSoilCalculator',
           'HbvSoilParameter',
           'HbvSoilResponse',
           'HbvSoilState',
           'HbvTankCalculator',
           'HbvTankParameter',
           'HbvTankResponse',
           'HbvTankState',
           'SnowTilesParameter',
           'IDWParameter',
           'IDWPrecipitationParameter',
           'IDWTemperatureParameter',
           'InterpolationParameter',
           'KLING_GUPTA',
           'KalmanBiasPredictor',
           'KalmanFilter',
           'KalmanParameter',
           'KalmanState',
           'KirchnerCalculator',
           'KirchnerParameter',
           'KirchnerResponse',
           'KirchnerState',
           'LandTypeFractions',
           'MethodStackParameter',
           'NASH_SUTCLIFFE',
           'OKCovarianceType',
           'OKParameter',
           'PenmanMonteithCalculator',
           'PenmanMonteithParameter',
           'PenmanMonteithResponse',
           'PrecipitationCorrectionCalculator',
           'PrecipitationCorrectionParameter',
           'PrecipitationSource',
           'PrecipitationSourceVector',
           'PriestleyTaylorCalculator',
           'PriestleyTaylorParameter',
           'PriestleyTaylorResponse',
           'RMSE',
           'ROUTED_DISCHARGE',
           'RadiationCalculator',
           'RadiationParameter',
           'RadiationResponse',
           'RadiationSource',
           'RadiationSourceVector',
           'RelHumSource',
           'RelHumSourceVector',
           'River',
           'RiverNetwork',
           'RoutingInfo',
           'SNOW_COVERED_AREA',
           'SNOW_WATER_EQUIVALENT',
           'SkaugenCalculator',
           'SkaugenParameter',
           'SkaugenResponse',
           'SkaugenState',
           'TargetSpecCalcType',
           'TargetSpecificationPts',
           'TargetSpecificationVector',
           'TemperatureSource',
           'TemperatureSourceVector',
           'TsTransform',
           'UHGParameter',
           'WindSpeedSource',
           'WindSpeedSourceVector',
           'bayesian_kriging_temperature',
           'catchment',
           'cell',
           'compute_geo_ts_values_at_time',
           'create_precipitation_source_vector_from_np_array',
           'create_radiation_source_vector_from_np_array',
           'create_rel_hum_source_vector_from_np_array',
           'create_temperature_source_vector_from_np_array',
           'create_wind_speed_source_vector_from_np_array',
           'glacier_melt_step',
           'idw_precipitation',
           'idw_radiation',
           'idw_relative_humidity',
           'idw_temperature',
           'idw_wind_speed',
           'make_uhg_from_gamma',
           'ordinary_kriging',
           'stat_scope',
           'version',
           'pt_gs_k',
           'pt_hps_k',
           'pt_hs_k',
           'pt_st_k',
           'pt_ss_k',
           'hbv_stack',
           'r_pm_gs_k',
           'r_pt_gs_k',
           'CalibrationOption',
           'OptimizerMethod',
           'CalibrationStatus',
           # added
           'DrmClient', 'DrmServer', 'RegionModelType',
           'SnowTilesParameter', 'SnowTilesState', 'SnowTilesCalculator', 'SnowTilesResponse',
           'shyftdata_dir', 'percentiles',
           'viz', 'repository', 'orchestration'

           ]

import os
from os import path
# we need timeseries, start with it early
from ..time_series import (IntVector, DoubleVector, TsVector, GeoPoint, GeoPointVector, TimeAxis)

# this is backward compatible

from ._api import *
from . import r_pm_gs_k
from . import r_pt_gs_k
from . import pt_gs_k
from . import pt_hps_k
from . import pt_hs_k
from . import pt_st_k
from . import pt_ss_k
from . import hbv_stack
from . import viz
from . import repository
from . import orchestration

from math import sqrt
import numpy as np

if "SHYFT_DATA" in os.environ:
    shyftdata_dir = os.environ["SHYFT_DATA"]
else:
    # If SHYFT_DATA environment variable is not here, then use a decent guess
    shyftdata_dir = path.join(path.dirname(__file__),path.pardir, path.pardir, path.pardir, path.pardir, "shyft-data")
shyftdata_dir = path.normpath(shyftdata_dir)


def percentiles(tsv: TsVector, time_axis: TimeAxis, percentile_list: IntVector) -> TsVector:
    return tsv.percentiles(time_axis, percentile_list)


TargetSpecificationVector.size = lambda self: len(self)


# Fix up LandTypeFractions

LandTypeFractions.__str__ = lambda \
        self: "LandTypeFractions(glacier={0},lake={1},reservoir={2},forest={3},unspecified={4})".format(self.glacier(),
                                                                                                        self.lake(),
                                                                                                        self.reservoir(),
                                                                                                        self.forest(),
                                                                                                        self.unspecified())


# Fix up GeoCellData
def StrGeoCellData(gcd):
    return "GeoCellData(mid_point={0},catchment_id={1},area={2},ltf={3})".format(str(gcd.mid_point()),
                                                                                 gcd.catchment_id(), gcd.area(),
                                                                                 str(gcd.land_type_fractions_info()))


GeoCellData.__str__ = lambda self: StrGeoCellData(self)
GeoCellData.__repr__ = GeoCellData.__str__

# Fix up ARegionEnvironment
TemperatureSource.vector_t = TemperatureSourceVector
PrecipitationSource.vector_t = PrecipitationSourceVector
RadiationSource.vector_t = RadiationSourceVector
RelHumSource.vector_t = RelHumSourceVector
WindSpeedSource.vector_t = WindSpeedSourceVector

Int64Vector = IntVector


def np_array(dv: DoubleVector):
    """
    convert flattened double-vector to numpy array
    Parameters
    ----------
    dv

    Returns
    -------
    numpy array.
    """
    f = dv.to_numpy()
    n = int(sqrt(dv.size()))
    m = f.reshape(n, n)
    return m


# fixup kalman state
KalmanState.x = property(lambda self: KalmanState.get_x(self).to_numpy(),
                         doc="represents the current bias estimate, kalman.state.x")
KalmanState.k = property(lambda self: KalmanState.get_k(self).to_numpy(),
                         doc="represents the current kalman gain factors, kalman.state.k")
KalmanState.P = property(lambda self: np_array(KalmanState.get_P(self)),
                         doc="returns numpy array of kalman.state.P, the nxn covariance matrix")
KalmanState.W = property(lambda self: np_array(KalmanState.get_W(self)),
                         doc="returns numpy array of kalman.state.W, the nxn noise matrix")


# fixup KalmanBiasPredictor
def KalmanBiasPredictor_update_with_forecast(bp, fc_set, obs, time_axis):
    """

    Parameters
    ----------
    bp
    fc_set : TemperatureSourceVector or TsVector
    obs : TimeSeries
    time_axis : TimeAxis

    Returns
    -------
    nothing
    """
    if isinstance(fc_set, TemperatureSourceVector):
        KalmanBiasPredictor.update_with_geo_forecast(bp, fc_set, obs, time_axis)
    else:
        KalmanBiasPredictor.update_with_forecast_vector(bp, fc_set, obs, time_axis)


def KalmanBiasPredictor_compute_running_bias(bp, fc_ts, obs_ts, time_axis):
    """
    compute the running bias timeseries,
    using one 'merged' - forecasts and one observation time - series.

    Before each day - period, the bias - values are copied out to form
    a continuous bias prediction time-series.

    Parameters
    ----------

    bias_predictor : KalmanBiasPredictor
        The bias predictor object it self

    forecast_ts : TimeSeries
        a merged forecast ts
        with period covering the observation_ts and time_axis supplied

    observation ts: TimeSeries
        the observation time-series

    time_axis : TimeAxis
        covering the period/timesteps to be updated
        e.g. yesterday, 3h resolution steps, according to the points in the filter

    Returns
    -------
    bias_ts : TimeSeries(time_axis,bias_vector,POINT_AVERAGE)
        computed running bias-ts
    """
    return KalmanBiasPredictor.compute_running_bias_ts(bp, fc_ts, obs_ts, time_axis)


KalmanBiasPredictor.update_with_forecast = KalmanBiasPredictor_update_with_forecast
KalmanBiasPredictor.compute_running_bias = KalmanBiasPredictor_compute_running_bias


def geo_point_source_vector_values_at_time(gtsv: GeoPointSourceVector, t: int):
    # if not isinstance(gtsv, GeoPointSourceVector):
    #    raise RuntimeError('Supplied list of timeseries must be of GeoPointSourceVector')
    return compute_geo_ts_values_at_time(gtsv, t).to_numpy()


GeoPointSourceVector.values_at_time = geo_point_source_vector_values_at_time
# GeoPointSourceVector.values_at_time.__doc__ = compute_geo_ts_values_at_time.__doc__.replace('DoubleVector','ndarray')
RadiationSourceVector.values_at_time = GeoPointSourceVector.values_at_time
PrecipitationSourceVector.values_at_time = GeoPointSourceVector.values_at_time
TemperatureSourceVector.values_at_time = GeoPointSourceVector.values_at_time
RelHumSourceVector.values_at_time = GeoPointSourceVector.values_at_time
WindSpeedSourceVector.values_at_time = GeoPointSourceVector.values_at_time

ARegionEnvironment.variables = property(
    lambda self: [
        ('temperature', self.temperature),
        ('precipitation', self.precipitation),
        ('radiation', self.radiation),
        ('rel_hum', self.rel_hum),
        ('wind_speed', self.wind_speed)
    ],
    doc='returns the list of available forcing variables as tuples(string,reference_to_variable)'
)

#
