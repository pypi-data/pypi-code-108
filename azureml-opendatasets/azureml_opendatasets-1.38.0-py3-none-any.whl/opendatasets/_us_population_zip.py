# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US population by zip."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsPopulationZip(NoParameterOpenDatasetBase):
    """Represents the US Population by Zip Code public dataset.

    This dataset contains US population by gender and race for each US ZIP code sourced from 2010
    Decennial Census. For more information about this dataset, including column descriptions,
    different ways to access the dataset, and examples, see `US Population by ZIP
    Code <https://azure.microsoft.com/services/open-datasets/catalog/us-decennial-census-zip/>`_
    in the Microsoft Azure Open Datasets catalog.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """

    _blob_accessor = BlobAccessorDescriptor("us-decennial-census-zip")
