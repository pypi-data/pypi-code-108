from dataclasses import dataclass
from shyft.time_series import (Calendar, UtcPeriod, time, TimeAxis, min_utctime, max_utctime, UtcTimeVector,
                               time_axis_extract_time_points_as_utctime, TimeAxisType)


def create_view_time_axis(*, cal: Calendar, view_period: UtcPeriod, clip_period: UtcPeriod, dt: time) -> TimeAxis:
    """
    This function creates a time axis with the range of the view_period, clipped to clip_period if specified,
    and snaps to its calendar resolution of dt.

    An *empty* TimeAxis() is returned if:
     - the overlap is _less than_ dt or no overlap
     - overlap period contains -oo or +oo
     - dt is zero

    For all other cases a TimeAxis is returned such that:
      dt < DAY:
        TimeAxis(t_start,dt,n)
      dt >= DAY
        TimeAxis(cal,t_start,dt,n)
      where
         t_start = cal.trim(overlap.start + dt/2,dt)
         n = UtcPeriod(t_start,cal.trim(overlap.end + dt/2,dt).diff_units(cal,dt)

    Parameters
    ----------
    cal: Calendar to use for calendar semantic trim/add if dt >= DAY
    view_period: the visual view-period
    clip_period: the clip to this period)
    dt: time step of the time axis

    Returns
    -------
    time_axis: TimeAxis
    """
    overlap = UtcPeriod.intersection(view_period, clip_period) if clip_period.valid() else view_period
    if dt <= 0 or not overlap.valid() or overlap.timespan() < dt or overlap.start == min_utctime or overlap.end == max_utctime:
        return TimeAxis()
    t_start = cal.trim(overlap.start + dt/2, dt)  # the + dt/2.0 ensure calendar rounding, as opposed to trunc/trim
    n = UtcPeriod(t_start, cal.trim(overlap.end + dt/2, dt)).diff_units(cal, dt)
    return TimeAxis(t_start, dt, n) if dt < cal.DAY else TimeAxis(cal, t_start, dt, n)


@dataclass
class TimeAxisProperties:
    """Data-class to store some of the properties of a TimeAxis"""
    period: UtcPeriod
    delta_t: time
    num_time_steps: int


def extend_period(ta: TimeAxisProperties, period: UtcPeriod) -> TimeAxisProperties:
    """Extends the input period such that it covers at least the range of input period."""
    t_start = ta.period.start
    t_end = ta.period.end
    dt = ta.delta_t
    n = ta.num_time_steps

    while t_start > period.start:
        t_start -= 1 * dt
        n += 1
    while t_end < period.end:
        n += 1
        t_end += 1 * dt
    return TimeAxisProperties(UtcPeriod(t_start, t_end), dt, n)


def extend_calendar_time_axis(time_axis: TimeAxis, period: UtcPeriod) -> TimeAxis:
    """
    Extends the input time-axis (with .timeaxis_type = TimeAxisType.CALENDAR) such that its .total_period() covers at
    least the range of the input period.
    """
    ta_properties = TimeAxisProperties(time_axis.total_period(), time_axis.calendar_dt.delta_t, time_axis.calendar_dt.n)
    ta = extend_period(ta_properties, period)
    return TimeAxis(time_axis.calendar_dt.calendar, ta.period.start, ta.delta_t, ta.num_time_steps)


def extend_fixed_time_axis(time_axis: TimeAxis, period: UtcPeriod) -> TimeAxis:
    """
    Extends the input time-axis (with .timeaxis_type = TimeAxisType.FIXED) such that its .total_period() covers at least
    the range of the input period.
    """
    ta_properties = TimeAxisProperties(time_axis.total_period(), time_axis.fixed_dt.delta_t, time_axis.fixed_dt.n)
    ta = extend_period(ta_properties, period)
    return TimeAxis(ta.period.start, ta.delta_t, ta.num_time_steps)


def extend_point_time_axis(time_axis: TimeAxis, period: UtcPeriod) -> TimeAxis:
    """
    Extends the input time-axis (with .timeaxis_type = TimeAxisType.POINT) such that its .total_period() covers the
    range of the input period.
    """
    time_points = UtcTimeVector()
    if time_axis.total_period().start > period.start:
        time_points.append(period.start)
        time_points.extend(time_axis_extract_time_points_as_utctime(time_axis))
    else:
        time_points = time_axis_extract_time_points_as_utctime(time_axis)
    if time_axis.total_period().end < period.end:
        time_points.append(period.end)
    return TimeAxis(time_points)


def extend_time_axis(*, ta: TimeAxis, p: UtcPeriod) -> TimeAxis:
    """
    Return an extended time-axis where .total_period() is at least
    the range of period p.
    If they are already included, return the original time-axis.
    """
    if len(ta) and p.valid() and p.start != min_utctime and p.end != min_utctime and (ta.total_period().start > p.start or ta.total_period().end < p.end):
        extend_ta_methods = {TimeAxisType.CALENDAR: extend_calendar_time_axis,
                             TimeAxisType.FIXED: extend_fixed_time_axis,
                             TimeAxisType.POINT: extend_point_time_axis}
        extend_ta_method = extend_ta_methods.get(ta.timeaxis_type, None)
        if extend_ta_method is not None:
            return extend_ta_method(ta, p)
    return ta


class ViewTimeAxisProperties:
    """
    At the view-level, describes the visual-wanted properties of the time-series data to be presented.
    The class have no logic, just group together properties that give a consistent view of current 'view-port'.

    The data-source can use this information to adapt it's call to the underlying TsAdapter(time-axis,unit)->tsvector
    so that it is optimal with respect to performance, as well as visualization.

    Attributes
    ----------
    dt: time-step for aggregation/average, like hour, day, week etc.
    cal: calendar for calendar semantic steps, so the time-steps dt are in multiple of dt, rounded to calendar
    view_period: the current entire view-period (usually also rounded to whole calendar/dt)
    padded_view_period: a period greater/equal to the view-period, to allow for smooth pan/scrolling
    extend_mode: if True, the data-source should ensure to include its own min/max range using the extend_time_axis method
    """

    def __init__(self, *, dt: time, cal: Calendar, view_period: UtcPeriod, padded_view_period: UtcPeriod, extend_mode:bool):
        self.dt: time = dt
        self.cal: Calendar = cal
        self.view_period: UtcPeriod = view_period
        self.padded_view_period: UtcPeriod = padded_view_period
        self.extend_mode:bool = extend_mode
