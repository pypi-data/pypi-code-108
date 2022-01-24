# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor ppi industry."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsLaborPPIIndustry(NoParameterOpenDatasetBase):
    """Represents the US Producer Price Index (PPI) - Industry public dataset.

    The Producer Price Index (PPI) is a measure of average change over time in the selling prices received
    by domestic producers for their output. The prices included in the PPI are from the first commercial
    transaction for products and services covered. This dataset contains PPIs for a wide range of industry
    sectors of the U.S. economy. For more information about this dataset, including column descriptions,
    different ways to access the dataset, and examples, see `US Producer Price Index -
    Industry <https://azure.microsoft.com/services/open-datasets/catalog/us-producer-price-index-industry/>`_
    in the Microsoft Azure Open Datasets catalog.

    For general information about Azure Open Datasets, see `Azure Open Datasets
    Documentation <https://docs.microsoft.com/azure/open-datasets/>`_.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("us-producer-price-index-industry")
