#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in Modules
import logging
import json
from abc import ABC

# Third Party Modules
import pandas as pd
from psycopg2 import sql

# Project Specific Modules
from pf_dre_core.mms import TimescaleClient
from pf_dre_core.mms import helpers as h

# Logging
logger = logging.getLogger(__name__)


class TimescaleClientNarrow(TimescaleClient, ABC):
    def __init__(self, dsn, tbl_name, standardized=True):
        pk = ['measurement_date', 'device_id', 'device_metric_type_id']
        TimescaleClient.__init__(self, dsn, tbl_name, pk, standardized)

    @staticmethod
    def get_agg_str(agg):
        if agg == 'avg':
            return "{0}(value)".format(agg)
        else:
            return "{0}(value, measurement_date)".format(agg)

    @staticmethod
    def standardize_df(df, **kwargs):
        """
        Convert Data Frame returned from Query into the standard pandas DF
        result format by creating a multiIndex on
        device_id, device_metric_type_id, measurement_date.
        :param df: Raw query Data Frame with generic pandas index and the
        following columns:
            'device_id' (int)
            'device_metric_type_id' (string)
            'measurement_date' (string)
            'value' (float)
        :return: Data frame in the format:
            - Index = ('measurement_date', 'device_id', 'device_metric_type_id')
            - Columns = ['value']
        """
        h.apply_standard_index(df, dropna=kwargs.get('dropna', False))
        return df

    def df_to_schema(self, df):
        """
        :param df: Dataframe to be updated
        This dataframe must have all the key metrics required for the schema in
        order to generate a valid dataframe.
        """
        if type(df.index) != pd.RangeIndex:
            df.reset_index(inplace=True)
        return df

    def get_all_metrics(self, device_ids, metrics, ts_start, ts_end):
        query = sql.SQL(
            "SELECT * "
            "FROM {} "
            "WHERE device_id IN ({}) "
            "AND device_metric_type_id IN ({}) "
            "AND measurement_date >= %s "
            "AND measurement_date <= %s ") \
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              device_ids +
                              metrics +
                              [h.validate_timestamp(ts_start),
                               h.validate_timestamp(ts_end)])

        return df

    def get_aggregated_metrics(self, res, device_ids, metrics,
                               ts_start, ts_end, agg='avg', fill=None):
        self.allowed_agg(agg)

        if fill == 'locf':
            # Linear interpolation between points
            value_str = "locf({0}) AS value".format(self.get_agg_str(agg))
        elif fill == 'interpolate':
            # Last Observation Carried Forward
            value_str = "interpolate({0}) AS value"\
                .format(self.get_agg_str(agg))
        elif fill == 'zero':
            # Last Observation Carried Forward
            value_str = "COALESCE({0}, 0) AS value" \
                .format(self.get_agg_str(agg))
        else:
            value_str = "{0} AS value".format(self.get_agg_str(agg))
        query = sql.SQL(
            "SELECT "
            "time_bucket_gapfill({}, measurement_date) as time, "
            "device_id, device_metric_type_id, {} "
            "FROM {} "
            "WHERE device_id IN ({}) "
            "AND device_metric_type_id IN ({}) "
            "AND measurement_date >= %s "
            "AND measurement_date < %s "
            "GROUP BY device_id, device_metric_type_id, time") \
            .format(sql.Literal(res),
                    sql.SQL(value_str),
                    sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              device_ids + metrics +
                              [h.validate_timestamp(ts_start),
                               h.validate_timestamp(ts_end)])
        return df

    def get_num_readings(self, device_ids, ts_start, ts_end, simulation=None):
        """
        :param device_ids: A list of device_ids to be queried
        :param simulation: Set a simulation name to lookup in the DB
        :param ts_start: Start time for the measurement_date index to be
        scanned (inclusive) [Datetime]
        :param ts_end: End time for the measurement_date index to be
        scanned (exclusive) [Datetime]
        :return: Data Frame in raw or standardized format:
        """
        cond = ""
        cond_vals = device_ids + [h.validate_timestamp(ts_start),
                                  h.validate_timestamp(ts_end)]
        if simulation is not None:
            cond = "AND simulation = %s "
            cond_vals.append(simulation)
        query = sql.SQL(
            "SELECT DISTINCT(device_id) as device_id, "
            "COUNT(device_id) as count "
            "FROM {} "
            "WHERE device_id IN ({}) "
            "AND measurement_date BETWEEN %s AND %s "
            "{}"
            "GROUP BY measurement_date, device_id") \
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(cond))
        old_state = self.standardized
        self.standardized = False
        df = self.query_to_df(query, cond_vals, dropna=True)
        self.standardized = old_state
        df.set_index('device_id', inplace=True)
        return df

    def get_latest_metrics(self, device_ids, metrics,
                           reference_time=None, window=None):
        """
        :param device_ids: A list of device_ids to be queried
        :param metrics: A list of metrics (Strings) to be queried for
        each device_id
        :param reference_time: Set a reference time for when the latest values
        are to be queried for. If this is not set the latest values for now will
        be queried. [Datetime]
        :param window: [Optional] The number of minutes prior to now that the
        latest values
        should be queried from.
        :return: Data Frame in raw or standardized format:
        """

        query = sql.SQL(
            "SELECT device_id, "
            "device_metric_type_id, "
            "last(measurement_date, measurement_date) AS measurement_date, "
            "last(value, measurement_date) AS value "
            "FROM {} "
            "WHERE device_id IN ({}) "
            "AND device_metric_type_id IN ({}) "
            "AND measurement_date >= %s "
            "AND measurement_date <= %s "
            "GROUP BY device_id, device_metric_type_id") \
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              device_ids + metrics +
                              h.get_ts_conditional_vals(reference_time, window),
                              dropna=True)
        return df


