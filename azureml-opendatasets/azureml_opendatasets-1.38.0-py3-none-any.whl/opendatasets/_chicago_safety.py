# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Chicago safety."""
from datetime import datetime

from dateutil import parser

from ._city_safety import CitySafety
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class ChicagoSafety(CitySafety):
    """Represents the Chicago Safety public dataset.

    This dataset contains 311 service requests from the city of Chicago, including historical sanitation
    code complaints, pot holes reported, and street light issues.
    For more information about this dataset, including column descriptions, different ways to access the dataset,
    and examples, see `Chicago Safety Data <https://azure.microsoft.com/services/open-datasets/catalog/
    chicago-safety-data/>`_ in the Microsoft Azure Open Datasets catalog.

    :param start_date: The date at which to start loading data, inclusive. If None, the ``default_start_date``
        is used.
    :type start_date: datetime
    :param end_date: The date at which to end loading data, inclusive. If None, the ``default_end_date``
        is used.
    :type end_date: datetime
    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `Chicago Safety Data <https://azure.microsoft.com/
        services/open-datasets/catalog/chicago-safety-data/>`__.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    default_start_date = parser.parse('2000-01-01')
    default_end_date = datetime.today()
    _blob_accessor = BlobAccessorDescriptor("city_safety_chicago")
    """const instance of blobInfo."""
