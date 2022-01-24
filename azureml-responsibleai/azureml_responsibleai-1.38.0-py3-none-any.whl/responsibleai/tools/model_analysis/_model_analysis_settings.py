# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional, Union
import uuid


from azureml.core import Dataset, Model, RunConfiguration, Workspace
from azureml.exceptions import AzureMLException
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentOutOfRange

from azureml.responsibleai.common.model_loader import ModelLoader


class ModelAnalysisSettings:
    """
    Settings object for persisting various settings used throughout a model analysis. This object is used for internal
    use cases only, end users should use the ModelAnalysisConfig.
    """

    def __init__(self,
                 *,
                 workspace: Optional[Workspace] = None,
                 title: str,
                 analysis_id: uuid.UUID = None,
                 model: Model,
                 model_loader: Union[ModelLoader, str],
                 model_type: str,
                 train_dataset: Dataset,
                 test_dataset: Dataset,
                 X_column_names: List[str],
                 target_column_name: str,
                 confidential_datastore_name: str,
                 datastore_prefix: Optional[str] = None,
                 run_configuration: RunConfiguration,
                 maximum_rows_for_test_dataset: int,
                 categorical_column_names: Optional[List[str]] = None):
        self._workspace = workspace
        self._title = title
        if analysis_id is None:
            self._analysis_id = uuid.uuid4()
        else:
            self._analysis_id = analysis_id
        self._model = model
        self._model_type = model_type  # Should verify against approved list

        # In the future, will want to allow a dataset or
        # snapshot to be specified
        self._train_dataset = train_dataset
        self._train_snapshot_id = str(uuid.uuid4())
        self._test_dataset = test_dataset
        self._test_snapshot_id = str(uuid.uuid4())
        self._datastore_prefix = datastore_prefix

        self._X_column_names: List[str] = X_column_names
        self._target_column_name = target_column_name
        if confidential_datastore_name is None:
            raise ValueError("Must supply confidential data store")
        self._confidential_datastore_name = confidential_datastore_name
        self._model_loader = model_loader
        self._run_configuration = run_configuration
        if maximum_rows_for_test_dataset <= 0:
            raise AzureMLException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange,
                    argument_name='maximum_rows_for_test',
                    min='1',
                    max=str(2**32)
                )
            )
        self._maximum_rows_for_test_dataset = maximum_rows_for_test_dataset
        self._categorical_column_names = categorical_column_names

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    @workspace.setter
    def workspace(self, workspace: Workspace) -> None:
        self._workspace = workspace

    @property
    def title(self) -> str:
        return self._title

    @ property
    def analysis_id(self) -> uuid.UUID:
        return self._analysis_id

    @property
    def model(self) -> Model:
        return self._model

    @property
    def model_type(self) -> str:
        return self._model_type

    @property
    def train_dataset(self) -> Dataset:
        return self._train_dataset

    @property
    def train_snapshot_id(self) -> str:
        return self._train_snapshot_id

    @property
    def test_dataset(self) -> Dataset:
        return self._test_dataset

    @property
    def test_snapshot_id(self) -> str:
        return self._test_snapshot_id

    @property
    def datastore_prefix(self) -> Optional[str]:
        return self._datastore_prefix

    @property
    def X_column_names(self) -> List[str]:
        return self._X_column_names

    @property
    def target_column_name(self) -> str:
        return self._target_column_name

    @property
    def confidential_datastore_name(self) -> str:
        return self._confidential_datastore_name

    @property
    def model_loader(self) -> Union[ModelLoader, str]:
        return self._model_loader

    @property
    def run_configuration(self) -> RunConfiguration:
        return self._run_configuration

    @property
    def maximum_rows_for_test_dataset(self) -> int:
        return self._maximum_rows_for_test_dataset

    @property
    def categorical_column_names(self) -> Optional[List[str]]:
        return self._categorical_column_names
