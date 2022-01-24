# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""US labor lfs."""

from ._no_parameter_open_dataset_base import NoParameterOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class UsLaborLFS(NoParameterOpenDatasetBase):
    """Represents the US Labor Force Statistics public dataset.

    This dataset contains data about the labor force in the United States, including labor force
    participation rates, and the civilian noninstitutional population by age, gender, race, and ethnic
    groups. For more information about this dataset, including column descriptions, different ways to
    access the dataset, and examples, see `US Labor Force Statistics <https://azure.microsoft.com/
    services/open-datasets/catalog/us-labor-force-statistics/>`_ in the Microsoft Azure Open Datasets catalog.

    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("us-labor-force-statistics")
