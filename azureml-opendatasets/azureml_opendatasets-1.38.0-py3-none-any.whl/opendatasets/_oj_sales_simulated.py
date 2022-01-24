# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""OJ Sales data."""
from azureml.data import FileDataset

from .accessories.open_dataset_base import ClassMethodOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class OjSalesSimulated(ClassMethodOpenDatasetBase):
    """Represents the Sample Orange Juice Sales Simulated data dataset.

    For more information about this dataset, including column descriptions, different ways to access the
    dataset, and examples, see `Sample: OJ Sales Simulated Data <https://azure.microsoft.com/services/
    open-datasets/catalog/sample-oj-sales-simulated/>`_ in the Microsoft Azure Open Datasets catalog.
    """

    _blob_accessor = BlobAccessorDescriptor("sample-oj-sales-simulated")

    @classmethod
    def get_file_dataset(
            cls,
            enable_telemetry: bool = True) -> FileDataset:
        """Return a :class:`azureml.data.FileDataset` containing the files.

        :param cls: Current class
        :param enable_telemetry: enable telemetry or not, defaults to True
        :type enable_telemetry: bool
        :return: File Datasets
        :rtype: azureml.data.FileDataset
        """
        open_datasets = cls._get_open_dataset(
            enable_telemetry=enable_telemetry)
        return open_datasets.get_file_dataset()
