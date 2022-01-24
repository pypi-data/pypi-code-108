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


class SimulationClient(TimescaleClient, ABC):
    """
        Inheriting from the ForecastJSONClient class, this class is used for
        accessing, and modifying simulation results in the MMS.
    """

    def __init__(self, dsn, tbl_name):
        pk = ['simulation_id', 'received_date', 'device_id']
        TimescaleClient.__init__(self, dsn, tbl_name, pk=pk,
                                 standardized=True)

    def df_to_schema(self, df):
        """
        :param df: Dataframe to be updated
        This dataframe must have all the key metrics required for the schema in
        order to generate a valid dataframe.
        """
        if type(df.index) != pd.RangeIndex:
            df.reset_index(inplace=True)
        # Measurement Date will be packed into JSON so cannot be Timestamp
        df['measurement_date'] = df['measurement_date']\
            .apply(lambda x: x.isoformat())
        try:
            idx1 = self.pk + ['device_metric_type_id']
            df = df\
                .groupby(idx1)\
                .apply(lambda x: dict({k: v for k, v in zip(
                    x.measurement_date, x.value)}))\
                .reset_index(name='metric_forecasts')
            idx2 = self.pk
            df = df\
                .groupby(idx2)\
                .apply(lambda x: json.dumps(dict({k: v for k, v in zip(
                    x.device_metric_type_id, x.metric_forecasts)})))\
                .reset_index(name='metrics')
            return df
        except Exception as e:
            print(e)
            raise e

    def get_latest_simulation(self, sim, device_ids, metrics,
                              reference_time=None, window=None):
        """
        :param sim: Simulation Id <Integer>
        :param device_ids: A list of device_ids to be queried
        :param metrics: A list of metrics (Strings) to be queried for
        each device_id
        :param reference_time: Set a reference time for when the
        latest values
        are to be queried for. If this is not set the latest values
        for now will
        be queried. [Datetime]
        :param window: [Optional] The number of minutes prior to now
        that the
        latest values
        should be queried from.
        :return: Data Frame in raw or standardized format:
        """
        query = sql.SQL(
            "WITH latest_simulation AS ("
            "   SELECT "
            "   simulation_id, device_id, "
            "   last(received_date, received_date) AS r, "
            "   last(metrics, received_date) AS metrics "
            "   FROM {} "
            "   WHERE received_date >= %s AND received_date <= %s "
            "   AND device_id IN ({}) "
            "   AND simulation_id = %s "
            "   GROUP BY simulation_id, device_id) "
            "SELECT latest_simulation.simulation_id AS simulation_id, "
            "latest_simulation.r AS received_date, "
            "latest_simulation.device_id AS device_id, "
            "m.m AS device_metric_type_id, "
            "j.key::timestamptz AS measurement_date, "
            "AVG(j.value::numeric) AS value "
            "FROM latest_simulation, "
            # list of metrics
            "jsonb_object_keys(latest_simulation.metrics) m, "
            # list of times and values for each metric
            "jsonb_each_text(latest_simulation.metrics->m) j "
            "WHERE m.m IN ({}) "
            "GROUP BY 1, 2, 3, 4, 5 "
            "ORDER BY 1") \
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              h.get_ts_conditional_vals(
                                  reference_time, window) +
                              device_ids + [sim] + metrics,
                              dropna=True)
        return df

    def get_all_simulations(self, sim, device_ids, metrics, ts_start, ts_end):
        """
        :param sim: Simulation Id <Integer>
        :param device_ids: A list of device_ids to be queried
        :param metrics: A list of metrics (Strings) to be queried for
        each device_id
        :param ts_start:
        :param ts_end:
        :return:
        """
        query = sql.SQL(
            "WITH sims AS ("
            "   SELECT simulation_id, received_date, device_id, metrics "
            "   FROM {} "
            "   WHERE received_date >= %s AND received_date <= %s "
            "   AND device_id IN ({}) "
            "   AND simulation_id = %s "
            "   GROUP BY simulation_id, received_date, device_id) "
            "SELECT sims.simulation_id AS simulation_id, "
            "sims.received_date AS received_date, "
            "sims.device_id AS device_id, " 
            "m.m AS device_metric_type_id, "
            "j.key::timestamptz AS measurement_date, "
            "AVG(j.value::numeric) AS value "
            "FROM sims, "
            # list of metrics
            "jsonb_object_keys(sims.metrics) m, "
            # list of times and values for each metric
            "jsonb_each_text(sims.metrics->m) j "
            "WHERE m.m IN ({}) "
            "GROUP BY 1, 2, 3, 4, 5 "
            "ORDER BY 1") \
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)),
                    sql.SQL(', ').join(sql.Placeholder() * len(metrics)))
        df = self.query_to_df(query,
                              [h.validate_timestamp(ts_start),
                               h.validate_timestamp(ts_end)] +
                              device_ids + [sim] + metrics,
                              dropna=True)
        return df

    def get_missing_sim_times(self, sim, device_ids, expected_resolution,
                              ts_start, ts_end):
        """
        :param sim: Simulation Id <Integer>
        :param device_ids: A list of device_ids to be queried
        :param expected_resolution: String Interval compatible with Timescale DB
        :param ts_start:
        :param ts_end:
        :return: Dataframe of (device_id, recieved_date) where no measurements
         are in DB
        """
        query = sql.SQL(
            "WITH counts AS ("
            "SELECT time_bucket_gapfill(%s, received_date) AS time, "
            "device_id, COUNT(metrics) "
            "FROM {} "
            "WHERE device_id IN ({}) "
            "AND simulation_id = %s "
            "AND received_date >= %s AND received_date <= %s "
            "GROUP BY time, device_id) "
            "SELECT time AS received_date, device_id "
            "FROM counts "
            "WHERE count IS NULL")\
            .format(sql.Identifier(self.tbl_name),
                    sql.SQL(', ').join(sql.Placeholder() * len(device_ids)))
        cond_vals = [expected_resolution] + device_ids + \
                    [sim, h.validate_timestamp(ts_start),
                     h.validate_timestamp(ts_end)]
        old_state = self.standardized
        self.standardized = False
        df = self.query_to_df(query,
                              cond_vals)
        self.standardized = old_state
        df.set_index(['device_id', 'received_date'], inplace=True)
        df.index = df.index.set_levels(
            [df.index.levels[0].astype('int64'),
             pd.to_datetime(df.index.levels[1], utc=True)])
        return df

    def simulation_exists(self, sim):
        """
        :param sim: The name of the simulation
        :return:
        """
        query = sql.SQL(
            "SELECT COUNT(*) as count "
            "FROM {} " 
            "WHERE simulation_id = %s "
            "LIMIT 1").format(sql.Identifier(self.tbl_name))

        with self.conn.cursor() as cur:
            cur.execute(query, (sim,))
            if cur.fetchone:
                return True
            else:
                return False
