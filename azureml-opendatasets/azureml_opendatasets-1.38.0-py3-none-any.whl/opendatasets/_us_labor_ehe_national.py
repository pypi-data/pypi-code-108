# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor ehe national."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsLaborEHENational(NoParameterOpenDatasetBase):
    """Represents the US National Employment Hours and Earnings public dataset.

    This dataset contains industry estimates of nonfarm employment, hours, and earnings of workers on
    payrolls in the United States. For more information about this dataset, including column descriptions,
    different ways to access the dataset, and examples, see `US National Employment Hours and
    Earning <https://azure.microsoft.com/services/open-datasets/catalog/us-employment-hours-earnings-national/>`_
    in the Microsoft Azure Open Datasets catalog.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("us-employment-hours-earnings-national")
