# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines runtime environment classes where Azure Open Datasets are used.

The classes in this module ensure Azure Open Datasets functionality is optimized for different environments.
In general, you do not need to instantiate these environment classes or worry about their implementation.
Instead, use the ``get_environ`` module function to return the environment.
"""

from typing import Union

from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame


class RuntimeEnv(object):
    """Defines the base class definition of runtime environments."""


class SparkEnv(RuntimeEnv):
    """Represents a Spark runtime environment."""


class PandasEnv(RuntimeEnv):
    """Represents a pandas runtime environment."""


def get_environ(data: Union[SparkDataFrame, PdDataFrame]):
    """Get the runtime environment."""
    if(isinstance(data, SparkDataFrame)):
        return SparkEnv()
    return PandasEnv()
