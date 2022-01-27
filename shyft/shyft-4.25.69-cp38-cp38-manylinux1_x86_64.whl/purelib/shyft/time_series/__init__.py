import os
from os import path

if os.name == 'nt':
    os.environ['PATH'] = path.join(path.dirname(__file__),'..','lib') + ';' + os.environ['PATH']
# first pull in type from the python extensions
from shyft.time_series._time_series import *

# Fix up vector types

DoubleVector.size = lambda self: len(self)
DoubleVector_FromNdArray = lambda x: DoubleVector.from_numpy(x)


def VectorString(v):
    return str(v.to_numpy())


Int64Vector = IntVector

DoubleVector.__str__ = lambda self: VectorString(self)

Calendar.__str__ = lambda self: "Calendar('{0}')".format(self.tz_info.name())


def ShowUtcTime(v):
    utc = Calendar()
    return "[" + ",".join([utc.to_string(t) for t in v]) + "]"


UtcTimeVector.size = lambda self: len(self)
UtcTimeVector.__str__ = lambda self: ShowUtcTime

IntVector.size = lambda self: len(self)
IntVector.__str__ = lambda self: VectorString(self)

StringVector.size = lambda self: len(self)

# ByteVector to/from string


ByteVector.__str__ = lambda self: byte_vector_to_hex_str(self)
ByteVector.from_str = byte_vector_from_hex_str

# fix up BW and pythonic syntax for TsVector

TsVector.size = lambda self: len(self)
TsVector.push_back = lambda self, ts: self.append(ts)

# fix bw. stl name
# UtcTimeVector.push_back = lambda self, x: self.append(x)
IntVector.push_back = lambda self, x: self.append(x)
DoubleVector.push_back = lambda self, x: self.append(x)
StringVector.push_back = lambda self, x: self.append(x)

# FIx up YMDhms
YMDhms.__str__ = lambda self: "YMDhms({0},{1},{2},{3},{4},{5},{6})".format(self.year, self.month, self.day, self.hour,
                                                                       self.minute, self.second, self.micro_second)

YMDhms.__repr__ = lambda self: "{0}({1},{2},{3},{4},{5},{6},{7})".format(self.__class__.__name__,
                                                                     self.year, self.month, self.day, self.hour,
                                                                     self.minute, self.second, self.micro_second)

YWdhms.__str__ = lambda self: "YWdhms({0},{1},{2},{3},{4},{5},{6})".format(self.iso_year, self.iso_week, self.week_day, self.hour,
                                                                       self.minute, self.second, self.micro_second)

YWdhms.__repr__ = lambda self: "{0}({1},{2},{3},{4},{5},{6},{7})".format(self.__class__.__name__,
                                                                     self.iso_year, self.iso_week, self.week_day, self.hour,
                                                                     self.minute, self.second, self.micro_second)

# Fix up UtcPeriod
UtcPeriod.to_string = lambda self: str(self)
UtcPeriod.__repr__ = UtcPeriod.__str__

# Allow convolve_policies to be |'ed together
convolve_policy.__or__ = lambda self, other: (convolve_policy)(self + other)


# Fix up TimeAxis

def ta_iter(x):
    x.counter = 0
    return x


def ta_next(ta):
    if ta.counter >= len(ta):
        del ta.counter
        raise StopIteration
    ta.counter += 1
    return ta(ta.counter - 1)


TimeAxisFixedDeltaT.__str__ = lambda self: "TimeAxisFixedDeltaT({0},{1},{2})".format(Calendar().to_string(self.start), self.delta_t, self.n)
TimeAxisFixedDeltaT.__repr__ = TimeAxisFixedDeltaT.__str__
TimeAxisFixedDeltaT.__len__ = lambda self: self.size()
TimeAxisFixedDeltaT.__call__ = lambda self, i: self.period(i)
TimeAxisFixedDeltaT.__iter__ = lambda self: ta_iter(self)
TimeAxisFixedDeltaT.__next__ = lambda self: ta_next(self)

