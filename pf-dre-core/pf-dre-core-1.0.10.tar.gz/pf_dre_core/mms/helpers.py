# Built-in Modules
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging
import urllib.parse

# Third Party Modules
import boto3
import pandas as pd
import numpy as np
import pytz

from dotenv import load_dotenv
from pf_dre_core.utils.config import get_secrets

# Logging
logger = logging.getLogger(__name__)

DB_TYPE_MAPPING = {
    "reference": "primary-ref-r",
    "policy": "primary-rw"
}


class InvalidDBType(Exception):
    pass


def get_db_connection_string(db_type='reference'):
    """
    :param db_type Either 'reference' or 'policy'
    :return: Postgres Connection string to pass to MMS Classes
    """
    if db_type in list(DB_TYPE_MAPPING.keys()):
        sys_name = 'pf-dre/timescale/{}'.format(DB_TYPE_MAPPING[db_type])
        s = get_secrets(sys_name,
                        ["host", "pass", "port", "schema", "user"])

        dsn = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
            urllib.parse.quote(s['user']),
            urllib.parse.quote(s['pass']),
            s['host'], s['port'], s['schema'])
        return dsn


def get_db_client_kwargs(db_type='reference'):
    """
    :param db_type: Either 'reference' or 'policy'
    :return:
    """
    if db_type in list(DB_TYPE_MAPPING.keys()):
        sys_name = 'pf-dre/timescale/{}'.format(DB_TYPE_MAPPING[db_type])
        params = get_secrets(sys_name,
                             ["host", "pass", "port", "schema", "user"])

        return {
            'dbname': params['schema'],
            'user': params['user'],
            'password': params['pass'],
            'host': params['host'],
            'port': params['port'],
        }
    else:
        msg = "DB type must be one of {}, not {}".format(
            list(DB_TYPE_MAPPING.keys()),
            db_type)
        logger.error(msg)
        raise InvalidDBType(msg)


def populate_forecast_df(df, received_date, device_id, measurement_df,
                         schema='json', check_duplicates=False):
    """
    :param df: Dataframe to be updated
    :param received_date: Datetime in ISO 8601 format
    '%Y-%m-%dT%H:%M:%S+00:00'
    :type received_date str
    :param measurement_df: Data Frame for the forecast containing index,
    'measurement_date' and columns for each metric.
    :type measurement_df `pd.DataFrame`
    :param device_id: id in devices table
    :type device_id int
    :param schema: json or narrow
    :type schema str
    :param check_duplicates:
    :type check_duplicates bool
    :return: Updated dataframe
    :param df: Dataframe to be updated

    :param device_id: String id in devices table
    :param metrics: Python object of device_metric_type_id: value (numeric)
    :param schema: json or narrow
    :return: Updated dataframe
    """
    # TODO: Check for null Values in measurement_df
    if schema == 'json':
        if df is None:
            df = pd.DataFrame(columns=['received_date',
                                       'device_id',
                                       'metrics'])
        if check_duplicates:
            # Only append if unique new key
            if ((df['received_date'] == received_date)
                    & (df['device_id'] == device_id)).any():
                return df
        metrics = measurement_df.to_dict()
        df = df.append({'received_date': received_date,
                        'device_id': device_id,
                        'metrics': json.dumps(metrics)}, ignore_index=True)
        return df
    else:
        raise NotImplementedError


def populate_df(df, measurement_date, device_id, metrics, schema='json',
                check_duplicates=False):
    """
    :param df: Data Frame to be updated
    :param measurement_date: Datetime in ISO 8601 format
    '%Y-%m-%dT%H:%M:%S+00:00'
    :type measurement_date str
    :param device_id: id in devices table
    :type device_id int
    :param metrics: Python object of device_metric_type_id: value (numeric)
    :type metrics: object
    :param schema: json or narrow
    :type schema str
    :param check_duplicates:
    :type check_duplicates bool
    :return: Updated dataframe
    """
    if schema == 'json':
        if df is None:
            df = pd.DataFrame(columns=['measurement_date',
                                       'device_id',
                                       'metrics'])
        if check_duplicates:
            # Only append if unique new key
            if ((df['measurement_date'] == measurement_date)
                    & (df['device_id'] == device_id)).any():
                return df

        df = df.append({'measurement_date': measurement_date,
                        'device_id': device_id,
                        'metrics': json.dumps(metrics)}, ignore_index=True)
    if schema == 'narrow':
        if df is None:
            df = pd.DataFrame(
                columns=['measurement_date', 'device_id',
                         'device_metric_type_id', 'value'])

        for metric, value in metrics.items():
            if check_duplicates:
                if ((df['measurement_date'] == measurement_date)
                        & (df['device_id'] == device_id)
                        & (df['device_metric_type_id'] == metric)).any():
                    # Only append if unique new key
                    continue
            df = df.append({'measurement_date': measurement_date,
                            'device_id': device_id,
                            'device_metric_type_id': metric,
                            'value': value,
                            'received_date': measurement_date},
                           ignore_index=True)
    return df


