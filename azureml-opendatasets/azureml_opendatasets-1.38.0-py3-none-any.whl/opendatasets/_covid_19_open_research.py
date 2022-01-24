# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""COVID-19 Open Research Dataset."""
from azureml.data import FileDataset

from .accessories.open_dataset_base import ClassMethodOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class COVID19OpenResearch(ClassMethodOpenDatasetBase):
    """Represents COVID-19 Open Research Dataset.

    For more information about this dataset, including column descriptions, different ways to access the
    dataset, and examples, see `COVID-19 Open Research Dataset <https://azure.microsoft.com/services/
    open-datasets/catalog/covid-19-open-research/>`_ in the Microsoft Azure Open Datasets catalog.
    """

    _blob_accessor = BlobAccessorDescriptor("covid-19-open-research")

    @classmethod
    def get_file_dataset(
            cls,
            enable_telemetry: bool = True) -> FileDataset:
        """Return a :class:`azureml.data.FileDataset` containing the files.

        :param cls: Current class
        :param enable_telemetry: Whether to enable telemetry or not. Defaults to True.
        :type enable_telemetry: bool
        :return: A file dataset.
        :rtype: azureml.data.FileDataset
        """
        open_datasets = cls._get_open_dataset(
            enable_telemetry=enable_telemetry)
        return open_datasets.get_file_dataset()
