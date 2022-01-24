# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""The COVID Tracking Project dataset."""

from typing import List, Optional
from .accessories.open_dataset_base import OpenDatasetBase
from .dataaccess._blob_accessor import BlobAccessorDescriptor


class COVIDTrackingProject(OpenDatasetBase):
    """Represents the COVID Tracking Project dataset.

    This datasets contains COVID Tracking Project dataset providing the latest numbers on tests, confirmed
    cases, hospitalizations, and patient outcomes from every US state and territory. For more information
    about this dataset, including column descriptions, different ways to access the dataset, and examples,
    see `COVID Tracking Project dataset <https://azure.microsoft.com/services/open-datasets/catalog
    /covid-tracking/>`_ in the Microsoft Azure Open Datasets catalog.

    .. remarks::

        The example below shows how to access the dataset.

        .. code-block:: python

            from azureml.opendatasets import COVIDTrackingProject

            covid_tracking = COVIDTrackingProject()
            covid_tracking_df = covid_tracking.to_pandas_dataframe()

    :param cols: A list of columns names to load from the dataset. If None, all columns are loaded. For
        information on the available columns in this dataset, see `COVID Tracking Project dataset
        <https://azure.microsoft.com/services/open-datasets/catalog/covid-tracking/>`__.
    :type cols: builtin.list[str]
    :param enable_telemetry: Whether to enable telemetry on this dataset.
    :type enable_telemetry: bool
    """
    _blob_accessor = BlobAccessorDescriptor("covid-tracking")

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
        super(COVIDTrackingProject, self).__init__(
            cols,
            enable_telemetry
        )
