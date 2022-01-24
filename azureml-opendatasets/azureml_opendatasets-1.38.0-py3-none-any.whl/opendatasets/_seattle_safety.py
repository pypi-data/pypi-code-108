# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Seattle safety."""

from ._city_safety import CitySafety
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class SeattleSafety(CitySafety):
    """Represents the Seattle Safety public dataset.

    This dataset contains Seattle Fire Department 911 dispatch data.
    For more information about this dataset, including column descriptions, different ways to access the dataset,
    and examples, see `Seattle Safety Data <https://azure.microsoft.com/services/open-datasets/catalog/
    seattle-safety-data/>`_ in the Microsoft Azure Open Datasets catalog.

    :param start_date: The date at which to start loading data, inclusive. If None, the ``default_start_date``
        is used.
    :type start_date: datetime
    :param end_date: The date at which to end loading data, inclusive. If None, the ``default_end_date``
        is used.
    :type end_date: datetime
    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `Seattle Safety Data <https://azure.microsoft.com/
        services/open-datasets/catalog/seattle-safety-data/>`__.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    """const instance of blob accessor."""
    _blob_accessor = BlobAccessorDescriptor("city_safety_seattle")