def apply_standard_index(df, dropna=False):
    """
    Data frame containing columns
     (measurement_date, device_id, device_metric_type_id, value)
    has multi-index applied and the contents of the index are sorted in
    ascending order.
    :param df: Tabular Data Frame with generic pandas index and the
        following columns:
            'device_id' (int)
            'device_metric_type_id' (string)
            'measurement_date' (string)
            'value' (float)
    :param dropna: Boolean, rows with null/ NaN value will be removed
    :return: Standardized Data Frame
    """
    idx = ['device_id', 'device_metric_type_id', 'measurement_date']
    df.set_index(idx, inplace=True)
    # Only need the value column
    df.drop(df.columns.difference(['value']), 1, inplace=True)
    df.index = df.index.set_levels(
        [df.index.levels[0].astype('int64'),
         df.index.levels[1],
         pd.to_datetime(df.index.levels[2]).tz_convert(tz=pytz.utc)])
    # Have time displayed from least recent to most recent.
    # Still grouped by device_id, metric_type first
    if dropna:
        df.dropna(inplace=True)
    df.sort_index(inplace=True, ascending=True)


def apply_forecast_index(df, dropna=False):
    """
    Data frame containing columns
    (received_date, device_id, device_metric_type_id, measurement_date, value)
    has multi-index applied and the contents of the index are sorted in
    ascending order.
    :param df: Tabular Data Frame with generic pandas index and the
    following columns:
        'received_date' (string)
        'device_id' (int)
        'device_metric_type_id' (string)
        'measurement_date' (string)
        'value' (float)
    :param dropna: Boolean, rows with null/ NaN value will be removed
    :return: Standardized Data Frame
    """
    idx = ['received_date', 'device_id',
           'device_metric_type_id', 'measurement_date']
    df.set_index(idx, inplace=True)
    # Only need the metrics column
    df.drop(df.columns.difference(['value']), 1, inplace=True)
    df.index = df.index.set_levels(
        [pd.to_datetime(df.index.levels[0]).tz_convert(tz=pytz.utc),
         df.index.levels[1].astype('int64'),
         df.index.levels[2],
         pd.to_datetime(df.index.levels[3]).tz_convert(tz=pytz.utc)])
    # Have time displayed from least recent to most recent.
    # Still grouped by device_id, metric_type first
    if dropna:
        df.dropna(inplace=True)
    df.sort_index(inplace=True, ascending=True)


def apply_simulation_index(df, dropna=False):
    """
        Data frame containing columns
        (simulation_name, received_date, device_id,
         device_metric_type_id, measurement_date, value)
        has multi-index applied and the contents of the index are sorted in
        ascending order.
        :param df: Tabular Data Frame with generic pandas index and the
        following columns:
            'simulation_name' (string)
            'received_date' (string)
            'device_id' (int)
            'device_metric_type_id' (string)
            'measurement_date' (string)
            'value' (float)
        :param dropna: Boolean, rows with null/ NaN value will be removed
        :return: Standardized Data Frame
    """
    idx = ['simulation_id', 'received_date',
           'device_id', 'device_metric_type_id',
           'measurement_date']
    df.set_index(idx, inplace=True)
    # Only need the value column
    df.drop(df.columns.difference(['value']), 1, inplace=True)
    df.index = df.index.set_levels(
        [df.index.levels[0],
         pd.to_datetime(df.index.levels[1]).tz_convert(tz=pytz.utc),
         df.index.levels[2].astype('int64'),
         df.index.levels[3],
         pd.to_datetime(df.index.levels[4]).tz_convert(tz=pytz.utc)])
    # Have time displayed from least recent to most recent.
    # Still grouped by device_id, metric_type first
    if dropna:
        df.dropna(inplace=True)
    df.sort_index(inplace=True, ascending=True)


def validate_timestamp(ts):
    """
    Check whether ts is a datetime object
    :param datetime ts: Datetime to be localized, can be tz-naive or aware
    :return: The localized timestamp or a value error if a datetime object is
    not passed
    """
    if isinstance(ts, datetime):
        ts = ts.astimezone(pytz.utc)
    else:
        raise ValueError("Reference Time must be type datetime but was"
                         " '{0}'".format(type(ts)))
    return ts


