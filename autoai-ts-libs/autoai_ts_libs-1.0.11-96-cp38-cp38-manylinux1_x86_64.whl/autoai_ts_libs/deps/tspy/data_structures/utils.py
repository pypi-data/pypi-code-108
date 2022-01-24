#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

from py4j.java_collections import ListConverter, MapConverter, JavaList
from py4j.java_gateway import is_instance_of, JavaObject

from autoai_ts_libs.deps.tspy.data_structures.forecasting.Prediction import Prediction
from autoai_ts_libs.deps.tspy.data_structures.time_series import TimeSeries
from autoai_ts_libs.deps.tspy.data_structures.observations.Segment import Segment
from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries

def second(jvm, num_seconds, unit):
    j_duration = jvm.java.time.Duration.ofSeconds(num_seconds)

    if unit is "n":
        return jvm.java.lang.Long(j_duration.toNanos())
    elif unit is "ms":
        return jvm.java.lang.Long(j_duration.toMillis())
    elif unit is "m":
        return jvm.java.lang.Long(j_duration.toMinutes())
    elif unit is "h":
        return jvm.java.lang.Long(j_duration.toHours())
    elif unit is "d":
        return jvm.java.lang.Long(j_duration.toDays())
    else:
        return jvm.java.lang.Long(j_duration.getSeconds())


def minute(jvm, num_minutes, unit):
    j_duration = jvm.java.time.Duration.ofMinutes(num_minutes)

    if unit is "n":
        return jvm.java.lang.Long(j_duration.toNanos())
    elif unit is "ms":
        return jvm.java.lang.Long(j_duration.toMillis())
    elif unit is "m":
        return jvm.java.lang.Long(j_duration.toMinutes())
    elif unit is "h":
        return jvm.java.lang.Long(j_duration.toHours())
    elif unit is "d":
        return jvm.java.lang.Long(j_duration.toDays())
    else:
        return jvm.java.lang.Long(j_duration.getSeconds())


def hour(jvm, num_hours, unit):
    j_duration = jvm.java.time.Duration.ofHours(num_hours)

    if unit is "n":
        return jvm.java.lang.Long(j_duration.toNanos())
    elif unit is "ms":
        return jvm.java.lang.Long(j_duration.toMillis())
    elif unit is "m":
        return jvm.java.lang.Long(j_duration.toMinutes())
    elif unit is "h":
        return jvm.java.lang.Long(j_duration.toHours())
    elif unit is "d":
        return jvm.java.lang.Long(j_duration.toDays())
    else:
        return jvm.java.lang.Long(j_duration.getSeconds())


def day(jvm, num_days, unit):
    j_duration = jvm.java.time.Duration.ofDays(num_days)

    if unit is "n":
        return jvm.java.lang.Long(j_duration.toNanos())
    elif unit is "ms":
        return jvm.java.lang.Long(j_duration.toMillis())
    elif unit is "m":
        return jvm.java.lang.Long(j_duration.toMinutes())
    elif unit is "h":
        return jvm.java.lang.Long(j_duration.toHours())
    elif unit is "d":
        return jvm.java.lang.Long(j_duration.toDays())
    else:
        return jvm.java.lang.Long(j_duration.getSeconds())


class UnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, obj):
        py_obj, obj_type = cast_to_py_if_necessary(self._tsc, obj, self._obj_type)
        self._obj_type = obj_type
        return cast_to_j_if_necessary(self._func(py_obj), self._tsc)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']

class UnaryMapFunctionResultingInOptional(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, obj):
        py_obj, obj_type = cast_to_py_if_necessary(self._tsc, obj, self._obj_type)
        self._obj_type = obj_type
        res = self._func(py_obj)

        if res is None:
            return self._tsc._jvm.java.util.Optional.empty()
        else:
            return self._tsc._jvm.java.util.Optional.of(cast_to_j_if_necessary(res, self._tsc))

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']

