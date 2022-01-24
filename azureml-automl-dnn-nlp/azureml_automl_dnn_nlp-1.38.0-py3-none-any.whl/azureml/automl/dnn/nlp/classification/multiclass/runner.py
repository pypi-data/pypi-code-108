# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""
import importlib
import logging
import os

import numpy as np
from transformers import AutoTokenizer

from azureml._common._error_definition import AzureMLError
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.classification.io.read import dataloader
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_model_wrapper
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer
from azureml.automl.dnn.nlp.classification.multiclass.utils import compute_metrics
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common._utils import (
    _get_language_code,
    is_data_labeling_run_with_file_dataset,
    prepare_run_properties,
    prepare_post_run_properties,
    save_script,
    save_conda_yml,
    is_main_process
)
from azureml.automl.dnn.nlp.common.constants import DataLiterals, OutputLiterals, TaskNames
from azureml.automl.runtime import _metrics_logging
from azureml.core.run import Run
from azureml.train.automl.runtime._entrypoints.utils.common import initialize_log_server

_logger = logging.getLogger(__name__)

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None


def run(automl_settings):
    """Invoke training by passing settings and write the output model.
    :param automl_settings: dictionary with automl settings
    """
    current_run = Run.get_context()
    try:
        is_labeling_run = is_data_labeling_run_with_file_dataset(current_run)
        workspace = current_run.experiment.workspace

        # Parse settings internally initializes logger
        automl_settings_obj = initialize_log_server(current_run.id, automl_settings)

        # Get dataset id
        dataset_id = automl_settings.get(DataLiterals.DATASET_ID, None)
        validation_dataset_id = automl_settings.get(DataLiterals.VALIDATION_DATASET_ID, None)
        Validation.validate_value(validation_dataset_id, name="validation_data")
        primary_metric = automl_settings_obj.primary_metric

        dataset_language = _get_language_code(automl_settings_obj.featurization)
        label_column_name = automl_settings_obj.label_column_name
        if label_column_name is None:
            if not is_labeling_run:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        ExecutionFailure,
                        error_details="Need to pass in label_column_name argument for training"
                    )
                )
            label_column_name = DataLiterals.LABEL_COLUMN

        model_name, _ = get_model_from_language(dataset_language)
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        training_set, validation_set, label_list, train_label_list, y_val, max_seq_length =\
            dataloader.load_multiclass_dataset(dataset_id, validation_dataset_id, label_column_name,
                                               workspace, tokenizer, is_labeling_run, DataLiterals.DATA_DIR)

        distributed = hasattr(automl_settings_obj, "enable_distributed_dnn_training") and \
            automl_settings_obj.enable_distributed_dnn_training is True and has_horovod
        trainer_class = TextClassificationTrainer(train_label_list, dataset_language, enable_distributed=distributed)
        prepare_run_properties(current_run, trainer_class.model_name_or_path)
        trainer_class.train(training_set)
        primary_metric_score = np.nan
        if is_main_process():
            if validation_set is not None:
                val_predictions = trainer_class.validate(validation_set)
                results = compute_metrics(y_val, val_predictions, label_list, train_label_list)
                primary_metric_score = results[primary_metric]
                log_binary = len(label_list) == 2
                _metrics_logging.log_metrics(current_run, results, log_binary=log_binary)

            model_wrapper = ModelWrapper(trainer_class.trainer.model, train_label_list, tokenizer, max_seq_length)
            model_path = save_model_wrapper(model_wrapper)

            multiclass_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                "io", "write", TaskNames.MULTICLASS)
            save_script(OutputLiterals.SCORE_SCRIPT, multiclass_directory)
            deploy_script_path = save_script(OutputLiterals.DEPLOY_SCRIPT, multiclass_directory)
            conda_file_path = save_conda_yml(current_run.get_environment())

            # 2147483648 is 2 GB of memory
            prepare_post_run_properties(current_run,
                                        model_path,
                                        2147483648,
                                        conda_file_path,
                                        deploy_script_path,
                                        primary_metric,
                                        primary_metric_score)
    except Exception as e:
        _logger.error("Multi-class runner script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(current_run, e)
        raise