def get_ts_conditional_vals(reference_time=None, window=None):
    """
    All timestamp based conditionals passed to the database must be in UTC.
    :param reference_time: Timestamp which is the upper bound of the time index
    (exclusive)
    :param window: The number of minutes prior to reference_time which forms
    the time interval for the query.
    :return:
    """
    if reference_time is None:
        reference_time = datetime.utcnow()
    else:
        reference_time = validate_timestamp(reference_time)
    ts_end = reference_time.isoformat(sep=' ', timespec='milliseconds')
    ts_start = (reference_time - timedelta(minutes=window))\
        .isoformat(sep=' ', timespec='milliseconds')

    return [ts_start, ts_end]


def get_clean_df(df, columns=None, min_size=None, all=False):
    """
    Handles any rows in the the dataframe where values in 'columns' are NAN by
    splitting the table. This ensures that a continguous dataframe result is
    returned.
    :param df: The dataframe to be cleaned by removing NAN columns
    :param columns: List of columns where NAN values are to be removed.
    :param min_size: The minimum number of rows required for dataframe to be
    returned.
    :param all: Boolean indicating whether all of the split dataframe blocks
    should be returned. The default value False ensures that only the latest
    clean datafram is returned.
    :return:
    Either a single dataframe or a list of dataframse if all = True.
    """
    if columns is None:
        # Split DataFrame on NaN values in any of 'columns'
        df_split = np.split(df, np.where(np.isnan(df))[0])
        # removing NaN entries
        df_split = [df.dropna() for df in df_split
                    if not isinstance(df, np.ndarray)]
    else:
        # Split DataFrame on NaN values in any of 'columns'
        df_split = np.split(df, np.where(np.isnan(df.loc[:, columns]))[0])
        # removing NaN entries
        df_split = [df.dropna(subset = columns) for df in df_split
                    if not isinstance(df, np.ndarray)]
    if min_size is not None:
        # Filter DataFrame by Size
        df_split = [df for df in df_split if len(df.index) >= min_size]
    if all:
        return df_split
    else:
        return df_split[-1]


def filter_std_df(df, metrics=None, device_ids=None, received_date=None,
                  simulation=None, ignore_nan=True):
    if received_date is None:
        received_date = []
    metrics = metrics if \
        not metrics or type(metrics) is list else [metrics]
    device_ids = device_ids if \
        not device_ids or type(device_ids) is list else [device_ids]
    rcv_date = received_date if \
        not received_date or type(received_date) is list else [received_date]
    simulation = simulation if \
        not simulation or type(simulation) is list else [simulation]
    filtered_df = df.copy()
    if simulation:
        filtered_df = filtered_df[filtered_df.index.get_level_values(
            'simulation_id').isin(simulation)]
    if rcv_date:
        filtered_df = filtered_df[filtered_df.index.get_level_values(
            'received_date').isin(rcv_date)]
    if device_ids:
        filtered_df = filtered_df[filtered_df.index.get_level_values(
            'device_id').isin(device_ids)]
    if metrics:
        filtered_df = filtered_df[filtered_df.index.get_level_values(
            'device_metric_type_id').isin(metrics)]
    if ignore_nan:
        filtered_df = filtered_df.dropna()
    return filtered_df


def get_lvfm(df, metric, device_id=None, ignore_nan=True):
    """
    Get Last Value For Metric from a dataframe, df in the standardized format
    :return: Value
    """
    if device_id is None:
        df_for_metric = df.xs(metric, level='device_metric_type_id')
        if ignore_nan:
            df_for_metric = df_for_metric.dropna()
        return df_for_metric.iloc[-1]['value']
    else:
        df_for_device_metric = df.loc[(device_id, metric), 'value']
        if ignore_nan:
            df_for_device_metric = df_for_device_metric.dropna()
        return df_for_device_metric.iloc[-1]


def get_fvfm(df, metric, device_id=None, ignore_nan=True):
    """
    Get First Value For Metric from a dataframe, df in the standardized format
    :return: Value
    """
    if device_id is None:
        df_for_metric = df.xs(metric, level='device_metric_type_id')
        if ignore_nan:
            df_for_metric = df_for_metric.dropna()
        return df_for_metric.iloc[0]['value']
    else:
        df_for_device_metric = df.loc[(device_id, metric), 'value']
        if ignore_nan:
            df_for_device_metric = df_for_device_metric.dropna()
        return df_for_device_metric.iloc[0]
