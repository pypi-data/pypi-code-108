# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains fucntionality for working with location data, with supported column classes."""

from typing import Optional
from enum import Enum


class CORAvailableType(Enum):
    """Defines field types for country and region data."""

    Unknown = 0
    CountryCode = 1
    CountryOrRegionName = 2
    All = CountryCode | CountryOrRegionName


class CountryOrRegionColumn:
    """Defines country or region column properties.

    :param countrycode_name: The name of the column that contains country code data.
    :type countrycode_name: str
    :param country_or_region_name: The name of the column that contains country or region data.
    :type country_or_region_name: str
    """

    def __init__(self, countrycode_name: Optional[str] = None, country_or_region_name: Optional[str] = None):
        """Initialize countrycode and country_or_region column names."""
        self.__countrycode_column_name = countrycode_name
        self.__country_or_region_column_name = country_or_region_name
        i = 0
        if self.__countrycode_column_name is not None:
            i |= CORAvailableType.CountryCode.value
        if self.__country_or_region_column_name is not None:
            i |= CORAvailableType.CountryOrRegionName.value
        self.__available_column_type = CORAvailableType(i)

    @property
    def countrycode_column_name(self):
        """Get the name of the column that contains country code data."""
        return self.__countrycode_column_name

    @property
    def country_or_region_column_name(self) -> str:
        """Get the name of the column that contains country or region data."""
        return self.__country_or_region_column_name

    @property
    def available_column_type(self) -> Optional[CORAvailableType]:
        """Get the available column type, CountryCode, CountryOrRegionName, or both."""
        return self.__available_column_type


class CountryOrRegionData:
    """Defines country or region data."""

    @property
    def countrycode_column_name(self):
        """Get the latitude column name."""
        return self.__countrycode_column_name

    @countrycode_column_name.setter
    def countrycode_column_name(self, value: str):
        """Set the latitude column name."""
        self.__countrycode_column_name = value

    @property
    def country_or_region_column_name(self) -> str:
        """Get the longitude column name."""
        return self.__country_or_region_column_name

    @country_or_region_column_name.setter
    def country_or_region_column_name(self, value: str):
        """Set the longitude column name."""
        self.__country_or_region_column_name = value

    @property
    def available_column_type(self) -> CORAvailableType:
        """Get the longitude column name."""
        return self.__available_column_type

    @available_column_type.setter
    def available_column_type(self, value: CORAvailableType):
        """Set the longitude column name."""
        self.__available_column_type = value
