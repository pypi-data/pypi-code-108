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

import datetime

from py4j.java_collections import ListConverter, MapConverter

from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries import MultiTimeSeries
from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS


class Factory:

    def __init__(self, tsc):
        self._tsc = tsc

    # def text_file(self, path, key_func, timestamp_func=None, skip_num_lines=0, sort=False):
    #     if timestamp_func is None:
    #         return MultiTimeSeries(
    #             self._tsc,
    #             self._tsc._jvm.com.ibm.research.data_structures.core.timeseries.MultiTimeSeries.textFile(
    #                 path,
    #                 utils.Function(key_func),
    #                 skip_num_lines,
    #                 sort
    #             )
    #         )
    #     else:
    #         return MultiTimeSeries(
    #             self._tsc,
    #             self._tsc._jvm.com.ibm.research.data_structures.core.utils.PythonConnector.textFile(
    #                 path,
    #                 utils.Function(key_func),
    #                 utils.Function(timestamp_func),
    #                 skip_num_lines,
    #                 sort
    #             )
    #         )

    # def csv(self, path, key_func, timestamp_func, value_func, delimiter=",", skip_num_lines=0, sort=False):
    #     return MultiTimeSeries(
    #         self._gateway,
    #         self._jvm,
    #         self._jvm.com.ibm.research.data_structures.core.timeseries.MultiTimeSeries.csv(
    #             path,
    #             delimiter,
    #             utils.Function(key_func),
    #             utils.Function(timestamp_func),
    #             utils.Function(value_func),
    #             skip_num_lines,
    #             sort
    #         )
    #     )

    def from_observations(self, list_key_observation_pairs):
        return MultiTimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.timeseries.MultiTimeSeries.fromObservations(
                ListConverter().convert(
                    list(map(
                        lambda tup: self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(tup[0], tup[1]._j_observation),
                        list_key_observation_pairs
                    )), self._tsc._gateway._gateway_client)
            )
        )

    def df_instants(self, df, key_columns=None, ts_column=None, granularity=None, start_time=None):
        keys = df.keys()
        keys_dict = {k: str(df[k].dtype) for k in keys}
        json_str = df.to_json()

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

        ts_index = None
        if ts_column is not None:
            ts_index = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(ts_column, keys_dict.get(ts_column))
            keys_dict.pop(ts_column)

        if key_columns is not None:
            keys_dict = {k: v for k, v in keys_dict.items() if k in key_columns}

        return MultiTimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameInstantsJsonString(
                json_str,
                ts_index,
                MapConverter().convert(keys_dict, self._tsc._gateway._gateway_client),
                j_trs
            )
        )


    def df_observations(self, df, key_column, ts_column=None, value_column=None, granularity=None, start_time=None):
        keys = df.keys()
        keys_dict = {k: str(df[k].dtype) for k in keys}
        json_str = df.to_json(orient="records")

        key_pair = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(key_column, keys_dict[key_column])
        keys_dict.pop(key_column)

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
                return MultiTimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        key_pair,
                        None,
                        MapConverter().convert(keys_dict, self._tsc._gateway._gateway_client),
                        j_trs
                    )
                )
            else:
                ts_pair = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(ts_column,
                                                                                       keys_dict.get(ts_column))
                keys_dict.pop(ts_column)
                if isinstance(value_column, list):
                    keys_dict = {k: v for k, v in keys_dict.items() if k in value_column}

                return MultiTimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        key_pair,
                        ts_pair,
                        MapConverter().convert(keys_dict, self._tsc._gateway._gateway_client),
                        j_trs
                    )
                )
        else:
            value_pair = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(value_column,
                                                                                       keys_dict.get(value_column))
            if ts_column is None:
                return MultiTimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        key_pair,
                        None,
                        value_pair,
                        j_trs
                    )
                )
            else:
                ts_pair = self._tsc._jvm.com.ibm.research.time_series.core.utils.Pair(ts_column,
                                                                                      keys_dict.get(ts_column))
                keys_dict.pop(ts_column)
                return MultiTimeSeries(
                    self._tsc,
                    self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.readDataFrameJsonString(
                        json_str,
                        key_pair,
                        ts_pair,
                        value_pair,
                        j_trs
                    )
                )

    def dict(self, ts_dict, granularity=None, start_time=None):
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

        j_ts_map = self._tsc._jvm.java.util.HashMap()
        for k, v in ts_dict.items():
            try:
                if trs is None:
                    j_ts_map.put(k, v._j_ts)
                else:
                    if v._j_ts.getTRS() is None:
                        raise Exception("your time series does not have a TRS and therefore cannot re-set the TRS")

                    j_ts_map.put(k, v._j_ts.withTRS(j_trs))
            except:
                if trs is None:
                    j_ts_map.put(k, self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.fromObservations(v._j_observations))
                else:
                    j_ts_map.put(k, self._tsc._jvm.com.ibm.research.time_series.core.timeseries.TimeSeries.fromObservations(v._j_observations, j_trs))

        return MultiTimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.timeseries.MultiTimeSeries(j_ts_map)
        )

