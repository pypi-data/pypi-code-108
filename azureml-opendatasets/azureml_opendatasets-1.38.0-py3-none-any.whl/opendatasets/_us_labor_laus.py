# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor laus."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsLaborLAUS(NoParameterOpenDatasetBase):
    """Represents the US Local Area Unemployment Statistics public dataset.

    This dataset contains monthly and annual employment, unemployment, and labor force data for Census
    regions and divisions, States, counties, metropolitan areas, and many cities in the United States.
    For more information about this dataset, including column descriptions, different ways to access the
    dataset, and examples, see `US Local Area Unemployment Statistics <https://azure.microsoft.com/
    services/open-datasets/catalog/us-local-area-unemployment-statistics/>`_ in the Microsoft Azure
    Open Datasets catalog.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("us-local-area-unemployment-statistics")
