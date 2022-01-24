# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Bing COVID-19 data."""

from typing import List, Optional
from .accessories.open_dataset_base import OpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class BingCOVID19Data(OpenDatasetBase):
    """Represents the Bing COVID-19 dataset.

    This datasets contains Bing COVID-19 data from multiple trusted, reliable sources, including the World Health
    Organization (WHO), Centers for Disease Control and Prevention (CDC), national and state public health
    departments, BNO News, 24/7 Wall St., and Wikipedia. For more information about this dataset, including
    column descriptions, different ways to access the dataset, and examples, see `Bing COVID-19 Data
    <https://azure.microsoft.com/services/open-datasets/catalog/bing-covid-19-data/>`_ in the Microsoft Azure
    Open Datasets catalog.

    .. remarks::

        The example below shows how to access the dataset.

        .. code-block:: python

            from azureml.opendatasets import BingCOVID19Data

            bing_covid = BingCOVID19Data()
            bing_covid_df = bing_covid.to_pandas_dataframe()

    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `Bing COVID-19 Data <https://azure.microsoft.com/
        services/open-datasets/catalog/bing-covid-19-data/>`__.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("bing-covid-19-data")

    def __init__(
            self,
            cols: Optional[List[str]] = None,
            enable_telemetry: bool = True):
        """
        Initialize filtering fields.

        :param cols: A list of column names you'd like to retrieve. None will get all columns.
        :type cols: Optional[List[str]]
        :param enable_telemetry: Indicates whether to send telemetry.
        :type enable_telemetry: bool
        """
        super(BingCOVID19Data, self).__init__(
            cols,
            enable_telemetry
        )