class UnaryMapFunctionTupleResultingInOptional(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, obj):
        py_obj, obj_type = cast_to_py_if_necessary(self._tsc, obj, self._obj_type)
        self._obj_type = obj_type
        res = self._func(py_obj)

        if res is None:
            return self._tsc._jvm.java.util.Optional.empty()
        else:
            return self._tsc._jvm.java.util.Optional.of(
                self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(
                    cast_to_j_if_necessary(res[0], self._tsc),
                    cast_to_j_if_necessary(res[1], self._tsc)
                )
            )

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class UnaryListPairMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, list_obj):
        py_list = []
        for x in list_obj:
            key = x.left()
            value = x.right()
            py_obj, obj_type = cast_to_py_if_necessary(self._tsc, value, self._obj_type)
            self._obj_type = obj_type
            py_list.append((key, py_obj))
        return cast_to_j_if_necessary(self._func(py_list), self._tsc)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class PairUnaryMapFunction(object):

    def __init__(self, func):
        self._func = func

    def evaluate(self, obj_j_pair):
        return self._func(obj_j_pair.left(), obj_j_pair.right())

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class SeriesWithKeyUnaryMapfunctionToSeries(object):
    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def evaluate(self, obj_j_pair):
        py_obs_coll = BoundTimeSeries(self._tsc, obj_j_pair.right())
        return self._func(obj_j_pair.left(), py_obs_coll)._j_observations

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class FlatUnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, obj):
        py_obj, obj_type = cast_to_py_if_necessary(self._tsc, obj)
        self._obj_type = obj_type
        py_list = self._func(py_obj)
        return ListConverter().convert(py_list, self._tsc._gateway._gateway_client)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class SegmentFlatUnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def evaluate(self, j_seg):
        py_list = self._func(Segment(self._tsc, j_seg.observations(), j_seg.start(), j_seg.end()))
        return ListConverter().convert(py_list, self._tsc._gateway._gateway_client)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class BinaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type1 = None
        self._obj_type2 = None
        self._out_type = None

    def evaluate(self, obj_1, obj_2):
        py_obj_1, obj_type1 = cast_to_py_if_necessary(self._tsc, obj_1, self._obj_type1)
        py_obj_2, obj_type2 = cast_to_py_if_necessary(self._tsc, obj_2, self._obj_type2)
        self._obj_type1 = obj_type1
        self._obj_type2 = obj_type2
        return cast_to_j_if_necessary(self._func(py_obj_1, py_obj_2), self._tsc)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.BinaryMapFunction']


class NaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, obj):
        py_obj, obj_type = cast_to_py_if_necessary(self._tsc, obj, self._obj_type)
        self._obj_type = obj_type
        py_res = self._func(py_obj)
        return cast_to_j_if_necessary(py_res, self._tsc)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.NaryMapFunction']


class Function(object):

    def __init__(self, func):
        self._func = func

    def apply(self, obj):
        return self._func(obj)

    class Java:
        implements = ['java.util.function.Function']


# have to fix this, ObservationCollection does not have an object_id
class Interpolator(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def interpolate(self, history, future, timestamp):
        py_history = BoundTimeSeries(self._tsc, history)
        py_future = BoundTimeSeries(self._tsc, future)
        return self._func(py_history, py_future, timestamp)

    def getHistorySize(self):
        return 1

    def getFutureSize(self):
        return 1

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.Interpolator']


class SegmentUnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._func = func
        self._tsc = tsc

    def evaluate(self, j_segment):
        return self._func(Segment(self._tsc, j_segment.observations(), j_segment.start(), j_segment.end()))

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class IObjectDistanceCalculator(object):

    def __init__(self, func):
        self._func = func

    def distance(self, o_1, o_2):
        return self._func(o_1, o_2)

    class Java:
        implements = [
            'com.ibm.research.time_series.transforms.reducers.distance.dtw.algorithm.IObjectDistanceCalculator']


class FilterFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, obj):
        py_obj, obj_type = cast_to_py_if_necessary(self._tsc, obj, self._obj_type)
        self._obj_type = obj_type
        return self._func(py_obj)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.FilterFunction']


class TimeSeriesFilterFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def evaluate(self, j_ts):
        py_ts = TimeSeries.TimeSeries(self._tsc, j_ts)
        return self._func(py_ts)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.FilterFunction']

class BoundTimeSeriesFilterFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def evaluate(self, j_bts):
        py_bts = BoundTimeSeries(self._tsc, j_bts)
        return self._func(py_bts)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.FilterFunction']


class SeriesFilterFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def apply(self, j_series):
        py_series = BoundTimeSeries(self._tsc, j_series)
        return self._func(py_series)

    class Java:
        implements = ['java.util.function.Function']


class SeriesUnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._func = func
        self._tsc = tsc

    def evaluate(self, j_obs_coll):
        py_obs_coll = BoundTimeSeries(self._tsc, j_obs_coll)
        return self._func(py_obs_coll)._j_observations

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class SeriesConsumer(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def accept(self, j_series):
        py_series = BoundTimeSeries(self._tsc, j_series)
        self._func(py_series)

    class Java:
        implements = ['java.util.function.Consumer']


class ObservationToKeyUnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func
        self._obj_type = None

    def evaluate(self, j_observation):
        py_obj_value, obj_type = cast_to_py_if_necessary(self._tsc, j_observation.getValue(), self._obj_type)
        self._obj_type = obj_type
        py_observation = Observation(self._tsc, j_observation.getTimeTick(), py_obj_value)
        return self._func(py_observation)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class ReduceTimeSeriesUnaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def evaluate(self, j_ts):
        py_ts = TimeSeries.TimeSeries(self._tsc, j_ts)
        return self._func(py_ts)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']


class ValueAndTimeSeriesBinaryMapFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def evaluate(self, value, j_ts):
        py_ts = TimeSeries.TimeSeries(self._tsc, j_ts)
        return self._func(value, py_ts)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.BinaryMapFunction']


class ValueAndSeriesBiFunction(object):

    def __init__(self, tsc, func):
        self._tsc = tsc
        self._func = func

    def apply(self, j_series, state):
        py_series = BoundTimeSeries(self._tsc, j_series)
        return self._func(py_series, state)

    class Java:
        implements = ['java.util.function.BiFunction']


class IMatcher(object):

    def __init__(self, func):
        self._func = func

    def match(self, obj_1, obj_2):
        return self._func(obj_1, obj_2)

    def getInsertCost(self, l):
        return 1.0

    def getDeleteCost(self, l):
        return 1.0

    def getSubstituteCost(self, l):
        return 1.0

    def getTransposeCost(self, l):
        return 1.0

    class Java:
        implements = ['com.ibm.research.time_series.transforms.reducers.distance.dl.algorithm.IMatcher']


# class Record:
#
#     def __init__(self, tsc, **kwargs):
#         self._tsc = tsc
#         self._kwargs = kwargs
#
#     def __contains__(self, item):
#         return self._kwargs.__contains__(item)
#
#     def __call__(self, **kwargs):
#         return Record(self._tsc, **kwargs)
#
#     def get(self, key):
#         return self._kwargs.get(key)
#
#     def set(self, key, value):
#         self._kwargs[key] = value
#
#     def toString(self):
#         return str(self._kwargs)
#
#     def __getitem__(self, item):
#         return self.get(item)
#
#     def __setitem__(self, key, value):
#         self.set(key, value)
#
#     def __str__(self):
#         return str(self._kwargs)
#
#     def __iter__(self):
#         keys = self.keys()
#         while keys.hasNext():
#             n = keys.next()
#             yield (n, self.get(n))
#
#     def keys(self):
#         return ListConverter().convert(self._kwargs.keys(), self._tsc._gateway._gateway_client).iterator()
#
#     class Java:
#         implements = ['com.ibm.research.time_series.core.utils.Record']

class Record(object):

    def __init__(self, tsc, j_obj=None, **kwargs):
        self._tsc = tsc
        if j_obj is None:
            lhm = tsc._jvm.java.util.LinkedHashMap(len(kwargs))
            for k, v in kwargs.items():
                lhm.put(k, v)
            self._j_obj = tsc._jvm.com.ibm.research.time_series.core.utils.PythonRecord(lhm)
        else:
            self._j_obj = j_obj

    def __contains__(self, item):
        return self._j_obj.contains(item)

    def __call__(self, **kwargs):
        return Record(self._tsc, None, **kwargs)

    def get(self, key):
        return self._j_obj.get(key)

    def set(self, key, value):
        self._j_obj.set(key, value)

    def toString(self):
        return str(self._j_obj.toString())

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __str__(self):
        return str(self._j_obj.toString())

    def __iter__(self):
        keys = self.keys()
        while keys.hasNext():
            n = keys.next()
            yield (n, self.get(n))

    def keys(self):
        return self._j_obj.keys()

    class Java:
        implements = ['com.ibm.research.time_series.core.utils.Record']


class JavaTimeSeriesReader:

    def __init__(self, tsc, py_reader):
        self._tsc = tsc
        self._py_reader = py_reader

    def read(self, start, end, inclusive_bounds):
        py_list = self._py_reader.read(start, end, inclusive_bounds)
        py_list_j_obs = list(map(lambda obs: obs._j_observation, py_list))
        return ListConverter().convert(py_list_j_obs, self._tsc._gateway._gateway_client).iterator()

    def close(self):
        self._py_reader.close()

    def start(self):
        return self._py_reader.start()

    def end(self):
        return self._py_reader.end()

    class Java:
        implements = ['com.ibm.research.time_series.core.io.TimeSeriesReader']

class IteratorMessageSupplier:

    def __init__(self, tsc, py_supplier):
        self._tsc = tsc
        self._py_supplier = py_supplier

    def get(self):
        return ListConverter().convert(self._py_supplier(), self._tsc._gateway._gateway_client)

    class Java:
        implements = ['java.util.function.Supplier']

class JavaPullStreamMultiTimeSeriesReader:

    def __init__(self, py_reader):
        self._py_reader = py_reader

    def parse(self, message):
        return self._py_reader._parse(message)

    def read(self):
        return self._py_reader._read()

    def isFinite(self):
        return False

    def isFinished(self):
        return False

    class Java:
        implements = ['com.ibm.research.time_series.streaming.io.StreamMultiTimeSeriesReader']

class JavaPushStreamMultiTimeSeriesReader:

    def __init__(self, py_reader):
        self._py_reader = py_reader

    def parse(self, message):
        return self._py_reader._parse(message)

    def read(self):
        return self._py_reader._read()

    def isFinite(self):
        return False

    def isFinished(self):
        return False

    class Java:
        implements = ['com.ibm.research.time_series.streaming.io.StreamMultiTimeSeriesReader']

class JavaPullStreamTimeSeriesReader:

    def __init__(self, py_reader):
        self._py_reader = py_reader

    def parse(self, message):
        return self._py_reader._parse(message)

    def read(self):
        return self._py_reader._read()

    def isFinite(self):
        return False

    def isFinished(self):
        return False

    class Java:
        implements = ['com.ibm.research.time_series.streaming.io.StreamTimeSeriesReader']

class JavaPushStreamTimeSeriesReader:

    def __init__(self, py_reader):
        self._py_reader = py_reader

    def parse(self, message):
        return self._py_reader._parse(message)

    def read(self):
        return self._py_reader._read()

    def isFinite(self):
        return False

    def isFinished(self):
        return False

    class Java:
        implements = ['com.ibm.research.time_series.streaming.io.StreamTimeSeriesReader']


class JavaToPythonUnaryTransformFunction:
    def __init__(self, tsc, py_func):
        self._tsc = tsc
        self._py_func = py_func

    def call(self, j_time_series, start, end, inclusive_bounds):
        return self._py_func.evaluate(
            TimeSeries.TimeSeries(self._tsc, j_time_series),
            start,
            end,
            inclusive_bounds
        )._j_observations

    class Java:
        implements = ['com.ibm.research.time_series.core.transform.python.PythonUnaryTransformFunction']


class JavaToPythonBinaryTransformFunction:
    def __init__(self, tsc, py_func):
        self._tsc = tsc
        self._py_func = py_func

    def call(self, j_time_series_l, j_time_series_r, start, end, inclusive_bounds):
        return self._py_func.evaluate(
            TimeSeries.TimeSeries(self._tsc, j_time_series_l),
            TimeSeries.TimeSeries(self._tsc, j_time_series_r),
            start,
            end,
            inclusive_bounds
        )._j_observations

    class Java:
        implements = ['com.ibm.research.time_series.core.transform.python.PythonBinaryTransformFunction']


class JavaMultiDataSink:
    def __init__(self, tsc, python_multi_data_sink):
        self._tsc = tsc
        self._python_multi_data_sink = python_multi_data_sink

    def dump(self, observations_map):
        self._python_multi_data_sink.dump({k: BoundTimeSeries(self._tsc, v) for k, v in observations_map.items()})

    class Java:
        implements = ['com.ibm.research.time_series.streaming.functions.MultiDataSink']


class JavaDataSink:
    def __init__(self, tsc, python_data_sink):
        self._tsc = tsc
        self._python_data_sink = python_data_sink

    def dump(self, observations):
        self._python_data_sink.dump(BoundTimeSeries(self._tsc, observations))

    class Java:
        implements = ['com.ibm.research.time_series.streaming.functions.DataSink']

class JavaTimeSeriesWriteFormat:
    def __init__(self, tsc, python_time_series_writer):
        self._tsc = tsc
        self._python_time_series_writer = python_time_series_writer

    def write(self, observations, encode_value, options):
        self._python_time_series_writer.write(
            BoundTimeSeries(self._tsc, observations),
            lambda x: cast_to_py_if_necessary(self._tsc, encode_value.evaluate(x))[0],
            {key: option for key, option in options.items()}
        )

    class Java:
        implements = ['com.ibm.research.time_series.core.io.TimeSeriesWriteFormat']

class JavaMultiTimeSeriesWriteFormat:
    def __init__(self, tsc, python_time_series_writer):
        self._tsc = tsc
        self._python_time_series_writer = python_time_series_writer

    def write(self, observations_dict, encode_key, encode_value, options):
        self._python_time_series_writer.write(
            {k: BoundTimeSeries(self._tsc, observations) for k, observations in observations_dict.items()},
            lambda x: cast_to_py_if_necessary(self._tsc, encode_key.evaluate(x))[0],
            lambda x: cast_to_py_if_necessary(self._tsc, encode_value.evaluate(x))[0],
            {key: option for key, option in options.items()}
        )

    class Java:
        implements = ['com.ibm.research.time_series.core.io.MultiTimeSeriesWriteFormat']

# todo this is can slow things down considerably because it is interfacing between java and python,
# but it is important for usability
def cast_to_py_if_necessary(tsc, obj, obj_type=None):
    if obj_type is None:
        if isinstance(obj, JavaObject):
            gateway = tsc._gateway
            # if is_instance_of(gateway, obj, "com.ibm.research.time_series.core.utils.Record"):
            #     return Record(tsc, obj), 1

            if is_instance_of(gateway, obj, "com.ibm.research.time_series.core.utils.Segment"):
                return Segment(tsc, obj, obj.start(), obj.end()), 2

            elif is_instance_of(gateway, obj, "com.ibm.research.time_series.core.utils.ObservationCollection"):
                return BoundTimeSeries(tsc, obj), 3

            elif is_instance_of(gateway, obj, "com.ibm.research.time_series.core.observation.Observation"):
                return Observation(tsc, obj.getTimeTick(), obj.getValue()), 4

            elif is_instance_of(gateway, obj, "com.ibm.research.time_series.core.utils.Pair"):
                return (obj.left(), obj.right()), 5

            elif is_instance_of(gateway, obj, "com.ibm.research.time_series.core.utils.Prediction"):
                return Prediction(tsc, obj), 6
            else:
                return obj, 0
        else:
            return obj, 0
    else:
        if obj_type == 0:
            return obj, 0
        # if obj_type == 1:
        #     return Record(tsc, obj), 1
        elif obj_type == 2:
            return Segment(tsc, obj, obj.start(), obj.end()), 2
        elif obj_type == 3:
            return BoundTimeSeries(tsc, obj), 3
        elif obj_type == 4:
            return Observation(tsc, obj.getTimeTick(), obj.getValue()), 4
        elif obj_type == 5:
            return (obj.left(), obj.right()), 5
        elif obj_type == 6:
            return Prediction(tsc, obj), 6

def cast_to_j_if_necessary(obj, tsc):
    if isinstance(obj, Record):
        return obj._j_obj
    elif isinstance(obj, Segment):
        return obj._j_segment
    elif isinstance(obj, BoundTimeSeries):
        return obj._j_observations
    elif isinstance(obj, Observation):
        return obj._j_observation
    elif isinstance(obj, list):
        return ListConverter().convert(obj, tsc._gateway._gateway_client)
    elif isinstance(obj, tuple):
        return tsc._jvm.com.ibm.research.time_series.core.utils.Pair(obj[0], obj[1])
    elif isinstance(obj, dict):
        return MapConverter().convert(obj, tsc._gateway._gateway_client)
    elif isinstance(obj, Prediction):
        return obj._j_prediction
    else:
        return obj


class FastUnaryMapFunction(object):

    def __init__(self, func):
        self._func = func

    def evaluate(self, obj):
        return self._func(obj)

    class Java:
        implements = ['com.ibm.research.time_series.core.functions.UnaryMapFunction']
