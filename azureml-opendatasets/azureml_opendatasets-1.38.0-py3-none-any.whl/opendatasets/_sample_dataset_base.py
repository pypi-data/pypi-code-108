# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Sample data base."""
from azureml.data import FileDataset, TabularDataset

from .accessories.open_dataset_base import ClassMethodOpenDatasetBase


class SampleDatasetBase(ClassMethodOpenDatasetBase):
    """Represents the Sample Dataset Base class.
    """

    @classmethod
    def get_tabular_dataset(
            cls,
            enable_telemetry: bool = True) -> TabularDataset:
        """Return a :class:`azureml.data.TabularDataset` containing the data.

        :param cls: Current class
        :param enable_telemetry: enable telemetry or not, defaults to True
        :type enable_telemetry: bool, optional
        :return: A tabular dataset.
        :rtype: azureml.data.TabularDataset
        """
        open_datasets = cls._get_open_dataset(
            enable_telemetry=enable_telemetry)
        return open_datasets.get_tabular_dataset()

    @classmethod
    def get_file_dataset(
            cls,
            enable_telemetry: bool = True) -> FileDataset:
        """Return a :class:`azureml.data.FileDataset` containing the files.

        :param cls: Current class
        :param enable_telemetry: enable telemetry or not, defaults to True
        :type enable_telemetry: bool, optional
        :return: File Datasets
        :rtype: azureml.data.FileDataset
        """
        open_datasets = cls._get_open_dataset(
            enable_telemetry=enable_telemetry)
        return open_datasets.get_file_dataset()