class TimescaleClientJSON(TimescaleClient, ABC):
    """
    Inheriting from the TimescaleClient base class, this class is used for
    accessing, and modifying instantaneous device metric data in the MMS.
    """
    def __init__(self, dsn, tbl_name, standardized=True):
        pk = ['measurement_date', 'device_id']
        TimescaleClient.__init__(self, dsn, tbl_name, pk, standardized)

    @staticmethod
    def get_value_str_single(agg, m):
        if agg == 'avg':
            return "{0}((metrics->>'{1}')::numeric)".format(agg, m)
        else:
            return "{0}((metrics->>'{1}')::numeric, measurement_date)"\
                .format(agg, m)

    @staticmethod
    def get_value_str(agg):
        x = "(metrics->>m.m)::NUMERIC"
        if agg == 'avg':
            return "{}({})".format(agg, x)
        else:
            return "{}({}, measurement_date)".format(agg, x)

    def df_to_schema(self, df):
        """
        :param df: Data frame to be updated
        This data frame must have all the key metrics required for the schema in
        order to generate a valid data frame.
        """
        if type(df.index) != pd.RangeIndex:
            df.reset_index(inplace=True)
        if {'value', 'device_metric_type_id'}.issubset(df.columns.tolist()):
            df = df.pivot(index=self.pk,
                          columns='device_metric_type_id',
                          values='value').rename_axis(None, axis=1)
            columns = df.columns.tolist()
            df['metrics'] = [
                {k: v for k, v in m.items()
                 if pd.notnull(v)}
                for m in df[columns].to_dict(orient='records')
            ]
            df['metrics'] = df['metrics'].apply(json.dumps)
            df = df.drop(columns=columns)
            df.reset_index(inplace=True)
            return df
        else:
            raise ValueError("Unable to parse dataframe")

    def standardize_raw_df(self, df, metrics=None, dropna=False):
        """
        Convert JSON blob 'metrics' from query into the standard
        pandas DF
        result format.
        :param df: Data frame matching the timescale JSON schema.
        :param metrics: List of metrics to be returned in the standard DF
        :param dropna: Boolean to indicate whether NaN rows should be removed
        :return: Data frame in the format:
            - Index = ('measurement_date', 'device_id', 'device_metric_type_id')
            - Columns = ['value']
        """

        # If the query returned raw rows (i.e. the metrics column), the JSON
        # data must be processed.
        if metrics is None:
            metrics = []
        if 'metrics' in list(df.columns):
            # Convert the JSON column to a pandas Series,
            # this creates columns for each key in the JSON
            try:
                # Datatype of Metrics column should always be json.
                df['metrics'] = df['metrics'].apply(json.loads)
            except TypeError:
                pass

            df = pd.concat([df.drop(['metrics'], axis=1),
                            df['metrics']
                           .apply(pd.Series)], axis=1)

            # Filter the columns so only the requested metrics are stored
            if metrics:
                df = df[[c for c in df.columns if c in self.pk + metrics]]
        # Unpivot the DataFrame so the metric columns are compiled into
        # a single key value column pairing (number of DF rows increase)
        df = df.melt(
            id_vars=self.pk,
            var_name='device_metric_type_id',
            value_name='value'
        )
        h.apply_standard_index(df, dropna=dropna)
        return df

    def get_all_metrics(self, device_ids, metrics, ts_start, ts_end):
        query = sql.SQL(
            "SELECT "
            "measurement_date, "
            "device_id, "
            "m.m AS device_metric_type_id, "
            "{} AS value "
            "FROM {} j, jsonb_object_keys(j.metrics) AS m "
            "WHERE device_id IN ({}) "
            "AND m.m IN ({}) "
            "AND measurement_date >= %s "
            "AND measurement_date <= %s "
            "GROUP BY 1, 2, 3")\
            .format(sql.SQL(self.get_value_str('avg')),
                    sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              device_ids + metrics +
                              [h.validate_timestamp(ts_start),
                               h.validate_timestamp(ts_end)])
        return df

    def get_aggregated_metrics(self, res, device_ids, metrics,
                               ts_start, ts_end, agg='avg', fill=None):
        self.allowed_agg(agg)

        if fill in ['locf', 'interpolate']:
            # Last Observation Carried Forward
            value_col = "{}({})".format(fill, self.get_value_str(agg))
        elif fill == 'zero':
            value_col = "COALESCE({}, 0)".format(self.get_value_str(agg))
        else:
            value_col = "{}".format(self.get_value_str(agg))

        query = sql.SQL(
            "SELECT "
            "time_bucket_gapfill({}, measurement_date) AS time, "
            "device_id, "
            "m.m AS device_metric_type_id, "
            "{} AS value "
            "FROM {} j, jsonb_object_keys(j.metrics) AS m "
            "WHERE device_id IN ({}) "
            "AND m.m IN ({}) "
            "AND measurement_date >= %s "
            "AND measurement_date < %s "
            "GROUP BY 1, 2, 3")\
            .format(sql.Literal(res),
                    sql.SQL(value_col),
                    sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              device_ids + metrics +
                              [h.validate_timestamp(ts_start),
                               h.validate_timestamp(ts_end)])
        return df

    def get_num_readings(self, device_ids, ts_start, ts_end):
        """
        :param device_ids: A list of device_ids to be queried
        :param ts_start: Start time for the measurement_date index to be
        scanned (inclusive) [Datetime]
        :param ts_end: End time for the measurement_date index to be
        scanned (exclusive) [Datetime]
        :return: Data Frame in raw or standardized format:
        """
        cond_vals = device_ids + [h.validate_timestamp(ts_start),
                                  h.validate_timestamp(ts_end)]
        query = sql.SQL(
            "SELECT device_id, "
            "COUNT(*) as count "
            "FROM {} "
            "WHERE device_id IN ({}) "
            "AND measurement_date BETWEEN %s AND %s "
            "GROUP BY device_id") \
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)))
        old_state = self.standardized
        self.standardized = False
        df = self.query_to_df(query,
                              cond_vals,
                              dropna=True)
        self.standardized = old_state
        df.set_index('device_id', inplace=True)
        return df

    def get_latest_metrics(self, device_ids, metrics,
                           reference_time=None, window=None):
        """
        :param device_ids: A list of device_ids to be queried
        :param metrics: A list of metrics (Strings) to be queried for
        each device_id
        :param reference_time: Set a reference time for when the latest values
        are to be queried for. If this is not set the latest values for now will
        be queried. [Datetime]
        :param window: [Optional] The number of minutes prior to now that the
        latest values
        should be queried from.
        :return: Data Frame in raw or standardized format:
        """
        query = sql.SQL(
            "SELECT "
            "last(measurement_date, measurement_date) AS measurement_date, "
            "device_id, "
            "m.m AS device_metric_type_id, "
            "{} AS value "
            "FROM {} j, jsonb_object_keys(j.metrics) AS m "
            "WHERE device_id IN ({}) "
            "AND m.m IN ({}) "
            "AND measurement_date BETWEEN %s AND %s "
            "GROUP BY device_id, device_metric_type_id") \
            .format(sql.SQL(self.get_value_str('last')),
                    sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              device_ids + metrics +
                              h.get_ts_conditional_vals(reference_time, window),
                              dropna=True)
        return df
