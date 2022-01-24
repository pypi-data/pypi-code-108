# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for NER."""

import logging
import os
from shutil import copyfile
from typing import List, Optional, Tuple

from torch.utils.data import Dataset
from transformers.tokenization_utils_base import PreTrainedTokenizerBase

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.dnn.nlp.common.constants import DataLiterals, NERModelParameters, Split
from azureml.automl.dnn.nlp.common._data_utils import download_file_dataset
from azureml.automl.dnn.nlp.ner.io.read.dataset_wrapper import DatasetWrapper
from azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper import load_dataset_for_labeling_service
from azureml.core.workspace import Workspace

_logger = logging.getLogger(__name__)


def load_dataset(
        workspace: Workspace,
        ner_dir: str,
        output_dir: str,
        labels_filename: str,
        tokenizer: PreTrainedTokenizerBase,
        dataset_id: str,
        validation_dataset_id: Optional[str],
        is_labeling_run: bool = False
) -> Tuple[Dataset, Dataset, List[str]]:
    """
    Save checkpoint to outputs directory.

    :param workspace: workspace where dataset is stored in blob
    :param ner_dir: directory where ner data should be downloaded
    :param output_dir: directory where output files of the training should be saved
    :param labels_filename: file storing unique labels from train and validation data
    :param tokenizer: pretrained bert tokenizer
    :param dataset_id: unique identifier to fetch dataset from datastore
    :param validation_dataset_id: unique identifier to fetch validation dataset from datastore
    :param is_labeling_run: whether the experiment is from labeling service
    """
    # Validate dataset ids
    Contract.assert_true(
        dataset_id != validation_dataset_id,
        DataLiterals.VALIDATION_DATASET_ID,
        reference_code=ReferenceCodes._NER_DUPLICATE_DATASET_ID,
        log_safe=True
    )

    if is_labeling_run:
        # Load datasets from dataset provided from labeling service
        train_ds_filename = load_dataset_for_labeling_service(
            workspace,
            dataset_id,
            ner_dir,
            DataLiterals.TRAIN_TEXT_FILENAME,
            Split.train
        )
        validation_ds_filename = None
        if validation_dataset_id:
            validation_ds_filename = load_dataset_for_labeling_service(
                workspace,
                validation_dataset_id,
                ner_dir,
                DataLiterals.VALIDATION_TEXT_FILENAME,
                Split.valid
            )
    else:
        # Load datasets from FileDataset
        train_ds_filename = download_file_dataset(
            dataset_id,
            Split.train,
            workspace,
            ner_dir
        )

        validation_ds_filename = None
        if validation_dataset_id:
            validation_ds_filename = download_file_dataset(
                validation_dataset_id,
                Split.valid,
                workspace,
                ner_dir
            )

    # Get unique labels
    label_list = _get_label_list(ner_dir, train_ds_filename)

    # Save label to refer during inference time
    _save_labels(ner_dir, output_dir, labels_filename, label_list)

    # Load Dataset
    file_path = os.path.join(ner_dir, train_ds_filename)
    with open(file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        train_data = f.read()
    train_dataset = DatasetWrapper(
        data=train_data,
        tokenizer=tokenizer,
        labels=label_list,
        max_seq_length=NERModelParameters.MAX_SEQ_LENGTH,
        mode=Split.train,
    )
    validation_dataset = None
    if validation_dataset_id:
        file_path = os.path.join(ner_dir, validation_ds_filename)
        with open(file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
            valid_data = f.read()
        validation_dataset = DatasetWrapper(
            data=valid_data,
            tokenizer=tokenizer,
            labels=label_list,
            max_seq_length=NERModelParameters.MAX_SEQ_LENGTH,
            mode=Split.valid,
        )

    return train_dataset, validation_dataset, label_list


def _get_label_list(
        ner_dir: str,
        train_ds_filename: str
) -> List[str]:
    """
    Get unique labels
    :param ner_dir: directory where train and validation datasets are
    :param output_dir: directory where labels file should be saved
    :param train_ds_filename: train dataset filename
    :param validation_ds_filename: validation dataset filename
    :param labels_filename: output labels filename
    :return:
    """
    # Get the unique label list
    unique_labels = set()
    file_path = os.path.join(ner_dir, train_ds_filename)
    with open(file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        for line in f:
            if line != "" and line != "\n":
                unique_labels.add(line.split()[-1])
    label_list = list(unique_labels)
    label_list.sort()

    return label_list


def _save_labels(
        ner_dir: str,
        output_dir: str,
        labels_filename: str,
        label_list: List[str]
) -> None:
    """
    Save labels to output folder
    :param ner_dir: directory where train and validation datasets are
    :param output_dir: directory where labels file should be saved
    :param labels_filename: output labels filename
    :param label_list: unique label list to save
    :return:
    """
    labels_data_path = os.path.join(ner_dir, labels_filename)
    labels_output_path = os.path.join(output_dir, labels_filename)
    with open(os.path.join(ner_dir, labels_filename), 'w') as f:
        for item in label_list:
            f.write("%s\n" % item)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    copyfile(labels_data_path, labels_output_path)
