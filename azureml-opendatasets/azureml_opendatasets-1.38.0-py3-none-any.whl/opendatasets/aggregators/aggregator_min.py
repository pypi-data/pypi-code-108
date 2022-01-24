# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the aggregator min class."""

from typing import Union

from pyspark.sql.functions import min

from ..environ import PandasEnv, SparkEnv
from .aggregator import Aggregator


class AggregatorMin(Aggregator):
    """Defines an aggregator that get the minimum based on join keys.

    .. remarks::

        Aggregators are typically not instantiated directly. Instead, specify the the type of aggregator when
        using using an enricher such as the :class:`azureml.opendatasets.enrichers.holiday_enricher.HolidayEnricher`
        object.

        The ``process_public_dataset(env, _public_dataset, cols, join_keys)`` method gets the maximum value.
    """

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('Aggregator', 'min')

    def process_public_dataset(
            self,
            env: Union[SparkEnv, PandasEnv],
            _public_dataset: object,
            cols: object,
            join_keys: list):
        """
        Get minimum value based on join_keys.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.environ.RuntimeEnv
        :param _public_dataset: The input public dataset.
        :type _public_dataset: azureml.opendatasets.accessories.public_data.PublicData
        :param cols: The column name list to retrieve.
        :type cols: builtin.list
        :param join_keys: A list of join key pairs.
        :type join_keys: builtin.list
        :return: An aggregated public dataset.
        """
        keys = [pair[1] for pair in join_keys]
        if isinstance(env, SparkEnv):
            min_aggs = []
            for col in _public_dataset.columns:
                if (cols is None or col in cols) and (col not in keys):
                    min_aggs.append(min(col))
            agg_public_dataset = _public_dataset.groupBy(*keys).agg(*min_aggs)
            return agg_public_dataset
        else:
            agg_public_dataset = _public_dataset.groupby(by=keys).min()
            agg_public_dataset.reset_index(inplace=True)
            return agg_public_dataset
