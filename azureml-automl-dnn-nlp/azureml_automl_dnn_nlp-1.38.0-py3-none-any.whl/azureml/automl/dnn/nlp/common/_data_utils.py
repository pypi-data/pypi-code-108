# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for reading input data."""

import logging
import os
import pandas as pd

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.dnn.nlp.common.constants import Split
from azureml.core import Dataset as AmlDataset
from azureml.data.abstract_dataset import AbstractDataset
from azureml.core.workspace import Workspace

_logger = logging.getLogger(__name__)


def get_dataset_by_id(
        dataset_id: str,
        data_split: Split,
        workspace: Workspace
) -> AbstractDataset:
    """
    get dataset based on dataset id

    :param dataset_id: dataset id to retrieve
    :param data_split: Label for data split
    :param workspace: workspace to retrieve dataset from
    :return: dataset
    """
    Contract.assert_non_empty(
        dataset_id,
        "dataset_id",
        reference_code=ReferenceCodes._DNN_NLP_EMPTY_DATASET_ID,
        log_safe=True
    )
    ds = AmlDataset.get_by_id(workspace, dataset_id)
    _logger.info("Fetched {} data. Type: {}".format(data_split.value, type(ds)))
    return ds


def get_dataframe_from_dataset_id(
        workspace: Workspace,
        dataset_id: str,
        data_split: Split
) -> pd.DataFrame:
    """
    Get the train and val dataframes using the train and val dataset ids and the user's workspace

    :param workspace: workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param data_split: Label for data split
    :return: dataframe
    """
    ds = get_dataset_by_id(dataset_id, data_split, workspace)
    df = ds.to_pandas_dataframe()
    return df


def download_file_dataset(
        dataset_id: str,
        data_split: Split,
        workspace: Workspace,
        ner_dir: str,
        overwrite: bool = False
) -> str:
    """
    load given dataset to data path and return the name of the file in reference

    :param dataset_id: dataset id to retrieve
    :param data_split: Label for data split
    :param workspace: workspace to retrieve dataset from
    :param ner_dir: directory where data should be downloaded
    :param overwrite: whether existing file can be overwritten
    :return: file name related to the dataset
    """
    _logger.info("Downloading file dataset for: {}".format(data_split.value))
    dataset = get_dataset_by_id(dataset_id, data_split, workspace)

    # to_path() returns format ["/filename.txt"], need to strip the "/"
    file_name = dataset.to_path()[0][1:]

    # Download data to ner_dir
    if not os.path.exists(ner_dir):
        os.makedirs(ner_dir)
    dataset.download(target_path=ner_dir, overwrite=overwrite)

    return file_name
