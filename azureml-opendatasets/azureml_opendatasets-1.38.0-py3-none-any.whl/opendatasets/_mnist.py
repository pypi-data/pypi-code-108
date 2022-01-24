# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MNIST data."""

from azureml.data import FileDataset, TabularDataset

from .accessories.open_dataset_base import ClassMethodOpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor
from .dataaccess._mnist_blob_accessor import MNISTFileBlobAccessor


class MNIST(ClassMethodOpenDatasetBase):
    """Represents the MNIST dataset of handwritten digits.

    The MNIST database of handwritten digits has a training set of 60,000 examples and a test set of
    10,000 examples. The digits have been size-normalized and centered in a fixed-size image. For more
    information about this dataset, including column descriptions, different ways to access the dataset,
    and examples, see `The MNIST database of handwritten digits <https://azure.microsoft.com/services/
    open-datasets/catalog/mnist/>`_ in the Microsoft Azure Open Datasets catalog.

    For an example of using the MNIST dataset, see the tutorial `Train image classification models with
    MNIST data and scikit-learn using Azure Machine Learning <https://docs.microsoft.com/azure/
    machine-learning/tutorial-train-models-with-aml>`_.
    """

    @classmethod
    def get_tabular_dataset(
            cls,
            dataset_filter='all',
            enable_telemetry: bool = True) -> TabularDataset:
        """Return a :class:`azureml.data.TabularDataset` containing the data.

        :param cls: Current class
        :param dataset_filter: A filter that determines what data is returned. Can be "all" (the default),
            "train", or "test".
        :type dataset_filter: str
        :param enable_telemetry: Whether to enable telemetry on this dataset.
        :type enable_telemetry: bool
        :return: A tabular dataset.
        :rtype: azureml.data.TabularDataset
        """
        cls._blob_accessor = BlobAccessorDescriptor("mnist")
        open_datasets = cls._get_open_dataset(
            enable_telemetry=enable_telemetry, dataset_filter=dataset_filter)
        return open_datasets.get_tabular_dataset()

    @classmethod
    def get_file_dataset(
            cls,
            dataset_filter='all',
            enable_telemetry: bool = True) -> FileDataset:
        """Return a :class:`azureml.data.FileDataset` containing the data.

        :param cls: Current class
        :param dataset_filter: A filter that determines what data is returned. Can be "all" (the default),
            "train", or "test".
        :type dataset_filter: str
        :param enable_telemetry: Whether to enable telemetry on this dataset.
        :type enable_telemetry: bool
        :return: A file dataset.
        :rtype: azureml.data.FileDataset
        """
        cls._blob_accessor = BlobAccessorDescriptor(
            "mnist", cls=MNISTFileBlobAccessor)
        open_datasets = cls._get_open_dataset(
            enable_telemetry=enable_telemetry, dataset_filter=dataset_filter)
        return open_datasets.get_file_dataset()
