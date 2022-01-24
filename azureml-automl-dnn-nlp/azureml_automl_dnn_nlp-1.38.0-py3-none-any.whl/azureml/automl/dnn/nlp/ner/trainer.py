# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Fine-tuning the library models for named entity recognition in CoNLL-2003 format."""
import logging
from typing import Any, Dict, List

from torch.utils.data import Dataset
from transformers import (
    AutoConfig,
    AutoModelForTokenClassification,
    Trainer,
    TrainingArguments,
)

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.automl_error_definitions import ExecutionFailure
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common.distributed_trainer import DistributedTrainer
from azureml.automl.dnn.nlp.common.constants import NERModelParameters, SystemSettings
from azureml.automl.dnn.nlp.ner._utils import remove_metric_prefix
from azureml.automl.dnn.nlp.ner.token_classification_metrics import TokenClassificationMetrics

logger = logging.getLogger(__name__)


class NERPytorchTrainer:
    """Class for training an NER model for a given dataset."""
    def __init__(
            self,
            label_list: List[str],
            model_name: str,
            download_dir: str,
            output_dir: str,
            enable_distributed: bool = False
    ):
        """
        Function to initialize pytorch ner trainer

        :param label_list: list of unique labels
        :param model_name: name of model to use
        :download_dir: download directory of CDN model
        :param output_dir: output directory to save results to
        """
        self.model_name = model_name
        self.output_dir = output_dir
        self.enable_distributed = enable_distributed

        self.label_list = label_list
        num_labels = len(label_list)

        # Load config
        config = AutoConfig.from_pretrained(
            self.model_name,
            num_labels=num_labels,
            finetuning_task=NERModelParameters.TASK_NAME
        )

        # Load model
        self.model = AutoModelForTokenClassification.from_pretrained(
            download_dir,
            from_tf=False,
            config=config
        )

        self.trainer = None

    def train(
            self,
            train_dataset: Dataset
    ) -> None:
        """
        Function to perform training on the model given a training dataset.
        :param train_dataset: dataset to train with
        :return:
        """
        with log_utils.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.TRAINING
        ):
            # Create trainer
            token_classification_metrics = TokenClassificationMetrics(self.label_list)
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                per_device_train_batch_size=NERModelParameters.PER_DEVICE_TRAIN_BATCH_SIZE,
                num_train_epochs=NERModelParameters.NUM_TRAIN_EPOCHS,
                save_strategy=NERModelParameters.SAVE_STRATEGY,
                logging_strategy=SystemSettings.LOGGING_STRATEGY,
                report_to=SystemSettings.REPORT_TO
            )
            if self.enable_distributed:
                self.trainer = DistributedTrainer(
                    model=self.model,
                    args=training_args,
                    train_dataset=train_dataset,
                    compute_metrics=token_classification_metrics.compute_metrics
                )
            else:
                self.trainer = Trainer(
                    model=self.model,
                    args=training_args,
                    train_dataset=train_dataset,
                    compute_metrics=token_classification_metrics.compute_metrics
                )

            # Train
            self.trainer.train()

            # Save model
            self.trainer.save_model()
            self.trainer.save_state()

    def validate(
            self,
            eval_dataset: Dataset
    ) -> Dict[str, Any]:
        """
        Function to perform evaluation on the trained model given a val dataset.
        :param eval_dataset: dataset to validate the model with
        :return:
        """
        if self.trainer is None:
            logger.error("Unable to validate when model has not been trained. Please train the model first.")
            raise ValidationException._with_error(
                AzureMLError.create(
                    ExecutionFailure,
                    operation_name="validate",
                    error_details="need to train before calling to validate"
                )
            )

        with log_utils.log_activity(
                logger,
                activity_name=constants.TelemetryConstants.VALIDATION
        ):
            metrics = self.trainer.evaluate(eval_dataset)
            metrics = remove_metric_prefix(metrics, "eval_")

        return metrics
