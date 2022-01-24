# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for NER."""
# flake8: noqa

import json
import logging
import os
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from azureml.automl.dnn.nlp.common._data_utils import get_dataframe_from_dataset_id
from azureml.automl.dnn.nlp.common.constants import DataLabelingLiterals, DataLiterals, OutputLiterals, Split
from azureml.core.workspace import Workspace

_logger = logging.getLogger(__name__)


def load_datasets_for_labeling_service(
        workspace: Workspace,
        dataset_id: str,
        validation_dataset_id: Optional[str],
        download_dir: str,
        include_label: bool
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """Load classification dataset from Labeling service.

    :param workspace: Workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param validation_dataset_id: Unique identifier to fetch validation dataset from datastore
    :param download_dir: Directory to download the text files into
    :param include_label: Whether to include label column
    :return: training dataframe, validation dataframe
    """
    train_df, _ = load_dataset_for_labeling_service(
        workspace,
        dataset_id,
        download_dir,
        include_label,
        Split.train
    )
    validation_df = None
    if validation_dataset_id:
        validation_df, _ = load_dataset_for_labeling_service(
            workspace,
            validation_dataset_id,
            download_dir,
            include_label,
            Split.valid
        )
    return train_df, validation_df


def load_dataset_for_labeling_service(
        workspace: Workspace,
        dataset_id: str,
        download_dir: str,
        include_label: bool,
        data_split: Split
) -> Tuple[str, List[str]]:
    """
    Load classification dataset from Labeling service.

    Labeling service will pass in TabularDataset that includes list of the paths for the actual text files
    and its label in a span format. This spans format data will be converted into tabular format that we support
    for our text classification tasks.

    :param workspace: workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param download_dir: Directory to download the text files into
    :param include_label: Whether to include label column
    :param data_split: Label for data split
    :return name of the converted data file and list of files referenced
    """
    # this import is needed to extract below information from the dataset
    # noinspection PyUnresolvedReferences
    import azureml.contrib.dataset
    _logger.info("Loading {} dataset for labeling service".format(data_split.value))
    dataset_df = get_dataframe_from_dataset_id(workspace, dataset_id, data_split)

    os.makedirs(download_dir, exist_ok=True)
    records = json.loads(dataset_df.to_json(orient='records'))
    processed_input_file_counter = 1

    data_dict = dict()
    input_file_paths = []

    for record in records:
        _logger.info("Processing file {} of {}".format(processed_input_file_counter, len(records)))
        if include_label:
            label = record["label"]
        else:
            label = None
        input_file_path = record[DataLabelingLiterals.IMAGE_URL][DataLabelingLiterals.RESOURCE_IDENTIFIER]
        datastore_name = record[DataLabelingLiterals.IMAGE_URL][
            DataLabelingLiterals.ARGUMENTS][DataLabelingLiterals.DATASTORENAME]
        datastore = workspace.datastores[datastore_name]

        # Download
        download_path = os.path.join(datastore_name, input_file_path)
        full_download_path = os.path.join(os.getcwd(), datastore_name, input_file_path)
        datastore.download(target_path=datastore_name, prefix=input_file_path, overwrite=True)
        data_dict[processed_input_file_counter-1] = _convert_to_dict_entry(full_download_path, label, include_label)
        input_file_paths.append(download_path)
        processed_input_file_counter += 1

    data_df = pd.DataFrame.from_dict(data_dict, orient='index')
    _logger.info("Finished loading {} dataset for labeling service".format(data_split.value))
    return data_df, input_file_paths


def _convert_to_dict_entry(input_file_path, label_objects, include_label):
    # read the text content
    with open(input_file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        input_text_content = f.read()

    # create dictionary entry
    dict_entry = dict()
    dict_entry[DataLiterals.TEXT_COLUMN] = input_text_content
    if include_label:
        dict_entry[DataLiterals.LABEL_COLUMN] = str(label_objects)
    return dict_entry


def format_multilabel_predicted_df(predicted_df: pd.DataFrame, label_column_name: str):
    # label column "a,b,c" to ["a", "b", "c"]
    # label confidence "0.1,0.2,0.3" to [0.1, 0.2, 0.3]
    predicted_df[label_column_name] = predicted_df[label_column_name].str.split(",")
    predicted_df[DataLiterals.LABEL_CONFIDENCE] = \
        predicted_df[DataLiterals.LABEL_CONFIDENCE].str.split(",").apply(lambda x: [float(i) for i in x])

    return predicted_df


def generate_predictions_output_for_labeling_service(
        predicted_df: pd.DataFrame,
        input_file_paths: List[str],
        output_file_name: str,
        label_column_name: str
) -> None:
    """
    Generate spans format output from predictions for labeling service

    :param predicted_df: predictions
    :param input_file_paths: list of test file downloaded paths
    :param output_file_name: name of the file to write the results to
    :param label_column_name: name of the label column from predicted_df
    """
    _logger.info("Generating output for labeling service")

    os.makedirs(OutputLiterals.OUTPUT_DIR, exist_ok=True)
    predictions_output_path = os.path.join(OutputLiterals.OUTPUT_DIR, output_file_name)

    # write converted entry to predictions.txt
    with open(predictions_output_path, "a") as f:
        for i in range(len(input_file_paths)):
            label_confidence = predicted_df[DataLiterals.LABEL_CONFIDENCE][i]
            if isinstance(label_confidence, np.floating):
                label_confidence = float(label_confidence)
            text_file_full_path = DataLiterals.DATASTORE_PREFIX + input_file_paths[i]
            result_entry = {
                DataLabelingLiterals.IMAGE_URL: text_file_full_path,
                DataLiterals.LABEL_COLUMN: predicted_df[label_column_name][i],
                DataLiterals.LABEL_CONFIDENCE: label_confidence
            }
            f.write(json.dumps(result_entry))
            f.write('\n')

    _logger.info("Successfully generated output for labeling service")
