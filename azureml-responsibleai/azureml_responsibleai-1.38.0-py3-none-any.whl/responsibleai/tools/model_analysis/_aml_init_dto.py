# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, Optional

from azureml.responsibleai.tools.model_analysis._model_analysis_settings import ModelAnalysisSettings

"""Module to hold the configuration for an initialisation run."""


class AMLInitDTO:
    """DTO for parameters required to initialise the snapshots and dashboard."""

    def __init__(self,
                 analysis_settings: ModelAnalysisSettings):
        """Construct the configuration from the ModelAnalysisSettings

        :param analysis_settings: The source configuration
        """
        self._title = analysis_settings.title
        self._analysis_id = str(analysis_settings.analysis_id)
        self._train_dataset_id = analysis_settings.train_dataset.id
        self._train_snapshot_id = analysis_settings.train_snapshot_id
        self._test_dataset_id = analysis_settings.test_dataset.id
        self._test_snapshot_id = analysis_settings.test_snapshot_id
        self._datastore_prefix = analysis_settings.datastore_prefix
        self._X_col_names = analysis_settings.X_column_names
        self._target_column_name = analysis_settings.target_column_name
        self._model_id = analysis_settings.model.id
        self._model_loader = analysis_settings.model_loader
        self._confidential_datastore_name = analysis_settings.confidential_datastore_name
        self._model_type = analysis_settings.model_type
        self._maximum_rows_for_test_dataset = analysis_settings.maximum_rows_for_test_dataset
        self._categorical_column_names = analysis_settings.categorical_column_names

    @property
    def title(self) -> str:
        """The title of the dashboard."""
        return self._title

    @property
    def analysis_id(self) -> str:
        return self._analysis_id

    @property
    def model_type(self) -> str:
        return self._model_type

    @property
    def train_dataset_id(self) -> str:
        return self._train_dataset_id

    @property
    def train_snapshot_id(self) -> str:
        return self._train_snapshot_id

    @property
    def test_dataset_id(self) -> str:
        return self._test_dataset_id

    @property
    def test_snapshot_id(self) -> str:
        return self._test_snapshot_id

    @property
    def datastore_prefix(self) -> Optional[str]:
        return self._datastore_prefix

    @property
    def X_column_names(self) -> List[str]:
        return self._X_col_names

    @property
    def target_column_name(self) -> str:
        return self._target_column_name

    @property
    def model_id(self) -> str:
        return self._model_id

    @property
    def model_loader(self):
        return self._model_loader

    @property
    def confidential_datastore_name(self) -> str:
        return self._confidential_datastore_name

    @property
    def maximum_rows_for_test_dataset(self) -> int:
        return self._maximum_rows_for_test_dataset

    @property
    def categorical_column_names(self) -> Optional[List[str]]:
        return self._categorical_column_names