TimeAxisCalendarDeltaT.__str__ = lambda self: "TimeAxisCalendarDeltaT(Calendar('{3}'),{0},{1},{2})".format(Calendar().to_string(self.start), self.delta_t, self.n, self.calendar.tz_info.name())
TimeAxisCalendarDeltaT.__repr__ = TimeAxisCalendarDeltaT.__str__
TimeAxisCalendarDeltaT.__len__ = lambda self: self.size()
TimeAxisCalendarDeltaT.__call__ = lambda self, i: self.period(i)
TimeAxisCalendarDeltaT.__iter__ = lambda self: ta_iter(self)
TimeAxisCalendarDeltaT.__next__ = lambda self: ta_next(self)

TimeAxisByPoints.__str__ = lambda self: "TimeAxisByPoints(total_period={0}, n={1},points={2} )".format(str(self.total_period()), len(self), repr(TimeAxis(self).time_points))
TimeAxisByPoints.__repr__ = TimeAxisByPoints.__str__
TimeAxisByPoints.__len__ = lambda self: self.size()
TimeAxisByPoints.__call__ = lambda self, i: self.period(i)
TimeAxisByPoints.__iter__ = lambda self: ta_iter(self)
TimeAxisByPoints.__next__ = lambda self: ta_next(self)


def nice_ta_string(time_axis):
    if time_axis.timeaxis_type == TimeAxisType.FIXED:
        ta = time_axis.fixed_dt
        return f"TimeAxis('{Calendar().to_string(ta.start)}', {ta.delta_t}, {ta.n})"
    if time_axis.timeaxis_type == TimeAxisType.CALENDAR:
        ta = time_axis.calendar_dt
        return f"TimeAxis( Calendar('{ta.calendar.tz_info.name()}'), '{ta.calendar.to_string(ta.start)}', {ta.delta_t}, {ta.n})"
    ta = time_axis.point_dt
    return f"TimeAxis( '{ta.total_period()}', {len(ta)},{repr(time_axis.time_points)})"


TimeAxis.__str__ = lambda self: nice_ta_string(self)
TimeAxis.__repr__ = TimeAxis.__str__
TimeAxis.__len__ = lambda self: self.size()
TimeAxis.__call__ = lambda self, i: self.period(i)
TimeAxis.__iter__ = lambda self: ta_iter(self)
TimeAxis.__next__ = lambda self: ta_next(self)

TimeAxis.time_points = property(lambda self: time_axis_extract_time_points(self).to_numpy(), doc= \
    """
     extract all time-points from a TimeAxis
     like
     [ time_axis.time(i) ].append(time_axis.total_period().end) if time_axis.size() else []
    
    Parameters
    ----------
    time_axis : TimeAxis
    
    Returns
    -------
    time_points:numpy.array(dtype=np.int64)
       [ time_axis.time(i) ].append(time_axis.total_period().end)
    """)

TimeAxis.time_points_double = property(lambda self: time_axis_extract_time_points_as_utctime(self).to_numpy_double(), doc= \
    """
    extract all time-points from a TimeAxis with microseconds
    like
    [ time_axis.time(i) ].append(time_axis.total_period().end) if time_axis.size() else []
    
    Parameters
    ----------
    time_axis : TimeAxis
    
    Returns
    -------
    time_points:numpy.array(dtype=np.float64)
       [ time_axis.time(i) ].append(time_axis.total_period().end)
    """)

# fix up property on timeseries
TimeSeries.time_axis = property(lambda self: self.get_time_axis(), doc="returns the time_axis of the timeseries")
TimeSeries.__len__ = lambda self: self.size()
TimeSeries.v = property(lambda self: self.values, doc="returns the point-values of timeseries, alias for .values")

TimeSeries.kling_gupta = lambda self, other_ts, s_r=1.0, s_a=1.0, s_b=1.0: kling_gupta(self, other_ts,
                                                                                       self.get_time_axis(), s_r, s_a,
                                                                                       s_b)
