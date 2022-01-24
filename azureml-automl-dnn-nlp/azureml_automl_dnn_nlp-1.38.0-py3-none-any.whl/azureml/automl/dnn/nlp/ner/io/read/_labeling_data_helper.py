# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for NER."""
# flake8: noqa

import json
import logging
import os
from typing import List, Tuple

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import DataPathNotFound
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._data_utils import get_dataframe_from_dataset_id
from azureml.automl.dnn.nlp.common.constants import DataLiterals, DataLabelingLiterals
from azureml.core.workspace import Workspace

_logger = logging.getLogger(__name__)


def load_dataset_for_labeling_service(
        workspace: Workspace,
        dataset_id: str,
        ner_dir: str,
        data_filename: str,
        data_label: str
) -> str:
    """
    Load dataset from Labeling service span format input.

    Labeling service will pass in TabularDataset that includes list of the paths for the actual text files
    and its label in a span format. This spans format data will be converted into conll format that we support
    for our NER task.

    :param workspace: workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param ner_dir: directory where data should be downloaded
    :param data_filename: filename to save converted dataset
    :param data_label: dataset type label
    """
    # this import is needed to extract below information from the dataset
    # noinspection PyUnresolvedReferences
    import azureml.contrib.dataset
    _logger.info("Loading dataset for labeling service")
    dataset_df = get_dataframe_from_dataset_id(workspace, dataset_id, data_label)

    os.makedirs(ner_dir, exist_ok=True)

    final_conll_path = os.path.join(ner_dir, data_filename)
    records = json.loads(dataset_df.to_json(orient='records'))
    processed_input_file_counter = 1

    for record in records:
        _logger.info("Processing file {} of {}".format(processed_input_file_counter, len(records)))
        label = record["label"]
        input_file_path = record[DataLabelingLiterals.IMAGE_URL][DataLabelingLiterals.RESOURCE_IDENTIFIER]
        datastore_name = record[DataLabelingLiterals.IMAGE_URL][
            DataLabelingLiterals.ARGUMENTS][DataLabelingLiterals.DATASTORENAME]
        datastore = workspace.datastores[datastore_name]

        # Download
        path_to_download = os.path.join(datastore_name, input_file_path)
        datastore.download(target_path=datastore_name, prefix=input_file_path, overwrite=True)
        _convert_to_conll(path_to_download, label, final_conll_path)
        processed_input_file_counter += 1

    return data_filename


def load_test_dataset_for_labeling_service(
        workspace: Workspace,
        dataset_id: str,
        ner_dir: str,
        data_filename: str,
        data_label: str
) -> Tuple[str, List[str]]:
    """
    Load test dataset from Labeling service span format input.

    Labeling service will pass in TabularDataset that includes list of the paths for the actual text files
    and its label in a span format. This spans format data will be converted into CoNLL format (for test dataset,
    we leave out the true labels if given).

    :param workspace: workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param ner_dir: directory where data should be downloaded
    :param data_filename: filename to save converted dataset
    :param data_label: dataset type label
    :return name of the converted test data file and list of files referenced
    """
    # noinspection PyUnresolvedReferences
    import azureml.contrib.dataset
    _logger.info("Loading test dataset for labeling service")
    dataset_df = get_dataframe_from_dataset_id(workspace, dataset_id, data_label)

    os.makedirs(ner_dir, exist_ok=True)

    records = json.loads(dataset_df.to_json(orient='records'))
    test_file_path = os.path.join(ner_dir, data_filename)
    input_file_paths = []
    processed_input_file_counter = 1

    for record in records:
        _logger.info("Processing file {} of {}".format(processed_input_file_counter, len(records)))

        # Extract test data file info
        input_file_path = record[DataLabelingLiterals.IMAGE_URL][DataLabelingLiterals.RESOURCE_IDENTIFIER]
        datastore_name = record[DataLabelingLiterals.IMAGE_URL][
            DataLabelingLiterals.ARGUMENTS][DataLabelingLiterals.DATASTORENAME]

        # Download test data file
        datastore = workspace.datastores[datastore_name]
        path_to_download = os.path.join(datastore_name, input_file_path)
        datastore.download(target_path=datastore_name, prefix=input_file_path, overwrite=True)

        _convert_to_conll_no_label(path_to_download, test_file_path)
        input_file_paths.append(path_to_download)
        processed_input_file_counter += 1

    return data_filename, input_file_paths


