# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""NYC Taxi FHV trip data."""

from ._nyc_taxi_base import NycTaxiBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class NycTlcFhv(NycTaxiBase):
    """Represents the NYC Taxi & Limousine Commission public dataset.

    This dataset contains For-Hire Vechicle (FHV) trip records, which include fields capturing the dispatching
    base license number and the pick-up date, time, and taxi zone location ID (shape file below). These records
    are generated from the FHV Trip Record submissions made by bases.
    For more information about this dataset, including column descriptions, different ways to access the dataset,
    and examples, see `NYC Taxi & Limousine Commission - For-Hire Vehicle (FHV) trip
    records <https://azure.microsoft.com/services/open-datasets/catalog/
    nyc-taxi-limousine-commission-for-hire-vehicle-trip-records/>`_ in the Microsoft Azure Open Datasets catalog.

    .. remarks::

        The example below shows how to access the dataset.

        .. code-block:: python

            from azureml.opendatasets import NycTlcFhv
            from dateutil import parser

            end_date = parser.parse('2018-06-06')
            start_date = parser.parse('2018-05-01')
            nyc_tlc = NycTlcFhv(start_date=start_date, end_date=end_date)
            nyc_tlc_df = nyc_tlc.to_pandas_dataframe()

    :param start_date: The date at which to start loading data, inclusive. If None, the ``default_start_date``
        is used.
    :type start_date: datetime
    :param end_date: The date at which to end loading data, inclusive. If None, the ``default_end_date``
        is used.
    :type end_date: datetime
    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `NYC Taxi & Limousine Commission -
        For-Hire Vehicle (FHV) trip records <https://azure.microsoft.com/services/open-datasets/catalog/
        nyc-taxi-limousine-commission-for-hire-vehicle-trip-records/>`__.
    :type cols: builtin.list[str]
    :param limit: A value indicating the number of days of data to load with ``to_pandas_dataframe()``.
        If not specified, the default of -1 means no limit on days loaded.
    :type limit: int
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    _blob_accessor = BlobAccessorDescriptor("nyc_tlc_fhv")
