# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for working with location data, with supported column classes."""

from typing import Union

import pandas as pd
from pandas import DataFrame as PdDataFrame
from pyspark.sql.dataframe import DataFrame as SparkDataFrame
from pyspark.sql.functions import col, max, min

from .._utils.random_utils import random_tag
from .._utils.zipcode_mapping import load_zipcode_mapping
from ..environ import RuntimeEnv, SparkEnv
from .customer_data import CustomerData


def _find_min_max_zipcode(dataset: Union[SparkDataFrame, PdDataFrame], zipcode_column_name: str):
    """
    Find the min/max zipcode in dataset.

    :param dataset: input (customer) dataset
    :param zipcode_column_name: zipcode column name in dataset
    :return: a tuple of minimnum and maximum zipcode
    """
    if isinstance(dataset, SparkDataFrame):
        min_zipcode = dataset.select(min(zipcode_column_name)).collect()[0][0]
        max_zipcode = dataset.select(max(zipcode_column_name)).collect()[0][0]
        return (min_zipcode, max_zipcode)
    else:
        min_zipcode = dataset[zipcode_column_name].min()
        max_zipcode = dataset[zipcode_column_name].max()
        return (min_zipcode, max_zipcode)


class LatLongColumn:
    """Defines a wrapper class for latitude and longitude.

    :param lat_name: The name of column containing latitude data.
    :type lat_name: str
    :param long_name: The name of the column containing longitude data.
    :type long_name: str
    """

    def __init__(self, lat_name: str, long_name: str):
        """Initialize latitude and longitude column names."""
        self.__lat_name = lat_name
        self.__long_name = long_name

    @property
    def lat_name(self) -> str:
        """Get the latitude column name."""
        return self.__lat_name

    @property
    def long_name(self) -> str:
        """Get the longitude column name."""
        return self.__long_name


class ZipCodeColumn:
    """Defines a wrapper class for zip code.

    :param column_name: The column name containing zip code data.
    :type column_name: str
    """

    def __init__(self, column_name: str):
        """Initialize with a zip code column name."""
        self.__name = column_name

    @property
    def name(self) -> str:
        """Get the zip code column name."""
        return self.__name


class LocationData:
    """Represents a location based on latitude and longitude column names."""

    @property
    def latitude_column_name(self):
        """Get the latitude column name."""
        return self.__latitude_column_name

    @latitude_column_name.setter
    def latitude_column_name(self, value: str):
        """Set the latitude column name."""
        self.__latitude_column_name = value

    @property
    def longitude_column_name(self) -> str:
        """Get the longitude column name."""
        return self.__longitude_column_name

    @longitude_column_name.setter
    def longitude_column_name(self, value: str):
        """Set the longitude column name."""
        self.__longitude_column_name = value


class LocationCustomerData(CustomerData, LocationData):
    """Defines a class combining customer data with location data.

    The LocationCustomerData class inherits from CustomerData and LocationData, extending the
    zip code column in CustomerData to latitude and longitude.
    """

    def extend_zip_column(self, env: RuntimeEnv, zipcode_column_name: str):
        """
        Extend the given zip code column to latitude and longitude columns.

        :param env: The runtime environment.
        :type env: azureml.opendatasets.environ.RuntimeEnv
        :param _zipcode_column_name: The zip code column name in the customer data object.
        :type _zipcode_column_name: str
        """
        zipcode_mapping_ds = load_zipcode_mapping(env)
        customer_ds = self.data

        (min_zipcode, max_zipcode) = _find_min_max_zipcode(
            customer_ds, zipcode_column_name)
        self.latitude_column_name = 'lat_' + random_tag()
        self.longitude_column_name = 'lng_' + random_tag()
        self.to_be_cleaned_up_column_names = [
            self.latitude_column_name, self.longitude_column_name]
        if isinstance(env, SparkEnv):
            zipcode_mapping_ren = zipcode_mapping_ds.withColumnRenamed(
                "LAT", self.latitude_column_name).withColumnRenamed(
                    "LNG", self.longitude_column_name).filter(
                        (zipcode_mapping_ds.ZIP >= min_zipcode) & (zipcode_mapping_ds.ZIP <= max_zipcode))

            self.data = customer_ds.alias('a').join(
                zipcode_mapping_ren.alias('b'),
                customer_ds[zipcode_column_name] == zipcode_mapping_ren.ZIP, "left_outer").select(
                    [col("a.*")] + [
                        col("b." + self.latitude_column_name),
                        col("b." + self.longitude_column_name)])

            self.data.cache()
        else:
            zipcode_mapping_ren = zipcode_mapping_ds[
                (zipcode_mapping_ds.ZIP >= min_zipcode) & (zipcode_mapping_ds.ZIP <= max_zipcode)].rename(
                    index=str,
                    columns={
                        "LAT": self.latitude_column_name,
                        "LNG": self.longitude_column_name})

            extended_dataset = pd.merge(
                customer_ds,
                zipcode_mapping_ren,
                left_on=[zipcode_column_name],
                right_on=['ZIP'],
                how='left').loc[
                    :,
                    list(customer_ds.columns) + [
                        self.latitude_column_name,
                        self.longitude_column_name]]

            self.data = extended_dataset
