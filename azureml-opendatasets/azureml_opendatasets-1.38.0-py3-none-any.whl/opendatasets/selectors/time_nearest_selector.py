# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the time nearest selector class."""

import copy
from typing import Union

from pyspark.sql.functions import udf
from pyspark.sql.types import TimestampType

from .._utils.random_utils import random_tag
from ..accessories.time_data import TimeData
from ..aggregators.aggregator import Aggregator
from ..environ import PandasEnv, RuntimeEnv, SparkEnv
from ..granularities.granularity import TimeGranularity
from .enricher_selector import EnricherTimeSelector


class TimeNearestSelector (EnricherTimeSelector):
    """Defines the time nearest selector with rounding to different time granularities."""

    def __init__(self, _granularity: TimeGranularity, enable_telemetry: bool = True):
        """Intialize with time granularity."""
        self.granularity = _granularity
        self.enable_telemetry = enable_telemetry
        if self.enable_telemetry:
            self.log_properties = self._get_common_log_properties()

    def _prepare_time_join(
            self,
            env: Union[SparkEnv, PandasEnv],
            public_data: TimeData,
            nearest_udf: object):
        """Prepare time join by adding rounded time column."""
        # round time to nearest hour for joining data and for input customer_data
        ds_join_time = 'ds_join_time' + random_tag()
        if isinstance(env, SparkEnv):
            _public_dataset = public_data.data
            public_dataset = _public_dataset.withColumn(
                ds_join_time,
                nearest_udf(_public_dataset[public_data.time_column_name]))\
                .drop(public_data.time_column_name)

            return public_dataset, ds_join_time
        else:
            public_dataset = public_data.data
            public_dataset[ds_join_time] = public_dataset[public_data.time_column_name].apply(
                nearest_udf).drop(columns=[public_data.time_column_name], axis=1)
            return public_dataset, ds_join_time

    def _time_join_nearest(
            self,
            env: Union[SparkEnv, PandasEnv],
            customer_data: TimeData,
            public_data: TimeData,
            aggregator: Aggregator,
            join_keys: list,
            debug: bool):
        """Join customer data with public data, with aggregator applied."""
        if isinstance(env, SparkEnv):
            nearest_udf = udf(self.round_to(self.granularity), TimestampType())
            public_dataset, ds_join_time = self._prepare_time_join(
                env, public_data, nearest_udf)

            # add 3p data in (cols already filtered for only join cols + cols that are needed)
            # join on time
            # make new col for time join if necessary
            customer_join_time = 'customer_join_time' + random_tag()
            join_keys.append((customer_join_time, ds_join_time))

            id_time_customer_dataset = customer_data.data.withColumn(
                customer_join_time,
                nearest_udf(customer_data.data[customer_data.time_column_name]))

            altered_customer_data = copy.copy(customer_data)
            altered_customer_data.data = id_time_customer_dataset

            if debug:
                print('* id_time_customer_dataset: %d' %
                      id_time_customer_dataset.count())
                print(id_time_customer_dataset)

            public_dataset = aggregator.process_public_dataset(
                env, public_dataset, public_data.cols, join_keys)

            if debug:
                print('* public_dataset in time_nearest_selector: %d' %
                      public_dataset.count())
                print(public_dataset)

            if not aggregator.should_direct_join:
                join_conditions = []
                for pair in join_keys:
                    join_conditions.append(
                        id_time_customer_dataset[pair[0]] == public_dataset[pair[1]])
                public_dataset = public_dataset.alias('a').join(
                    id_time_customer_dataset.alias('b'),
                    join_conditions)\
                    .select('a.*')

            if debug:
                print(
                    '* public_dataset after join with id_time_customer_dataset: %d' %
                    (public_dataset.count()))
                print(public_dataset)

            filtered_public_data = copy.copy(public_data)
            filtered_public_data.data = public_dataset

            if debug:
                print('* join_keys: %s' + str(join_keys))

            return altered_customer_data, filtered_public_data, join_keys
        else:
            nearest_udf = self.round_to(self.granularity)
            public_dataset, ds_join_time = self._prepare_time_join(
                env, public_data, nearest_udf)

            # add 3p data in (cols already filtered for only join cols + cols that are needed)
            # join on time
            # make new col for time join if necessary
            customer_join_time = 'customer_join_time' + random_tag()
            join_keys.append((customer_join_time, ds_join_time))

            id_time_customer_dataset = customer_data.data
            id_time_customer_dataset[customer_join_time] = id_time_customer_dataset[customer_data.time_column_name]\
                .apply(nearest_udf)

            altered_customer_data = copy.copy(customer_data)
            altered_customer_data.data = id_time_customer_dataset

            if debug:
                print('* id_time_customer_dataset: %d' %
                      len(id_time_customer_dataset.index))
                print(id_time_customer_dataset.head(5))
                print('* public_dataset in time_nearest_selector: %d' %
                      len(public_dataset.index))
                print(public_dataset.head(5))

            public_dataset = aggregator.process_public_dataset(
                env, public_dataset, public_data.cols, join_keys)

            if debug:
                print('* public_dataset in time_nearest_selector: %d' %
                      len(public_dataset.index))
                print(public_dataset.head(5))

            if not aggregator.should_direct_join:
                customer_keys, public_keys = list(zip(*join_keys))
                public_dataset = public_dataset.merge(
                    id_time_customer_dataset,
                    left_on=list(public_keys),
                    right_on=list(customer_keys))[list(public_dataset.columns)]

            if debug:
                print('* public_dataset after join with id_time_customer_dataset: %d' %
                      len(public_dataset.index))
                print(public_dataset.head(5))

            filtered_public_data = copy.copy(public_data)
            filtered_public_data.data = public_dataset

            if debug:
                print('* join_keys: %s' + str(join_keys))

            return altered_customer_data, filtered_public_data, join_keys

    def process(
            self,
            env: RuntimeEnv,
            customer_data: TimeData,
            public_data: TimeData,
            aggregator: Aggregator,
            join_keys: list = None,
            debug: bool = False):
        """Enrich customer data with public data using the specified aggregator.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.environ.RuntimeEnv
        :param customer_data: An instance of a TimeData derived class.
        :type customer_data: azureml.opendatasets.accessories.time_data.TimeData
        :param public_data: An instance of a TimeData derived class.
        :type public_data: azureml.opendatasets.accessories.time_data.TimeData
        :param aggregator: An aggregator.
        :type aggregator: azureml.opendatasets.aggregators.aggregator.Aggregator
        :param join_keys: A list of join key pairs.
        :type join_keys: builtin.list
        :param debug: Indicates whether to print debug logs.
        :type debug: bool
        :return: A tuple of altered customer data class instance, altered public data class instance, and
            a list of join key pairs.
        :rtype: tuple
        """
        if self.enable_telemetry:
            self.log_properties['RegistryId'] = public_data.registry_id
            time_gran_log_property = self.granularity.get_log_property()
            if time_gran_log_property is not None and len(time_gran_log_property) == 2:
                self.log_properties[time_gran_log_property[0]] = \
                    time_gran_log_property[1]

        # join on time
        my_join_keys = join_keys.copy() if bool(join_keys) else []
        return self._time_join_nearest(env, customer_data, public_data, aggregator, my_join_keys, debug)
