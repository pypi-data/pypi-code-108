# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import os
import pandas as pd
from datetime import datetime

from azureml.automl.core.shared import constants
from azureml.automl.core.shared.exceptions import (AutoMLException, ClientException)
from azureml.automl.core.shared.utilities import get_error_code
from azureml.core import Run
from azureml.core.model import Model
from azureml.exceptions import AzureMLException
from azureml.train.automl import AutoMLConfig
from azureml.train.automl.runtime._many_models.train_helper import Arguments
from azureml.train.automl.runtime._many_models.automl_prs_driver_base import AutoMLPRSDriverBase


class ManyModelsAutoMLTrainDriver(AutoMLPRSDriverBase):
    """The driver code for Many models AutoML train run."""

    def __init__(
            self,
            current_step_run: Run,
            automl_settings: Dict[str, Any],
            args: Arguments
    ):
        """The driver code for Many models AutoML train run."""
        super(ManyModelsAutoMLTrainDriver, self).__init__(current_step_run)
        self.automl_settings = automl_settings
        self.args = args
        self._automl_run_properties = {'many_models_run': True}  # type: Dict[str, Any]
        self.partition_column_names = self.automl_settings.get('partition_column_names', [])

    def run(self, input_data_file: str, output_data_file: str) -> Any:
        """Run the data file."""
        self._console_writer.println(output_data_file)
        timestamp_column = self.automl_settings.get('time_column_name', None)

        model_name = ''
        current_run = None
        tags_dict = {}  # type: Dict[str, str]

        date1 = datetime.now()
        self._console_writer.println('start (' + input_data_file + ') ' + str(datetime.now()))

        file_name_with_extension = os.path.basename(input_data_file)
        file_name, file_extension = os.path.splitext(file_name_with_extension)

        try:
            data = self.read_input_data(input_data_file, [timestamp_column])
            self.pre_run(data, file_name_with_extension)
            tags_dict = self.get_tag_dict(file_name_with_extension)

            if self.args.retrain_failed_models:
                trained_model_logs = self.get_trained_models_logs(tags_dict, file_name, date1)
                if trained_model_logs is not None:
                    return trained_model_logs

            fitted_model, current_run, best_child_run = self._train_model(
                input_data_file, data, self.automl_settings, self.current_step_run)

            model_name = 'automl_' + tags_dict['Hash']

            logs = self.post_run(
                tags_dict, best_child_run, current_run, fitted_model, date1, input_data_file, model_name
            )
        except (ClientException, AzureMLException, AutoMLException) as error:
            logs = self.post_run_exception(
                tags_dict, current_run, date1, input_data_file, model_name, error
            )

        return logs

    def _train_model(
            self,
            file_path: str,
            data: pd.DataFrame,
            automl_settings: Dict[str, Any],
            current_step_run: Run) -> Tuple[Model, Run, Run]:
        """
        Train AutoML model.

        :param file_path: The path to training file.
        :param data: The training data.
        :param automl_settings: The settings for training.
        :param current_step_run: current run.
        :return: the tuple with fitted model, local parent run and
                 the best child run.
        """
        file_name = file_path.split('/')[-1][:-4]
        self._console_writer.println(file_name)
        self._console_writer.println("in train_model")
        self._console_writer.println('data')
        self._console_writer.println(str(data.head(5)))
        self._console_writer.println(str(automl_settings))
        automl_config = AutoMLConfig(training_data=data, **automl_settings)

        self._console_writer.println("submit_child")
        local_run = current_step_run.submit_child(automl_config, show_output=True)

        self._console_writer.println(str(local_run))

        best_child_run, fitted_model = local_run.get_output()

        return fitted_model, local_run, best_child_run

    def get_tag_dict(self, file_name_with_extension: str) -> Dict[str, str]:
        """
        Get the tags, which will be set to model.

        :param file_name_with_extension: The
        :return: The dictionary with tags.
        """
        tags_dict = {'ModelType': 'AutoML'}
        tags_dict.update(self._automl_run_properties['many_models_data_tags'])

        tags_dict.update({'InputData': file_name_with_extension})
        tags_dict.update({'StepRunId': self.current_step_run.id})
        tags_dict.update({'RunId': self.current_step_run.parent.id})

        tags_dict.update({'Hash': self.get_hashed_model_string()})

        return tags_dict

    def get_hashed_model_string(self) -> str:
        """Get hashed model string."""
        model_string = '_'.join(
            str(v) for k, v in sorted(self._automl_run_properties['many_models_data_tags'].items()))
        self._console_writer.println("model string to encode " + model_string)
        sha = hashlib.sha256()
        sha.update(model_string.encode())
        return sha.hexdigest()

    def modify_run_properties(self, data: pd.DataFrame, file_name_with_extension: str) -> None:
        """
        Modify AutoML run properties based on input data and input file name.

        :param data: Input data.
        :param file_name_with_extension: The input data file name.
        """
        group_columns_dict = {}
        for column_name in self.partition_column_names:
            group_columns_dict.update({column_name: str(data.iat[0, data.columns.get_loc(column_name)])})
            # train model
        self._automl_run_properties['many_models_data_tags'] = group_columns_dict
        self._automl_run_properties['many_models_input_file'] = file_name_with_extension

    def get_trained_models_logs(
            self, tags_dict: Dict[str, str], file_name: str, start_time: datetime
    ) -> Optional[List[Any]]:
        """
        Return the logging record about the models found by tags.

        :param tags_dict: The dictionary of tags to get the models.
        :param file_name: Input file name.
        :param start_time: the start of training.
        :return: If the model can be found, return the logs, else return None.
        """
        self._console_writer.println('querying for existing models')
        try:
            tags = [[k, v] for k, v in tags_dict.items()]
            models = Model.list(self.current_step_run.experiment.workspace, tags=tags, latest=True)

            if models:
                self._console_writer.println(
                    "Model already exists for the dataset {}. Skipping now.".format(models[0].name))
                return self._compose_logs(file_name, start_time, models[0])
            else:
                self._console_writer.println('No models can be found.')
        except Exception as error:
            self._console_writer.println('Failed to list the models. ' + 'Error message: ' + str(error))
        return None

    def pre_run(self, data: pd.DataFrame, file_name_with_extension: str) -> None:
        """
        Pre-automl training run execution.

        :param data: Input data.
        :param file_name_with_extension: The input file name.
        """
        self.modify_run_properties(data, file_name_with_extension)

    def post_run(
            self, tags_dict: Dict[str, str], best_child_run: Run, current_run: Run, fitted_model: Model,
            start_time: datetime, input_data_file: str, model_name: str
    ) -> List[Any]:
        """Register the model and generating the logs."""

        current_run.add_properties({
            k: str(self._automl_run_properties[k])
            for k in self._automl_run_properties
        })

        logs = []  # type: List[Any]
        error_message = None
        error_code = None
        error_type = None

        try:
            self._console_writer.println('done training')

            self._console_writer.println('Trained best model ' + model_name)

            self._console_writer.println(str(best_child_run))
            self._console_writer.println(str(fitted_model))
            self._console_writer.println(model_name)

            self._console_writer.println('register model')

            best_child_run.register_model(
                model_name=model_name, model_path=constants.MODEL_PATH, description='AutoML', tags=tags_dict)
            self._console_writer.println('Registered ' + model_name)
        except Exception as error:
            raise AzureMLException('Failed to register the model. Error message: {}'.format(error)) from error

        date2 = datetime.now()

        logs.append('AutoML')
        logs.append(input_data_file)
        logs.append('Succeeded')
        logs.append(current_run.id)
        logs.append(current_run.get_status())
        logs.append(model_name)
        logs.append(tags_dict)
        logs.append(str(start_time))
        logs.append(str(date2))
        logs.append(error_type)
        logs.append(error_code)
        logs.append(error_message)

        self._console_writer.println('ending (' + input_data_file + ') ' + str(date2))
        return logs

    def post_run_exception(
            self, tags_dict: Dict[str, str], current_run: Run,
            start_time: datetime, input_data_file: str, model_name: str, error: BaseException
    ) -> List[Any]:
        """Handle the exception the AutoML run meet."""
        logs = []  # type: List[Any]
        date2 = datetime.now()
        error_message = 'Failed to train the model. ' + 'Error : ' + str(error)

        logs.append('AutoML')
        logs.append(input_data_file)
        logs.append('Failed')

        if current_run:
            logs.append(current_run.id)
            logs.append(current_run.get_status())
        else:
            logs.append(current_run)
            logs.append('Failed')

        logs.append(model_name)
        logs.append(tags_dict)
        logs.append(str(start_time))
        logs.append(str(date2))
        if isinstance(error, AutoMLException):
            logs.append(error.error_type)
        else:
            logs.append(None)
        logs.append(get_error_code(error))
        logs.append(error_message)

        self._console_writer.println(error_message)
        self._console_writer.println('ending (' + input_data_file + ') ' + str(date2))
        return logs

    def _compose_logs(
            self,
            input_data_file: str,
            start_time: datetime,
            model: Optional[Model] = None
    ) -> List[Any]:
        logs = []  # type: List[Any]
        logs.append('AutoML')
        logs.append(input_data_file)
        logs.append(None)
        logs.append(None)
        logs.append(model.name if model is not None else None)
        logs.append(model.tags if model is not None else None)
        logs.append(start_time)
        logs.append(datetime.now())
        logs.append(None)
        logs.append(None)
        logs.append(None)
        return logs
