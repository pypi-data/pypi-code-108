# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
""" Finetuning the library models for multi-class classification."""

import logging
import numpy as np
import os
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    default_data_collator,
)

from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.dnn.nlp.common.distributed_trainer import DistributedTrainer

from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common.constants import OutputLiterals, SystemSettings


logger = logging.getLogger(__name__)


class TextClassificationTrainer:
    """Class to perform training on a text classification model given a dataset"""

    def __init__(self, train_label_list: np.ndarray, dataset_language: str, enable_distributed: bool = False):
        """
        Function to initialize text-classification trainer

        :param train_label_list: List of labels coming from the training data
        :param dataset_language: Language code of dataset
        :param enable_distributed: Enable distributed training on multiple gpus and machines
        """
        self.train_label_list = train_label_list
        self.num_labels = len(train_label_list)
        self.enable_distributed = enable_distributed
        self.model_name_or_path, download_dir = get_model_from_language(dataset_language, need_path=True)

        config = AutoConfig.from_pretrained(
            self.model_name_or_path,
            num_labels=self.num_labels,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name_or_path,
            use_fast=True,
        )
        # Load model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            download_dir,
            from_tf=False,
            config=config,
        )
        self.trainer = None

        self.training_args = TrainingArguments(
            output_dir=OutputLiterals.OUTPUT_DIR,
            per_device_train_batch_size=MultiClassParameters.TRAIN_BATCH_SIZE,
            per_device_eval_batch_size=MultiClassParameters.VALID_BATCH_SIZE,
            num_train_epochs=MultiClassParameters.EPOCHS,
            save_strategy=MultiClassParameters.SAVE_STRATEGY,
            gradient_accumulation_steps=MultiClassParameters.GRADIENT_ACCUMULATION_STEPS,
            logging_strategy=SystemSettings.LOGGING_STRATEGY,
            report_to=SystemSettings.REPORT_TO
        )

        # Padding strategy
        pad_to_max_length = MultiClassParameters.PAD_TO_MAX_LENGTH
        # TODO: look at fp16 when the right time comes
        if pad_to_max_length:
            self.data_collator = default_data_collator
        else:
            self.data_collator = None

    def train(self, train_dataset: PyTorchMulticlassDatasetWrapper):
        """
        Function to perform training on the model given a training dataset

        :param training_set: PyTorchDataset object containing training data
        """

        if self.enable_distributed:
            self.trainer = DistributedTrainer(
                model=self.model,
                args=self.training_args,
                train_dataset=train_dataset,
                tokenizer=self.tokenizer,
                data_collator=self.data_collator,
            )
        else:
            self.trainer = Trainer(
                model=self.model,
                args=self.training_args,
                train_dataset=train_dataset,
                tokenizer=self.tokenizer,
                data_collator=self.data_collator,
            )

        train_result = self.trainer.train()
        metrics = train_result.metrics

        self.trainer.save_model()  # Saves the tokenizer too for easy upload
        self.trainer.save_metrics("train", metrics)
        self.trainer.save_state()
        if not os.path.exists(OutputLiterals.OUTPUT_DIR):
            os.mkdir(OutputLiterals.OUTPUT_DIR)
        np.save(OutputLiterals.OUTPUT_DIR + '/' + OutputLiterals.LABEL_LIST_FILE_NAME, self.train_label_list)

    def validate(self, eval_dataset: PyTorchMulticlassDatasetWrapper) -> np.ndarray:
        """
        Function to perform evaluate on the model given the trainer object and validation dataset

        :param eval_dataset: PyTorchDataset object containing validation data
        :return resulting predictions for the val dataset (from the cross entropy loss)
        """
        logger.info("*** Evaluate ***")
        return self.trainer.predict(test_dataset=eval_dataset).predictions