TimeSeries.kling_gupta.__doc__ = \
    """
    computes the kling_gupta correlation using self as observation, and self.time_axis as
    the comparison time-axis

    Parameters
    ----------
    other_ts : Timeseries
     the predicted/calculated time-series to correlate
    s_r : float
     the kling gupta scale r factor(weight the correlation of goal function)
    s_a : float
     the kling gupta scale a factor(weight the relative average of the goal function)
    s_b : float
     the kling gupta scale b factor(weight the relative standard deviation of the goal function)

    Return
    ------
    KGEs : float

    """

TimeSeries.nash_sutcliffe = lambda self, other_ts: nash_sutcliffe(self, other_ts, self.get_time_axis())
TimeSeries.nash_sutcliffe.__doc__ = \
    """
    Computes the Nash-Sutcliffe model effiency coefficient (n.s)
    for the two time-series over the specified time_axis
    Ref:  http://en.wikipedia.org/wiki/Nash%E2%80%93Sutcliffe_model_efficiency_coefficient
    Parameters
    ----------
    observed_ts : TimeSeries
     the observed time-series
    model_ts : TimeSeries
     the time-series that is the model simulated / calculated ts
    time_axis : TimeAxis
     the time-axis that is used for the computation
    Return
    ------
     float: The n.s performance, that have a maximum at 1.0
    """

TsFixed.values = property(lambda self: self.v, doc="returns the point values, .v of the timeseries")
TsFixed.time_axis = property(lambda self: self.get_time_axis(), doc="returns the time_axis of the timeseries")
TsPoint.values = property(lambda self: self.v, doc="returns the point values, .v of the timeseries")
TsPoint.time_axis = property(lambda self: self.get_time_axis(), doc="returns the time_axis of the timeseries")

# some minor fixup to ease work with core-time-series vs TimeSeries
TsFixed.TimeSeries = property(lambda self: TimeSeries(self), doc="return a fully featured TimeSeries from the core TsFixed ")
TsFixed.nash_sutcliffe = lambda self, other_ts: nash_sutcliffe(self.TimeSeries, other_ts, TimeAxis(self.get_time_axis()))
TsFixed.kling_gupta = lambda self, other_ts, s_r=1.0, s_a=1.0, s_b=1.0: kling_gupta(self.TimeSeries, other_ts,
                                                                                    TimeAxis(self.get_time_axis()), s_r, s_a,
                                                                                    s_b)

TsPoint.TimeSeries = property(lambda self: TimeSeries(self.get_time_axis(), self.v, self.point_interpretation()), doc="return a fully featured TimeSeries from the core TsPoint")
TsPoint.nash_sutcliffe = lambda self, other_ts: nash_sutcliffe(self.TimeSeries, other_ts, TimeAxis(self.get_time_axis()))
TsPoint.kling_gupta = lambda self, other_ts, s_r=1.0, s_a=1.0, s_b=1.0: kling_gupta(self.TimeSeries, other_ts,
                                                                                    TimeAxis(self.get_time_axis()), s_r, s_a,
                                                                                    s_b)


def ts_vector_values_at_time(tsv: TsVector, t: int):
    if not isinstance(tsv, TsVector):
        if not isinstance(tsv, list):
            raise RuntimeError('Supplied list of timeseries must be of type TsVector or list(TimeSeries)')
        list_of_ts = tsv
        tsv = TsVector()
        for ts in list_of_ts:
            tsv.append(ts)
    if not isinstance(t, time):
        t = time(t)
    return tsv.values_at(t).to_numpy()


# ts_vector_values_at_time.__doc__ = TsVector.values_at.__doc__.replace('DoubleVector','ndarray').replace('TsVector','TsVector or list(TimeSeries)')

TsVector.values_at_time = ts_vector_values_at_time
# TsVector.values_at_time.__doc__ = TsVector.values_at.__doc__.replace('DoubleVector','ndarray')

# Fix up GeoPoint
GeoPoint.__str__ = lambda self: "GeoPoint({0},{1},{2})".format(self.x, self.y, self.z)
GeoPoint_difference = lambda a, b: GeoPoint.difference(a, b)
GeoPoint_xy_distance = lambda a, b: GeoPoint.xy_distance(a, b)


# need to create the `__all__` attribute for documentation.
# if you want sphinx-apidoc to autodoc a module/class it should be
# included below.
# generate using ipython: import `shyft._time_series import  as ts` and `dir(ts)`, then clean
# concatenate several lists from this file and from the list you create:

