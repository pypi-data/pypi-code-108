# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Scoring functions that can load a serialized model and predict."""

import json
import logging
import numpy as np
import os
import pandas as pd
import scipy
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    default_data_collator,
)
from typing import Optional, Tuple

from azureml.automl.dnn.nlp.classification.common.constants import (
    DatasetLiterals, MultiClassInferenceLiterals
)
from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import (
    generate_predictions_output_for_labeling_service, load_dataset_for_labeling_service
)
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchMulticlassDatasetWrapper
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_predicted_results
from azureml.automl.dnn.nlp.common._data_utils import get_dataframe_from_dataset_id
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language
from azureml.automl.dnn.nlp.common._utils import _get_language_code, is_data_labeling_run_with_file_dataset
from azureml.automl.dnn.nlp.common.constants import (
    DataLiterals,
    OutputLiterals,
    Split,
    Warnings
)
from azureml.core.run import Run

logger = logging.getLogger(__name__)


class MulticlassInferencer:
    """Class to perform inferencing using training runId and on an unlabeled dataset"""

    def __init__(self,
                 run: Run,
                 device: str):
        """Function to initialize the inferencing object

        :param: Run object
        :param device: device to be used for inferencing
        """
        self.run_object = run
        self.device = device

        if self.device == "cpu":
            logger.warning(Warnings.CPU_DEVICE_WARNING)

        self.workspace = self.run_object.experiment.workspace

    def download_file(
            self,
            run: Run,
            artifact_type: str,
            path: str,
            file_name: str
    ) -> None:
        """Downloads files associated with the run.

        :param run: run context of the run that produced the model
        :param artifact_type: artifact file type
        :param path: artifacts directory path
        :param file_name: file name for artifact
        """
        logger.info("Start downloading {} artifact".format(artifact_type))
        run.download_file(os.path.join(path, file_name), output_file_path=file_name)
        logger.info("Finished downloading {} artifact".format(artifact_type))

    def load_training_artifacts(
            self,
            run: Run,
            artifacts_dir: str,
            dataset_language: str
    ) -> Tuple[AutoModelForSequenceClassification, AutoTokenizer, np.ndarray]:
        """Load the training artifacts.

        :param run: run context of the run that produced the model
        :param artifacts_dir: artifacts directory
        :param dataset_language: language code of dataset
        :return: returns the model, tokenizer and train_label_list from the model's training
        """
        logger.info("Start fetching training artifacts")
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_TOKENIZER, artifacts_dir,
                           MultiClassInferenceLiterals.TOKENIZER_FILE_NAME)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_MODEL, artifacts_dir,
                           MultiClassInferenceLiterals.MODEL_FILE_NAME)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_TRAINING_ARGS, artifacts_dir,
                           MultiClassInferenceLiterals.TRAINING_ARGS)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_LABELS, artifacts_dir,
                           MultiClassInferenceLiterals.LABEL_LIST)
        self.download_file(run, OutputLiterals.ARTIFACT_TYPE_LABELS, artifacts_dir,
                           MultiClassInferenceLiterals.MAX_SEQ_LENGTH)
        model_name_or_path, _ = get_model_from_language(dataset_language)
        # TODO: figure out why the tokenizer.config isn't working out
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        train_label_list = np.load(MultiClassInferenceLiterals.LABEL_LIST, allow_pickle=True)
        max_seq_length = np.load(MultiClassInferenceLiterals.MAX_SEQ_LENGTH, allow_pickle=True)
        config = AutoConfig.from_pretrained(model_name_or_path, num_labels=len(train_label_list))
        model = AutoModelForSequenceClassification.from_pretrained(MultiClassInferenceLiterals.MODEL_FILE_NAME,
                                                                   config=config)
        logger.info("Training artifacts restored successfully")
        return model, tokenizer, train_label_list, max_seq_length.item()

    def predict(self,
                trainer: Trainer,
                test_dataset: PyTorchMulticlassDatasetWrapper,
                df: pd.DataFrame,
                train_label_list: np.ndarray,
                label_column_name: str) -> pd.DataFrame:
        """Generate predictions using model

        :param trainer: Trainer object using which the model was trained
        :param test_dataset: Datasets.dataset object containing test data
        :param df: DataFrame to make predictions on
        :param train_label_list: list of labels from training data
        :param label_column_name: Name/title of the label column
        :return: Dataframe with predictions
        """
        predictions = trainer.predict(test_dataset=test_dataset).predictions
        preds = np.argmax(predictions, axis=1)
        probas = scipy.special.softmax(predictions, axis=1)
        pred_probas = np.amax(probas, axis=1)
        predicted_labels = [train_label_list[item] for item in preds]
        if trainer.is_world_process_zero():
            df[label_column_name] = predicted_labels
            df[DataLiterals.LABEL_CONFIDENCE] = pred_probas
        return df

    def score(
            self,
            input_dataset_id: str,
            enable_datapoint_id_output: Optional[bool] = None
    ) -> pd.DataFrame:
        """Generate predictions from input files.

        :param input_dataset_id: The input dataset id
        :param enable_datapoint_id_output: Whether to include datapoint_id in the output
        :return: Dataframe with predictions
        """
        label_column_name = json.loads(
            self.run_object.parent.parent.properties.get("AMLSettingsJsonString")
        ).get('label_column_name', DataLiterals.LABEL_COLUMN)
        featurization = json.loads(
            self.run_object.parent.parent.properties.get("AMLSettingsJsonString"))['featurization']
        dataset_language = _get_language_code(featurization)

        model, tokenizer, train_label_list, max_seq_length = self.load_training_artifacts(self.run_object,
                                                                                          OutputLiterals.OUTPUT_DIR,
                                                                                          dataset_language)

        is_file_dataset_labeling_run = is_data_labeling_run_with_file_dataset(self.run_object)
        input_file_paths = []
        # Fetch data
        if is_file_dataset_labeling_run:
            df, input_file_paths = load_dataset_for_labeling_service(
                self.workspace, input_dataset_id, DataLiterals.DATA_DIR, False, Split.test
            )
        else:
            df = get_dataframe_from_dataset_id(
                self.workspace, input_dataset_id, Split.test
            )

        # Drop label column if it exists since it is for scoring
        # Drop datapoint_id column as it is not part of the text to be trained for but keep data to add back later
        columns_to_drop = [label_column_name, DatasetLiterals.DATAPOINT_ID]
        datapoint_column = pd.Series()
        if enable_datapoint_id_output:
            datapoint_column = df[DatasetLiterals.DATAPOINT_ID]
        df = df[df.columns.difference(columns_to_drop)]

        # Create final inference data
        inference_data = PyTorchMulticlassDatasetWrapper(df, train_label_list, tokenizer,
                                                         max_seq_length, label_column_name=None)

        # TODO: compute metrics will be added when we support TSI in NLP DNN
        trainer = Trainer(
            model=model,
            tokenizer=tokenizer,
            data_collator=default_data_collator,
        )

        predicted_df = self.predict(trainer, inference_data, df, train_label_list, label_column_name)

        if is_file_dataset_labeling_run:
            generate_predictions_output_for_labeling_service(
                predicted_df, input_file_paths, OutputLiterals.PREDICTIONS_TXT_FILE_NAME, label_column_name
            )
        else:
            # Don't save the actual text in the inference data to the generated predictions file for privacy reasons
            if enable_datapoint_id_output:
                predicted_df[DatasetLiterals.DATAPOINT_ID] = datapoint_column
                output_cols = [DatasetLiterals.DATAPOINT_ID, label_column_name, DataLiterals.LABEL_CONFIDENCE]
                predicted_df = predicted_df[output_cols]
            else:
                output_cols = [label_column_name, DataLiterals.LABEL_CONFIDENCE]
                predicted_df = predicted_df[output_cols]

            save_predicted_results(
                predicted_df, OutputLiterals.PREDICTIONS_CSV_FILE_NAME
            )

        return predicted_df
