# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the aggregator top class."""

from typing import Union

import pandas as pd
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

from .._utils.random_utils import random_tag
from ..environ import PandasEnv, SparkEnv
from .aggregator import Aggregator


class AggregatorTop(Aggregator):
    """Defines an aggregator that gets the top N based on join keys.

    .. remarks::

        Aggregators are typically not instantiated directly. Instead, specify the the type of aggregator when
        using using an enricher such as the :class:`azureml.opendatasets.enrichers.holiday_enricher.HolidayEnricher`
        object.

        The ``process_public_dataset(env, _public_dataset, cols, join_keys)`` method gets the maximum value.
    """

    def get_log_property(self):
        """Get log property tuple, None if no property."""
        return ('Aggregator', 'top')

    def __init__(self, n: int = 1):
        """Initialize with top numbers."""
        self.top = n

    def process_public_dataset(
            self,
            env: Union[SparkEnv, PandasEnv],
            _public_dataset: object,
            cols: object,
            join_keys: list):
        """
        Get the top N values based on the input join keys.

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
            window = Window.partitionBy(keys).orderBy(*keys)
            rn = 'rn' + random_tag()
            top_public_dataset = _public_dataset.withColumn(rn, row_number().over(window))\
                .where(col(rn) <= self.top).drop(rn)
            return top_public_dataset
        else:
            agg_public_dataset = _public_dataset.groupby(by=keys)\
                .apply(pd.DataFrame.head, self.top)
            return agg_public_dataset.reset_index(drop=True)