def generate_results_for_labeling_service(
        predictions_file_path: str,
        input_file_paths: List[str]
) -> None:
    """
    Generate spans format output from predictions for labeling service

    :param predictions_file_path: predictions file path
    :param input_file_paths: list of test file downloaded paths
    """
    _logger.info("Generating output for labeling service")

    # Convert predictions in CoNLL format into spans format for labeling service
    with open(predictions_file_path, "r", encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        labeled_conll = f.read()

    # Remove original predictions.txt
    os.remove(predictions_file_path)

    # write converted entry to predictions.txt
    inferencing_results = labeled_conll.split('\n\n')
    for i in range(len(input_file_paths)):
        _logger.info("Processing file {} of {}".format(i + 1, len(input_file_paths)))
        input_conll = inferencing_results[i].split('\n')
        _convert_to_spans(input_conll, input_file_paths[i], predictions_file_path)


def _convert_to_conll(text_file_path, label_objects, output_file_path):
    # read the input file path
    input_file_path = os.path.join(os.getcwd(), text_file_path)

    conll_output_list = []
    offset_dict = {}

    # map all the offsetStarts to another dict
    for label in label_objects:
        cur_key = label['offsetStart']
        offset_dict[int(cur_key)] = [int(label['offsetEnd']), label['label']]

    # read the text content
    with open(input_file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        input_text_content = f.read()

    offset_dict_keys = list(offset_dict.keys())
    offset_dict_keys.sort()

    start_index = 0
    for offset in offset_dict_keys:
        _tokenize(
            start_index, offset, input_text_content, conll_output_list
        )
        _tokenize(
            offset, offset_dict[offset][0], input_text_content, conll_output_list, offset_dict[offset][1]
        )
        start_index = offset_dict[offset][0]

    # tokenize remaining text
    _tokenize(
        start_index, len(input_text_content), input_text_content, conll_output_list
    )

    # write conll to output file
    with open(output_file_path, "a") as f:
        f.writelines(conll_output_list)
        f.write('\n')


def _convert_to_conll_no_label(text_file_path, output_file_path):
    # read the input file path
    input_file_path = os.path.join(os.getcwd(), text_file_path)

    conll_output_list = []

    # read the text content
    with open(input_file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        input_text_content = f.read()

    start_index = 0
    # tokenize the text
    _tokenize_exclude_label(start_index, len(input_text_content), input_text_content, conll_output_list)

    # write conll to output file
    with open(output_file_path, "a") as f:
        f.writelines(conll_output_list)
        f.write('\n')


def _convert_to_spans(input_conll, text_file_path, output_file_path):
    try:
        input_file_path = os.path.join(os.getcwd(), text_file_path)

        with open(input_file_path, "r", encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
            input_text = f.read()
    except Exception as e:
        raise DataException._with_error(
            AzureMLError.create(
                DataPathNotFound, target="input_text", dprep_error=e)
        )

    offset_dict = {}
    i = 0
    j = 0
    prev_offset_start = 0
    prev_label_suffix = ''

    for line in input_conll:
        tokens = line.split()
        word = tokens[0]
        label = tokens[1]
        label_prefix = label[0]
        label_suffix = label[2:]
        confidence = tokens[2]
        if label_prefix == 'B':
            offset_dict[i] = [i + len(word), label_suffix, confidence]
            prev_offset_start = i
            prev_confidence = confidence
        elif label_prefix == 'I':
            if prev_label_suffix == label_suffix:
                offset_dict[prev_offset_start] = [i + len(word), label_suffix, prev_confidence]
            else:
                offset_dict[i] = [i + len(word), label_suffix, confidence]
                prev_offset_start = i
                prev_confidence = confidence
        else:
            prev_confidence = None
        prev_label_suffix = label_suffix

        # move index forward by length of the word
        i = i + len(word)
        j = j + len(word)

        while j < len(input_text) and input_text[j] == ' ':
            i = i + 1
            j = j + 1

    label_list = []
    confidence_list = []

    for offset in offset_dict:
        label_list.append({
            'label': str(offset_dict[offset][1]),
            'offsetStart': int(offset),
            'offsetEnd': int(offset_dict[offset][0])
        })
        confidence_list.append(float(offset_dict[offset][2]))

    text_file_full_path = DataLiterals.DATASTORE_PREFIX + text_file_path
    final_result = {
        DataLabelingLiterals.IMAGE_URL: text_file_full_path,
        DataLiterals.LABEL_COLUMN: label_list,
        DataLiterals.LABEL_CONFIDENCE: confidence_list
    }

    with open(output_file_path, "a") as f:
        f.write(json.dumps(final_result))
        f.write('\n')


def _tokenize(start_index, end_index, input_text_content, conll_output_list, tag=None):
    if start_index == end_index:
        return

    # split into tokens based on space
    tokens = input_text_content[start_index:end_index].split()

    if tag is None:
        for token in tokens:
            if token.isalpha():
                conll_output_list.append(token + ' O' + '\n')
            else:
                cur_string = ''
                # special case to handle tokens starting with a digit to handle numbers or dates
                if token[0].isdigit():
                    # check whether the last char is something other than digit then it will be its own token
                    if not token[len(token) - 1].isdigit():
                        conll_output_list.append(token[0:len(token) - 1] + ' O' + '\n')
                        conll_output_list.append(token[len(token) - 1] + ' O' + '\n')
                    # else print the whole number/date together
                    else:
                        conll_output_list.append(token + ' O' + '\n')
                else:
                    index = 0
                    for ch in token:
                        if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'):
                            cur_string += ch
                        else:
                            # output the alphabetical token so far
                            if len(cur_string) > 0:
                                conll_output_list.append(cur_string + ' O' + '\n')
                                cur_string = ''
                            # special case to handle " ' "
                            if ch == "'":
                                conll_output_list.append(token[index:] + ' O' + '\n')
                                break
                            # every other special character is its own token
                            else:
                                conll_output_list.append(ch + ' O' + '\n')
                        index = index + 1

                    if len(cur_string) > 0:
                        conll_output_list.append(cur_string + ' O' + '\n')
    else:
        conll_output_list.append(tokens[0] + ' B-' + tag + '\n')
        for t_index in range(1, len(tokens)):
            conll_output_list.append(tokens[t_index] + ' I-' + tag + '\n')


def _tokenize_exclude_label(start_index, end_index, input_text_content, conll_output_list):
    if start_index == end_index:
        return

    # split into tokens based on space
    tokens = input_text_content[start_index:end_index].split()

    for token in tokens:
        if token.isalpha():
            conll_output_list.append(token + '\n')
        else:
            cur_string = ''
            # special case to handle tokens starting with a digit to handle numbers or dates
            if token[0].isdigit():
                # check whether the last char is something other than digit then it will be its own token
                if not token[len(token) - 1].isdigit():
                    conll_output_list.append(token[0:len(token) - 1] + '\n')
                    conll_output_list.append(token[len(token) - 1] + '\n')
                # else print the whole number/date together
                else:
                    conll_output_list.append(token + '\n')
            else:
                index = 0
                for ch in token:
                    if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'):
                        cur_string += ch
                    else:
                        # output the alphabetical token so far
                        if len(cur_string) > 0:
                            conll_output_list.append(cur_string + '\n')
                            cur_string = ''
                        # special case to handle " ' "
                        if ch == "'":
                            conll_output_list.append(token[index:] + '\n')
                            break
                        # every other special character is its own token
                        else:
                            conll_output_list.append(ch + '\n')
                    index = index + 1

                if len(cur_string) > 0:
                    conll_output_list.append(cur_string + '\n')
