# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains the base class of all customer data."""

from typing import List, Optional

from pyspark.sql.functions import monotonically_increasing_id

from .._utils.spark_utils import has_column
from ..environ import RuntimeEnv, SparkEnv, get_environ


class CustomerData:
    """Defines the base class of customer data."""

    def __init__(self, _data):
        """Initialize with customer data frame.

        :param _data: A data frame.
        :type _data: pandas.DataFrame
        """
        self.env = get_environ(_data)
        self.__data = _data
        self.__to_be_cleaned_up_column_names = []

    @property
    def to_be_cleaned_up_column_names(self) -> List[str]:
        """Get column names to be cleaned up.

        :return: A list of columns to be cleaned up.
        """
        return self.__to_be_cleaned_up_column_names

    @to_be_cleaned_up_column_names.setter
    def to_be_cleaned_up_column_names(self, value: List[str]):
        """Set column names to be cleaned up.

        :param value: A list of column names.
        """
        self.__to_be_cleaned_up_column_names = value

    @property
    def data(self) -> Optional[object]:
        """Get dataframe."""
        return self.__data

    @data.setter
    def data(self, value: object):
        """Set dataframe."""
        self.__data = value

    def add_row_id(self, env: RuntimeEnv):
        """Add row ID to customer data, in order to distinguish after join."""
        if isinstance(env, SparkEnv):
            if not has_column(self.__data, CustomerData.row_id_col_name()):
                self.__data = self.__data.withColumn(
                    CustomerData.row_id_col_name(), monotonically_increasing_id())

    @staticmethod
    def row_id_col_name() -> str:
        """Get row ID column name.

        :return: The row ID column name.
        """
        return 'row_id'
