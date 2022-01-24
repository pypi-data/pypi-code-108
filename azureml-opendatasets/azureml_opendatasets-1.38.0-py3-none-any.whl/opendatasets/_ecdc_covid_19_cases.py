# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The European Centre for Disease Prevention and Control (ECDC) Covid-19 Cases."""

from typing import List, Optional

from .accessories.open_dataset_base import OpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class EcdcCOVIDCases(OpenDatasetBase):
    """Represents the European Centre for Disease Prevention and Control (ECDC) Covid-19 Cases.

    This datasets contains from the European Center for Disease Prevention and Control (ECDC).
    Each row/entry contains the number of new cases reported per day and per country/region. For more
    information about this dataset, including column descriptions, different ways to access the dataset,
    and examples, see `European Centre for Disease Prevention and Control (ECDC) Covid-19 Cases
    <https://azure.microsoft.com/services/open-datasets/catalog/ecdc-covid-19-cases/>`_ in the Microsoft Azure
    Open Datasets catalog.

    .. remarks::

        The example below shows how to access the dataset.

        .. code-block:: python

            from azureml.opendatasets import EcdcCOVIDCases

            ecdc_covid = EcdcCOVIDCases()
            ecdc_covid_df = ecdc_covid.to_pandas_dataframe()

    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `European Centre for Disease Prevention and
        Control (ECDC) Covid-19 Cases <https://azure.microsoft.com/services/open-datasets/catalog
        /ecdc-covid-19-cases/>`__.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("ecdc-covid-19-cases")

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
        super(EcdcCOVIDCases, self).__init__(
            cols,
            enable_telemetry
        )
