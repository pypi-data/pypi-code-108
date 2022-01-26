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

import sys

from py4j.java_collections import ListConverter, MapConverter

from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
import datetime
from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
from autoai_ts_libs.deps.tspy.data_structures import utils


class Factory:

    def __init__(self, tsc):
        self._tsc = tsc

    def from_observations(self, observations, granularity=None, start_time=None):
        if granularity is None and start_time is None:
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.fromObservations(observations._j_observations)
            )
        else:
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            trs = TRS(self._tsc, granularity, start_time)
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.fromObservations(
                    observations._j_observations,
                    trs._j_trs
                ),
                trs
            )


    def list(self, list_of_values, ts_func=None, granularity=None, start_time=None):
        if granularity is None and start_time is None:
            list_of_values = [utils.cast_to_j_if_necessary(v, self._tsc) for v in list_of_values]
            if ts_func is None:
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.list(
                        ListConverter().convert(list_of_values, self._tsc._gateway._gateway_client)
                    )
                )
            else:
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.list(
                        ListConverter().convert(list_of_values, self._tsc._gateway._gateway_client),
                        utils.Function(ts_func)
                    )
                )
        else:
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            trs = TRS(self._tsc, granularity, start_time)
            list_of_values = [utils.cast_to_j_if_necessary(v, self._tsc) for v in list_of_values]
            if ts_func is None:
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.list(
                        ListConverter().convert(list_of_values, self._tsc._gateway._gateway_client),
                        trs._j_trs
                    ),
                    trs
                )
            else:
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.list(
                        ListConverter().convert(list_of_values, self._tsc._gateway._gateway_client),
                        utils.Function(ts_func),
                        trs._j_trs
                    ),
                    trs
                )

    def reader(self, time_series_reader, granularity=None, start_time=None):
        if granularity is None and start_time is None:
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.reader(
                    utils.JavaTimeSeriesReader(self._tsc, time_series_reader)
                )
            )
        else:
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            trs = TRS(self._tsc, granularity, start_time)
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.reader(
                    utils.JavaTimeSeriesReader(self._tsc, time_series_reader),
                    trs._j_trs
                ),
                trs
            )

    def mq(self, host, queue_name, cache_size=sys.maxsize, to_timestamp_op=None):
        if to_timestamp_op is None:
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.mq.timeseries.MQTimeSeries.mq(
                    host,
                    queue_name,
                    cache_size
                )
            )
        else:
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.mq.timeseries.MQTimeSeries.mq(
                    host,
                    queue_name,
                    cache_size,
                    utils.UnaryMapFunction(self._tsc, to_timestamp_op)
                )
            )

    def kafka(self, topic, host="localhost", port=9092, cache_size=sys.maxsize, to_timestamp_op=None):
        if to_timestamp_op is None:
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.kafka.timeseries.KafkaTimeSeries.kafka(
                    host, port, topic, cache_size
                )
            )
        else:
            return TimeSeries(
                self._tsc,
                self._tsc._jvm.com.ibm.research.time_series.kafka.timeseries.KafkaTimeSeries.kafka(
                    host, port, topic, cache_size, utils.UnaryMapFunction(self._tsc, to_timestamp_op)
                )
            )

    def df(self, df, ts_column=None, value_column=None, granularity=None, start_time=None):
        json_str = df.to_json(orient="records")
        keys = df.keys()
        keys_dict = {k: str(df[k].dtype) for k in keys}

        if granularity is None and start_time is None:
            trs = None
            j_trs = None
        else:
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            trs = TRS(self._tsc, granularity, start_time)
            j_trs = trs._j_trs

        if value_column is None or isinstance(value_column, list):

            if ts_column is None:
                if isinstance(value_column, list):
                    keys_dict = {k: v for k, v in keys_dict.items() if k in value_column}
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        None,
                        MapConverter().convert(keys_dict, self._tsc._gateway._gateway_client),
                        j_trs
                    ),
                    trs
                )
            else:
                ts_pair = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(ts_column, keys_dict[ts_column])
                keys_dict.pop(ts_column)
                if isinstance(value_column, list):
                    keys_dict = {k: v for k, v in keys_dict.items() if k in value_column if k != ts_column}
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        ts_pair,
                        MapConverter().convert(keys_dict, self._tsc._gateway._gateway_client),
                        j_trs
                    ),
                    trs
                )
        else:

            if ts_column is None:
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        None,
                        self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(value_column, keys_dict[value_column]),
                        j_trs
                    ),
                    trs
                )
            else:
                return TimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(ts_column, keys_dict[ts_column]),
                        self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(value_column, keys_dict[value_column]),
                        j_trs
                    ),
                    trs
                )
