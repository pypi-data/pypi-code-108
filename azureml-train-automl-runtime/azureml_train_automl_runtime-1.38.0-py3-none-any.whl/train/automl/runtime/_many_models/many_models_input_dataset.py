# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Class for Many models input dataset.
"""
from typing import cast, List, Optional, Union
import time

from azureml.core import Dataset
from azureml.data import FileDataset, LinkTabularOutputDatasetConfig, TabularDataset
from azureml.pipeline.core import PipelineParameter
from azureml.pipeline.core import PipelineData

from azureml.train.automl.constants import HTSConstants, HTSSupportedInputType
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.train.automl._hts import hts_client_utilities


class ManyModelsInputDataset:
    """Class used to get different dataset for many models and HTS steps."""
    TRAINING_LEVEL_DATA_NAME = 'prepared_training_level_data'

    def __init__(
            self,
            input_dataset_type: HTSSupportedInputType,
            dataset: Union[FileDataset, TabularDataset],
            dataset_consumption_config: DatasetConsumptionConfig,
            use_train_level: bool = False
    ):
        """
        Class used to get different dataset for many models steps.

        :param input_dataset_type: The type of a input dataset.
        :param dataset: The file dataset or tabular dataset of the input data.
        :param dataset_consumption_config: The consumption config for the input.
        :param use_train_level: If true the output dataset will use train level, else will use the input dataset.
        """
        self.dataset_consumption_config = dataset_consumption_config
        self.dataset = dataset
        self.input_dataset_type = input_dataset_type
        self.identifier = int(time.time())
        self.agg_blob_dir = HTSConstants.DEFAULT_ARG_VALUE
        self.agg_dataset_name = HTSConstants.DEFAULT_ARG_VALUE
        self.agg_file_dataset = None
        if use_train_level:
            self._training_level_dataset = PipelineData(
                ManyModelsInputDataset.TRAINING_LEVEL_DATA_NAME, is_directory=True).as_dataset()
        else:
            self._training_level_dataset = None
        if self.is_partition_step_needed:
            self.link_partition_output_config = LinkTabularOutputDatasetConfig(
                name=HTSConstants.HTS_OUTPUT_PARTITIONED)
        else:
            self.link_partition_output_config = None

    @property
    def partitioned_dataset_name(self) -> Optional[str]:
        """
        Get the partitioned dataset name used in the following step.

        :return: The dataset name.
        """
        if self.is_partition_step_needed:
            return "{}_partitioned_{}".format(self.dataset_consumption_config.name, self.identifier)
        return None

    @property
    def is_partition_step_needed(self) -> bool:
        """The flag to show whether a partition step is needed for the pipeline."""
        return cast(bool, self.input_dataset_type == HTSSupportedInputType.TABULAR_DATASET)

    @property
    def partition_step_input(self) -> Optional[DatasetConsumptionConfig]:
        """The partition step input."""
        if self.is_partition_step_needed:
            return self.dataset_consumption_config
        return None

    @property
    def python_script_partitioned_input(self) -> DatasetConsumptionConfig:
        """The input of a PythonScriptStep after partitioning."""
        if self.input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            return self.dataset_consumption_config.as_mount()
        elif self.input_dataset_type == HTSSupportedInputType.TABULAR_DATASET and \
                self.link_partition_output_config is not None:
            return self.link_partition_output_config.as_input("partitioned_dataset")
        return self.dataset_consumption_config

    @property
    def prs_input(self) -> DatasetConsumptionConfig:
        """The input for the PRS step."""
        if self.is_partition_step_needed and self.link_partition_output_config is not None:
            return self.link_partition_output_config.as_input("partitioned_dataset")
        if self._training_level_dataset is not None and self.input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            return self._training_level_dataset
        return self.dataset_consumption_config

    @property
    def training_level_dataset(self) -> Optional[PipelineData]:
        """Get training level dataset."""
        if self.input_dataset_type == HTSSupportedInputType.FILE_DATASET:
            return self._training_level_dataset
        return None

    def create_file_dataset(self, workspace, datastore, console_writer):
        """Create a file dataset."""
        dataset_prefix = "hts_agg"
        if datastore is None:
            datastore = workspace.get_default_datastore()
        self.agg_blob_dir = "{}_{}".format(dataset_prefix, self.identifier)
        self.agg_dataset_name = "{}_{}".format(dataset_prefix, self.identifier)

        new_dataset = Dataset.File.from_files(path=datastore.path(self.agg_blob_dir + '/'), validate=False)
        self.agg_file_dataset = new_dataset.register(workspace, self.agg_dataset_name, create_new_version=True)
        console_writer.println("Aggregation dataset is created with the name {}".format(self.agg_dataset_name))

    @staticmethod
    def from_input_data(
            input_data: Union[DatasetConsumptionConfig, FileDataset, TabularDataset],
            partition_column_names: List[str],
            input_dataset_name: str = "input_dataset",
            use_train_level: bool = False
    ) -> 'ManyModelsInputDataset':
        """
        Build dataset info from input data.
        """
        if isinstance(input_data, DatasetConsumptionConfig):
            input_dataset = input_data.dataset
            consumption_config = input_data
            if isinstance(input_dataset, PipelineParameter):
                input_dataset = input_dataset.default_value
        else:
            input_dataset = input_data
            consumption_config = DatasetConsumptionConfig(input_dataset_name, input_data)
        input_dataset_type = hts_client_utilities.get_input_dataset_type(input_dataset, partition_column_names)
        return ManyModelsInputDataset(
            input_dataset_type=input_dataset_type,
            dataset=input_dataset,
            dataset_consumption_config=consumption_config,
            use_train_level=use_train_level
        )
