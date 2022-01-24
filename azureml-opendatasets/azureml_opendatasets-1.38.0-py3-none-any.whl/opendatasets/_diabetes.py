# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Diabetes data."""

from ._sample_dataset_base import SampleDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class Diabetes(SampleDatasetBase):
    """Represents the Sample Diabetes public dataset.

    The Diabetes dataset has 442 samples with 10 features, making it ideal for getting started with machine
    learning algorithms. For more information about this dataset, including column descriptions, different
    ways to access the dataset, and examples, see `Sample: Diabetes <https://azure.microsoft.com/
    services/open-datasets/catalog/sample-diabetes/>`_ in the Microsoft Azure Open Datasets catalog.
    """

    _blob_accessor = BlobAccessorDescriptor("sample-diabetes")
