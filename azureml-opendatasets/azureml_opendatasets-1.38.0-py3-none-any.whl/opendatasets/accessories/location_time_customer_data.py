# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for wrapping customer data with location and time columns."""

from typing import Union

from .customer_data import CustomerData
from .location_data import LatLongColumn, LocationCustomerData, ZipCodeColumn
from .time_data import TimeCustomerData


class LocationTimeCustomerData(LocationCustomerData, TimeCustomerData):
    """Defines a class wrapper for customer data which contains location column and time column.

    .. remarks::

        The example below shows how to use LocationTimeCustomerData.

        .. code-block:: python

            LocationTimeCustomerData(data, _latlong_column, _time_column_name)
            LocationTimeCustomerData(data, _zipcode_column, _time_column_name)
    """

    def __init__(self, data: object, _location_column: Union[LatLongColumn, ZipCodeColumn], _time_column_name: str):
        """Initialize the class using Union[LatLongColumn, ZipCodeColumn] class instance.

        :param data: An object representing customer data.
        :type data: object
        :param _location_column: An instance of a location column.
        :type _location_column: Union[LatLongColumn, ZipCodeColumn]
        :param _time_column_name: A datetime column name.
        :type _time_column_name: str
        """
        if isinstance(_location_column, LatLongColumn):
            self.time_column_name = _time_column_name
            (self.latitude_column_name, self.longitude_column_name) = [
                _location_column.lat_name, _location_column.long_name]
            CustomerData.__init__(self, data)
            self.extend_time_column(self.env)
        else:
            self.time_column_name = _time_column_name
            CustomerData.__init__(self, data)
            self.extend_zip_column(self.env, _location_column.name)
            self.extend_time_column(self.env)
