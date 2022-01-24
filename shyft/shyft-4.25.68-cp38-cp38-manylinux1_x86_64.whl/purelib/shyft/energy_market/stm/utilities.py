from typing import List

from shyft.time_series import time
from shyft.energy_market.core import XyPointCurve, XyPointCurveWithZ, TurbineEfficiency, TurbineDescription, XyPointCurveWithZList
from shyft.energy_market.stm import t_xy, t_turbine_description, t_xyz_list
from shyft import time_series as sa


def create_t_double(t0: time, v: float) -> sa.TimeSeries:
    """ to ease construction """
    cal = sa.Calendar()
    ta = sa.TimeAxis(t0, t0 + 10*cal.YEAR, 1)
    r = sa.TimeSeries(ta, [v], sa.POINT_AVERAGE_VALUE)
    return r


def create_t_xy(t0: time, point_curve: XyPointCurve) -> t_xy:
    """ to ease construction """
    r = t_xy()
    r[t0] = point_curve
    return r

def create_t_xyz_list(t0: time, point_curve: XyPointCurve, z: float) -> t_xyz_list:
    r = t_xyz_list()
    v = XyPointCurveWithZ()
    v.xy_point_curve = point_curve
    v.z = z
    r[t0] = XyPointCurveWithZList([v])
    return r


def create_t_turbine_description(t0: time, efficiency_curves: List[XyPointCurveWithZ]) -> t_turbine_description:
    """ to ease construction """
    r = t_turbine_description()
    te = TurbineEfficiency(efficiency_curves)
    td = TurbineDescription([te])
    r[t0] = td
    return r


def create_t_turbine_description_pelton(t0: time,
                                        turbine_efficiencies: List[TurbineEfficiency]) -> t_turbine_description:
    """ to ease construction """
    r = t_turbine_description()
    td = TurbineDescription(turbine_efficiencies)
    r[t0] = td
    return r
