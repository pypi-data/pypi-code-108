# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor cpi."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsLaborCPI(NoParameterOpenDatasetBase):
    """Represents the US Consumer Price Index public dataset.

    The Consumer Price Index (CPI) is a measure of the average change over time in the prices paid by
    urban consumers for a market basket of consumer goods and services. For more information about this
    dataset, including column descriptions, different ways to access the dataset, and examples, see
    `US Consumer Price Index <https://azure.microsoft.com/services/open-datasets/catalog/
    us-consumer-price-index/>`_ in the Microsoft Azure Open Datasets catalog.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    _blob_accessor = BlobAccessorDescriptor("us-consumer-price-index")
