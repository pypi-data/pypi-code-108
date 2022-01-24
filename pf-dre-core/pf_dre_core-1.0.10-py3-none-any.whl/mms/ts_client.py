#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in Modules
import logging
import csv
from io import StringIO

# Third Party Modules
import pandas as pd
from pandas.io.sql import DatabaseError
import psycopg2
from psycopg2 import extras

# Project Specific Modules
from pf_dre_core.mms.base import BaseClient
from pf_dre_core.mms import helpers as h

# Logging
logger = logging.getLogger(__name__)


class TimescaleClient(BaseClient):
    """
    The following base class is used to read data to and write data from the
    postgres Meter Management System using TimescaleDB for timeseries data.
    """

    def __init__(self, dsn, tbl_name, pk, standardized=True):
        BaseClient.__init__(self, dsn)
        self.tbl_name = tbl_name
        self.standardized = standardized
        self.pk = pk
        self.allowed_aggs = ['first', 'last', 'avg']

    def standardize_df(self, df, dropna=False):
        """
        Convert Data Frame returned from Query into the standard pandas DF
        result format by creating a multiIndex on
        device_id, device_metric_type_id, measurement_date.
        :param df: Tabular Data Frame with generic pandas index and the
        following columns:
            'simulation_name' (string) [ONLY for Simulation DFs]
            'received_date' (string) [ONLY for Simulation and Forecast DFs]
            'device_id' (int)
            'device_metric_type_id' (string)
            'measurement_date' (string)
            'value' (float)
        :param dropna: Boolean, rows with null/ NaN value will be removed
        :return: Data frame in the format:
            - Index = (['simulation_name',
                       'received_date'],
                       'measurement_date',
                       'device_id',
                       'device_metric_type_id')
            - Columns = ['value']
        """
        if 'simulation_id' in self.pk:
            # Simulation Index
            h.apply_simulation_index(df, dropna=dropna)
        elif 'received_date' in self.pk:
            # Forecast Index
            h.apply_forecast_index(df, dropna=dropna)
        else:
            # Real Time Index
            h.apply_standard_index(df, dropna=dropna)
        return df

    def rollback(self, keep_alive=False):
        self.conn.rollback()
        if not keep_alive:
            self.conn.close()

    def commit(self):
        self.conn.commit()
        self.conn.close()

    def allowed_agg(self, agg):
        if agg not in self.allowed_aggs:
            raise ValueError("agg must be one of: {0}"
                             .format(self.allowed_aggs))
        return

    def query_to_df(self, query, qry_params, **standardize_args):
        try:
            df = pd.read_sql(query,
                             con=self.conn,
                             params=qry_params)
            if df.empty:
                return None
            df.rename(columns={'time': 'measurement_date'}, inplace=True)

            if self.standardized:
                df = self.standardize_df(df, **standardize_args)
            return df

        except DatabaseError as error:
            logger.error("DB Error: {0}".format(error))
            return None

        except psycopg2.Error as error:
            logger.error("psycopg2 Error: {0}".format(error))
            self.rollback()
            return None

    def df_to_schema(self, df):
        return df

    def get_all_metrics(self, *args):
        raise NotImplementedError

    def get_aggregated_metrics(self, *args):
        raise NotImplementedError

    def df_from_data_model(self, data_model, res, ts_start, ts_end):
        """
        Using the standardized data_model object format:

        "features": <-- Forms the columns of the Dataframe
            "feature_name>: <-- DataFrame Column Name
                <timeseries_name>: <Arithmetic operation>
                ...Dict of Timeseries (From MMS Queries)...
                <timeseries_name>: <Arithmetic operation>
            ...Dict of Features...
            "uncontrollable_demand":
                net_demand: '+'
                pv_generation: '-'
                controllable_generation: '-'
        "timeseries":
            <timeseries_name>:
                "device_ids":
                    - <device_id> INT
                "metrics":
                    - <device_metric_type_id>
                "agg": <aggregate method>
                "fill": <fill method>
            ...Dict of Timeseries, definitions for MMS Queries...
            "net_demand":
                "device_ids":
                    - 281
                    - 282
                    - 283
                "metrics":
                    - 'P'
                "agg": 'avg'
                "fill": 'interpolate'
        :param data_model:
        :param res:
        :param ts_end:
        :param ts_start:
        :return: A compiled dataframe in accordance with the Data Model
        """
        stats = {'timeseries': {}, 'features': {}}
        features_df = None
        timeseries_dfs = {}
        timeseries = data_model.get('timeseries')
        features = data_model.get('features')
        for name, ts in timeseries.items():
            logger.debug('Querying data for timeseries {0}'.format(name))
            timeseries_dfs[name] = self.get_aggregated_metrics(
                res,
                ts.get('device_ids'),
                ts.get('metrics'),
                ts_start, ts_end,
                ts.get('agg'), ts.get('fill'))
            if timeseries_dfs[name] is None:
                stats['timeseries'].update({
                    name: "No result"
                })
            else:
                stats['timeseries'].update({
                    name: dict(zip(
                        timeseries_dfs[name].groupby(
                            ['device_id']).count().index.values,
                        ["{} rows".format(count)
                         for count in timeseries_dfs[name].groupby(
                            ['device_id']).count().values[:, 0]]
                    ))
                })
        for feature, components in features.items():
            # Dictionary of features for model
            feature_df = None
            logger.debug('Preparing feature {0}'.format(feature))
            for component, operation in components.items():
                # Dictionary of feature components.
                logger.debug('Using component {0}'.format(component))
                # Does not need to be only a sum operation.
                if timeseries_dfs[component] is None:
                    continue
                component_df = timeseries_dfs[component] \
                    .groupby(['measurement_date']) \
                    .sum(min_count=1)
                if feature_df is None:
                    if operation == '+':
                        feature_df = component_df.copy()
                    if operation == '-':
                        feature_df = (-1 * component_df).copy()
                else:
                    if operation == '+':
                        feature_df = feature_df.add(component_df)
                    if operation == '-':
                        feature_df = feature_df.subtract(component_df)
            if feature_df is not None:
                feature_df.rename(columns={'value': feature}, inplace=True)
                stats['features'].update({
                    feature: "{} rows".format(
                        feature_df.count().values[0])
                })
            else:
                feature_df = pd.DataFrame(columns=['measurement_date', feature])
                feature_df.set_index('measurement_date', inplace=True)
                stats['features'].update({feature: "No result"})
            if features_df is None:
                features_df = feature_df.copy()
            else:
                features_df = features_df.join(feature_df)
        return features_df, stats

    def execute_values(self, df, method='fail', parse_df=False):
        """
        Using psycopg2.extras.execute_values() to insert the Data Frame
        :param df: Data frame matching the schema of 'table' in the MMS.
        :param method: Action to perform when a duplicate row is
        :param parse_df: Boolean indicating whether the dataframe should first
        passed through the df_to_schema method to form the correct format.
        encountered in the DB.
            - fail: Do not insert any rows in the transaction
            - update: Update the duplicate rows
            - ignore: Ignore the duplicate rows
        """
        if parse_df:
            df = self.df_to_schema(df)
        # Comma-separated Data Frame columns, excluding index
        upsert_col_names = list(set(df.columns) - set(self.pk))
        upsert_setters = ', '.join(["{} = EXCLUDED.{}".format(a, a)
                                    for a in upsert_col_names])
        # Comma-separated Data Frame columns, including index
        cols = ','.join(list(df.columns))
        # Create a list of tuples from the Data Frame values
        tuples = [tuple(x) for x in df.to_numpy()]

        if method == 'fail':
            query = "INSERT INTO %s(%s) " \
                    "VALUES %%s " \
                    "RETURNING %s " % (self.tbl_name, cols, ','.join(self.pk))
        elif method == 'ignore':
            query = "INSERT INTO %s(%s) " \
                    "VALUES %%s " \
                    "ON CONFLICT (%s)" \
                    "DO NOTHING " \
                    "RETURNING %s " % (self.tbl_name, cols,
                                       ','.join(self.pk), ','.join(self.pk))
        elif method == 'update':
            query = "INSERT INTO %s(%s) " \
                    "VALUES %%s " \
                    "ON CONFLICT (%s)" \
                    "DO UPDATE SET %s " \
                    "RETURNING %s" % (self.tbl_name, cols,
                                      ','.join(self.pk), upsert_setters,
                                      ','.join(self.pk))
        else:
            raise ValueError("Param method must be one of 'fail', "
                             "'update', 'ignore'.")

        # SQL query to execute
        try:
            with self.conn.cursor() as cursor:
                extras.execute_values(cursor, query, tuples, page_size=1000)
                return cursor.fetchall()
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23505':
                raise psycopg2.IntegrityError(
                    "Cannot overwrite existing data in the MMS using 'fail' "
                    "method")
            else:
                raise e

        except psycopg2.DatabaseError as error:
            print("Unexpected Error: %s" % error)
            self.rollback()
            raise error

    def copy_df_from_stringio(self, df, parse_df=False):
        """
        Save the Data Frame in memory and use copy_from() to copy it to
        the table
        :param df: Data frame matching the schema of 'table' in the MMS.
        The index of the data frame will always be measurement_date
        :param parse_df: Boolean indicating whether the dataframe should first
        passed through the df_to_schema method to form the correct format.
        :return: True if successful
        """
        if parse_df:
            df = self.df_to_schema(df)
        s_buf = StringIO()
        cols = list(df.columns)
        # df_idx = df.set_index('measurement_date', inplace=False)
        df.to_csv(s_buf, sep='\t', quoting=csv.QUOTE_NONE,
                  header=False, index=False)
        s_buf.seek(0)
        try:
            with self.conn.cursor() as cursor:
                cursor.copy_from(s_buf, self.tbl_name, columns=cols,
                                 sep='\t', size=8192)
                return cursor.rowcount
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23505':
                print("Will not copy over existing data in the MMS, ignoring")
            return 0
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            self.rollback()
            raise error
