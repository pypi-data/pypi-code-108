# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor ppi commodity."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsLaborPPICommodity(NoParameterOpenDatasetBase):
    """Represents the US Producer Price Index (PPI) - Commodities public dataset.

    The Producer Price Index (PPI) is a measure of average change over time in the selling prices
    received by domestic producers for their output. The prices included in the PPI are from the
    first commercial transaction for products and services covered. This dataset contains PPIs for
    individual products and groups of products released monthly. For more information about this
    dataset, including column descriptions, different ways to access the dataset, and examples, see
    `US Producer Price Index - Commodities <https://azure.microsoft.com/services/open-datasets/
    catalog/us-producer-price-index-commodities/>`_ in the Microsoft Azure Open Datasets catalog.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    _blob_accessor = BlobAccessorDescriptor(
        "us-producer-price-index-commodities")
