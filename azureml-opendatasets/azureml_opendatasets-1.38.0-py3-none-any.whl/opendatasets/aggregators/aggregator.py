# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines the base class for all aggregators."""

import copy
from typing import List, Tuple, Union

from ..accessories.customer_data import CustomerData
from ..accessories.public_data import PublicData
from ..environ import PandasEnv, RuntimeEnv, SparkEnv


class Aggregator:
    """Defines an aggregation against specified columns identified with join keys.

    .. remarks::

        Aggregators are typically not instantiated directly. Instead, specify the the type of aggregator when
        using using an enricher such as the :class:`azureml.opendatasets.enrichers.holiday_enricher.HolidayEnricher`
        object.

        Derived aggregators include :class:`azureml.opendatasets.aggregators.aggregator_all.AggregatorAll`,
        :class:`azureml.opendatasets.aggregators.aggregator_avg.AggregatorAvg`,
        :class:`azureml.opendatasets.aggregators.aggregator_max.AggregatorMax`,
        :class:`azureml.opendatasets.aggregators.aggregator_min.AggregatorMin`,
        :class:`azureml.opendatasets.aggregators.aggregator_top.AggregatorTop`.

        The ``process(env, customer_data, public_data, join_keys, debug)`` method performs the aggregation.
    """

    should_direct_join = True

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return None

    def process_public_dataset(
            self,
            env: RuntimeEnv,
            _public_dataset: object,
            cols: List[str] = None,
            join_keys: List[Tuple[str, str]] = []) -> object:
        """Perform aggregation on specified public data columns.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.environ.RuntimeEnv
        :param _public_dataset: A public dataset dataframe.
        :type _public_dataset: pandas.DataFrame
        :param cols: A list of column names to retrieve.
        :type cols: builtin.list
        :param join_keys: A list of join keys to use.
        :type join_keys: builtin.list

        :return: A new DataFrame of the public dataset.
        :rtype: object
        """
        return _public_dataset

    def process(
            self,
            env: Union[SparkEnv, PandasEnv],
            customer_data: CustomerData,
            public_data: PublicData,
            join_keys: list,
            debug: bool):
        """
        Left join customer_data with public_data on join_keys.

        Drop all columns in join_keys and all columns which is in the list of
        to_be_cleaned_up_column_names afterward.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.environ.RuntimeEnv
        :param customer_data: The customer data.
        :type customer_data: :class:`azureml.opendatasets.accessories.customer_data.CustomerData`
        :param public_data: The public data.
        :type public_data: :class:`azureml.opendatasets.accessories.public_data.PublicData`
        :param join_keys: A list of join key pairs.
        :type join_keys: builtin.list[tuple]
        :param debug: Indicates whether to print debug info.
        :type debug: bool

        :return: A tuple of (
            a new instance of class CustomerData,
            unchanged instance of PublicData,
            a new joined instance of class CustomerData,
            join keys (list of tuple))
        :rtype: tuple[
                    :class:`azureml.opendatasets.accessories.customer_data.CustomerData`,
                    :class:`azureml.opendatasets.accessories.public_data.PublicData`,
                    :class:`azureml.opendatasets.accessories.customer_data.CustomerData`,
                    builtin.list[tuple([str, str])]
        """
        customer_dataset = customer_data.data
        public_dataset = public_data.data
        if isinstance(env, SparkEnv):
            if debug:
                print('* customer_dataset: %d' % customer_dataset.count())
                print(customer_dataset)
                print('* processed_public_dataset: %d' %
                      public_dataset.count())
                print(public_dataset)

            join_conditions = []
            for pair in join_keys:
                join_conditions.append(
                    customer_dataset[pair[0]] == public_dataset[pair[1]])
            joined_dataset = customer_dataset.join(
                public_dataset,
                join_conditions,
                how="left")

            if debug:
                print('* joined_dataset: %d' % joined_dataset.count())
                print(joined_dataset)

            if not debug:
                joined_dataset = self._clean_up_columns(
                    env, customer_data, joined_dataset, join_keys)
            joined_data = copy.copy(customer_data)
            joined_data.data = joined_dataset

            return customer_data, public_data, joined_data, join_keys
        else:
            if debug:
                print('* customer_dataset: %d' % len(customer_dataset.index))
                print(customer_dataset.head(5))
                print('* processed_public_dataset: %d' %
                      len(public_dataset.index))
                print(public_dataset.head(5))

            customer_keys, public_keys = list(zip(*join_keys))
            joined_dataset = customer_dataset.merge(
                public_dataset,
                left_on=customer_keys,
                right_on=public_keys,
                how="left")

            if debug:
                print('* joined_dataset: %d' % len(joined_dataset.index))
                print(joined_dataset.head(5))

            if not debug:
                joined_dataset = self._clean_up_columns(
                    env, customer_data, joined_dataset, join_keys)
            joined_data = copy.copy(customer_data)
            joined_data.data = joined_dataset

            return customer_data, public_data, joined_data, join_keys

    def _clean_up_columns(
            self,
            env: Union[SparkEnv, PandasEnv],
            _joined_data: CustomerData,
            _joined_dataset: object,
            join_keys: list):
        """Clean up columns.

        :param _joined_data: customer data
        :param _joined_dataset: customer data frame
        :param join_keys: join keys
        :return: cleaned data frame
        """
        if isinstance(env, SparkEnv):
            target_columns = \
                [key for pair in join_keys for key in pair] + \
                _joined_data.to_be_cleaned_up_column_names
            cleaned_joined_dataset = _joined_dataset\
                .drop(*target_columns)
            return cleaned_joined_dataset
        else:
            to_be_target_columns = \
                [key for pair in join_keys for key in pair] + \
                _joined_data.to_be_cleaned_up_column_names
            joined_dataset_columns = list(_joined_dataset.columns)
            target_columns = []
            for col in to_be_target_columns:
                if col in joined_dataset_columns:
                    target_columns.append(col)
                else:
                    if (col + '_x') in joined_dataset_columns:
                        target_columns.append(col + '_x')
                    if (col + '_y') in joined_dataset_columns:
                        target_columns.append(col + '_y')
            cleaned_joined_dataset = _joined_dataset\
                .drop(columns=target_columns, axis=1)
            return cleaned_joined_dataset
