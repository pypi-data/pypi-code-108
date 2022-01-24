# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Entry script that is invoked by the driver script from automl."""
import importlib
import logging
import os

import numpy as np

from azureml._common._error_definition import AzureMLError
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_multilabel_dataset
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_model_wrapper, save_metrics
from azureml.automl.dnn.nlp.classification.multilabel.bert_class import BERTClass
from azureml.automl.dnn.nlp.classification.multilabel.distributed_trainer import HorovodDistributedTrainer
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper
from azureml.automl.dnn.nlp.classification.multilabel.trainer import PytorchTrainer
from azureml.automl.dnn.nlp.common._utils import (
    _get_language_code,
    is_data_labeling_run_with_file_dataset,
    is_main_process,
    prepare_post_run_properties,
    prepare_run_properties,
    save_conda_yml,
    save_script
)
from azureml.automl.dnn.nlp.common.constants import (
    DataLiterals, ModelNames, OutputLiterals, TaskNames
)
from azureml.automl.runtime.shared.score import constants
from azureml.core.run import Run
from azureml.train.automl.runtime._entrypoints.utils.common import initialize_log_server

horovod_spec = importlib.util.find_spec("horovod")
has_horovod = horovod_spec is not None

_logger = logging.getLogger(__name__)


def run(automl_settings):
    """Invoke training by passing settings and write the output model.
    :param automl_settings: dictionary with automl settings
    """
    current_run = Run.get_context()
    try:
        is_labeling_run = is_data_labeling_run_with_file_dataset(current_run)

        workspace = current_run.experiment.workspace
        prepare_run_properties(current_run, ModelNames.BERT_BASE_UNCASED)

        # Parse settings internally initializes logger
        automl_settings_obj = initialize_log_server(current_run.id, automl_settings)

        # Get dataset id
        dataset_id = automl_settings.get(DataLiterals.DATASET_ID, None)
        validation_dataset_id = automl_settings.get(DataLiterals.VALIDATION_DATASET_ID, None)
        Validation.validate_value(validation_dataset_id, name="validation_data")

        # Extract settings needed
        is_gpu = automl_settings_obj.is_gpu if hasattr(automl_settings_obj, "is_gpu") else True
        primary_metric = automl_settings_obj.primary_metric
        label_column_name = automl_settings_obj.label_column_name
        if label_column_name is None:
            if not is_labeling_run:
                raise ValidationException._with_error(
                    AzureMLError.create(
                        ExecutionFailure,
                        operation_name="runner",
                        error_details="Need to pass in label_column_name argument for training"
                    )
                )
            label_column_name = DataLiterals.LABEL_COLUMN
        dataset_language = _get_language_code(automl_settings_obj.featurization)

        # Load Dataset
        training_set, validation_set, num_label_cols, vectorizer = load_multilabel_dataset(
            dataset_id, validation_dataset_id, label_column_name, workspace, dataset_language,
            is_labeling_run, DataLiterals.DATA_DIR
        )

        # Get Trainer
        if hasattr(automl_settings_obj, "enable_distributed_dnn_training") and \
                automl_settings_obj.enable_distributed_dnn_training is True and has_horovod:
            trainer = HorovodDistributedTrainer(BERTClass, dataset_language, num_label_cols)
        else:
            trainer = PytorchTrainer(BERTClass, dataset_language, num_label_cols, is_gpu)

        # Train
        model = trainer.train(training_set)

        primary_metric_score = np.nan
        if is_main_process():
            # Validate and Log Metrics if validation set is provided
            if validation_set is not None:
                metrics_dict, metrics_dict_with_thresholds = trainer.compute_metrics(validation_set)

                # Log metrics
                for metric_name in constants.TEXT_CLASSIFICATION_MULTILABEL_SET:
                    current_run.log(metric_name, metrics_dict[metric_name])
                primary_metric_score = metrics_dict[primary_metric]

                save_metrics(metrics_dict_with_thresholds)

            model_wrapper = ModelWrapper(
                model, training_set.tokenizer, dataset_language, vectorizer, label_column_name
            )
            multilabel_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                "io", "write", TaskNames.MULTILABEL)
            model_path = save_model_wrapper(model_wrapper)

            save_script(OutputLiterals.SCORE_SCRIPT, multilabel_directory)
            deploy_script_path = save_script(OutputLiterals.DEPLOY_SCRIPT, multilabel_directory)
            conda_file_path = save_conda_yml(current_run.get_environment())

            # 2147483648 bytes is 2GB
            # TODO: set the model size based on real model, tokenizer, etc size
            prepare_post_run_properties(
                current_run,
                model_path,
                2147483648,
                conda_file_path,
                deploy_script_path,
                primary_metric,
                primary_metric_score
            )
    except Exception as e:
        _logger.error("Multi-label runner script terminated with an exception of type: {}".format(type(e)))
        run_lifecycle_utilities.fail_run(current_run, e)
        raise