__all__ = [
    'QueueMessageInfo',
    'QueueMessageInfoVector',
    'GeoPoint',
    'GeoPointVector',
    'GeoTimeSeries',
    'GeoTimeSeriesVector',
    'GeoQuery',
    'GeoGridSpec',
    'GeoTimeSeriesConfiguration',
    'GeoMatrix',
    'GeoTsMatrix',
    'GeoMatrixShape',
    'GeoEvalArgs',
    'GeoSlice',
    'Int64Vector',
    'ts_vector_values_at_time',
    'time_series_to_bokeh_plot_data',
    'time_axis_extract_time_points_as_utctime_tz',
    'ext_path_url',
    'ext_query_url',
    'ALLOW_ANY_MISSING',
    'ALLOW_INITIAL_MISSING',
    'AT_VALUE',
    'AverageAccessorTs',
    'BACKWARD',
    'ByteVector',
    'CALENDAR',
    'CENTER',
    'CacheStats',
    'Calendar',
    'CoreTsVector',
    'DEFAULT',
    'DISALLOW_MISSING',
    'DoubleVector',
    'DoubleVectorVector',
    'DtsClient',
    'DtsServer',
    'FILL_NAN',
    'FILL_VALUE',
    'FIXED',
    'FORWARD',
    'IcePackingParameters',
    'IcePackingRecessionParameters',
    'IntVector',
    'KrlsRbfPredictor',
    'LHS_LAST',
    'POINT',
    'POINT_AVERAGE_VALUE',
    'POINT_INSTANT_VALUE',
    'Point',
    'QacParameter',
    'RHS_FIRST',
    'RatingCurveFunction',
    'RatingCurveParameters',
    'RatingCurveSegment',
    'RatingCurveSegments',
    'RatingCurveTimeFunction',
    'RatingCurveTimeFunctions',
    'StringVector',
    'TRIM_IN',
    'TRIM_OUT',
    'TimeAxis',
    'TimeAxisByPoints',
    'TimeAxisCalendarDeltaT',
    'TimeAxisFixedDeltaT',
    'TimeAxisType',
    'TimeSeries',
    'TsBindInfo',
    'TsBindInfoVector',
    'TsFactory',
    'TsFixed',
    'TsInfo',
    'TsInfoVector',
    'TsPoint',
    'TsVector',
    'TsVectorSet',
    'TzInfo',
    'USE_LAST',
    'UtcPeriod',
    'UtcTimeVector',
    'YMDhms',
    'YWdhms',
    # '__doc__',
    # '__file__',
    # '__loader__',
    # '__name__',
    # '__package__',
    # '__spec__',
    # '_finalize',
    'accumulate',
    'average',
    'byte_vector_from_file',
    'byte_vector_from_hex_str',
    'byte_vector_to_file',
    'byte_vector_to_hex_str',
    'convolve_policy',
    'create_glacier_melt_ts_m3s',
    'create_periodic_pattern_ts',
    'create_ts_vector_from_np_array',
    'deltahours',
    'deltaminutes',
    'derivative_method',
    'dtss_finalize',
    'extend_fill_policy',
    'extend_split_policy',
    'extract_shyft_url_container',
    'extract_shyft_url_path',
    'extract_shyft_url_query_parameters',
    'ice_packing_temperature_policy',
    'integral',
    'intersection',
    'is_npos',
    'kling_gupta',
    'log',
    'max',
    'max_utctime',
    'min',
    'min_utctime',
    'nash_sutcliffe',
    'no_utctime',
    'npos',
    'point_interpretation_policy',
    'pow',
    'quantile_map_forecast',
    'shyft_url',
    'statistics_property',
    'time',
    'time_axis_extract_time_points',
    'time_axis_extract_time_points_as_utctime',
    'time_shift',
    'trim_policy',
    'ts_stringify',
    'urldecode',
    'urlencode',
    'utctime_now',
    'version',
    'win_set_priority',
    'win_short_path',
    'ModelInfo',
    'ModelInfoVector'
]
